"""
Video Stitcher Module

Combines audio narration with Manim-generated visuals using ffmpeg.
Handles timing synchronization and video encoding.
"""

import logging
from typing import Callable, Optional
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

            # Default subtitle style
            if not subtitle_style:
                subtitle_style = "FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3"

            # Build ffmpeg command
            # Note: On some systems, the subtitles filter path needs escaping
            srt_path_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")

            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vf", f"subtitles={srt_path_escaped}:force_style='{subtitle_style}'",
                "-c:a", "copy",
                "-y",
                str(output_path),
            ]

            logger.info(f"Running ffmpeg with subtitles")

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

            if not output_path.exists():
                raise Exception(f"Output file not created: {output_path}")

            logger.info(f"Subtitles added successfully: {output_path}")

            if progress_callback:
                progress_callback("Subtitles added successfully", 95)

            return output_path

        except Exception as e:
            logger.error(f"Failed to add subtitles: {e}")
            raise Exception(f"Subtitle addition failed: {e}")
