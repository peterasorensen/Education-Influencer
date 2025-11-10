# Educational Video Generation Backend

A powerful FastAPI backend for generating educational videos with AI-powered multi-voice narration and Manim animations.

## Features

- Multi-voice conversational scripts using OpenAI GPT-4o
- Different TTS voices for each character (Alex and Maya)
- Accurate timestamp extraction with Whisper
- Manim-aware visual instruction generation
- Self-fixing Manim code generation (up to 3 retries)
- Video stitching with ffmpeg
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
│   ├── manim_generator.py           # Manim code generation & validation
│   └── video_stitcher.py            # Video/audio combination
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
   # Edit .env and add your OpenAI API key
   ```

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
  "enable_subtitles": true
}
```

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

1. **Script Generation** (0-20%)
   - Generate multi-voice conversational script with GPT-4o
   - Create engaging dialogue between Alex (boy) and Maya (girl)

2. **Audio Generation** (20-45%)
   - Generate audio for each character with different TTS voices
   - Combine segments with appropriate silence

3. **Timestamp Extraction** (45-55%)
   - Extract precise timestamps using Whisper
   - Generate SRT subtitle file
   - Align script with timestamps

4. **Visual Instruction Generation** (55-60%)
   - Generate Manim-aware visual instructions
   - Specify animations, transitions, and layouts

5. **Manim Code Generation** (60-75%)
   - Generate Manim Python code from visual instructions
   - Validate and self-fix (up to 3 retries)

6. **Manim Rendering** (75-85%)
   - Render Manim code to video

7. **Video Stitching** (85-95%)
   - Combine Manim video with audio narration
   - Add subtitles if enabled

8. **Completion** (95-100%)
   - Final video ready for download

## Example Usage

### Using curl
```bash
# Start video generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Machine Learning",
    "duration_seconds": 90,
    "quality": "medium_quality",
    "enable_subtitles": true
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

# Start generation
response = requests.post(
    "http://localhost:8000/api/generate",
    json={
        "topic": "Introduction to Neural Networks",
        "duration_seconds": 60,
        "quality": "medium_quality",
        "enable_subtitles": True
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

## Troubleshooting

### Manim rendering fails
- Ensure LaTeX is properly installed
- Try rendering a simple example: `manim --version`
- Check Manim logs in output directory

### Audio generation fails
- Verify OpenAI API key is correct
- Check API quota and billing
- Ensure pydub can find ffmpeg: `ffmpeg -version`

### WebSocket connection issues
- Ensure no firewall blocking WebSocket connections
- Check CORS settings in main.py

### Out of memory
- Reduce video quality setting
- Limit concurrent jobs
- Reduce duration_seconds

## Performance Tips

1. **Use appropriate quality settings**
   - `low_quality`: Fast rendering, 480p
   - `medium_quality`: Balanced, 720p (recommended)
   - `high_quality`: Best quality, 1080p (slower)

2. **Optimize for shorter videos**
   - 30-90 seconds is optimal
   - Longer videos require more processing time

3. **Monitor system resources**
   - Manim rendering is CPU-intensive
   - Limit concurrent jobs based on available cores

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
