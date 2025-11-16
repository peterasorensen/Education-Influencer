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
            # 1. Scale both videos to same width (1080px for 9:16)
            # 2. Crop/scale to half height each (960px each for total 1920px height)
            # 3. Stack them vertically
            # 4. Add audio track
            # 5. Ensure duration matches audio
            cmd = [
                "ffmpeg",
                "-i", str(top_video_path),
                "-i", str(bottom_video_path),
                "-i", str(audio_path),
                "-filter_complex",
                (
                    # Scale and crop top video to 1080x960 (top half)
                    "[0:v]scale=1080:960:force_original_aspect_ratio=decrease,"
                    "pad=1080:960:(ow-iw)/2:(oh-ih)/2[top];"
                    # Scale and crop bottom video to 1080x960 (bottom half)
                    "[1:v]scale=1080:960:force_original_aspect_ratio=decrease,"
                    "pad=1080:960:(ow-iw)/2:(oh-ih)/2[bottom];"
                    # Stack vertically
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

            # Build ffmpeg command to trim video
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-t", str(duration),  # Trim to exact duration
                "-c", "copy",  # Copy without re-encoding (faster)
                "-y",
                str(output_path),
            ]

            logger.info(f"Running ffmpeg trim: {' '.join(cmd)}")

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
                # Run ffmpeg concat
                cmd = [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy",  # Copy streams without re-encoding (faster)
                    "-y",
                    str(output_path),
                ]

                logger.info(f"Running ffmpeg concatenation")

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
