# Quick Start Guide

Get up and running with the Educational Video Generation Backend in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- Python 3.9 or higher
- ffmpeg installed
- An OpenAI API key

## Installation Steps

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Replace 'your_openai_api_key_here' with your actual key
nano .env  # or use your preferred editor
```

Your `.env` file should look like:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

### 5. Verify Setup
```bash
python test_setup.py
```

This will check if all dependencies are properly installed.

### 6. Start the Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

### 7. Test the API

Open your browser and visit:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Generate Your First Video

### Option 1: Using the Example Client (Recommended)

```bash
# In a new terminal (keep server running in the first terminal)
python example_client.py "How does gravity work?"
```

This will:
1. Submit a video generation request
2. Monitor progress in real-time
3. Download the final video to `./downloads/`

### Option 2: Using curl

```bash
# Start video generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Introduction to Python Programming",
    "duration_seconds": 60,
    "quality": "medium_quality",
    "enable_subtitles": true
  }'

# This will return a job_id, use it to check status:
curl http://localhost:8000/api/jobs/{job_id}
```

### Option 3: Using Python Requests

```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate",
    json={
        "topic": "What is machine learning?",
        "duration_seconds": 90,
        "quality": "medium_quality",
        "enable_subtitles": True
    }
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")
```

## Video Generation Pipeline

When you submit a topic, the system will:

1. **Generate Script** (0-20%) - Create conversational dialogue between Alex and Maya
2. **Generate Audio** (20-45%) - Synthesize speech with different voices
3. **Extract Timestamps** (45-55%) - Get precise timing with Whisper
4. **Generate Visual Instructions** (55-60%) - Plan Manim animations
5. **Generate Manim Code** (60-75%) - Create and validate Python code
6. **Render Animation** (75-85%) - Compile Manim video
7. **Stitch Video** (85-95%) - Combine audio and video
8. **Add Subtitles** (95-100%) - Embed SRT subtitles

Total time: 3-10 minutes depending on complexity and quality settings.

## Accessing Your Video

Videos are saved in the `output/{job_id}/` directory with the following structure:

```
output/
└── {job_id}/
    ├── script.json              # Generated script
    ├── audio_segments/          # Individual audio files
    ├── narration.mp3            # Combined audio
    ├── subtitles.srt            # Subtitle file
    ├── visual_instructions.json # Visual plan
    ├── animation.py             # Manim code
    ├── manim_output/            # Manim render output
    ├── video_no_subs.mp4        # Video without subtitles
    └── final_video.mp4          # Final video with subtitles
```

Download via API:
```
http://localhost:8000/api/videos/{job_id}/final_video.mp4
```

## Configuration Options

### Video Quality
- `low_quality` - 480p, fast rendering (~2-3 min)
- `medium_quality` - 720p, balanced (default, ~4-6 min)
- `high_quality` - 1080p, best quality (~8-12 min)

### Duration
- Minimum: 30 seconds
- Maximum: 300 seconds (5 minutes)
- Recommended: 60-90 seconds for best results

### Subtitles
- Enable: `"enable_subtitles": true` (default)
- Disable: `"enable_subtitles": false`

## Troubleshooting

### "OPENAI_API_KEY not set"
- Make sure you created `.env` file
- Verify the API key is correct and starts with `sk-`
- Restart the server after editing `.env`

### "ffmpeg not found"
Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### "Manim not found"
```bash
pip install manim

# Also install LaTeX for text rendering:
# macOS: brew install --cask mactex
# Ubuntu: sudo apt-get install texlive-full
```

### Video generation fails
- Check server logs in terminal
- Review error messages in WebSocket or job status
- Ensure you have enough disk space (500MB+ free)
- Try with a simpler topic first

## Docker Deployment (Alternative)

If you prefer Docker:

```bash
# Copy .env file
cp .env.example .env
# Edit .env with your API key

# Build and run
docker-compose up --build

# Server will be available at http://localhost:8000
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API at http://localhost:8000/docs
3. Customize voices in `pipeline/audio_generator.py`
4. Modify Manim templates in `pipeline/manim_generator.py`
5. Add custom features to the pipeline

## Support

For issues:
1. Check `test_setup.py` output
2. Review server logs
3. Visit http://localhost:8000/docs for API documentation
4. Check the `output/` directory for intermediate files

## Example Topics to Try

- "How does photosynthesis work?"
- "What is quantum computing?"
- "Introduction to neural networks"
- "How do black holes form?"
- "What is the Pythagorean theorem?"
- "How does DNA replication work?"

Happy video generation!
