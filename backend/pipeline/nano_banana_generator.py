"""
Nano Banana Image Generator Module

Uses Google's Nano Banana model to transform celebrity images based on text prompts.
Generates customized character images while preserving the original as reference.
"""

import logging
from typing import Optional
from pathlib import Path
import asyncio
import replicate
import os
import httpx

logger = logging.getLogger(__name__)


class NanoBananaGenerator:
    """Generate customized character images using Nano Banana."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Nano Banana generator.

        Args:
            api_token: Replicate API token (defaults to REPLICATE_API_TOKEN env var)
        """
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            logger.warning("REPLICATE_API_TOKEN not set. Nano Banana generation will fail.")

        # Set token in environment for replicate SDK
        if self.api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token

    async def generate_image(
        self,
        prompt: str,
        input_image_path: Path,
        output_path: Path,
        aspect_ratio: str = "match_input_image",
        output_format: str = "jpg",
    ) -> Path:
        """
        Generate a customized character image using Nano Banana.

        Args:
            prompt: Text description of desired image transformation
            input_image_path: Path to the reference/input image
            output_path: Path to save the generated image
            aspect_ratio: Aspect ratio for output (default: match_input_image)
            output_format: Output format - jpg or png (default: jpg)

        Returns:
            Path to the generated image file

        Raises:
            Exception: If image generation fails
        """
        try:
            logger.info(f"Generating Nano Banana image with prompt: '{prompt}'")
            logger.info(f"Input image: {input_image_path}")

            # Verify input image exists
            if not input_image_path.exists():
                raise FileNotFoundError(f"Input image not found: {input_image_path}")

            # Prepare output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Open input image for upload
            with open(input_image_path, "rb") as image_file:
                # Run Nano Banana model
                logger.info("Running google/nano-banana model...")

                output = await asyncio.to_thread(
                    replicate.run,
                    "google/nano-banana",
                    input={
                        "prompt": prompt,
                        "image_input": [image_file],
                        "aspect_ratio": aspect_ratio,
                        "output_format": output_format,
                    }
                )

            logger.info(f"Nano Banana generation complete")

            # Download the generated image
            if isinstance(output, str):
                # It's a URL
                image_url = output
            elif isinstance(output, list) and len(output) > 0:
                # It's a list of URLs, take the first one
                image_url = output[0]
            elif hasattr(output, 'read'):
                # It's a FileOutput object
                image_data = output.read()
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                logger.info(f"Generated image saved to {output_path}")
                return output_path
            else:
                raise Exception(f"Unexpected output format from Nano Banana: {type(output)}")

            # Download from URL
            logger.info(f"Downloading generated image from: {image_url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()

                with open(output_path, 'wb') as f:
                    f.write(response.content)

            logger.info(f"Generated image saved to {output_path}")

            # Validate the downloaded image
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"Generated image size: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
            else:
                raise Exception(f"Generated image was not created at {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Failed to generate Nano Banana image: {e}")
            raise Exception(f"Nano Banana image generation failed: {e}")
