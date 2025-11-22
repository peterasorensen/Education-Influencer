"""
Lipsync Generator Module

Synchronizes audio with video using Replicate's Pixverse lipsync model.
Creates realistic lip-synced videos from silent videos and audio clips.
"""

import logging
from typing import Callable, Optional, List
from pathlib import Path
import asyncio
import replicate
import os

logger = logging.getLogger(__name__)


class LipsyncGenerator:
    """Generate lip-synced videos using configurable Replicate models."""

    # Supported models
    MODELS = {
        "tmappdev": "tmappdev/lipsync:569bcd925698ea23d4bece4528546992012d84267ce2438ecc803618ce23764c",  # Default, most reliable
        "kling": "kwaivgi/kling-lip-sync",  # Alternative (has issues with file uploads)
        "pixverse": "pixverse/lipsync",     # Alternative option
    }

    def __init__(self, api_token: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the lipsync generator.

        Args:
            api_token: Replicate API token (defaults to REPLICATE_API_TOKEN env var)
            model: Model to use (defaults to LIPSYNC_MODEL env var or kling)
        """
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            logger.warning("REPLICATE_API_TOKEN not set. API calls will fail.")

        # Set token in environment for replicate SDK
        if self.api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token

        # Determine which model to use
        model_name = model or os.getenv("LIPSYNC_MODEL", "tmappdev")

        # Handle both full model paths and short names
        if model_name in self.MODELS.values():
            self.model = model_name
        elif model_name in self.MODELS:
            self.model = self.MODELS[model_name]
        else:
            logger.warning(f"Unknown lipsync model '{model_name}', defaulting to tmappdev")
            self.model = self.MODELS["tmappdev"]

        logger.info(f"LipsyncGenerator initialized with model: {self.model}")

    async def sync_audio_to_video(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Sync audio to video using lip-sync technology.

        Args:
            video_path: Path to the silent video (from image-to-video generation)
            audio_path: Path to the audio file to sync
            output_path: Path to save the lip-synced video
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the lip-synced video file

        Raises:
            Exception: If lip-sync fails
        """
        try:
            logger.info(f"Syncing audio {audio_path} to video {video_path}")

            if progress_callback:
                progress_callback(f"Synchronizing audio to video...", 0)

            # Verify input files exist and are valid
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Check file sizes to ensure they're not empty or corrupted
            video_size = video_path.stat().st_size
            audio_size = audio_path.stat().st_size

            if video_size == 0:
                raise ValueError(f"Video file is empty: {video_path}")
            if audio_size == 0:
                raise ValueError(f"Audio file is empty: {audio_path}")

            logger.info(f"File validation passed - video: {video_size} bytes ({video_size/1024/1024:.2f} MB), audio: {audio_size} bytes ({audio_size/1024:.2f} KB)")
            logger.info(f"Video path: {video_path.absolute()}")
            logger.info(f"Audio path: {audio_path.absolute()}")

            # Try to verify video file is valid by checking magic bytes
            try:
                with open(video_path, "rb") as f:
                    header = f.read(12)
                    logger.info(f"Video file header (first 12 bytes): {header.hex()}")

                    # MP4 files should start with specific patterns
                    # Common patterns: 00 00 00 ?? 66 74 79 70 (ftyp box)
                    if b'ftyp' not in header:
                        logger.warning(f"Video file may not be a valid MP4 - 'ftyp' signature not found in header")
            except Exception as e:
                logger.warning(f"Failed to read video header: {e}")

            # Check audio file format
            try:
                with open(audio_path, "rb") as f:
                    audio_header = f.read(4)
                    logger.info(f"Audio file header (first 4 bytes): {audio_header.hex()}")

                    # MP3 files often start with ID3 or FF FB/FF F3
                    if audio_header.startswith(b'ID3'):
                        logger.info("Audio file: MP3 with ID3 tags")
                    elif audio_header[0:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2']:
                        logger.info("Audio file: MP3 without ID3 tags")
                    else:
                        logger.warning(f"Audio file may not be valid MP3")
            except Exception as e:
                logger.warning(f"Failed to read audio header: {e}")

            # Prepare output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Open files for upload - keep them open during the entire Replicate call
            with open(video_path, "rb") as video_file, open(audio_path, "rb") as audio_file:
                # Ensure file pointers are at the start
                video_file.seek(0)
                audio_file.seek(0)

                logger.info(f"Opened files - video_file type: {type(video_file)}, audio_file type: {type(audio_file)}")
                logger.info(f"Video file readable: {video_file.readable()}, Audio file readable: {audio_file.readable()}")

                # Prepare model-specific parameters
                if "tmappdev" in self.model:
                    # tmappdev/lipsync uses audio_input and video_input
                    logger.info(f"Running tmappdev lipsync model: {self.model}")
                    logger.info(f"  video_input parameter: {video_path.name} ({video_size/1024/1024:.2f} MB)")
                    logger.info(f"  audio_input parameter: {audio_path.name} ({audio_size/1024:.2f} KB)")

                    model_input = {
                        "video_input": video_file,
                        "audio_input": audio_file,
                        "fps": 25,
                        "bbox_shift": 0,
                    }
                    timeout_seconds = 1800  # 30 minute timeout (no artificial cap)
                elif "kling" in self.model:
                    # Kling lip-sync uses video_url and audio_file
                    logger.info(f"Running Kling lip-sync model: {self.model}")
                    logger.info(f"  video_url parameter: {video_path.name} ({video_size/1024/1024:.2f} MB)")
                    logger.info(f"  audio_file parameter: {audio_path.name} ({audio_size/1024:.2f} KB)")

                    model_input = {
                        "video_url": video_file,
                        "audio_file": audio_file,
                    }
                    timeout_seconds = 1800  # 30 minute timeout (no artificial cap)
                else:
                    # Pixverse uses video and audio
                    logger.info(f"Running Pixverse lipsync model: {self.model}")
                    logger.info(f"  video parameter: {video_path.name} ({video_size/1024/1024:.2f} MB)")
                    logger.info(f"  audio parameter: {audio_path.name} ({audio_size/1024:.2f} KB)")

                    model_input = {
                        "video": video_file,
                        "audio": audio_file,
                    }
                    timeout_seconds = 1800  # 30 minute timeout (no artificial cap)

                logger.info(f"Calling replicate.run with model: {self.model}")
                logger.info(f"Input parameters: {list(model_input.keys())}")

                # Run with timeout to prevent infinite polling
                try:
                    output = await asyncio.wait_for(
                        asyncio.to_thread(
                            replicate.run,
                            self.model,
                            input=model_input
                        ),
                        timeout=timeout_seconds
                    )
                    logger.info(f"Replicate call succeeded, output type: {type(output)}")
                except asyncio.TimeoutError:
                    if "tmappdev" in self.model:
                        model_name = "tmappdev"
                    elif "kling" in self.model:
                        model_name = "Kling"
                    else:
                        model_name = "Pixverse"
                    raise Exception(f"{model_name} lipsync timed out after {timeout_seconds//60} minutes. Lipsync may have failed on Replicate's side.")
                except Exception as e:
                    logger.error(f"Replicate call failed with error: {type(e).__name__}: {e}")
                    raise

            if progress_callback:
                progress_callback(f"Lipsync complete, downloading...", 50)

            # Download the output video
            video_url = None

            if isinstance(output, str):
                # It's a URL
                video_url = output
            elif hasattr(output, 'read'):
                # It's a FileOutput object
                video_data = output.read()
                with open(output_path, 'wb') as f:
                    f.write(video_data)

                # Log for debugging (FileOutput might have URL attribute)
                if hasattr(output, 'url'):
                    video_url = output.url
                    logger.info(f"Replicate lipsync URL: {video_url}")

                logger.info(f"Lip-synced video saved to {output_path}")

                if progress_callback:
                    progress_callback(f"Lipsync complete", 100)

                # Save URL to metadata file for debugging
                if video_url:
                    metadata_file = output_path.parent / f"{output_path.stem}_replicate_url.txt"
                    metadata_file.write_text(f"Replicate URL: {video_url}\nGenerated: {output_path.name}\n")

                return output_path
            else:
                # It might be an iterable or list
                video_url = output[0] if isinstance(output, list) else output

            # Log the Replicate URL for debugging
            logger.info(f"Replicate lipsync URL: {video_url}")

            # Download from URL
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)

            logger.info(f"Lip-synced video saved to {output_path}")

            # Save URL to metadata file for debugging
            metadata_file = output_path.parent / f"{output_path.stem}_replicate_url.txt"
            metadata_file.write_text(f"Replicate URL: {video_url}\nGenerated: {output_path.name}\n")

            if progress_callback:
                progress_callback(f"Lipsync complete", 100)

            return output_path

        except Exception as e:
            logger.error(f"Failed to sync audio to video: {e}")
            raise Exception(f"Lipsync failed: {e}")

    async def sync_multiple_segments(
        self,
        video_segments: List[Path],
        audio_segments: List[Path],
        output_dir: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Path]:
        """
        Sync multiple audio segments to their corresponding video segments.

        Args:
            video_segments: List of paths to silent video segments
            audio_segments: List of paths to audio segments (must match length)
            output_dir: Directory to save lip-synced videos
            progress_callback: Optional callback for progress updates

        Returns:
            List of paths to lip-synced video files

        Raises:
            Exception: If counts don't match or sync fails
        """
        try:
            if len(video_segments) != len(audio_segments):
                raise ValueError(
                    f"Mismatch: {len(video_segments)} videos but {len(audio_segments)} audio files"
                )

            logger.info(f"Syncing {len(video_segments)} video segments with audio")

            output_dir.mkdir(parents=True, exist_ok=True)
            synced_videos = []

            total_segments = len(video_segments)
            for idx, (video_path, audio_path) in enumerate(zip(video_segments, audio_segments)):
                if progress_callback:
                    progress = int((idx / total_segments) * 100)
                    progress_callback(
                        f"Lip-syncing segment {idx + 1}/{total_segments}...",
                        progress
                    )

                # Generate output path
                output_path = output_dir / f"lipsynced_segment_{idx:03d}.mp4"

                # Sync this segment
                await self.sync_audio_to_video(
                    video_path=video_path,
                    audio_path=audio_path,
                    output_path=output_path,
                )

                synced_videos.append(output_path)

            logger.info(f"Synced {len(synced_videos)} video segments")

            if progress_callback:
                progress_callback("All segments lip-synced", 100)

            return synced_videos

        except Exception as e:
            logger.error(f"Failed to sync multiple segments: {e}")
            raise Exception(f"Multi-segment lipsync failed: {e}")
