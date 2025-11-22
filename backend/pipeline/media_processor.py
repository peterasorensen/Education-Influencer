"""
Media file processing for custom photo and audio uploads.

Processes images (resize, thumbnail, format conversion) and audio (format conversion, normalization).
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple
import io

from PIL import Image
from pydub import AudioSegment

logger = logging.getLogger(__name__)


class MediaProcessor:
    """Processes media files for storage and use in video generation."""

    # Processing settings
    THUMBNAIL_SIZE = (256, 256)
    TARGET_IMAGE_FORMAT = "JPEG"
    TARGET_AUDIO_FORMAT = "mp3"
    TARGET_SAMPLE_RATE = 24000
    MAX_AUDIO_DURATION = 5.0  # seconds

    def __init__(self):
        """Initialize media processor."""
        self.validate_dependencies()

    @staticmethod
    def validate_dependencies():
        """Check if required dependencies are available."""
        try:
            # Check if ffmpeg is available
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                logger.warning("ffmpeg not found. Audio processing may fail.")
        except FileNotFoundError:
            logger.warning("ffmpeg not found in PATH. Audio processing may fail.")

    def create_thumbnail(self, image: Image.Image, size: Tuple[int, int] = None) -> Image.Image:
        """
        Create a thumbnail from an image.

        Args:
            image: PIL Image object
            size: Thumbnail size (width, height), defaults to THUMBNAIL_SIZE

        Returns:
            Thumbnail image
        """
        if size is None:
            size = self.THUMBNAIL_SIZE

        # Create a copy to avoid modifying original
        img_copy = image.copy()

        # Convert to RGB if necessary (for JPEG compatibility)
        if img_copy.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img_copy.size, (255, 255, 255))
            if img_copy.mode == 'P':
                img_copy = img_copy.convert('RGBA')
            background.paste(img_copy, mask=img_copy.split()[-1] if img_copy.mode == 'RGBA' else None)
            img_copy = background

        # Use thumbnail method to maintain aspect ratio
        img_copy.thumbnail(size, Image.Resampling.LANCZOS)

        logger.info(f"Created thumbnail: {img_copy.size}")
        return img_copy

    def process_photo(self, image_data: bytes) -> Tuple[bytes, bytes, Tuple[int, int]]:
        """
        Process uploaded photo: convert to JPEG, create thumbnail, strip EXIF.

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple of (processed_image_bytes, thumbnail_bytes, dimensions)
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            original_size = image.size

            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                logger.info(f"Converting image from {image.mode} to RGB")
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                    image = background
                else:
                    image = image.convert('RGB')

            # Strip EXIF data (privacy/security)
            data = list(image.getdata())
            clean_image = Image.new(image.mode, image.size)
            clean_image.putdata(data)

            # Save main image as JPEG
            main_buffer = io.BytesIO()
            clean_image.save(main_buffer, format=self.TARGET_IMAGE_FORMAT, quality=90, optimize=True)
            main_bytes = main_buffer.getvalue()

            # Create and save thumbnail
            thumbnail = self.create_thumbnail(clean_image)
            thumb_buffer = io.BytesIO()
            thumbnail.save(thumb_buffer, format=self.TARGET_IMAGE_FORMAT, quality=85, optimize=True)
            thumb_bytes = thumb_buffer.getvalue()

            logger.info(f"Processed photo: {original_size} -> main: {len(main_bytes)} bytes, thumbnail: {len(thumb_bytes)} bytes")

            return main_bytes, thumb_bytes, original_size

        except Exception as e:
            logger.error(f"Failed to process photo: {e}")
            raise Exception(f"Photo processing failed: {str(e)}")

    def convert_audio_format(self, audio_path: Path, output_path: Path) -> None:
        """
        Convert audio to MP3 format using ffmpeg.

        Args:
            audio_path: Path to input audio file
            output_path: Path to output MP3 file
        """
        try:
            # Use ffmpeg for conversion with specific parameters
            # -ac 1: mono channel
            # -ar 24000: 24kHz sample rate
            # -ab 128k: 128kbps bitrate
            # -t 5: trim to max 5 seconds
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),
                "-ac", "1",  # Mono
                "-ar", str(self.TARGET_SAMPLE_RATE),  # 24kHz
                "-ab", "128k",  # 128 kbps
                "-t", str(self.MAX_AUDIO_DURATION),  # Max 5 seconds
                "-y",  # Overwrite output
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"Audio converted: {audio_path} -> {output_path}")

        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg conversion failed: {e.stderr}")
            raise Exception(f"Audio conversion failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Failed to convert audio: {e}")
            raise Exception(f"Audio conversion failed: {str(e)}")

    def process_audio(self, audio_data: bytes, original_filename: str) -> Tuple[bytes, float, int]:
        """
        Process uploaded audio: convert to mono MP3 at 24kHz, trim to max 5 seconds.

        Args:
            audio_data: Raw audio bytes
            original_filename: Original filename (for format detection)

        Returns:
            Tuple of (processed_audio_bytes, duration, sample_rate)
        """
        temp_input = None
        temp_output = None

        try:
            # Determine input format from filename
            suffix = Path(original_filename).suffix.lower()
            if not suffix:
                suffix = ".mp3"

            # Create temporary input file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
                tmp_in.write(audio_data)
                temp_input = Path(tmp_in.name)

            # Create temporary output file
            temp_output = Path(tempfile.mktemp(suffix=".mp3"))

            # Convert using ffmpeg
            self.convert_audio_format(temp_input, temp_output)

            # Read processed audio
            with open(temp_output, 'rb') as f:
                processed_bytes = f.read()

            # Get duration using pydub
            audio_segment = AudioSegment.from_file(str(temp_output))
            duration = len(audio_segment) / 1000.0  # Convert to seconds

            logger.info(f"Processed audio: {len(audio_data)} bytes -> {len(processed_bytes)} bytes, duration: {duration:.2f}s, sample_rate: {self.TARGET_SAMPLE_RATE}Hz")

            return processed_bytes, duration, self.TARGET_SAMPLE_RATE

        except Exception as e:
            logger.error(f"Failed to process audio: {e}")
            raise Exception(f"Audio processing failed: {str(e)}")

        finally:
            # Clean up temporary files
            if temp_input and temp_input.exists():
                temp_input.unlink(missing_ok=True)
            if temp_output and temp_output.exists():
                temp_output.unlink(missing_ok=True)

    def trim_audio(self, audio_data: bytes, max_duration: float = None) -> bytes:
        """
        Trim audio to maximum duration.

        Args:
            audio_data: Audio bytes
            max_duration: Maximum duration in seconds (defaults to MAX_AUDIO_DURATION)

        Returns:
            Trimmed audio bytes
        """
        if max_duration is None:
            max_duration = self.MAX_AUDIO_DURATION

        try:
            # Load audio
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))

            # Get current duration
            current_duration = len(audio_segment) / 1000.0

            if current_duration <= max_duration:
                logger.info(f"Audio already within duration limit: {current_duration:.2f}s <= {max_duration:.2f}s")
                return audio_data

            # Trim to max duration
            max_duration_ms = int(max_duration * 1000)
            trimmed_audio = audio_segment[:max_duration_ms]

            # Export to bytes
            buffer = io.BytesIO()
            trimmed_audio.export(buffer, format="mp3")
            trimmed_bytes = buffer.getvalue()

            logger.info(f"Trimmed audio: {current_duration:.2f}s -> {max_duration:.2f}s")

            return trimmed_bytes

        except Exception as e:
            logger.error(f"Failed to trim audio: {e}")
            raise Exception(f"Audio trimming failed: {str(e)}")
