"""
Timestamp Extractor Module

Extracts accurate timestamps from audio using OpenAI Whisper.
Generates SRT-formatted subtitles with word-level timing.
"""

import logging
from typing import Callable, Optional, List, Dict
from pathlib import Path
import asyncio
from openai import AsyncOpenAI
import re

logger = logging.getLogger(__name__)


class TimestampExtractor:
    """Extract timestamps from audio using OpenAI Whisper."""

    def __init__(self, api_key: str):
        """
        Initialize the timestamp extractor.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "whisper-1"

    async def extract_timestamps(
        self,
        audio_path: Path,
        output_srt_path: Optional[Path] = None,
        output_word_timestamps_path: Optional[Path] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Dict:
        """
        Extract timestamps from audio file using Whisper with WORD-LEVEL granularity.

        Args:
            audio_path: Path to the audio file
            output_srt_path: Optional path to save SRT subtitle file
            output_word_timestamps_path: Optional path to save word-level timestamps JSON
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary containing:
            - text: Full transcription text
            - segments: List of timed segments with text and word-level timestamps
            - srt: SRT-formatted subtitle text
            - duration: Total audio duration in seconds
            - word_timestamps: Detailed word-level timing data

        Raises:
            Exception: If timestamp extraction fails
        """
        try:
            if progress_callback:
                progress_callback("Extracting word-level timestamps with Whisper...", 45)

            logger.info(f"Processing audio file: {audio_path}")

            # Open and transcribe audio file with WORD-LEVEL timestamps
            with open(audio_path, "rb") as audio_file:
                try:
                    # Try with word-level timestamps (requires openai>=1.14.0)
                    response = await self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["word", "segment"],  # CRITICAL: Enable word-level timestamps
                    )
                except TypeError as e:
                    if "timestamp_granularities" in str(e):
                        logger.warning("Word-level timestamps not supported (openai library too old). Please upgrade: pip install openai>=1.14.0")
                        logger.warning("Falling back to segment-level timestamps only...")
                        # Fallback to segment-level only (works with older openai versions)
                        response = await self.client.audio.transcriptions.create(
                            model=self.model,
                            file=audio_file,
                            response_format="verbose_json",
                        )
                    else:
                        raise

            logger.info("Whisper transcription complete with word-level timestamps")

            # Extract segments with timestamps AND word-level data
            segments = []
            if hasattr(response, 'segments') and response.segments:
                for idx, segment in enumerate(response.segments):
                    # Handle both dict and object attribute access
                    start = segment.get("start") if isinstance(segment, dict) else segment.start
                    end = segment.get("end") if isinstance(segment, dict) else segment.end
                    text = segment.get("text") if isinstance(segment, dict) else segment.text

                    # Extract word-level timestamps for this segment
                    words = []
                    if isinstance(segment, dict) and "words" in segment:
                        words = segment["words"]
                    elif hasattr(segment, "words") and segment.words:
                        words = [
                            {
                                "word": w.word if hasattr(w, "word") else w.get("word"),
                                "start": w.start if hasattr(w, "start") else w.get("start"),
                                "end": w.end if hasattr(w, "end") else w.get("end"),
                            }
                            for w in segment.words
                        ]

                    segments.append(
                        {
                            "id": idx,
                            "start": start,
                            "end": end,
                            "text": text.strip(),
                            "words": words,  # NEW: Word-level timestamps
                        }
                    )
            else:
                # Fallback: create single segment from full text
                logger.warning("No segments found in response, creating single segment")
                segments.append(
                    {
                        "id": 0,
                        "start": 0.0,
                        "end": 60.0,  # Default 60 seconds
                        "text": response.text.strip() if hasattr(response, 'text') else "",
                        "words": [],  # No word-level data in fallback
                    }
                )

            # Generate SRT content (segment-level subtitles)
            srt_content = self._generate_srt(segments)

            # Save SRT file if path provided
            if output_srt_path:
                output_srt_path.parent.mkdir(parents=True, exist_ok=True)
                await asyncio.to_thread(
                    output_srt_path.write_text, srt_content, encoding="utf-8"
                )
                logger.info(f"SRT subtitles saved to {output_srt_path}")

            # Save word-level timestamps JSON if path provided
            if output_word_timestamps_path:
                import json
                word_timestamps_data = {
                    "segments": segments  # Already includes word-level data
                }
                output_word_timestamps_path.parent.mkdir(parents=True, exist_ok=True)
                await asyncio.to_thread(
                    output_word_timestamps_path.write_text,
                    json.dumps(word_timestamps_data, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                logger.info(f"Word-level timestamps saved to {output_word_timestamps_path}")

            # Extract full text from response
            full_text = ""
            if hasattr(response, 'text'):
                full_text = response.text
            elif segments:
                # Concatenate all segment texts
                full_text = " ".join(seg["text"] for seg in segments)

            # Count total words extracted
            total_words = sum(len(seg.get("words", [])) for seg in segments)

            result = {
                "text": full_text,
                "segments": segments,
                "srt": srt_content,
                "duration": segments[-1]["end"] if segments else 0,
                "word_count": total_words,  # NEW: Total word count
            }

            if progress_callback:
                progress_callback(
                    f"Extracted {len(segments)} segments with {total_words} words", 50
                )

            logger.info(f"Extracted {len(segments)} segments with {total_words} word-level timestamps, duration: {result['duration']:.2f}s")

            return result

        except Exception as e:
            logger.error(f"Timestamp extraction failed: {e}")
            raise Exception(f"Failed to extract timestamps: {e}")

    def _generate_srt(self, segments: List[Dict]) -> str:
        """
        Generate SRT-formatted subtitle content.

        Args:
            segments: List of segments with start, end, and text

        Returns:
            SRT-formatted string
        """
        srt_lines = []

        for segment in segments:
            # Segment number
            srt_lines.append(str(segment["id"] + 1))

            # Timestamp line
            start_time = self._format_timestamp(segment["start"])
            end_time = self._format_timestamp(segment["end"])
            srt_lines.append(f"{start_time} --> {end_time}")

            # Text content
            srt_lines.append(segment["text"])

            # Empty line between segments
            srt_lines.append("")

        return "\n".join(srt_lines)

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as SRT timestamp (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    async def align_script_with_timestamps(
        self,
        script: List[Dict[str, str]],
        timestamp_data: Dict,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict]:
        """
        Align script segments with extracted timestamps.

        Args:
            script: Original script with speaker and text
            timestamp_data: Timestamp data from extract_timestamps
            progress_callback: Optional callback for progress updates

        Returns:
            List of script segments with added timing information:
            [{"speaker": "Alex", "text": "...", "start": 0.5, "end": 3.2}, ...]

        Raises:
            Exception: If alignment fails
        """
        try:
            if progress_callback:
                progress_callback("Aligning script with timestamps...", 50)

            segments = timestamp_data["segments"]
            aligned_script = []

            # Simple alignment: match script segments to timestamp segments
            segment_idx = 0
            for script_segment in script:
                if segment_idx >= len(segments):
                    # No more timestamps, use approximate timing
                    logger.warning(
                        f"No timestamp for segment: {script_segment['text'][:50]}"
                    )
                    if aligned_script:
                        # Use last end time
                        last_end = aligned_script[-1]["end"]
                        aligned_script.append(
                            {
                                **script_segment,
                                "start": last_end,
                                "end": last_end + 2.0,  # Assume 2 seconds
                            }
                        )
                    else:
                        aligned_script.append(
                            {**script_segment, "start": 0.0, "end": 2.0}
                        )
                    continue

                # Find best matching timestamp segment
                script_words = set(script_segment["text"].lower().split())
                best_match_idx = segment_idx
                best_match_score = 0

                # Look ahead a few segments for best match
                for i in range(segment_idx, min(segment_idx + 3, len(segments))):
                    segment_words = set(segments[i]["text"].lower().split())
                    common_words = script_words & segment_words
                    score = len(common_words)

                    if score > best_match_score:
                        best_match_score = score
                        best_match_idx = i

                # Use the best match
                matched_segment = segments[best_match_idx]
                aligned_script.append(
                    {
                        **script_segment,
                        "start": matched_segment["start"],
                        "end": matched_segment["end"],
                    }
                )

                segment_idx = best_match_idx + 1

            logger.info(f"Aligned {len(aligned_script)} script segments with timestamps")

            if progress_callback:
                progress_callback("Script alignment complete", 55)

            return aligned_script

        except Exception as e:
            logger.error(f"Script alignment failed: {e}")
            raise Exception(f"Failed to align script with timestamps: {e}")

    def extract_key_words_for_animation(self, segments: List[Dict]) -> List[Dict]:
        """
        Extract key words from segments for animation synchronization.
        Identifies important words (nouns, verbs, adjectives) that should trigger animations.

        Args:
            segments: List of segments with word-level timestamps

        Returns:
            List of key words with timing and suggested animation actions:
            [{"word": "Einstein", "time": 1.2, "segment_id": 0, "type": "noun"}, ...]
        """
        import re

        # Keywords that typically warrant animation emphasis
        important_word_patterns = [
            r'\b[A-Z][a-z]+',  # Proper nouns (capitalized words)
            r'\b(equation|formula|theory|concept|principle|law|rule|function|variable|constant)\b',  # Math/science terms
            r'\b(increase|decrease|grow|shrink|expand|contract|transform|change|shift|rotate|move)\b',  # Action verbs
            r'\b(important|critical|key|main|central|essential|fundamental|significant)\b',  # Emphasis adjectives
            r'\b(first|second|third|finally|next|then|now|here|this|that)\b',  # Sequence/reference words
        ]

        key_words = []
        for segment in segments:
            segment_id = segment.get("id", 0)
            words = segment.get("words", [])

            for word_data in words:
                word_text = word_data.get("word", "").strip()
                word_start = word_data.get("start", 0.0)

                # Check if word matches any important pattern
                for pattern in important_word_patterns:
                    if re.search(pattern, word_text, re.IGNORECASE):
                        key_words.append({
                            "word": word_text,
                            "time": word_start,
                            "segment_id": segment_id,
                            "pattern_matched": pattern
                        })
                        break

        logger.info(f"Extracted {len(key_words)} key words for animation sync")
        return key_words

    def parse_srt_file(self, srt_path: Path) -> List[Dict]:
        """
        Parse an SRT file into structured segments.

        Args:
            srt_path: Path to SRT file

        Returns:
            List of segments with id, start, end, and text
        """
        try:
            content = srt_path.read_text(encoding="utf-8")
            segments = []

            # Split by double newlines to get individual subtitle blocks
            blocks = re.split(r"\n\n+", content.strip())

            for block in blocks:
                lines = block.strip().split("\n")
                if len(lines) < 3:
                    continue

                # Parse segment ID
                segment_id = int(lines[0])

                # Parse timestamps
                timestamp_line = lines[1]
                match = re.match(
                    r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})",
                    timestamp_line,
                )
                if not match:
                    continue

                start_h, start_m, start_s, start_ms = map(int, match.groups()[:4])
                end_h, end_m, end_s, end_ms = map(int, match.groups()[4:])

                start = start_h * 3600 + start_m * 60 + start_s + start_ms / 1000
                end = end_h * 3600 + end_m * 60 + end_s + end_ms / 1000

                # Parse text (may be multiple lines)
                text = "\n".join(lines[2:])

                segments.append(
                    {"id": segment_id - 1, "start": start, "end": end, "text": text}
                )

            logger.info(f"Parsed {len(segments)} segments from SRT file")
            return segments

        except Exception as e:
            logger.error(f"Failed to parse SRT file: {e}")
            raise Exception(f"SRT parsing failed: {e}")
