"""
Media file validation for custom photo and audio uploads.

Validates file types, sizes, and formats for security and compatibility.
"""

import logging
import re
from pathlib import Path
from typing import Tuple, Optional
import io

from PIL import Image
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)


class MediaValidator:
    """Validates uploaded media files for security and compatibility."""

    # File size limits
    MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_AUDIO_SIZE = 2 * 1024 * 1024   # 2 MB

    # Image constraints
    MIN_IMAGE_DIMENSION = 512
    MAX_IMAGE_DIMENSION = 4096

    # Audio constraints
    MIN_AUDIO_DURATION = 2.0  # seconds
    MAX_AUDIO_DURATION = 5.0  # seconds

    # Allowed MIME types
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg": [b"\xff\xd8\xff"],
        "image/png": [b"\x89PNG\r\n\x1a\n"],
        "image/webp": [b"RIFF", b"WEBP"],
    }

    ALLOWED_AUDIO_TYPES = {
        "audio/mpeg": [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2", b"ID3"],
        "audio/wav": [b"RIFF", b"WAVE"],
        "audio/webm": [b"\x1a\x45\xdf\xa3"],
    }

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing special characters and spaces.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name

        # Remove extension temporarily
        name, ext = Path(filename).stem, Path(filename).suffix

        # Replace spaces and special chars with underscores
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

        # Remove multiple consecutive underscores
        name = re.sub(r'_+', '_', name)

        # Trim underscores from start/end
        name = name.strip('_')

        # Truncate to reasonable length
        if len(name) > 50:
            name = name[:50]

        # Ensure we have something
        if not name:
            name = "upload"

        return f"{name}{ext.lower()}"

    @staticmethod
    def check_file_signature(file_data: bytes, mime_type: str, allowed_types: dict) -> bool:
        """
        Check file magic bytes to verify file type.

        Args:
            file_data: First bytes of the file
            mime_type: Claimed MIME type
            allowed_types: Dictionary of allowed MIME types and their signatures

        Returns:
            True if file signature matches claimed type
        """
        if mime_type not in allowed_types:
            return False

        signatures = allowed_types[mime_type]
        for signature in signatures:
            if file_data.startswith(signature):
                return True

        # Special case for WebP (signature is at offset 8)
        if mime_type == "image/webp" and len(file_data) >= 12:
            if file_data[:4] == b"RIFF" and file_data[8:12] == b"WEBP":
                return True

        # Special case for WAV (WAVE signature at offset 8)
        if mime_type == "audio/wav" and len(file_data) >= 12:
            if file_data[:4] == b"RIFF" and file_data[8:12] == b"WAVE":
                return True

        return False

    @staticmethod
    def strip_exif_data(image: Image.Image) -> Image.Image:
        """
        Remove EXIF metadata from image for privacy/security.

        Args:
            image: PIL Image object

        Returns:
            Image without EXIF data
        """
        # Create a new image without EXIF data
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        return image_without_exif

    async def validate_photo(self, photo: UploadFile) -> Tuple[bytes, str]:
        """
        Validate uploaded photo file.

        Args:
            photo: Uploaded photo file

        Returns:
            Tuple of (file_content, sanitized_filename)

        Raises:
            HTTPException: If validation fails
        """
        # Check file size
        content = await photo.read()
        file_size = len(content)

        if file_size > self.MAX_PHOTO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Photo size exceeds maximum allowed size of {self.MAX_PHOTO_SIZE / 1024 / 1024:.1f}MB"
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="Photo file is empty")

        # Check MIME type
        mime_type = photo.content_type
        if mime_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type: {mime_type}. Allowed: JPEG, PNG, WebP"
            )

        # Verify file signature (magic bytes)
        if not self.check_file_signature(content[:12], mime_type, self.ALLOWED_IMAGE_TYPES):
            raise HTTPException(
                status_code=400,
                detail="File signature does not match claimed image type (possible file spoofing)"
            )

        # Validate image can be opened and check dimensions
        try:
            image = Image.open(io.BytesIO(content))
            width, height = image.size

            if width < self.MIN_IMAGE_DIMENSION or height < self.MIN_IMAGE_DIMENSION:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image dimensions too small. Minimum: {self.MIN_IMAGE_DIMENSION}x{self.MIN_IMAGE_DIMENSION}"
                )

            if width > self.MAX_IMAGE_DIMENSION or height > self.MAX_IMAGE_DIMENSION:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image dimensions too large. Maximum: {self.MAX_IMAGE_DIMENSION}x{self.MAX_IMAGE_DIMENSION}"
                )

        except Exception as e:
            logger.error(f"Failed to validate image: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted image file: {str(e)}")

        # Sanitize filename
        sanitized_filename = self.sanitize_filename(photo.filename or "photo.jpg")

        logger.info(f"Photo validated: {sanitized_filename}, size: {file_size} bytes, dimensions: {width}x{height}")

        return content, sanitized_filename

    async def validate_audio(self, audio: UploadFile) -> Tuple[bytes, str, float]:
        """
        Validate uploaded audio file.

        Args:
            audio: Uploaded audio file

        Returns:
            Tuple of (file_content, sanitized_filename, duration)

        Raises:
            HTTPException: If validation fails
        """
        # Check file size
        content = await audio.read()
        file_size = len(content)

        if file_size > self.MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Audio size exceeds maximum allowed size of {self.MAX_AUDIO_SIZE / 1024 / 1024:.1f}MB"
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="Audio file is empty")

        # Check MIME type
        mime_type = audio.content_type
        if mime_type not in self.ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio type: {mime_type}. Allowed: MP3, WAV, WebM"
            )

        # Verify file signature (magic bytes)
        if not self.check_file_signature(content[:12], mime_type, self.ALLOWED_AUDIO_TYPES):
            raise HTTPException(
                status_code=400,
                detail="File signature does not match claimed audio type (possible file spoofing)"
            )

        # Get audio duration using mutagen or pydub
        try:
            import tempfile
            from mutagen.mp3 import MP3
            from mutagen.wave import WAVE
            from pydub import AudioSegment

            # Write to temp file for duration check
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename or "audio").suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                # Try mutagen first (more accurate)
                if mime_type == "audio/mpeg":
                    audio_file = MP3(tmp_path)
                    duration = audio_file.info.length
                elif mime_type == "audio/wav":
                    audio_file = WAVE(tmp_path)
                    duration = audio_file.info.length
                else:
                    # Fallback to pydub for WebM
                    audio_segment = AudioSegment.from_file(tmp_path)
                    duration = len(audio_segment) / 1000.0

                # Validate duration
                if duration < self.MIN_AUDIO_DURATION:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Audio too short. Minimum duration: {self.MIN_AUDIO_DURATION}s, got: {duration:.2f}s"
                    )

                if duration > self.MAX_AUDIO_DURATION:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Audio too long. Maximum duration: {self.MAX_AUDIO_DURATION}s, got: {duration:.2f}s"
                    )

            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to validate audio: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted audio file: {str(e)}")

        # Sanitize filename
        sanitized_filename = self.sanitize_filename(audio.filename or "audio.mp3")

        logger.info(f"Audio validated: {sanitized_filename}, size: {file_size} bytes, duration: {duration:.2f}s")

        return content, sanitized_filename, duration
