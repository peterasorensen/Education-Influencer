"""
Test script for media upload functionality.
"""

import asyncio
import io
from pathlib import Path
from PIL import Image
from pydub import AudioSegment
from pydub.generators import Sine

from pipeline.media_validator import MediaValidator
from pipeline.media_processor import MediaProcessor
from pipeline.media_storage import MediaStorage


class MockUploadFile:
    """Mock UploadFile for testing."""

    def __init__(self, content: bytes, filename: str, content_type: str):
        self.content = content
        self.filename = filename
        self.content_type = content_type
        self._read = False

    async def read(self):
        if not self._read:
            self._read = True
            return self.content
        return b""


async def test_photo_upload():
    """Test photo upload workflow."""
    print("\n=== Testing Photo Upload ===")

    # Create a test image
    img = Image.new('RGB', (1024, 1024), color='blue')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=90)
    img_data = img_buffer.getvalue()

    # Create mock upload file
    mock_file = MockUploadFile(img_data, "test_photo.jpg", "image/jpeg")

    # Test validation
    validator = MediaValidator()
    try:
        photo_data, sanitized_filename = await validator.validate_photo(mock_file)
        print(f"✓ Photo validated: {sanitized_filename}, size: {len(photo_data)} bytes")
    except Exception as e:
        print(f"✗ Photo validation failed: {e}")
        return False

    # Test processing
    processor = MediaProcessor()
    try:
        processed_photo, thumbnail, dimensions = processor.process_photo(photo_data)
        print(f"✓ Photo processed: {dimensions}, main: {len(processed_photo)} bytes, thumb: {len(thumbnail)} bytes")
    except Exception as e:
        print(f"✗ Photo processing failed: {e}")
        return False

    # Test storage
    storage = MediaStorage()
    try:
        metadata = storage.save_photo(
            user_id="test_user",
            photo_data=processed_photo,
            thumbnail_data=thumbnail,
            filename=sanitized_filename,
            dimensions=dimensions
        )
        print(f"✓ Photo saved: {metadata.photo_id}")
        print(f"  - URL: {metadata.photo_url}")
        print(f"  - Thumbnail: {metadata.thumbnail_url}")

        # Verify file exists
        photo_path = storage.get_photo_path("test_user", metadata.photo_id)
        if photo_path and photo_path.exists():
            print(f"✓ Photo file exists: {photo_path}")
        else:
            print(f"✗ Photo file not found")
            return False

        # Test retrieval
        user_media = storage.get_user_media("test_user")
        print(f"✓ User has {len(user_media['photos'])} photos")

        # Test deletion
        success = storage.delete_photo("test_user", metadata.photo_id)
        if success:
            print(f"✓ Photo deleted successfully")
        else:
            print(f"✗ Photo deletion failed")
            return False

    except Exception as e:
        print(f"✗ Photo storage failed: {e}")
        return False

    print("✓ Photo upload workflow completed successfully\n")
    return True


async def test_audio_upload():
    """Test audio upload workflow."""
    print("\n=== Testing Audio Upload ===")

    # Create a test audio (3 second sine wave)
    audio = Sine(440).to_audio_segment(duration=3000)  # 3 seconds
    audio_buffer = io.BytesIO()
    audio.export(audio_buffer, format='mp3')
    audio_data = audio_buffer.getvalue()

    # Create mock upload file
    mock_file = MockUploadFile(audio_data, "test_audio.mp3", "audio/mpeg")

    # Test validation
    validator = MediaValidator()
    try:
        validated_audio, sanitized_filename, duration = await validator.validate_audio(mock_file)
        print(f"✓ Audio validated: {sanitized_filename}, duration: {duration:.2f}s, size: {len(validated_audio)} bytes")
    except Exception as e:
        print(f"✗ Audio validation failed: {e}")
        return False

    # Test processing
    processor = MediaProcessor()
    try:
        processed_audio, final_duration, sample_rate = processor.process_audio(validated_audio, sanitized_filename)
        print(f"✓ Audio processed: {final_duration:.2f}s, {sample_rate}Hz, {len(processed_audio)} bytes")
    except Exception as e:
        print(f"✗ Audio processing failed: {e}")
        return False

    # Test storage
    storage = MediaStorage()
    try:
        metadata = storage.save_audio(
            user_id="test_user",
            audio_data=processed_audio,
            filename=sanitized_filename,
            duration=final_duration,
            sample_rate=sample_rate
        )
        print(f"✓ Audio saved: {metadata.audio_id}")
        print(f"  - URL: {metadata.audio_url}")
        print(f"  - Duration: {metadata.duration:.2f}s")

        # Verify file exists
        audio_path = storage.get_audio_path("test_user", metadata.audio_id)
        if audio_path and audio_path.exists():
            print(f"✓ Audio file exists: {audio_path}")
        else:
            print(f"✗ Audio file not found")
            return False

        # Test retrieval
        user_media = storage.get_user_media("test_user")
        print(f"✓ User has {len(user_media['audio'])} audio files")

        # Test deletion
        success = storage.delete_audio("test_user", metadata.audio_id)
        if success:
            print(f"✓ Audio deleted successfully")
        else:
            print(f"✗ Audio deletion failed")
            return False

    except Exception as e:
        print(f"✗ Audio storage failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("✓ Audio upload workflow completed successfully\n")
    return True


async def test_validation_errors():
    """Test validation error handling."""
    print("\n=== Testing Validation Errors ===")

    validator = MediaValidator()

    # Test oversized photo
    print("Testing oversized photo...")
    large_img = Image.new('RGB', (5000, 5000), color='red')
    img_buffer = io.BytesIO()
    large_img.save(img_buffer, format='JPEG')
    mock_file = MockUploadFile(img_buffer.getvalue(), "large.jpg", "image/jpeg")

    try:
        await validator.validate_photo(mock_file)
        print("✗ Should have rejected oversized image")
    except Exception as e:
        print(f"✓ Correctly rejected oversized image: {e}")

    # Test invalid file type
    print("Testing invalid file type...")
    mock_file = MockUploadFile(b"fake image data", "fake.jpg", "image/jpeg")

    try:
        await validator.validate_photo(mock_file)
        print("✗ Should have rejected invalid file")
    except Exception as e:
        print(f"✓ Correctly rejected invalid file: {e}")

    print("✓ Validation error handling works correctly\n")
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MEDIA UPLOAD FUNCTIONALITY TEST")
    print("=" * 60)

    results = []

    # Run tests
    results.append(await test_photo_upload())
    results.append(await test_audio_upload())
    results.append(await test_validation_errors())

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
