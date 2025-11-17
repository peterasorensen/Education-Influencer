"""
Audio Generator Module

Generates audio for each character using OpenAI TTS with different voices.
Combines individual audio segments into a complete narration track.
Supports voice cloning using Tortoise TTS via Replicate.
"""

import logging
from typing import Callable, Optional, List, Dict
from pathlib import Path
import asyncio
from openai import AsyncOpenAI
from pydub import AudioSegment
import replicate
import os
import tempfile
import json

logger = logging.getLogger(__name__)


class AudioGenerator:
    """Generate audio using OpenAI TTS with different voices for each character."""

    # Available voices for dynamic assignment
    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(
        self,
        api_key: str,
        replicate_token: Optional[str] = None,
        audio_model: Optional[str] = None,
        celebrity_audio_samples: Optional[Dict[str, Path]] = None,
    ):
        """
        Initialize the audio generator.

        Args:
            api_key: OpenAI API key
            replicate_token: Optional Replicate API token for Tortoise TTS
            audio_model: Optional audio model to use (e.g., Tortoise TTS)
            celebrity_audio_samples: Optional dict mapping celebrity names to audio sample paths
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "tts-1"
        self.speaker_voice_map = {}
        self.voice_index = 0

        # Replicate/Tortoise TTS support
        self.replicate_token = replicate_token
        self.audio_model = audio_model
        self.celebrity_audio_samples = celebrity_audio_samples or {}
        self.use_tortoise = audio_model and "tortoise" in audio_model.lower()

        if self.use_tortoise:
            if not replicate_token:
                logger.warning("Tortoise TTS enabled but no Replicate token provided. Falling back to OpenAI TTS.")
                self.use_tortoise = False
            else:
                logger.info(f"Using Tortoise TTS model: {audio_model}")
                os.environ["REPLICATE_API_TOKEN"] = replicate_token

    def _get_voice_for_speaker(self, speaker: str) -> str:
        """Assign a unique voice to each speaker dynamically."""
        if speaker not in self.speaker_voice_map:
            voice = self.AVAILABLE_VOICES[self.voice_index % len(self.AVAILABLE_VOICES)]
            self.speaker_voice_map[speaker] = voice
            self.voice_index += 1
        return self.speaker_voice_map[speaker]

    def _get_audio_sample_for_speaker(self, speaker: str) -> Optional[Path]:
        """
        Map speaker to celebrity audio sample based on speaker name or assigned voice.

        Args:
            speaker: Speaker name

        Returns:
            Path to audio sample or None if not using Tortoise TTS
        """
        if not self.use_tortoise:
            return None

        # Direct name mapping (if speaker is literally "Drake" or "Sydney")
        speaker_lower = speaker.lower()
        if "drake" in speaker_lower:
            return self.celebrity_audio_samples.get("drake")
        elif "sydney" in speaker_lower:
            return self.celebrity_audio_samples.get("sydney_sweeney")

        # Otherwise, map based on assigned voice
        voice = self._get_voice_for_speaker(speaker)

        # Map voices to celebrities (same logic as in main.py)
        male_voices = ["onyx", "echo", "fable"]
        female_voices = ["nova", "shimmer", "alloy"]

        if voice in male_voices:
            return self.celebrity_audio_samples.get("drake")
        elif voice in female_voices:
            return self.celebrity_audio_samples.get("sydney_sweeney")
        else:
            # Default to drake
            return self.celebrity_audio_samples.get("drake")

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
            # Get voice for speaker (assigns voice if not already assigned)
            voice = self._get_voice_for_speaker(speaker)

            # Use Tortoise TTS if enabled
            if self.use_tortoise:
                return await self._generate_tortoise_audio(text, speaker, output_path)

            # Otherwise use OpenAI TTS (default)
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

    async def _generate_tortoise_audio(
        self, text: str, speaker: str, output_path: Path
    ) -> Path:
        """
        Generate audio using Tortoise TTS via Replicate.

        Args:
            text: The text to convert to speech
            speaker: The speaker name (determines audio sample)
            output_path: Path to save the audio file

        Returns:
            Path to the generated audio file

        Raises:
            Exception: If audio generation fails
        """
        try:
            # Get audio sample for this speaker
            audio_sample = self._get_audio_sample_for_speaker(speaker)

            if not audio_sample or not audio_sample.exists():
                logger.warning(f"Audio sample not found for {speaker}, falling back to OpenAI TTS")
                return await self._generate_openai_audio(text, speaker, output_path)

            logger.info(f"Generating Tortoise TTS audio for {speaker} using sample: {audio_sample}")

            # Run Tortoise TTS model - Replicate accepts file handles
            # We need to open the file and keep it open during the API call
            with open(audio_sample, "rb") as audio_file:
                output = await asyncio.to_thread(
                    replicate.run,
                    self.audio_model,
                    input={
                        "text": text,
                        "speaker_reference": audio_file,
                    }
                )

            # Download the output audio
            if output:
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Handle different output types from Replicate
                import httpx

                # Extract URL from output (could be string, FileOutput, or iterator)
                if isinstance(output, str):
                    output_url = output
                elif hasattr(output, 'url'):
                    output_url = output.url
                elif hasattr(output, '__iter__') and not isinstance(output, str):
                    # Iterator - take first item
                    output_url = next(iter(output))
                    if hasattr(output_url, 'url'):
                        output_url = output_url.url
                else:
                    output_url = str(output)

                logger.info(f"Downloading Tortoise TTS output from: {output_url}")

                # Download to temporary file first
                temp_path = output_path.with_suffix('.tmp.mp3')

                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(output_url)
                    response.raise_for_status()

                    with open(temp_path, "wb") as f:
                        f.write(response.content)

                logger.info(f"Downloaded Tortoise TTS output to {temp_path} ({len(response.content)} bytes)")

                # Re-encode using ffmpeg to ensure compatibility with pydub
                # Tortoise TTS might output MP3s that pydub can't parse directly
                import subprocess

                try:
                    logger.info(f"Re-encoding MP3 for pydub compatibility...")
                    result = await asyncio.to_thread(
                        subprocess.run,
                        [
                            "ffmpeg", "-y", "-i", str(temp_path),
                            "-acodec", "libmp3lame", "-ab", "192k",
                            "-ar", "24000",  # Standard sample rate
                            str(output_path)
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode != 0:
                        logger.error(f"ffmpeg re-encoding failed: {result.stderr}")
                        # Fall back to using temp file as-is
                        import shutil
                        shutil.move(str(temp_path), str(output_path))
                    else:
                        # Remove temp file
                        temp_path.unlink()
                        logger.info(f"Successfully re-encoded MP3")

                except Exception as e:
                    logger.error(f"Re-encoding failed: {e}, using original file")
                    # Fall back to using temp file as-is
                    import shutil
                    shutil.move(str(temp_path), str(output_path))

                logger.info(f"Tortoise TTS audio saved to {output_path}")
                return output_path
            else:
                raise Exception("Tortoise TTS returned no output")

        except Exception as e:
            logger.error(f"Failed to generate Tortoise TTS audio for {speaker}: {e}")
            # Fall back to OpenAI TTS
            logger.warning(f"Falling back to OpenAI TTS for {speaker}")
            return await self._generate_openai_audio(text, speaker, output_path)

    async def _generate_openai_audio(
        self, text: str, speaker: str, output_path: Path
    ) -> Path:
        """
        Generate audio using OpenAI TTS (fallback method).

        Args:
            text: The text to convert to speech
            speaker: The speaker name (determines voice)
            output_path: Path to save the audio file

        Returns:
            Path to the generated audio file

        Raises:
            Exception: If audio generation fails
        """
        voice = self._get_voice_for_speaker(speaker)
        logger.info(f"Generating OpenAI TTS audio for {speaker} with voice {voice}")

        # Generate speech
        response = await self.client.audio.speech.create(
            model=self.model, voice=voice, input=text, response_format="mp3"
        )

        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(response.stream_to_file, str(output_path))

        logger.info(f"Audio saved to {output_path}")
        return output_path

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

            # Save speaker-to-voice mapping for resume functionality
            voice_map_path = output_dir.parent / "speaker_voice_map.json"
            voice_map_path.write_text(json.dumps(self.speaker_voice_map, indent=2))
            logger.info(f"Speaker voice map saved to {voice_map_path}")

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

            # FFmpeg parameters to handle MP3s without proper headers or with unusual formats
            # This is especially useful for MP3s generated by Tortoise TTS
            ffmpeg_params = [
                "-analyzeduration", "10000000",  # Analyze up to 10MB
                "-probesize", "10000000",        # Probe up to 10MB
                "-err_detect", "ignore_err",     # Ignore decoding errors
            ]

            # Load first segment with robust parameters
            combined = await asyncio.to_thread(
                AudioSegment.from_mp3,
                str(segment_files[0]),
                parameters=ffmpeg_params
            )

            # Create silence segment
            silence = AudioSegment.silent(duration=silence_duration_ms)

            # Add remaining segments with silence
            for segment_file in segment_files[1:]:
                audio_segment = await asyncio.to_thread(
                    AudioSegment.from_mp3,
                    str(segment_file),
                    parameters=ffmpeg_params
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
