"""
Celebrity Loader - Dynamic Celebrity Asset Discovery

Automatically discovers celebrity assets from the assets directory.
Looks for image and audio files in each celebrity subdirectory.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class CelebrityLoader:
    """Dynamically load celebrity assets from the assets directory."""

    def __init__(self, assets_dir: Path):
        """
        Initialize the celebrity loader.

        Args:
            assets_dir: Path to the assets directory
        """
        self.assets_dir = Path(assets_dir)
        self.celebrities: Dict[str, Dict[str, Path]] = {}
        self._load_celebrities()

    def _load_celebrities(self):
        """Scan assets directory and load all celebrity configurations."""
        if not self.assets_dir.exists():
            logger.warning(f"Assets directory not found: {self.assets_dir}")
            return

        # Scan each subdirectory in assets/
        for celeb_dir in self.assets_dir.iterdir():
            if not celeb_dir.is_dir():
                continue

            # Skip hidden directories and common non-celebrity folders
            if celeb_dir.name.startswith('.') or celeb_dir.name in ['__pycache__', 'temp', 'cache']:
                continue

            # Find image and audio files
            image_path = self._find_first_image(celeb_dir)
            audio_path = self._find_first_audio(celeb_dir)

            # Only add if we found at least an image
            if image_path:
                celeb_id = celeb_dir.name
                display_name = self._get_display_name(celeb_dir)

                self.celebrities[celeb_id] = {
                    "id": celeb_id,
                    "name": display_name,
                    "image": image_path,
                    "audio": audio_path,  # May be None
                }

                logger.info(f"Loaded celebrity: {celeb_id} ({display_name})")
                logger.info(f"  Image: {image_path.name if image_path else 'None'}")
                logger.info(f"  Audio: {audio_path.name if audio_path else 'None'}")
            else:
                logger.warning(f"Skipping {celeb_dir.name}: No image file found")

        logger.info(f"Loaded {len(self.celebrities)} celebrities total")

    def _find_first_image(self, directory: Path) -> Optional[Path]:
        """
        Find the first image file in a directory.

        Args:
            directory: Directory to search

        Returns:
            Path to first image file, or None if not found
        """
        image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif']

        for ext in image_extensions:
            # Try exact match first (e.g., goku.png)
            exact_match = directory / f"{directory.name}{ext}"
            if exact_match.exists():
                return exact_match

        # Fall back to any image file
        for ext in image_extensions:
            images = list(directory.glob(f"*{ext}"))
            if images:
                return images[0]

        return None

    def _find_first_audio(self, directory: Path) -> Optional[Path]:
        """
        Find the first audio file in a directory.

        Args:
            directory: Directory to search

        Returns:
            Path to first audio file, or None if not found
        """
        audio_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac']

        for ext in audio_extensions:
            # Try exact match first (e.g., goku.mp3)
            exact_match = directory / f"{directory.name}{ext}"
            if exact_match.exists():
                return exact_match

        # Fall back to any audio file
        for ext in audio_extensions:
            audios = list(directory.glob(f"*{ext}"))
            if audios:
                return audios[0]

        return None

    def _get_display_name(self, directory: Path) -> str:
        """
        Get display name for a celebrity from name.txt or directory name.

        Args:
            directory: Celebrity directory

        Returns:
            Display name for the celebrity
        """
        # Check for name.txt file
        name_file = directory / "name.txt"
        if name_file.exists():
            try:
                display_name = name_file.read_text(encoding='utf-8').strip()
                if display_name:
                    return display_name
            except Exception as e:
                logger.warning(f"Failed to read {name_file}: {e}")

        # Fall back to formatting directory name
        # Convert snake_case or kebab-case to Title Case
        name = directory.name.replace('_', ' ').replace('-', ' ')
        return name.title()

    def get_all_celebrities(self) -> Dict[str, Dict[str, Path]]:
        """
        Get all loaded celebrities.

        Returns:
            Dictionary of celebrity ID -> celebrity config
        """
        return self.celebrities

    def get_celebrity_images(self) -> Dict[str, Path]:
        """
        Get mapping of celebrity ID -> image path.

        Returns:
            Dictionary of celebrity ID -> image path
        """
        return {
            celeb_id: config["image"]
            for celeb_id, config in self.celebrities.items()
            if config.get("image")
        }

    def get_celebrity_audio(self) -> Dict[str, Path]:
        """
        Get mapping of celebrity ID -> audio path.

        Returns:
            Dictionary of celebrity ID -> audio path (excludes celebrities without audio)
        """
        return {
            celeb_id: config["audio"]
            for celeb_id, config in self.celebrities.items()
            if config.get("audio")
        }

    def create_name_files(self):
        """
        Create name.txt files for celebrities that don't have one.

        This generates a display name from the directory name and saves it.
        """
        for celeb_id, config in self.celebrities.items():
            celeb_dir = self.assets_dir / celeb_id
            name_file = celeb_dir / "name.txt"

            if not name_file.exists():
                display_name = config["name"]
                name_file.write_text(display_name, encoding='utf-8')
                logger.info(f"Created name.txt for {celeb_id}: {display_name}")
