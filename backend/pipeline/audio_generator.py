"""
Audio Generator Module

Generates audio for each character using OpenAI TTS with different voices.
Combines individual audio segments into a complete narration track.
"""

import logging
from typing import Callable, Optional, List, Dict
from pathlib import Path
import asyncio
from openai import AsyncOpenAI
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class AudioGenerator:
    """Generate audio using OpenAI TTS with different voices for each character."""

    # Available voices for dynamic assignment
    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, api_key: str):
        """
        Initialize the audio generator.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "tts-1"
        self.speaker_voice_map = {}
        self.voice_index = 0

    def _get_voice_for_speaker(self, speaker: str) -> str:
        """Assign a unique voice to each speaker dynamically."""
        if speaker not in self.speaker_voice_map:
            voice = self.AVAILABLE_VOICES[self.voice_index % len(self.AVAILABLE_VOICES)]
            self.speaker_voice_map[speaker] = voice
            self.voice_index += 1
        return self.speaker_voice_map[speaker]

    async def generate_audio_segment(
        self, text: str, speaker: str, output_path: Path
    ) -> Path:
        """
        Generate audio for a single script segment.

        Args:
            text: The text to convert to speech
            speaker: The speaker name (determines voice)
            output_path: Path to save the audio file

        Returns:
            Path to the generated audio file

        Raises:
            Exception: If audio generation fails
        """
        try:
            # Get voice for speaker
            voice = self._get_voice_for_speaker(speaker)

            logger.info(f"Generating audio for {speaker} with voice {voice}")

            # Generate speech
            response = await self.client.audio.speech.create(
                model=self.model, voice=voice, input=text, response_format="mp3"
            )

            # Save to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(response.stream_to_file, str(output_path))

            logger.info(f"Audio saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate audio for {speaker}: {e}")
            raise Exception(f"Audio generation failed for {speaker}: {e}")

    async def generate_full_audio(
        self,
        script: List[Dict[str, str]],
        output_dir: Path,
        final_output_path: Path,
        silence_duration_ms: int = 500,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Generate audio for the complete script with all speakers.

        Args:
            script: List of script segments with speaker and text
            output_dir: Directory to save individual audio segments
            final_output_path: Path for the final combined audio file
            silence_duration_ms: Duration of silence between segments in milliseconds
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the final combined audio file

        Raises:
            Exception: If audio generation fails
        """
        try:
            if progress_callback:
                progress_callback("Starting audio generation...", 20)

            output_dir.mkdir(parents=True, exist_ok=True)
            segment_files = []

            # Generate audio for each segment
            total_segments = len(script)
            for idx, segment in enumerate(script):
                speaker = segment["speaker"]
                text = segment["text"]

                if progress_callback:
                    progress = 20 + int((idx / total_segments) * 20)
                    progress_callback(
                        f"Generating audio for {speaker} ({idx + 1}/{total_segments})...",
                        progress,
                    )

                # Generate audio segment
                segment_path = output_dir / f"segment_{idx:03d}_{speaker}.mp3"
                await self.generate_audio_segment(text, speaker, segment_path)
                segment_files.append(segment_path)

            if progress_callback:
                progress_callback("Combining audio segments...", 40)

            # Combine all segments with silence in between
            combined_audio = await self._combine_audio_segments(
                segment_files, silence_duration_ms
            )

            # Export final audio
            final_output_path.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(
                combined_audio.export,
                str(final_output_path),
                format="mp3",
                bitrate="192k",
            )

            logger.info(f"Final audio saved to {final_output_path}")

            if progress_callback:
                progress_callback("Audio generation complete", 45)

            return final_output_path

        except Exception as e:
            logger.error(f"Failed to generate full audio: {e}")
            raise Exception(f"Full audio generation failed: {e}")

    async def _combine_audio_segments(
        self, segment_files: List[Path], silence_duration_ms: int
    ) -> AudioSegment:
        """
        Combine multiple audio segments with silence in between.

        Args:
            segment_files: List of paths to audio segments
            silence_duration_ms: Duration of silence between segments

        Returns:
            Combined AudioSegment

        Raises:
            Exception: If combining fails
        """
        try:
            logger.info(f"Combining {len(segment_files)} audio segments")

            # Load first segment
            combined = await asyncio.to_thread(
                AudioSegment.from_mp3, str(segment_files[0])
            )

            # Create silence segment
            silence = AudioSegment.silent(duration=silence_duration_ms)

            # Add remaining segments with silence
            for segment_file in segment_files[1:]:
                audio_segment = await asyncio.to_thread(
                    AudioSegment.from_mp3, str(segment_file)
                )
                combined = combined + silence + audio_segment

            logger.info(
                f"Combined audio duration: {len(combined) / 1000:.2f} seconds"
            )
            return combined

        except Exception as e:
            logger.error(f"Failed to combine audio segments: {e}")
            raise Exception(f"Audio combination failed: {e}")

    async def generate_silent_audio(
        self, duration_seconds: float, output_path: Path
    ) -> Path:
        """
        Generate a silent audio file of specified duration.

        Args:
            duration_seconds: Duration in seconds
            output_path: Path to save the silent audio

        Returns:
            Path to the generated silent audio file
        """
        try:
            logger.info(f"Generating {duration_seconds}s of silence")

            silence = AudioSegment.silent(duration=int(duration_seconds * 1000))
            output_path.parent.mkdir(parents=True, exist_ok=True)

            await asyncio.to_thread(
                silence.export, str(output_path), format="mp3", bitrate="192k"
            )

            logger.info(f"Silent audio saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate silent audio: {e}")
            raise Exception(f"Silent audio generation failed: {e}")
