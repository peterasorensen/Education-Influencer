# Educational Video Generation Backend

A powerful FastAPI backend for generating mobile-friendly 9:16 educational videos with AI-powered multi-voice narration, Manim animations, and lip-synced celebrity presenters.

## Features

- **9:16 Mobile-Friendly Videos** - Vertical format optimized for TikTok/Instagram/YouTube Shorts
- **Lip-Synced Celebrity Narrators** - Drake and Sydney Sweeney lip-sync to educational content
- **Dual-Layer Video Composition**
  - Top half: Educational Manim animations
  - Bottom half: Lip-synced celebrity presenter
- Multi-voice conversational scripts using OpenAI GPT-4o
- Different TTS voices for each character (Alex and Maya)
- Accurate timestamp extraction with Whisper
- Manim-aware visual instruction generation
- Self-fixing Manim code generation (up to 3 retries)
- Video stitching and compositing with ffmpeg
- Real-time progress updates via WebSocket
- Subtitle support (SRT format)

## Architecture

```
backend/
├── main.py                          # FastAPI server
├── pipeline/
│   ├── __init__.py
│   ├── script_generator.py          # Multi-voice script generation
│   ├── audio_generator.py           # TTS audio synthesis
│   ├── timestamp_extractor.py       # Whisper timestamp extraction
│   ├── visual_script_generator.py   # Visual instruction generation
│   ├── manim_generator.py           # Manim code generation & validation (9:16 support)
│   ├── image_to_video_generator.py  # Celebrity image-to-video (Seedance/Kling)
│   ├── lipsync_generator.py         # Audio-video lip-sync (Kling/Pixverse)
│   └── video_stitcher.py            # Video compositing & stitching
├── assets/
│   ├── drake.jpg                    # Celebrity images
│   └── sydneysweeney.png
├── requirements.txt
└── .env.example
```

## Prerequisites

### System Dependencies

1. **Python 3.9+**
   ```bash
   python --version  # Verify Python 3.9 or higher
   ```

2. **FFmpeg** (for audio/video processing)
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **LaTeX** (for Manim text rendering)
   ```bash
   # macOS
   brew install --cask mactex

   # Ubuntu/Debian
   sudo apt-get install texlive texlive-latex-extra texlive-fonts-extra texlive-science

   # Windows
   # Download MiKTeX from https://miktex.org/download
   ```

### Python Dependencies

Install all Python packages:
```bash
pip install -r requirements.txt
```

## Setup

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # - OPENAI_API_KEY (required)
   # - REPLICATE_API_TOKEN (required for celebrity videos)
   # - IMAGE_TO_VIDEO_MODEL (optional, defaults to bytedance/seedance-1-pro-fast)
   # - LIPSYNC_MODEL (optional, defaults to kwaivgi/kling-lip-sync)
   ```

   Get API keys:
   - OpenAI: https://platform.openai.com/api-keys
   - Replicate: https://replicate.com/account/api-tokens

   **Model Costs** (per segment, defaults in parentheses):
   - Image-to-video: Seedance ~$0.04 (default) | Kling v2.5 ~$0.20
   - Lip-sync: Kling ~$0.03 (default) | Pixverse ~$0.10
   - **Total per 60s video** (12 segments): ~$0.84 with defaults 🎉

5. **Verify Manim installation**
   ```bash
   manim --version
   ```

## Running the Server

### Development Mode
```bash
python main.py
```

Or with custom port:
```bash
python main.py 8080
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### POST /api/generate
Generate an educational video.

**Request Body:**
```json
{
  "topic": "How does quantum computing work?",
  "duration_seconds": 60,
  "quality": "medium_quality",
  "enable_subtitles": true,
  "celebrity": "drake"
}
```

**Parameters:**
- `topic` (string, required): Educational topic to explain
- `duration_seconds` (int, 30-300): Target video duration
- `quality` (string): `low_quality`, `medium_quality`, or `high_quality`
- `enable_subtitles` (bool): Add subtitles to final video
- `celebrity` (string): `drake` or `sydney_sweeney`

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Video generation job started. Connect to WebSocket for progress updates."
}
```

### GET /api/jobs/{job_id}
Get job status.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "Extracting timestamps...",
  "video_url": null,
  "error": null
}
```

### WebSocket /ws/{job_id}
Real-time progress updates.

**Messages:**
```json
// Progress update
{
  "type": "progress",
  "progress": 45,
  "message": "Extracting timestamps..."
}

// Completion
{
  "type": "complete",
  "video_url": "/api/videos/{job_id}/final_video.mp4"
}

// Error
{
  "type": "error",
  "error": "Error message here"
}
```

### GET /api/videos/{job_id}/{filename}
Download generated video.

## Pipeline Workflow

1. **Script Generation** (0-15%)
   - Generate multi-voice conversational script with GPT-4o
   - Create engaging dialogue between Alex and Maya

2. **Audio Generation** (15-35%)
   - Generate audio for each character with different TTS voices
   - Combine segments with appropriate silence

3. **Timestamp Extraction** (35-45%)
   - Extract precise timestamps using Whisper
   - Generate SRT subtitle file
   - Align script with timestamps

4. **Visual Instruction Generation** (45-50%)
   - Generate Manim-aware visual instructions
   - Specify animations, transitions, and layouts

5. **Manim Animation Rendering** (50-60%)
   - Generate and render Manim code in 9:16 format (top half)
   - Validate and self-fix (up to 3 retries)

6. **Celebrity Video Generation** (60-75%)
   - Convert celebrity image to animated video using Kling v2.5
   - Match audio duration with expressive talking motion

7. **Lip-Sync Processing** (75-90%)
   - Sync celebrity video with audio using Pixverse
   - Ensure realistic lip movements

8. **Video Compositing** (90-100%)
   - Stack Manim video (top) and celebrity video (bottom)
   - Create final 9:16 mobile video
   - Add subtitles if enabled

## Example Usage

### Using curl
```bash
# Start video generation with Drake
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Machine Learning",
    "duration_seconds": 60,
    "quality": "medium_quality",
    "enable_subtitles": true,
    "celebrity": "drake"
  }'

# Check job status
curl http://localhost:8000/api/jobs/{job_id}

# Download video
curl -O http://localhost:8000/api/videos/{job_id}/final_video.mp4
```

### Using Python
```python
import requests
import websocket
import json

# Start generation with Sydney Sweeney
response = requests.post(
    "http://localhost:8000/api/generate",
    json={
        "topic": "Introduction to Neural Networks",
        "duration_seconds": 60,
        "quality": "medium_quality",
        "enable_subtitles": True,
        "celebrity": "sydney_sweeney"
    }
)
job_id = response.json()["job_id"]

# Connect to WebSocket for progress
ws = websocket.WebSocket()
ws.connect(f"ws://localhost:8000/ws/{job_id}")

while True:
    message = json.loads(ws.recv())
    print(f"{message['type']}: {message}")

    if message["type"] == "complete":
        video_url = message["video_url"]
        print(f"Video ready: {video_url}")
        break
```

## Voice Configuration

The system uses different OpenAI TTS voices for each character:

- **Alex** (boy): `onyx` voice - deep, warm
- **Maya** (girl): `nova` voice - friendly, clear

You can customize voices in `pipeline/audio_generator.py`:
```python
VOICE_MAP = {
    "Alex": "onyx",
    "Maya": "nova",
    # Add more characters/voices as needed
}
```

Available OpenAI TTS voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

## Video Output Format

- **Aspect Ratio**: 9:16 (mobile portrait)
- **Resolution**: 720x1280 (medium), 1080x1920 (high)
- **Top Half**: Educational Manim animations
- **Bottom Half**: Lip-synced celebrity presenter
- **Audio**: AAC 192kbps
- **Subtitles**: Embedded (optional)

## Celebrity Assets

Available celebrities:
- **Drake** (`"drake"`) - Male presenter
- **Sydney Sweeney** (`"sydney_sweeney"`) - Female presenter

To add new celebrities:
1. Add high-quality front-facing portrait to `backend/assets/`
2. Update `CELEBRITY_IMAGES` dict in `main.py`

## Troubleshooting

### Manim rendering fails
- Ensure LaTeX is properly installed
- Try rendering a simple example: `manim --version`
- Check Manim logs in output directory

### Audio generation fails
- Verify OpenAI API key is correct
- Check API quota and billing
- Ensure pydub can find ffmpeg: `ffmpeg -version`

### Celebrity video generation fails
- Verify REPLICATE_API_TOKEN is set correctly
- Check Replicate API quota at https://replicate.com/account
- Ensure celebrity images exist in `assets/` directory
- Check Replicate API status

### Lip-sync issues
- Verify audio quality is good (192kbps recommended)
- Ensure video was generated successfully before lip-sync
- Check Replicate API logs for errors

### WebSocket connection issues
- Ensure no firewall blocking WebSocket connections
- Check CORS settings in main.py

### Out of memory
- Reduce video quality setting
- Limit concurrent jobs
- Reduce duration_seconds

## Performance Tips

1. **Use appropriate quality settings**
   - `low_quality`: Fast rendering, 480x854 (9:16)
   - `medium_quality`: Balanced, 720x1280 (recommended)
   - `high_quality`: Best quality, 1080x1920 (slower)

2. **Optimize for shorter videos**
   - 30-60 seconds is optimal for cost and processing time
   - Longer videos require more Replicate API credits

3. **Monitor costs**
   - Kling v2.5: ~$0.10-0.30 per video
   - Pixverse lipsync: ~$0.05-0.15 per video
   - Total: ~$0.15-0.45 per educational video

4. **Processing time**
   - Total pipeline: 2-4 minutes (vs 1-2 min without celebrity)
   - Image-to-video: 30-60 seconds
   - Lip-sync: 20-40 seconds

## Development

### Running tests
```bash
pytest tests/
```

### Adding new pipeline modules
1. Create module in `pipeline/` directory
2. Import in `pipeline/__init__.py`
3. Integrate into main pipeline in `main.py`

### Custom Manim scenes
Modify `pipeline/manim_generator.py` to customize:
- Scene class structure
- Animation styles
- Default layouts

## License

MIT License

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review logs in the output directory
- Ensure all system dependencies are installed
