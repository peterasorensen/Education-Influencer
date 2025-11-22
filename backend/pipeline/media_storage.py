"""
Media storage management for custom photo and audio uploads.

Manages file storage, metadata persistence, and media retrieval.
"""

import logging
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from models.media_models import PhotoMetadata, AudioMetadata

logger = logging.getLogger(__name__)


class MediaStorage:
    """Manages storage of uploaded media files and their metadata."""

    def __init__(self, base_upload_dir: Path = None):
        """
        Initialize media storage.

        Args:
            base_upload_dir: Base directory for uploads (defaults to ./uploads)
        """
        if base_upload_dir is None:
            base_upload_dir = Path("./uploads")

        self.base_dir = base_upload_dir
        self.photos_dir = self.base_dir / "photos"
        self.audio_dir = self.base_dir / "audio"
        self.metadata_dir = self.base_dir / "metadata"

        # Create directories
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Media storage initialized at {self.base_dir}")

    def _get_user_photo_dir(self, user_id: str) -> Path:
        """Get user-specific photo directory."""
        user_dir = self.photos_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _get_user_audio_dir(self, user_id: str) -> Path:
        """Get user-specific audio directory."""
        user_dir = self.audio_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _get_metadata_path(self, user_id: str) -> Path:
        """Get path to user's metadata file."""
        return self.metadata_dir / f"{user_id}.json"

    def _load_metadata(self, user_id: str) -> Dict:
        """
        Load user's media metadata.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with 'photos' and 'audio' lists
        """
        metadata_path = self._get_metadata_path(user_id)

        if not metadata_path.exists():
            return {"photos": [], "audio": []}

        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata for user {user_id}: {e}")
            return {"photos": [], "audio": []}

    def _save_metadata(self, user_id: str, metadata: Dict) -> None:
        """
        Save user's media metadata.

        Args:
            user_id: User identifier
            metadata: Metadata dictionary
        """
        metadata_path = self._get_metadata_path(user_id)

        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved metadata for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save metadata for user {user_id}: {e}")
            raise Exception(f"Failed to save metadata: {str(e)}")

    def save_photo(
        self,
        user_id: str,
        photo_data: bytes,
        thumbnail_data: bytes,
        filename: str,
        dimensions: Tuple[int, int]
    ) -> PhotoMetadata:
        """
        Save photo and thumbnail to storage.

        Args:
            user_id: User identifier
            photo_data: Processed photo bytes
            thumbnail_data: Thumbnail bytes
            filename: Sanitized filename
            dimensions: Image dimensions (width, height)

        Returns:
            PhotoMetadata object
        """
        try:
            # Generate unique photo ID
            photo_id = str(uuid.uuid4())

            # Get user directory
            user_dir = self._get_user_photo_dir(user_id)

            # Save main photo
            photo_path = user_dir / f"{photo_id}.jpg"
            with open(photo_path, 'wb') as f:
                f.write(photo_data)

            # Save thumbnail
            thumbnail_path = user_dir / f"{photo_id}_thumb.jpg"
            with open(thumbnail_path, 'wb') as f:
                f.write(thumbnail_data)

            # Create metadata
            metadata = PhotoMetadata(
                photo_id=photo_id,
                photo_url=f"/api/media/photos/{user_id}/{photo_id}.jpg",
                thumbnail_url=f"/api/media/photos/{user_id}/{photo_id}_thumb.jpg",
                filename=filename,
                size=len(photo_data),
                dimensions=dimensions,
                created_at=datetime.now().isoformat()
            )

            # Update user metadata
            user_metadata = self._load_metadata(user_id)
            user_metadata["photos"].append(metadata.model_dump())
            self._save_metadata(user_id, user_metadata)

            logger.info(f"Saved photo {photo_id} for user {user_id}: {photo_path}")

            return metadata

        except Exception as e:
            logger.error(f"Failed to save photo: {e}")
            raise Exception(f"Failed to save photo: {str(e)}")

    def save_audio(
        self,
        user_id: str,
        audio_data: bytes,
        filename: str,
        duration: float,
        sample_rate: int
    ) -> AudioMetadata:
        """
        Save audio to storage.

        Args:
            user_id: User identifier
            audio_data: Processed audio bytes
            filename: Sanitized filename
            duration: Audio duration in seconds
            sample_rate: Audio sample rate

        Returns:
            AudioMetadata object
        """
        try:
            # Generate unique audio ID
            audio_id = str(uuid.uuid4())

            # Get user directory
            user_dir = self._get_user_audio_dir(user_id)

            # Save audio
            audio_path = user_dir / f"{audio_id}.mp3"
            with open(audio_path, 'wb') as f:
                f.write(audio_data)

            # Create metadata
            metadata = AudioMetadata(
                audio_id=audio_id,
                audio_url=f"/api/media/audio/{user_id}/{audio_id}.mp3",
                filename=filename,
                size=len(audio_data),
                duration=duration,
                sample_rate=sample_rate,
                created_at=datetime.now().isoformat()
            )

            # Update user metadata
            user_metadata = self._load_metadata(user_id)
            user_metadata["audio"].append(metadata.model_dump())
            self._save_metadata(user_id, user_metadata)

            logger.info(f"Saved audio {audio_id} for user {user_id}: {audio_path}")

            return metadata

        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise Exception(f"Failed to save audio: {str(e)}")

    def get_user_media(self, user_id: str) -> Dict[str, List]:
        """
        Get all media for a user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with 'photos' and 'audio' lists
        """
        return self._load_metadata(user_id)

    def get_photo_path(self, user_id: str, photo_id: str) -> Optional[Path]:
        """
        Get path to a photo file.

        Args:
            user_id: User identifier
            photo_id: Photo identifier

        Returns:
            Path to photo file, or None if not found
        """
        photo_path = self._get_user_photo_dir(user_id) / f"{photo_id}.jpg"
        return photo_path if photo_path.exists() else None

    def get_audio_path(self, user_id: str, audio_id: str) -> Optional[Path]:
        """
        Get path to an audio file.

        Args:
            user_id: User identifier
            audio_id: Audio identifier

        Returns:
            Path to audio file, or None if not found
        """
        audio_path = self._get_user_audio_dir(user_id) / f"{audio_id}.mp3"
        return audio_path if audio_path.exists() else None

    def delete_photo(self, user_id: str, photo_id: str) -> bool:
        """
        Delete a photo and its thumbnail.

        Args:
            user_id: User identifier
            photo_id: Photo identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get paths
            user_dir = self._get_user_photo_dir(user_id)
            photo_path = user_dir / f"{photo_id}.jpg"
            thumbnail_path = user_dir / f"{photo_id}_thumb.jpg"

            # Delete files
            deleted = False
            if photo_path.exists():
                photo_path.unlink()
                deleted = True

            if thumbnail_path.exists():
                thumbnail_path.unlink()

            if not deleted:
                logger.warning(f"Photo {photo_id} not found for user {user_id}")
                return False

            # Update metadata
            user_metadata = self._load_metadata(user_id)
            user_metadata["photos"] = [
                p for p in user_metadata["photos"]
                if p["photo_id"] != photo_id
            ]
            self._save_metadata(user_id, user_metadata)

            logger.info(f"Deleted photo {photo_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete photo {photo_id}: {e}")
            return False

    def delete_audio(self, user_id: str, audio_id: str) -> bool:
        """
        Delete an audio file.

        Args:
            user_id: User identifier
            audio_id: Audio identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get path
            user_dir = self._get_user_audio_dir(user_id)
            audio_path = user_dir / f"{audio_id}.mp3"

            # Delete file
            if not audio_path.exists():
                logger.warning(f"Audio {audio_id} not found for user {user_id}")
                return False

            audio_path.unlink()

            # Update metadata
            user_metadata = self._load_metadata(user_id)
            user_metadata["audio"] = [
                a for a in user_metadata["audio"]
                if a["audio_id"] != audio_id
            ]
            self._save_metadata(user_id, user_metadata)

            logger.info(f"Deleted audio {audio_id} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete audio {audio_id}: {e}")
            return False

    def get_photo_metadata(self, user_id: str, photo_id: str) -> Optional[PhotoMetadata]:
        """
        Get metadata for a specific photo.

        Args:
            user_id: User identifier
            photo_id: Photo identifier

        Returns:
            PhotoMetadata object or None if not found
        """
        user_metadata = self._load_metadata(user_id)
        for photo in user_metadata["photos"]:
            if photo["photo_id"] == photo_id:
                return PhotoMetadata(**photo)
        return None

    def get_audio_metadata(self, user_id: str, audio_id: str) -> Optional[AudioMetadata]:
        """
        Get metadata for a specific audio file.

        Args:
            user_id: User identifier
            audio_id: Audio identifier

        Returns:
            AudioMetadata object or None if not found
        """
        user_metadata = self._load_metadata(user_id)
        for audio in user_metadata["audio"]:
            if audio["audio_id"] == audio_id:
                return AudioMetadata(**audio)
        return None
