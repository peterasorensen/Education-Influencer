"""
Example client for the Educational Video Generation API.

Demonstrates how to:
1. Submit a video generation request
2. Monitor progress via WebSocket
3. Download the final video
"""

import asyncio
import json
import sys
from pathlib import Path
import websockets
import requests


class VideoGenerationClient:
    """Client for interacting with the video generation API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.http_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")

    def generate_video(
        self,
        topic: str,
        duration_seconds: int = 60,
        quality: str = "medium_quality",
        enable_subtitles: bool = True,
    ) -> str:
        """
        Start video generation.

        Args:
            topic: Educational topic
            duration_seconds: Target duration
            quality: Video quality setting
            enable_subtitles: Whether to add subtitles

        Returns:
            Job ID for tracking progress
        """
        url = f"{self.http_url}/api/generate"
        payload = {
            "topic": topic,
            "duration_seconds": duration_seconds,
            "quality": quality,
            "enable_subtitles": enable_subtitles,
        }

        print(f"Submitting video generation request...")
        print(f"Topic: {topic}")
        print(f"Duration: {duration_seconds}s")
        print(f"Quality: {quality}")

        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        job_id = data["job_id"]

        print(f"\n✓ Job created: {job_id}")
        print(f"Status: {data['status']}")
        print(f"Message: {data['message']}\n")

        return job_id

    async def monitor_progress(self, job_id: str) -> str:
        """
        Monitor job progress via WebSocket.

        Args:
            job_id: Job identifier

        Returns:
            Video URL when complete
        """
        ws_url = f"{self.ws_url}/ws/{job_id}"

        print(f"Connecting to WebSocket: {ws_url}")

        async with websockets.connect(ws_url) as websocket:
            print("✓ Connected! Monitoring progress...\n")

            # Send heartbeat every 30 seconds to keep connection alive
            async def heartbeat():
                while True:
                    await asyncio.sleep(30)
                    try:
                        await websocket.send("ping")
                    except:
                        break

            heartbeat_task = asyncio.create_task(heartbeat())

            try:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    msg_type = data.get("type")

                    if msg_type == "status":
                        print(f"Status: {data['status']}")
                        print(f"Progress: {data['progress']}%")
                        print(f"Message: {data['message']}\n")

                    elif msg_type == "progress":
                        progress = data.get("progress", 0)
                        message = data.get("message", "")
                        print(f"[{progress:3d}%] {message}")

                    elif msg_type == "complete":
                        video_url = data["video_url"]
                        print(f"\n✓ Video generation complete!")
                        print(f"Video URL: {self.http_url}{video_url}")
                        return video_url

                    elif msg_type == "error":
                        error = data["error"]
                        print(f"\n✗ Error: {error}")
                        raise Exception(error)

            finally:
                heartbeat_task.cancel()

    def download_video(self, video_url: str, output_path: Path):
        """
        Download the generated video.

        Args:
            video_url: Relative video URL from the API
            output_path: Local path to save the video
        """
        full_url = f"{self.http_url}{video_url}"
        print(f"\nDownloading video from: {full_url}")

        response = requests.get(full_url, stream=True)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rDownload progress: {progress:.1f}%", end="", flush=True)

        print(f"\n✓ Video saved to: {output_path}")
        print(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

    def get_job_status(self, job_id: str) -> dict:
        """
        Get current job status (polling alternative to WebSocket).

        Args:
            job_id: Job identifier

        Returns:
            Job status dictionary
        """
        url = f"{self.http_url}/api/jobs/{job_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    async def generate_and_download(
        self,
        topic: str,
        output_path: Path,
        duration_seconds: int = 60,
        quality: str = "medium_quality",
        enable_subtitles: bool = True,
    ):
        """
        Complete workflow: generate video and download.

        Args:
            topic: Educational topic
            output_path: Where to save the final video
            duration_seconds: Target duration
            quality: Video quality
            enable_subtitles: Whether to add subtitles
        """
        # Submit generation request
        job_id = self.generate_video(
            topic=topic,
            duration_seconds=duration_seconds,
            quality=quality,
            enable_subtitles=enable_subtitles,
        )

        # Monitor progress
        video_url = await self.monitor_progress(job_id)

        # Download video
        self.download_video(video_url, output_path)

        print("\n" + "=" * 60)
        print("✓ All done!")
        print("=" * 60)


async def main():
    """Main function for example usage."""
    # Configuration
    API_URL = "http://localhost:8000"
    TOPIC = "How does photosynthesis work?"
    DURATION = 90
    QUALITY = "medium_quality"
    OUTPUT_FILE = Path("./downloads/photosynthesis_video.mp4")

    # Allow command-line override
    if len(sys.argv) > 1:
        TOPIC = " ".join(sys.argv[1:])

    print("=" * 60)
    print("Educational Video Generation Client")
    print("=" * 60)

    # Create client
    client = VideoGenerationClient(base_url=API_URL)

    # Check server health
    try:
        health = requests.get(f"{API_URL}/health").json()
        print(f"✓ Server is healthy: {health['status']}")
        print(f"Timestamp: {health['timestamp']}\n")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print(f"Make sure the server is running at {API_URL}")
        return

    # Generate and download video
    try:
        await client.generate_and_download(
            topic=TOPIC,
            output_path=OUTPUT_FILE,
            duration_seconds=DURATION,
            quality=QUALITY,
            enable_subtitles=True,
        )
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
