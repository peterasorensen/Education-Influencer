# Educational Video Generation Backend

A powerful FastAPI backend for generating mobile-friendly 9:16 educational videos with AI-powered multi-voice narration, Manim animations, and lip-synced celebrity presenters.

## Features

- **9:16 Mobile-Friendly Videos** - Vertical format optimized for TikTok/Instagram/YouTube Shorts
- **Lip-Synced Celebrity Narrators** - Drake and Sydney Sweeney alternate based on speaker voice
- **Dual-Layer Video Composition**
  - Top half (9:8): Educational Manim animations
  - Bottom half (9:8): Lip-synced celebrity presenter
- **Storyboard-Based Generation** - Structured JSON timeline with visual states (not raw Manim code)
- **Spatial Tracking System** - Prevents visual overlap, intelligent object placement
- **Layout Engine** - Automatic Manim code generation with collision detection
- **World-Class Educational Prompts** - Builds intuition, uses analogies, creates "aha" moments
- Multi-voice conversational scripts (Teacher/Student or Alex/Maya)
- Different TTS voices for each character
- Accurate timestamp extraction with Whisper
- Self-fixing Manim code generation (up to 3 retries)
- ZERO-tolerance audio/video sync (frame-perfect trimming)
- Real-time progress updates via WebSocket
- Subtitle support (single-line, positioned at dividing line)

## Quick Start

### Prerequisites

1. **Python 3.9+**
2. **FFmpeg** (for audio/video processing)
3. **LaTeX** (for Manim text rendering)

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add:
# - OPENAI_API_KEY (required)
# - REPLICATE_API_TOKEN (required for celebrity videos)
```

Get API keys:
- OpenAI: https://platform.openai.com/api-keys
- Replicate: https://replicate.com/account/api-tokens

### Running the Server

```bash
# Development mode
python main.py

# Or with custom port
python main.py 8080

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at `http://localhost:8000`

## Architecture

```
backend/
├── main.py                          # FastAPI server
├── pipeline/
│   ├── script_generator.py          # World-class educational script generation
│   ├── audio_generator.py           # TTS audio synthesis
│   ├── timestamp_extractor.py       # Whisper timestamp extraction
│   ├── storyboard_generator.py      # Structured visual storyboard (JSON timeline)
│   ├── spatial_tracker.py           # Canvas object tracking, overlap prevention
│   ├── layout_engine.py             # Storyboard → Manim code with smart positioning
│   ├── manim_generator.py           # Manim validation & rendering (9:8 support)
│   ├── image_to_video_generator.py  # Celebrity image-to-video (Seedance/Kling)
│   ├── lipsync_generator.py         # Audio-video lip-sync (tmappdev/Kling/Pixverse)
│   ├── video_stitcher.py            # Video compositing & stitching
│   └── resume_detector.py           # Resume from failed jobs
├── assets/
│   ├── drake.jpg                    # Celebrity images
│   └── sydneysweeney.png
├── requirements.txt
└── .env.example
```

## Pipeline Overview

### New Storyboard-Based Pipeline

1. **Script Generation** (0-15%)
   - Generate world-class educational script with GPT-4o
   - Create engaging dialogue with intuition-building and "aha" moments

2. **Audio Generation** (15-35%)
   - Generate audio for each character with different TTS voices
   - Combine segments with appropriate silence

3. **Timestamp Extraction** (35-45%)
   - Extract precise timestamps using Whisper
   - Generate SRT subtitle file
   - Align script with timestamps

4. **Storyboard Generation** (45-48%)
   - Generate structured visual timeline (JSON format)
   - Specify objects, positions, animations, transitions
   - Uses spatial tracking to prevent overlaps

5. **Manim Code Generation & Rendering** (48-60%)
   - Layout engine converts storyboard → Manim code with smart positioning
   - Render in 9:8 format (top half)
   - Validate and self-fix (up to 3 retries)

6. **Celebrity Video Generation** (60-75%)
   - Generate video per segment using Seedance/Kling
   - Alternate Drake/Sydney based on speaker voice
   - Trim to EXACT audio duration (frame-perfect)

7. **Lip-Sync Processing** (75-90%)
   - Sync each celebrity video segment with audio using tmappdev
   - ZERO-tolerance duration matching
   - Trim to EXACT audio duration after sync

8. **Video Compositing** (90-100%)
   - Stack 9:8 Manim video (top) and 9:8 celebrity video (bottom) → 9:16
   - Add single-line subtitles at dividing line
   - Create final mobile video

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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

### GET /api/jobs/{job_id}

Get job status.

### WebSocket /ws/{job_id}

Real-time progress updates.

### GET /api/videos/{job_id}/{filename}

Download generated video.

## Storyboard System

The backend uses a storyboard-based approach to generate educational content:

### Key Components

1. **Storyboard Generator** - Creates structured JSON timeline from script
   - Scene descriptions with pedagogical intent
   - Object specifications (type, content, position, style)
   - Animation timing synchronized with narration
   - Cleanup management for spatial organization

2. **Spatial Tracker** - Prevents visual overlaps
   - 9:8 aspect ratio canvas (1080x960 pixels)
   - 9x8 grid spatial indexing
   - Object lifecycle tracking (start/end times)
   - Intelligent layout suggestions

3. **Layout Engine** - Converts storyboard to Manim code
   - Multiple layout strategies (center-focused, grid, flow, etc.)
   - Automatic collision detection
   - Smart object placement
   - Clean, working Manim code generation

### Storyboard JSON Format

```json
{
  "metadata": {
    "topic": "Your Topic",
    "duration": 60.0,
    "num_scenes": 10
  },
  "scenes": [
    {
      "id": "scene_0",
      "timestamp": {"start": 0.0, "end": 3.0},
      "narration": "Introduction text",
      "visual_type": "title|equation|diagram|shape|text",
      "description": "Complete scene description",
      "elements": ["Text", "MathTex"],
      "region": "center|top_center|bottom_center|etc",
      "cleanup": ["previous_scene_ids"],
      "transitions": ["Write", "FadeIn"],
      "properties": {
        "font_size": 48,
        "color": "BLUE"
      }
    }
  ]
}
```

### Canvas Regions

The 9:8 canvas is divided into 9 regions (3x3 grid):

```
┌─────────────┬─────────────┬─────────────┐
│  TOP_LEFT   │ TOP_CENTER  │  TOP_RIGHT  │
├─────────────┼─────────────┼─────────────┤
│CENTER_LEFT  │   CENTER    │CENTER_RIGHT │
├─────────────┼─────────────┼─────────────┤
│ BOTTOM_LEFT │BOTTOM_CENTER│BOTTOM_RIGHT │
└─────────────┴─────────────┴─────────────┘
```

- Horizontal Range: -5.4 to 5.4 (10.8 units wide)
- Vertical Range: -4.8 to 4.8 (9.6 units tall)
- Center: (0, 0)

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

Available OpenAI TTS voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

## Video Output Format

- **Aspect Ratio**: 9:16 (mobile portrait) = Two 9:8 halves stacked
- **Resolution**: 720x1280 (medium), 1080x1920 (high)
- **Top Half (9:8)**: Educational Manim animations (720x640 or 1080x960)
- **Bottom Half (9:8)**: Lip-synced celebrity presenter (720x640 or 1080x960)
- **Audio**: AAC 192kbps, frame-perfectly synced
- **Subtitles**: Single-line, positioned at middle dividing line (optional)

## Model Costs

**Per segment defaults:**
- Image-to-video: Seedance ~$0.04 (default) | Kling v2.5 ~$0.20
- Lip-sync: tmappdev ~$0.03 (default) | Kling ~$0.03 | Pixverse ~$0.10
- **Total per 60s video** (12 segments): ~$0.84 with defaults

**Resume/Retry Feature:**
- If generation fails, you can resume from the last completed step
- Skips cleanup and reuses completed steps (saves time and money!)
- Just pass `resume_job_id` with the previous job ID in your request

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

### Objects overlapping in animations
- The spatial tracker should prevent this automatically
- Check `storyboard.json` for region assignments
- Ensure cleanup is specified for old objects
- Review occupancy grid at key timestamps

### Text going off screen or objects overlapping
The system includes automatic text wrapping and spatial tracking:
- Generated Manim code includes `wrap_text()` helper for 9:8 canvas
- Spatial tracking prevents overlaps with `is_position_clear()` and `place_object()`
- Canvas boundaries: x [-5.4, 5.4], y [-4.8, 4.8] for 9:8 aspect ratio
- Safe text width: 8.8 units maximum
- Built-in validation with up to 3 self-fixing retries

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

3. **Processing time**
   - Total pipeline: 2-4 minutes
   - Storyboard generation: 2-5 seconds (same as old visual instructions)
   - Layout engine: <100ms
   - Image-to-video: 30-60 seconds
   - Lip-sync: 20-40 seconds

## Development

### Adding new pipeline modules
1. Create module in `pipeline/` directory
2. Import in `pipeline/__init__.py`
3. Integrate into main pipeline in `main.py`

### Working with Storyboards

The storyboard system provides powerful tools for creating educational content:

**Programmatic Creation:**
```python
from pipeline import StoryboardGenerator, LayoutEngine

# Generate storyboard from script
storyboard_gen = StoryboardGenerator(api_key)
storyboard = await storyboard_gen.generate_storyboard(
    script=script,
    topic=topic,
    aligned_timestamps=timestamps
)

# Convert to Manim code
layout_engine = LayoutEngine()
manim_code = layout_engine.process_storyboard(storyboard)
```

**Spatial Tracking:**
```python
from pipeline import SpatialTracker, ObjectType, Region

tracker = SpatialTracker()

# Add object
tracker.add_object(
    object_id="title",
    object_type=ObjectType.TITLE,
    content="Introduction",
    position=(0, 4.0),
    dimensions=(3.0, 0.8),
    start_time=0.0,
    end_time=3.0
)

# Find available space
position = tracker.find_available_space(
    dimensions=(2.0, 1.5),
    time=5.0,
    preferred_regions=[Region.CENTER]
)
```

### Debugging Replicate Outputs

All Replicate API calls automatically log URLs in two places:

1. **Console Logs**: Look for `Replicate video URL:` and `Replicate lipsync URL:`
2. **Metadata Files**: Check `output/{job_id}/celebrity_videos/segment_XXX_replicate_url.txt`

URLs are valid for 24 hours. Download important videos within this timeframe.

```bash
# Find all Replicate URLs for a job
find output/{job_id} -name "*_replicate_url.txt" -exec cat {} \;
```

## Backward Compatibility

The system maintains 100% backward compatibility:
- Old `visual_instructions.json` format still works
- Resume detector supports both formats
- No API changes required
- Automatic format detection

## License

MIT License

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review logs in the output directory
- Ensure all system dependencies are installed
- Check the troubleshooting section above
