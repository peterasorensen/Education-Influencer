# EduVideo AI - Educational Short Video Generator

An AI-powered web application that automatically generates engaging 1-minute educational videos from a simple text prompt. The app creates multi-voice scripts, synthesizes audio, generates Manim animations, and stitches everything together into a polished video.

## Features

### Video Generation AI
- **AI Script Generation**: GPT-4o creates conversational, catchy scripts with multiple voices (boy and girl characters)
- **Text-to-Speech**: OpenAI's TTS models generate natural-sounding audio with distinct voices per character
- **Precision Timestamps**: Whisper extracts word-level timing for perfect synchronization
- **Manim Animations**: Auto-generates mathematical animations, diagrams, and visual aids
- **Self-Healing Pipeline**: Automatically fixes Manim code errors with retry logic
- **Real-Time Progress**: WebSocket updates show pipeline progress in the UI
- **Modern UI**: Clean, gradient-based interface with smooth animations

### 🎬 NEW: Professional Video Editor
- **Screen Recording**: Capture display, window, or custom area with microphone support
- **Multi-Track Editing**: Unlimited video and audio tracks with drag & drop
- **Smart Zoom Effects**: Auto-follow cursor or manually set zoom points (1.0x-2.0x)
- **Professional Export**: MP4/WebM with quality presets using FFmpeg.wasm
- **Timeline Tools**: Trim, split, move clips with undo/redo support
- **Media Library**: Import videos, audio, images with auto-generated thumbnails
- **Browser-Based**: No server required, runs entirely in your browser

👉 **[Video Editor Quick Start Guide](frontend/QUICK_START.md)**
👉 **[Complete Video Editor Documentation](frontend/VIDEO_EDITOR_README.md)**

## Pipeline Architecture

The system processes videos through 6 automated steps:

1. **Script Generation** - Multi-voice dialogue creation with GPT-4o
2. **Audio Synthesis** - TTS audio generation with character-specific voices
3. **Timestamp Extraction** - Whisper-based word and segment timing
4. **Visual Planning** - Manim-aware visual instruction generation
5. **Animation Generation** - Self-fixing Manim code creation and rendering
6. **Video Stitching** - FFmpeg-based audio/video combination

## Project Structure

```
educational-influencer/
├── backend/              # Python FastAPI server
│   ├── main.py          # API server with WebSocket support
│   ├── pipeline/        # Video generation modules
│   │   ├── script_generator.py
│   │   ├── audio_generator.py
│   │   ├── timestamp_extractor.py
│   │   ├── visual_script_generator.py
│   │   ├── manim_generator.py
│   │   └── video_stitcher.py
│   └── requirements.txt
├── frontend/            # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx              # Main video generation app
│   │   ├── video-editor/        # 🎬 NEW: Professional video editor
│   │   │   ├── components/      # Editor UI components
│   │   │   ├── store/           # Zustand state management
│   │   │   ├── theme/           # Design system
│   │   │   └── hooks/           # Recording & editing hooks
│   │   └── types.ts
│   ├── video-editor.html        # Video editor entry point
│   ├── QUICK_START.md          # Video editor quick start
│   ├── VIDEO_EDITOR_README.md  # Full editor documentation
│   └── package.json
└── README.md                    # This file
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- FFmpeg
- LaTeX (for Manim text rendering)
- OpenAI API key

### Installation

**1. Clone and navigate to the project:**
```bash
cd educational-influencer
```

**2. Set up the backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**3. Set up the frontend:**
```bash
cd ../frontend
npm install

# Create .env file (optional, defaults to localhost:8000)
cp .env.example .env
```

**4. Start the backend server:**
```bash
cd ../backend
source venv/bin/activate
python main.py
```

Backend runs at: `http://localhost:8000`

**5. Start the frontend (in a new terminal):**
```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Generate Your First Video

1. Open `http://localhost:5173` in your browser
2. Enter an educational topic (e.g., "Explain the Pythagorean theorem")
3. Click "Generate Video"
4. Watch the progress bar as the pipeline runs
5. View and download your video when complete

## System Requirements

### macOS
```bash
# Install FFmpeg
brew install ffmpeg

# Install LaTeX
brew install --cask mactex
```

### Linux (Ubuntu/Debian)
```bash
# Install FFmpeg
sudo apt-get install ffmpeg

# Install LaTeX
sudo apt-get install texlive-full
```

### Windows
- Download FFmpeg from https://ffmpeg.org/download.html
- Download MiKTeX from https://miktex.org/download

## Configuration

### Backend Configuration (`.env`)

```env
OPENAI_API_KEY=your_api_key_here
OUTPUT_DIR=./output
TEMP_DIR=./temp
MAX_RETRIES=3
MANIM_QUALITY=high
VIDEO_RESOLUTION=1080p
```

### Frontend Configuration (`.env`)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## API Documentation

### REST Endpoints

**Generate Video**
```
POST /api/generate
Content-Type: application/json

{
  "topic": "Explain photosynthesis"
}

Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

**Check Status**
```
GET /api/jobs/{job_id}

Response:
{
  "job_id": "...",
  "status": "completed",
  "progress": 100,
  "video_url": "/api/videos/{job_id}/final_video.mp4"
}
```

**Download Video**
```
GET /api/videos/{job_id}/final_video.mp4
```

### WebSocket

**Connect**
```
ws://localhost:8000/ws/{job_id}
```

**Messages**
```json
{
  "type": "progress",
  "step": "Generating script",
  "progress": 15,
  "message": "Creating conversational dialogue..."
}
```

## Troubleshooting

### Backend Issues

**Import errors**
```bash
pip install --upgrade openai pydub manim
```

**FFmpeg not found**
```bash
which ffmpeg  # Should show path
brew install ffmpeg  # macOS
```

**Manim LaTeX errors**
```bash
# Install full LaTeX distribution
brew install --cask mactex  # macOS
```

### Frontend Issues

**Port 5173 already in use**
```bash
# Edit vite.config.ts to change port
```

**WebSocket connection failed**
```bash
# Ensure backend is running on port 8000
curl http://localhost:8000/health
```

## Development

### Running Tests

**Backend**
```bash
cd backend
python test_setup.py
python -m pytest tests/
```

**Frontend**
```bash
cd frontend
npm test
```

### Code Quality

**Backend**
```bash
# Format code
black .

# Type checking
mypy .

# Linting
flake8 .
```

**Frontend**
```bash
# Type checking
npm run type-check

# Linting
npm run lint
```

## Docker Deployment (Optional)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## Performance Tips

1. **Use GPU for Manim** (if available) - Set `MANIM_RENDERER=opengl` in `.env`
2. **Adjust video quality** - Lower quality for faster generation: `MANIM_QUALITY=medium`
3. **Concurrent jobs** - Backend supports multiple simultaneous generations
4. **Cache management** - Clear temp files regularly to save disk space

## Example Topics

Try these prompts for great results:

- "Explain the water cycle with animations"
- "How does compound interest work?"
- "What causes the phases of the moon?"
- "Demonstrate the quadratic formula step by step"
- "Explain Newton's three laws of motion"
- "How does DNA replication work?"

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OpenAI API** - GPT-4o, TTS, Whisper
- **Manim** - Mathematical animation engine
- **Pydub** - Audio processing
- **FFmpeg** - Video processing
- **WebSockets** - Real-time communication

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Vanilla CSS** - Custom styling

## Contributing

This is a proof-of-concept project. Feel free to fork and extend!

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- OpenAI for GPT-4o, TTS, and Whisper APIs
- 3Blue1Brown for creating Manim
- The FastAPI and React communities

---

Built with AI for AI-powered education
