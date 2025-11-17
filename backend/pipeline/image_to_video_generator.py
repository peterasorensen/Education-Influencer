"""
Image to Video Generator Module

Converts static images to expressive videos using Replicate's Kling v2.5 model.
Generates video clips with motion based on prompts, synced to audio duration.
"""

import logging
from typing import Callable, Optional, List, Dict
from pathlib import Path
import asyncio
import replicate
import os
import math

logger = logging.getLogger(__name__)


class ImageToVideoGenerator:
    """Generate videos from images using configurable Replicate models."""

    # Supported models
    MODELS = {
        "seedance": "bytedance/seedance-1-pro-fast",  # Cheaper, faster
        "kling": "kwaivgi/kling-v2.5-turbo-pro",      # Higher quality
    }

    def __init__(self, api_token: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the image to video generator.

        Args:
            api_token: Replicate API token (defaults to REPLICATE_API_TOKEN env var)
            model: Model to use (defaults to IMAGE_TO_VIDEO_MODEL env var or seedance)
        """
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            logger.warning("REPLICATE_API_TOKEN not set. API calls will fail.")

        # Set token in environment for replicate SDK
        if self.api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token

        # Determine which model to use
        model_name = model or os.getenv("IMAGE_TO_VIDEO_MODEL", "bytedance/seedance-1-pro-fast")

        # Handle both full model paths and short names
        if model_name in self.MODELS.values():
            self.model = model_name
        elif model_name in self.MODELS:
            self.model = self.MODELS[model_name]
        else:
            logger.warning(f"Unknown model '{model_name}', defaulting to seedance")
            self.model = self.MODELS["seedance"]

        logger.info(f"ImageToVideoGenerator initialized with model: {self.model}")

    async def generate_video_from_image(
        self,
        image_path: Path,
        duration: float,
        prompt: str,
        output_path: Path,
        aspect_ratio: str = "9:16",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Generate a video from a static image with expressive motion.

        Args:
            image_path: Path to the input image
            duration: Target duration in seconds
            prompt: Motion/expression prompt describing the desired animation
            output_path: Path to save the generated video
            aspect_ratio: Video aspect ratio (default: 9:16 for mobile)
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the generated video file

        Raises:
            Exception: If video generation fails
        """
        try:
            logger.info(f"Generating video from {image_path} with prompt: '{prompt}'")

            if progress_callback:
                progress_callback(f"Generating video from image...", 0)

            # Verify input image exists
            if not image_path.exists():
                raise FileNotFoundError(f"Input image not found: {image_path}")

            # Prepare output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Open image file for upload
            with open(image_path, "rb") as image_file:
                # Prepare model-specific parameters
                if "seedance" in self.model:
                    # Seedance model: accepts 2-12 seconds, any integer
                    # Use ceiling to ensure we generate enough video (will trim to exact duration after)
                    video_duration = max(2, min(12, math.ceil(duration)))  # Clamp to 2-12 range, use ceiling
                    logger.info(f"Running Seedance model with duration: {video_duration}s (requested: {duration:.2f}s, will trim after), aspect_ratio: {aspect_ratio}, resolution: 480p")

                    model_input = {
                        "prompt": prompt,
                        "image": image_file,
                        "duration": video_duration,  # Seedance uses int, not string
                        "aspect_ratio": aspect_ratio,
                        "resolution": "480p",  # Always 480p for cost savings
                        "fps": 24,  # Default FPS
                        "camera_fixed": False,  # Allow camera movement
                    }
                    timeout_seconds = 180  # 3 minute timeout for faster Seedance
                else:
                    # Kling v2.5 model: only accepts duration of 5 or 10 seconds
                    # Use minimum duration that can fit the requested duration (ceiling logic)
                    # Example: 3s audio → need 5s video (will trim to 3s later)
                    #          7s audio → need 10s video (will trim to 7s later)
                    if duration <= 5:
                        video_duration = 5
                    else:
                        video_duration = 10

                    logger.info(f"Running Kling v2.5 model with duration: {video_duration}s (requested: {duration}s, will trim after), aspect_ratio: {aspect_ratio}")

                    model_input = {
                        "prompt": prompt,
                        "image": image_file,
                        "duration": video_duration,  # Must be 5 or 10
                        "aspect_ratio": aspect_ratio,
                    }
                    timeout_seconds = 300  # 5 minute timeout for Kling

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
                    model_name = "Seedance" if "seedance" in self.model else "Kling"
                    raise Exception(f"{model_name} model timed out after {timeout_seconds//60} minutes. Video generation may have failed on Replicate's side.")

            if progress_callback:
                progress_callback(f"Video generation complete, downloading...", 50)

            # Output is a URL or file output
            # Download the video to output_path
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
                    logger.info(f"Replicate video URL: {video_url}")

                logger.info(f"Video saved to {output_path}")

                # Validate downloaded video
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    logger.info(f"Downloaded video size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

                    # Check video file header
                    with open(output_path, 'rb') as f:
                        header = f.read(12)
                        logger.info(f"Video file header: {header.hex()}")
                        if b'ftyp' in header:
                            logger.info("Video file appears to be valid MP4")
                        else:
                            logger.warning("Video file may not be valid MP4 - 'ftyp' signature not found")
                else:
                    logger.error(f"Video file was not created at {output_path}")

                if progress_callback:
                    progress_callback(f"Video generation complete", 100)

                # Save URL to metadata file for debugging
                if video_url:
                    metadata_file = output_path.parent / f"{output_path.stem}_replicate_url.txt"
                    metadata_file.write_text(f"Replicate URL: {video_url}\nGenerated: {output_path.name}\n")

                return output_path
            else:
                # It might be an iterable or list
                video_url = output[0] if isinstance(output, list) else output

            # Log the Replicate URL for debugging
            logger.info(f"Replicate video URL: {video_url}")

            # Download from URL
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)

            logger.info(f"Video saved to {output_path}")

            # Validate downloaded video
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"Downloaded video size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

                # Check video file header
                with open(output_path, 'rb') as f:
                    header = f.read(12)
                    logger.info(f"Video file header: {header.hex()}")
                    if b'ftyp' in header:
                        logger.info("Video file appears to be valid MP4")
                    else:
                        logger.warning("Video file may not be valid MP4 - 'ftyp' signature not found")
            else:
                logger.error(f"Video file was not created at {output_path}")

            # Save URL to metadata file for debugging
            metadata_file = output_path.parent / f"{output_path.stem}_replicate_url.txt"
            metadata_file.write_text(f"Replicate URL: {video_url}\nGenerated: {output_path.name}\n")

            if progress_callback:
                progress_callback(f"Video generation complete", 100)

            return output_path

        except Exception as e:
            logger.error(f"Failed to generate video from image: {e}")
            raise Exception(f"Image to video generation failed: {e}")

    async def generate_celebrity_videos(
        self,
        audio_segments: List[Dict],
        celebrity_image: Path,
        output_dir: Path,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Path]:
        """
        Generate multiple video segments from a celebrity image, one for each audio segment.

        Args:
            audio_segments: List of audio segment info with duration and timestamps
            celebrity_image: Path to celebrity image
            output_dir: Directory to save video segments
            progress_callback: Optional callback for progress updates

        Returns:
            List of paths to generated video files

        Raises:
            Exception: If video generation fails
        """
        try:
            logger.info(f"Generating {len(audio_segments)} video segments from {celebrity_image}")

            output_dir.mkdir(parents=True, exist_ok=True)
            video_files = []

            # Motion prompts for natural talking variations
            motion_prompts = [
                "natural head movement while speaking, slight nodding, friendly expression",
                "expressive talking, subtle gestures, engaging eye contact",
                "animated speaking with natural facial expressions and head tilts",
                "conversational speaking with warm smile and slight head movements",
                "energetic talking with enthusiastic expressions and natural gestures",
            ]

            total_segments = len(audio_segments)
            for idx, segment in enumerate(audio_segments):
                if progress_callback:
                    progress = int((idx / total_segments) * 100)
                    progress_callback(
                        f"Generating celebrity video {idx + 1}/{total_segments}...",
                        progress
                    )

                # Get duration for this segment
                duration = segment.get("duration", 5.0)

                # Cycle through motion prompts for variety
                prompt = motion_prompts[idx % len(motion_prompts)]

                # Generate video segment
                segment_path = output_dir / f"celebrity_segment_{idx:03d}.mp4"
                await self.generate_video_from_image(
                    image_path=celebrity_image,
                    duration=duration,
                    prompt=prompt,
                    output_path=segment_path,
                    aspect_ratio="9:16",
                )

                video_files.append(segment_path)

            logger.info(f"Generated {len(video_files)} celebrity video segments")

            if progress_callback:
                progress_callback("Celebrity video generation complete", 100)

            return video_files

        except Exception as e:
            logger.error(f"Failed to generate celebrity videos: {e}")
            raise Exception(f"Celebrity video generation failed: {e}")
