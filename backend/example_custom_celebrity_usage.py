"""
Example: Using Custom Celebrity Upload API

This script demonstrates how to:
1. Upload a custom photo
2. Upload a custom audio clip
3. Generate a video using the custom media
"""

import requests
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
USER_ID = "example_user"

# File paths (replace with your actual files)
PHOTO_PATH = "my_photo.jpg"  # Your photo file
AUDIO_PATH = "my_voice.mp3"  # Your 2-5 second audio clip


def upload_photo(photo_path: str, user_id: str = USER_ID) -> dict:
    """Upload a custom photo."""
    print(f"\n1. Uploading photo: {photo_path}")

    url = f"{BASE_URL}/api/upload/photo"

    with open(photo_path, 'rb') as f:
        files = {'photo': f}
        data = {'user_id': user_id}
        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Photo uploaded successfully!")
        print(f"   Photo ID: {result['photo_id']}")
        print(f"   URL: {result['photo_url']}")
        print(f"   Thumbnail: {result['thumbnail_url']}")
        return result
    else:
        print(f"   ✗ Upload failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        return None


def upload_audio(audio_path: str, user_id: str = USER_ID) -> dict:
    """Upload a custom audio clip."""
    print(f"\n2. Uploading audio: {audio_path}")

    url = f"{BASE_URL}/api/upload/audio"

    with open(audio_path, 'rb') as f:
        files = {'audio': f}
        data = {'user_id': user_id}
        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Audio uploaded successfully!")
        print(f"   Audio ID: {result['audio_id']}")
        print(f"   URL: {result['audio_url']}")
        print(f"   Duration: {result['duration']:.2f}s")
        return result
    else:
        print(f"   ✗ Upload failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        return None


def get_user_media(user_id: str = USER_ID) -> dict:
    """Get all media for a user."""
    print(f"\n3. Getting all media for user: {user_id}")

    url = f"{BASE_URL}/api/media/user/{user_id}"
    response = requests.get(url)

    if response.status_code == 200:
        media = response.json()
        print(f"   ✓ Found {len(media['photos'])} photos and {len(media['audio'])} audio clips")
        return media
    else:
        print(f"   ✗ Failed to get media: {response.status_code}")
        return None


def generate_video_with_custom_celebrity(
    topic: str,
    photo_id: str,
    audio_id: str,
    user_id: str = USER_ID
) -> dict:
    """Generate a video using custom celebrity."""
    print(f"\n4. Generating video with custom celebrity")
    print(f"   Topic: {topic}")
    print(f"   Photo ID: {photo_id}")
    print(f"   Audio ID: {audio_id}")

    url = f"{BASE_URL}/api/generate"

    payload = {
        "topic": topic,
        "duration_seconds": 60,
        "quality": "medium_quality",
        "enable_subtitles": True,
        "renderer": "manim",

        # Custom celebrity settings
        "celebrity_mode": "custom",
        "custom_photo_id": photo_id,
        "custom_audio_id": audio_id,
        "user_id": user_id
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Video generation started!")
        print(f"   Job ID: {result['jobId']}")
        print(f"   Status: {result['status']}")
        return result
    else:
        print(f"   ✗ Generation failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        return None


def monitor_video_generation(job_id: str, max_wait: int = 600):
    """Monitor video generation progress."""
    print(f"\n5. Monitoring video generation (Job ID: {job_id})")

    url = f"{BASE_URL}/api/jobs/{job_id}"
    start_time = time.time()

    while time.time() - start_time < max_wait:
        response = requests.get(url)

        if response.status_code == 200:
            status = response.json()
            progress = status.get('progress', 0)
            message = status.get('message', '')

            print(f"\r   Progress: {progress}% - {message}    ", end='', flush=True)

            if status['status'] == 'completed':
                video_url = status.get('video_url')
                print(f"\n   ✓ Video completed!")
                print(f"   Video URL: {BASE_URL}{video_url}")
                return video_url
            elif status['status'] == 'failed':
                error = status.get('error', 'Unknown error')
                print(f"\n   ✗ Video generation failed: {error}")
                return None

        time.sleep(2)

    print(f"\n   ✗ Timeout waiting for video generation")
    return None


def delete_media(photo_id: str = None, audio_id: str = None, user_id: str = USER_ID):
    """Delete uploaded media."""
    print(f"\n6. Cleaning up uploaded media")

    if photo_id:
        url = f"{BASE_URL}/api/media/photos/{user_id}/{photo_id}"
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"   ✓ Photo deleted: {photo_id}")
        else:
            print(f"   ✗ Failed to delete photo")

    if audio_id:
        url = f"{BASE_URL}/api/media/audio/{user_id}/{audio_id}"
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"   ✓ Audio deleted: {audio_id}")
        else:
            print(f"   ✗ Failed to delete audio")


def main():
    """Run the complete workflow."""
    print("=" * 70)
    print("CUSTOM CELEBRITY VIDEO GENERATION - EXAMPLE")
    print("=" * 70)

    # Check if files exist
    if not Path(PHOTO_PATH).exists():
        print(f"\n✗ Photo file not found: {PHOTO_PATH}")
        print("  Please update PHOTO_PATH in this script to point to your photo.")
        return

    if not Path(AUDIO_PATH).exists():
        print(f"\n✗ Audio file not found: {AUDIO_PATH}")
        print("  Please update AUDIO_PATH in this script to point to your audio clip.")
        return

    # 1. Upload photo
    photo_result = upload_photo(PHOTO_PATH)
    if not photo_result:
        return

    # 2. Upload audio
    audio_result = upload_audio(AUDIO_PATH)
    if not audio_result:
        return

    # 3. View all media
    get_user_media()

    # 4. Generate video
    video_result = generate_video_with_custom_celebrity(
        topic="Introduction to Machine Learning",
        photo_id=photo_result['photo_id'],
        audio_id=audio_result['audio_id']
    )

    if not video_result:
        return

    # 5. Monitor progress (optional - can also use WebSocket)
    # video_url = monitor_video_generation(video_result['jobId'])

    # 6. Cleanup (optional)
    # delete_media(
    #     photo_id=photo_result['photo_id'],
    #     audio_id=audio_result['audio_id']
    # )

    print("\n" + "=" * 70)
    print("EXAMPLE COMPLETED")
    print("=" * 70)
    print(f"\nYour custom celebrity is ready!")
    print(f"Photo ID: {photo_result['photo_id']}")
    print(f"Audio ID: {audio_result['audio_id']}")
    print(f"\nTo generate more videos, use:")
    print(f'  POST {BASE_URL}/api/generate')
    print(f'  with celebrity_mode="custom" and the IDs above')


if __name__ == "__main__":
    main()
