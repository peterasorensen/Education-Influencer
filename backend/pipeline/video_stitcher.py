"""
Video Stitcher Module

Combines audio narration with Manim-generated visuals using ffmpeg.
Handles timing synchronization and video encoding.
"""

import logging
from typing import Callable, Optional, List
from pathlib import Path
import asyncio
import subprocess
import json

logger = logging.getLogger(__name__)


class VideoStitcher:
    """Combine audio and video using ffmpeg."""

    def __init__(self):
        """Initialize the video stitcher."""
        pass

    async def stitch_video(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Combine video and audio into final output.

        Args:
            video_path: Path to the Manim-generated video (silent)
            audio_path: Path to the generated audio file
            output_path: Path for the final combined video
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the final video file

        Raises:
            Exception: If stitching fails
        """
        try:
            if progress_callback:
                progress_callback("Combining audio and video...", 85)

            logger.info(f"Stitching video: {video_path} with audio: {audio_path}")

            # Verify input files exist
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Get video and audio durations
            video_duration = await self._get_duration(video_path)
            audio_duration = await self._get_duration(audio_path)

            logger.info(
                f"Video duration: {video_duration:.2f}s, Audio duration: {audio_duration:.2f}s"
            )

            # Prepare output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build ffmpeg command based on duration difference
            if video_duration < audio_duration - 1.0:
                # Video is shorter - loop it to match audio duration
                logger.info(f"Looping video to match audio duration")
                cmd = [
                    "ffmpeg",
                    "-stream_loop", "-1",  # Loop video indefinitely
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",  # Stop when audio ends
                    "-y",
                    str(output_path),
                ]
            elif audio_duration < video_duration - 1.0:
                # Audio is shorter - trim video to match
                logger.info(f"Trimming video to match audio duration")
                cmd = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",  # Stop when audio ends
                    "-y",
                    str(output_path),
                ]
            else:
                # Durations are close - just combine
                logger.info(f"Combining video and audio (durations match)")
                cmd = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    "-y",
                    str(output_path),
                ]

            logger.info(f"Running ffmpeg: {' '.join(cmd)}")

            # Run ffmpeg
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                error_msg = f"ffmpeg failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Verify output file
            if not output_path.exists():
                raise Exception(f"Output file not created: {output_path}")

            output_size = output_path.stat().st_size
            logger.info(
                f"Video stitching complete. Output size: {output_size / 1024 / 1024:.2f} MB"
            )

            if progress_callback:
                progress_callback("Video stitching complete", 95)

            return output_path

        except subprocess.TimeoutExpired:
            error_msg = "Video stitching timeout (5 minutes)"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Video stitching failed: {e}")
            raise Exception(f"Failed to stitch video: {e}")

    async def stitch_video_advanced(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        sync_mode: str = "stretch",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Advanced video stitching with sync options.

        Args:
            video_path: Path to the Manim-generated video
            audio_path: Path to the generated audio
            output_path: Path for the final video
            sync_mode: How to handle duration mismatch:
                - "stretch": Stretch video to match audio duration
                - "loop": Loop video to match audio duration
                - "trim": Trim longer stream to match shorter one
                - "shortest": Use shortest duration (default ffmpeg behavior)
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the final video file

        Raises:
            Exception: If stitching fails
        """
        try:
            if progress_callback:
                progress_callback(
                    f"Combining video and audio (mode: {sync_mode})...", 85
                )

            logger.info(f"Advanced stitching with sync mode: {sync_mode}")

            # Get durations
            video_duration = await self._get_duration(video_path)
            audio_duration = await self._get_duration(audio_path)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            if sync_mode == "stretch":
                # Stretch video to match audio duration
                cmd = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-filter_complex",
                    f"[0:v]setpts={video_duration/audio_duration}*PTS[v]",
                    "-map", "[v]",
                    "-map", "1:a",
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-y",
                    str(output_path),
                ]

            elif sync_mode == "loop":
                # Loop video to match audio duration
                cmd = [
                    "ffmpeg",
                    "-stream_loop", "-1",  # Loop indefinitely
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",  # Stop when audio ends
                    "-y",
                    str(output_path),
                ]

            elif sync_mode == "trim":
                # Trim to shortest duration
                min_duration = min(video_duration, audio_duration)
                cmd = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-t", str(min_duration),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-y",
                    str(output_path),
                ]

            else:  # shortest or default
                cmd = [
                    "ffmpeg",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    "-y",
                    str(output_path),
                ]

            logger.info(f"Running ffmpeg: {' '.join(cmd)}")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                error_msg = f"ffmpeg failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            if not output_path.exists():
                raise Exception(f"Output file not created: {output_path}")

            logger.info(f"Advanced stitching complete: {output_path}")

            if progress_callback:
                progress_callback("Video stitching complete", 95)

            return output_path

        except Exception as e:
            logger.error(f"Advanced video stitching failed: {e}")
            raise Exception(f"Failed to stitch video: {e}")

    async def _get_duration(self, media_path: Path) -> float:
        """
        Get duration of a media file using ffprobe.

        Args:
            media_path: Path to media file

        Returns:
            Duration in seconds

        Raises:
            Exception: If duration extraction fails
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(media_path),
            ]

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                raise Exception(f"ffprobe failed: {result.stderr}")

            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])

            return duration

        except Exception as e:
            logger.error(f"Failed to get duration for {media_path}: {e}")
            raise Exception(f"Duration extraction failed: {e}")

    async def extract_audio(
        self,
        video_path: Path,
        output_path: Path,
    ) -> Path:
        """
        Extract audio from video file.

        Args:
            video_path: Path to video file
            output_path: Path for extracted audio file

        Returns:
            Path to extracted audio file

        Raises:
            Exception: If audio extraction fails
        """
        try:
            logger.info(f"Extracting audio from {video_path} to {output_path}")

            # Verify input file exists
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")

            # Prepare output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build ffmpeg command to extract audio
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vn",  # No video
                "-acodec", "libmp3lame",  # MP3 codec
                "-b:a", "192k",  # Audio bitrate
                "-y",  # Overwrite output file
                str(output_path),
            ]

            # Run ffmpeg command
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                raise Exception(f"ffmpeg audio extraction failed: {result.stderr}")

            logger.info(f"Audio extracted successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to extract audio from {video_path}: {e}")
            raise Exception(f"Audio extraction failed: {e}")

    async def add_subtitles(
        self,
        video_path: Path,
        srt_path: Path,
        output_path: Path,
        subtitle_style: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Add subtitles to video from SRT file.

        Args:
            video_path: Path to video file
            srt_path: Path to SRT subtitle file
            output_path: Path for output video with subtitles
            subtitle_style: Optional subtitle style (ffmpeg subtitles filter style)
            progress_callback: Optional callback for progress updates

        Returns:
            Path to video with subtitles

        Raises:
            Exception: If subtitle addition fails
        """
        try:
            if progress_callback:
                progress_callback("Adding subtitles to video...", 90)

            logger.info(f"Adding subtitles from {srt_path} to {video_path}")

            # Verify files exist
            if not video_path.exists():
                raise FileNotFoundError(f"Video not found: {video_path}")
            if not srt_path.exists():
                raise FileNotFoundError(f"SRT file not found: {srt_path}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Process SRT to ensure single-line display
            processed_srt = await self._process_srt_for_single_line(srt_path)

            # Default subtitle style
            # For 9:16 video (1080x1920), position at y=960 (middle, dividing line)
            # Alignment=8 for top-center alignment (positions from top)
            # MarginV=960 sets position 960px from top (at the dividing line)
            # FontSize=22 for smaller, readable text (reduced from 28)
            # BorderStyle=3 for opaque background box (BorderStyle=4 is invalid)
            # BackColour=&H80000000 (semi-transparent black background)
            # Outline=0 (no outline needed with background box)
            # Shadow=0 for no shadow (cleaner look)
            if not subtitle_style:
                subtitle_style = "FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,BackColour=&H80000000,Alignment=8,MarginV=960,Outline=0,Shadow=0"

            # Build ffmpeg command
            # Note: On some systems, the subtitles filter path needs escaping
            processed_srt_escaped = str(processed_srt).replace("\\", "/").replace(":", "\\:")

            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vf", f"subtitles={processed_srt_escaped}:force_style='{subtitle_style}'",
                "-c:a", "copy",
                "-y",
                str(output_path),
            ]

            logger.info(f"Running ffmpeg with subtitles (single-line, top-aligned at y=960 from top)")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                error_msg = f"Subtitle addition failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Clean up processed SRT file
            if processed_srt != srt_path:
                processed_srt.unlink(missing_ok=True)

            if not output_path.exists():
                raise Exception(f"Output file not created: {output_path}")

            logger.info(f"Subtitles added successfully: {output_path}")

            if progress_callback:
                progress_callback("Subtitles added successfully", 95)

            return output_path

        except Exception as e:
            logger.error(f"Failed to add subtitles: {e}")
            raise Exception(f"Subtitle addition failed: {e}")

    async def _process_srt_for_single_line(self, srt_path: Path) -> Path:
        """
        Process SRT file to ensure single-line display with max 5-6 words per subtitle.

        This method:
        1. Removes line breaks within segments (ensures single line)
        2. Splits long subtitles into chunks of max 6 words
        3. Distributes timing proportionally across chunks

        Args:
            srt_path: Path to original SRT file

        Returns:
            Path to processed SRT file (same as input if no changes needed)
        """
        try:
            content = await asyncio.to_thread(srt_path.read_text, encoding="utf-8")

            # Split into subtitle blocks
            blocks = content.strip().split("\n\n")
            processed_blocks = []
            subtitle_index = 1

            for block in blocks:
                lines = block.split("\n")
                if len(lines) < 3:
                    processed_blocks.append(block)
                    continue

                # Parse timestamp line (format: "00:00:01,000 --> 00:00:05,000")
                timestamp_line = lines[1]

                # Remaining lines are the subtitle text - join them into single line
                text_lines = lines[2:]
                single_line_text = " ".join(line.strip() for line in text_lines if line.strip())

                # Split text into chunks of max 6 words
                words = single_line_text.split()
                max_words_per_chunk = 6

                if len(words) <= max_words_per_chunk:
                    # Text is short enough, keep as single subtitle
                    processed_block = f"{subtitle_index}\n{timestamp_line}\n{single_line_text}"
                    processed_blocks.append(processed_block)
                    subtitle_index += 1
                else:
                    # Split into chunks and distribute timing
                    chunks = []
                    for i in range(0, len(words), max_words_per_chunk):
                        chunk = " ".join(words[i:i + max_words_per_chunk])
                        chunks.append(chunk)

                    # Parse start and end times
                    time_parts = timestamp_line.split(" --> ")
                    if len(time_parts) == 2:
                        start_time_str = time_parts[0].strip()
                        end_time_str = time_parts[1].strip()

                        start_ms = self._parse_srt_time(start_time_str)
                        end_ms = self._parse_srt_time(end_time_str)
                        total_duration = end_ms - start_ms

                        # Distribute time proportionally across chunks
                        chunk_duration = total_duration / len(chunks)

                        for i, chunk_text in enumerate(chunks):
                            chunk_start_ms = start_ms + (i * chunk_duration)
                            chunk_end_ms = start_ms + ((i + 1) * chunk_duration)

                            chunk_start_str = self._format_srt_time(chunk_start_ms)
                            chunk_end_str = self._format_srt_time(chunk_end_ms)

                            chunk_block = f"{subtitle_index}\n{chunk_start_str} --> {chunk_end_str}\n{chunk_text}"
                            processed_blocks.append(chunk_block)
                            subtitle_index += 1
                    else:
                        # Invalid timestamp format, keep original
                        processed_block = f"{subtitle_index}\n{timestamp_line}\n{single_line_text}"
                        processed_blocks.append(processed_block)
                        subtitle_index += 1

            # Create processed SRT file
            processed_content = "\n\n".join(processed_blocks)
            processed_srt_path = srt_path.parent / f"{srt_path.stem}_processed.srt"

            await asyncio.to_thread(
                processed_srt_path.write_text, processed_content, encoding="utf-8"
            )

            logger.info(f"Processed SRT for single-line display with word chunking (max 6 words): {processed_srt_path}")
            return processed_srt_path

        except Exception as e:
            logger.warning(f"Failed to process SRT file, using original: {e}")
            return srt_path

    def _parse_srt_time(self, time_str: str) -> float:
        """
        Parse SRT timestamp to milliseconds.

        Args:
            time_str: SRT timestamp (e.g., "00:00:01,500")

        Returns:
            Time in milliseconds
        """
        # Format: HH:MM:SS,mmm
        time_parts = time_str.replace(",", ":").split(":")
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
        milliseconds = int(time_parts[3])

        total_ms = (hours * 3600000) + (minutes * 60000) + (seconds * 1000) + milliseconds
        return total_ms

    def _format_srt_time(self, ms: float) -> str:
        """
        Format milliseconds to SRT timestamp.

        Args:
            ms: Time in milliseconds

        Returns:
            SRT timestamp string (e.g., "00:00:01,500")
        """
        total_seconds = int(ms / 1000)
        milliseconds = int(ms % 1000)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    async def composite_top_bottom_videos(
        self,
        top_video_path: Path,
        bottom_video_path: Path,
        audio_path: Optional[Path] = None,
        output_path: Path = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Composite two videos vertically (top half and bottom half) into a 9:16 video.

        This creates a mobile-friendly video where:
        - Top half: Educational content (Manim animations, no audio)
        - Bottom half: Lip-synced celebrity video (with audio already baked in)

        Args:
            top_video_path: Path to video for top half (educational content, no audio)
            bottom_video_path: Path to video for bottom half (celebrity with lip-synced audio baked in)
            audio_path: DEPRECATED - Audio from bottom_video_path will be used instead
            output_path: Path for output composite video
            progress_callback: Optional callback for progress updates

        Returns:
            Path to composite video

        Raises:
            Exception: If compositing fails
        """
        try:
            if progress_callback:
                progress_callback("Compositing top and bottom videos...", 0)

            logger.info(f"Compositing {top_video_path} (top) and {bottom_video_path} (bottom)")

            # Verify files exist
            if not top_video_path.exists():
                raise FileNotFoundError(f"Top video not found: {top_video_path}")
            if not bottom_video_path.exists():
                raise FileNotFoundError(f"Bottom video not found: {bottom_video_path}")

            if audio_path is not None:
                logger.warning(f"DEPRECATED: audio_path parameter ignored. Using audio from bottom video (celebrity_lipsynced_full.mp4) which already has lip-synced audio baked in.")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Get durations - use bottom video as the authoritative source since it has the audio
            bottom_duration = await self._get_duration(bottom_video_path)
            top_duration = await self._get_duration(top_video_path)

            logger.info(f"Input durations - Top: {top_duration:.4f}s, Bottom (with audio): {bottom_duration:.4f}s")

            # CRITICAL FIX: Use bottom video duration as reference (it has the lip-synced audio baked in)
            # Trim both videos to match the bottom video's duration to ensure perfect sync
            # Using filter_complex to trim ensures frame-accurate cutting at the filter level
            #
            # The bug was: We were re-adding full_audio.mp3 on top of celebrity_lipsynced_full.mp4
            # which already has the lip-synced audio baked in. This caused:
            # 1. Duration mismatches between final_video.mp4 and celebrity_lipsynced_full.mp4
            # 2. Audio/video sync issues
            # 3. Re-splicing audio on top of videos that already have audio
            #
            # Solution: Use audio from bottom video (celebrity_lipsynced_full.mp4) directly
            # and trim both videos to match the bottom video's duration
            cmd = [
                "ffmpeg",
                "-i", str(top_video_path),
                "-i", str(bottom_video_path),
                "-filter_complex",
                (
                    # TRIM top video to exact bottom video duration FIRST (before scaling)
                    f"[0:v]trim=duration={bottom_duration},setpts=PTS-STARTPTS,"
                    # Then scale to 1080x960 (9:8 aspect ratio for top half)
                    "scale=1080:960:force_original_aspect_ratio=increase,"
                    "crop=1080:960[top];"
                    # TRIM bottom video to its own duration to ensure consistency (before scaling)
                    f"[1:v]trim=duration={bottom_duration},setpts=PTS-STARTPTS,"
                    # Then scale and crop to 1080x960 (9:8 bottom half from 9:16 source)
                    "scale=1080:960:force_original_aspect_ratio=increase,"
                    "crop=1080:960[bottom];"
                    # Stack vertically to create final 1080x1920 (9:16)
                    "[top][bottom]vstack=inputs=2[v]"
                ),
                "-map", "[v]",
                "-map", "1:a",  # Use audio from bottom video (celebrity_lipsynced_full.mp4 with lip-synced audio)
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "copy",  # Copy audio as-is (already encoded and synced in bottom video)
                # Remove -t and -shortest since trimming is now done in the filter
                # This ensures the output matches the trimmed filter output exactly
                "-y",
                str(output_path),
            ]

            logger.info(f"Running ffmpeg composite with input trimming to {bottom_duration:.4f}s (using audio from bottom video)")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.returncode != 0:
                error_msg = f"Video compositing failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            if not output_path.exists():
                raise Exception(f"Output file not created: {output_path}")

            # Verify output duration matches bottom video (which has the lip-synced audio)
            output_duration = await self._get_duration(output_path)
            duration_diff = abs(output_duration - bottom_duration)
            logger.info(f"Composite output duration: {output_duration:.4f}s (target: {bottom_duration:.4f}s, diff: {duration_diff:.4f}s)")

            if duration_diff > 0.1:
                logger.warning(f"Composite duration differs from bottom video by {duration_diff:.4f}s (may cause sync issues)")
            else:
                logger.info(f"SUCCESS: Final video duration matches celebrity_lipsynced_full.mp4 exactly!")

            logger.info(f"Video compositing complete: {output_path}")

            if progress_callback:
                progress_callback("Video compositing complete", 100)

            return output_path

        except Exception as e:
            logger.error(f"Failed to composite videos: {e}")
            raise Exception(f"Video compositing failed: {e}")

    async def trim_video_to_duration(
        self,
        video_path: Path,
        duration: float,
        output_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Trim a video to EXACT duration with ZERO tolerance.

        Uses frame-accurate trimming with re-encoding and audio re-encoding
        to ensure the output duration matches the target EXACTLY.

        Args:
            video_path: Path to input video
            duration: Target duration in seconds (will be matched exactly)
            output_path: Path for trimmed output video
            progress_callback: Optional callback for progress updates

        Returns:
            Path to trimmed video

        Raises:
            Exception: If trimming fails
        """
        try:
            if progress_callback:
                progress_callback(f"Trimming video to {duration:.4f}s...", 0)

            logger.info(f"Trimming {video_path} to EXACT duration: {duration:.4f}s")

            # Verify input file exists
            if not video_path.exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Get input video duration for logging
            input_duration = await self._get_duration(video_path)
            logger.info(f"Input video duration: {input_duration:.4f}s, target: {duration:.4f}s, diff: {abs(input_duration - duration):.4f}s")

            # Build ffmpeg command for FRAME-PERFECT trimming
            # Strategy:
            # 1. Use -t for duration limit (not -to, as -t is more accurate)
            # 2. Re-encode video and audio for frame-accurate cutting
            # 3. Use -vsync cfr for constant frame rate
            # 4. Use -af asetpts=PTS-STARTPTS to reset audio timestamps
            # 5. Use -fflags +genpts to regenerate timestamps for perfect sync
            # 6. Use high precision for duration (ffmpeg handles microseconds)
            cmd = [
                "ffmpeg",
                "-fflags", "+genpts",  # Generate presentation timestamps for accuracy
                "-i", str(video_path),
                "-t", f"{duration:.6f}",  # Trim to EXACT duration with microsecond precision
                "-c:v", "libx264",  # Re-encode video for frame-accurate cutting
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",  # Re-encode audio for sample-accurate cutting
                "-b:a", "192k",
                "-ar", "48000",  # Standard audio sample rate
                "-vsync", "cfr",  # Constant frame rate (no frame drops or duplicates)
                "-af", "asetpts=PTS-STARTPTS",  # Reset audio timestamps to start at 0
                "-avoid_negative_ts", "make_zero",  # Ensure timestamps start at zero
                "-y",
                str(output_path),
            ]

            logger.info(f"Running ffmpeg frame-perfect trim with microsecond precision: {duration:.6f}s")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                error_msg = f"Video trimming failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            if not output_path.exists():
                raise Exception(f"Output file not created: {output_path}")

            # Verify output duration
            output_duration = await self._get_duration(output_path)
            duration_diff = abs(output_duration - duration)
            logger.info(f"Video trimmed: output={output_duration:.4f}s, target={duration:.4f}s, diff={duration_diff:.4f}s")

            if duration_diff > 0.001:  # Log warning if off by more than 1ms
                logger.warning(f"Trimmed video differs from target by {duration_diff:.4f}s (this may accumulate over many segments)")

            if progress_callback:
                progress_callback("Video trimming complete", 100)

            return output_path

        except Exception as e:
            logger.error(f"Failed to trim video: {e}")
            raise Exception(f"Video trimming failed: {e}")

    async def concatenate_videos(
        self,
        video_paths: List[Path],
        output_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Concatenate multiple video segments into a single video.

        Args:
            video_paths: List of paths to video segments (in order)
            output_path: Path for output concatenated video
            progress_callback: Optional callback for progress updates

        Returns:
            Path to concatenated video

        Raises:
            Exception: If concatenation fails
        """
        try:
            if progress_callback:
                progress_callback(f"Concatenating {len(video_paths)} video segments...", 0)

            logger.info(f"Concatenating {len(video_paths)} video segments")

            if not video_paths:
                raise ValueError("No video paths provided")

            # Verify all files exist
            for path in video_paths:
                if not path.exists():
                    raise FileNotFoundError(f"Video not found: {path}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a temporary file list for ffmpeg concat
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                concat_file = Path(f.name)
                for video_path in video_paths:
                    # Write absolute path with proper escaping
                    f.write(f"file '{video_path.absolute()}'\n")

            try:
                # Run ffmpeg concat with re-encoding to prevent timing drift
                # ZERO TOLERANCE STRATEGY + CORRUPTION HANDLING:
                # 1. Use concat demuxer with re-encoding (not concat filter)
                # 2. Re-encode both video and audio for frame/sample accurate concatenation
                # 3. Use -vsync cfr to ensure constant frame rate across all segments
                # 4. Use -fflags +genpts to regenerate timestamps for perfect continuity
                # 5. Use -af aresample=async=1 to ensure audio samples align perfectly
                # 6. Reset timestamps to ensure no gaps or overlaps between segments
                # 7. Handle corrupted AAC from Replicate lip-sync (ignore decoding errors)
                cmd = [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-err_detect", "ignore_err",  # Ignore corrupted AAC frames from Replicate
                    "-fflags", "+genpts+igndts",  # Generate perfect timestamps + ignore DTS errors
                    "-i", str(concat_file),
                    "-c:v", "libx264",  # Re-encode video for frame-accurate concatenation
                    "-preset", "medium",
                    "-crf", "23",
                    "-c:a", "aac",  # Re-encode audio to fix corrupted AAC from lip-sync
                    "-b:a", "192k",
                    "-ar", "48000",  # Ensure consistent audio sample rate
                    "-strict", "experimental",  # Allow experimental AAC encoder features
                    "-vsync", "cfr",  # Constant frame rate (no frame drops/duplicates)
                    "-af", "aresample=async=1:first_pts=0",  # Resample audio to prevent drift, reset timestamps
                    "-avoid_negative_ts", "make_zero",  # Ensure timestamps start at zero
                    "-max_muxing_queue_size", "9999",  # Large queue for problematic streams
                    "-y",
                    str(output_path),
                ]

                logger.info(f"Running ffmpeg concatenation with ZERO TOLERANCE (frame-perfect re-encoding + corrupted AAC handling)")

                result = await asyncio.to_thread(
                    subprocess.run,
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode != 0:
                    error_msg = f"Video concatenation failed: {result.stderr}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

            finally:
                # Clean up temp file
                concat_file.unlink(missing_ok=True)

            if not output_path.exists():
                raise Exception(f"Output file not created: {output_path}")

            logger.info(f"Video concatenation complete: {output_path}")

            if progress_callback:
                progress_callback("Video concatenation complete", 100)

            return output_path

        except Exception as e:
            logger.error(f"Failed to concatenate videos: {e}")
            raise Exception(f"Video concatenation failed: {e}")
