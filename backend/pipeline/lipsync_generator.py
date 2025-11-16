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
        "kling": "kwaivgi/kling-lip-sync",  # Cheaper, faster
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
        model_name = model or os.getenv("LIPSYNC_MODEL", "kwaivgi/kling-lip-sync")

        # Handle both full model paths and short names
        if model_name in self.MODELS.values():
            self.model = model_name
        elif model_name in self.MODELS:
            self.model = self.MODELS[model_name]
        else:
            logger.warning(f"Unknown lipsync model '{model_name}', defaulting to kling")
            self.model = self.MODELS["kling"]

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

            # Verify input files exist
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Prepare output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Open files for upload
            with open(video_path, "rb") as video_file, open(audio_path, "rb") as audio_file:
                # Prepare model-specific parameters
                if "kling" in self.model:
                    # Kling lip-sync uses video_url and audio_file
                    logger.info(f"Running Kling lip-sync model")

                    model_input = {
                        "video_url": video_file,  # Kling accepts file handle as video_url
                        "audio_file": audio_file,
                    }
                    timeout_seconds = 180  # 3 minute timeout for faster Kling
                else:
                    # Pixverse uses video and audio
                    logger.info(f"Running Pixverse lipsync model")

                    model_input = {
                        "video": video_file,
                        "audio": audio_file,
                    }
                    timeout_seconds = 300  # 5 minute timeout for Pixverse

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
                except asyncio.TimeoutError:
                    model_name = "Kling" if "kling" in self.model else "Pixverse"
                    raise Exception(f"{model_name} lipsync timed out after {timeout_seconds//60} minutes. Lipsync may have failed on Replicate's side.")

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
