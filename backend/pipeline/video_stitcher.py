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
            # MarginV controls vertical position from bottom (1920 - 960 = 960)
            # FontSize=28 for smaller, readable text
            # BorderStyle=4 for semi-transparent background box
            # BackColour=&H80000000 (semi-transparent black background)
            # Alignment=2 for center horizontal alignment
            # Outline=1 for subtle text outline
            # Shadow=0 for no shadow (cleaner look)
            if not subtitle_style:
                subtitle_style = "FontSize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=4,BackColour=&H80000000,Alignment=2,MarginV=960,Outline=1,Shadow=0"

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

            logger.info(f"Running ffmpeg with subtitles (single-line, positioned at y=960)")

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
        Process SRT file to ensure single-line display by removing line breaks within segments.

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

            for block in blocks:
                lines = block.split("\n")
                if len(lines) < 3:
                    processed_blocks.append(block)
                    continue

                # First line is the index, second is timestamp
                index_line = lines[0]
                timestamp_line = lines[1]

                # Remaining lines are the subtitle text - join them into single line
                text_lines = lines[2:]
                single_line_text = " ".join(line.strip() for line in text_lines if line.strip())

                # Reconstruct the block with single-line text
                processed_block = f"{index_line}\n{timestamp_line}\n{single_line_text}"
                processed_blocks.append(processed_block)

            # Create processed SRT file
            processed_content = "\n\n".join(processed_blocks)
            processed_srt_path = srt_path.parent / f"{srt_path.stem}_processed.srt"

            await asyncio.to_thread(
                processed_srt_path.write_text, processed_content, encoding="utf-8"
            )

            logger.info(f"Processed SRT for single-line display: {processed_srt_path}")
            return processed_srt_path

        except Exception as e:
            logger.warning(f"Failed to process SRT file, using original: {e}")
            return srt_path

    async def composite_top_bottom_videos(
        self,
        top_video_path: Path,
        bottom_video_path: Path,
        audio_path: Path,
        output_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Composite two videos vertically (top half and bottom half) into a 9:16 video.

        This creates a mobile-friendly video where:
        - Top half: Educational content (Manim animations)
        - Bottom half: Lip-synced celebrity video

        Args:
            top_video_path: Path to video for top half (educational content)
            bottom_video_path: Path to video for bottom half (celebrity)
            audio_path: Path to audio file (will be the final audio track)
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
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio not found: {audio_path}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Get audio duration to ensure all videos match
            audio_duration = await self._get_duration(audio_path)

            # Build ffmpeg command for vertical stacking
            # This will:
            # 1. Scale both videos to 1080x960 (9:8 aspect ratio each)
            # 2. Stack them vertically to create 1080x1920 (9:16 final output)
            # 3. Add audio track
            # 4. Ensure duration matches audio
            #
            # Note: Top video (manim) should already be rendered at 9:8 (e.g., 1080x960)
            # Bottom video (celebrity) will be scaled/cropped from 9:16 to 9:8
            cmd = [
                "ffmpeg",
                "-i", str(top_video_path),
                "-i", str(bottom_video_path),
                "-i", str(audio_path),
                "-filter_complex",
                (
                    # Scale top video to exactly 1080x960 (should already be this size if rendered correctly)
                    # Use 'increase' to fill the frame, then crop to exact size
                    "[0:v]scale=1080:960:force_original_aspect_ratio=increase,"
                    "crop=1080:960[top];"
                    # Scale and crop bottom video to 1080x960 (9:8 bottom half)
                    # This crops the 9:16 celebrity video to show just the top portion
                    "[1:v]scale=1080:960:force_original_aspect_ratio=increase,"
                    "crop=1080:960[bottom];"
                    # Stack vertically to create final 1080x1920 (9:16)
                    "[top][bottom]vstack=inputs=2[v]"
                ),
                "-map", "[v]",
                "-map", "2:a",  # Use audio from third input
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", str(audio_duration),  # Match audio duration
                "-shortest",
                "-y",
                str(output_path),
            ]

            logger.info(f"Running ffmpeg composite")

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
        Trim a video to exact duration.

        Args:
            video_path: Path to input video
            duration: Target duration in seconds
            output_path: Path for trimmed output video
            progress_callback: Optional callback for progress updates

        Returns:
            Path to trimmed video

        Raises:
            Exception: If trimming fails
        """
        try:
            if progress_callback:
                progress_callback(f"Trimming video to {duration}s...", 0)

            logger.info(f"Trimming {video_path} to {duration}s")

            # Verify input file exists
            if not video_path.exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build ffmpeg command to trim video with re-encoding for accuracy
            # Note: We re-encode because '-c copy' can result in imprecise cuts at non-keyframes
            # Re-encoding ensures we get EXACTLY the duration we want
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-t", str(duration),  # Trim to exact duration
                "-c:v", "libx264",  # Re-encode for precise trimming
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",  # Re-encode audio
                "-b:a", "192k",
                "-vsync", "cfr",  # Constant frame rate
                "-y",
                str(output_path),
            ]

            logger.info(f"Running ffmpeg trim with re-encoding for precision: {duration:.2f}s")

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

            logger.info(f"Video trimmed successfully: {output_path}")

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
                # Note: We re-encode because '-c copy' can cause timing drift when segments
                # have slightly different timestamps or frame rates from different sources
                cmd = [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_file),
                    "-c:v", "libx264",  # Re-encode video to ensure consistent timing
                    "-preset", "medium",
                    "-crf", "23",
                    "-c:a", "aac",  # Re-encode audio for consistency
                    "-b:a", "192k",
                    "-vsync", "cfr",  # Constant frame rate to prevent drift
                    "-y",
                    str(output_path),
                ]

                logger.info(f"Running ffmpeg concatenation with re-encoding (prevents timing drift)")

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
