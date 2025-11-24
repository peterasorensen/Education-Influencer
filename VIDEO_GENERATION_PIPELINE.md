# Video Generation Pipeline Breakdown

## Overview
AI-powered educational video generation system that creates 1-minute educational videos from text prompts. The pipeline orchestrates multiple AI services to produce professional-quality videos with synchronized audio, animations, and lip-synced celebrity presenters.

## Pipeline Architecture

### 🎯 **1. Script Generation** (5-15%)
**Duration**: 10-20 seconds | **Models**: GPT-4o | **Output**: `script.json`

- **Character Profile Generation**: Creates authentic personalities for teacher/student roles based on celebrity selection
- **Relationship Dynamics**: Generates character relationships and interaction patterns
- **Dialogue Creation**: Produces conversational, educational scripts with natural flow
- **Multi-Voice Mapping**: Assigns speakers to celebrities for audio generation
- **Context Injection**: Incorporates refined context from user follow-up questions

### 🎤 **2. Audio Synthesis** (15-35%)
**Duration**: 30-60 seconds | **Models**: OpenAI TTS, Tortoise TTS, MiniMax | **Output**: `narration.mp3`, `audio_segments/`

- **Voice Assignment**: Maps speakers to celebrity voices (Drake, Sydney Sweeney, Goku, etc.)
- **Parallel Generation**: Creates audio segments simultaneously for each script segment
- **Quality Enhancement**: Applies voice cloning and emotion synthesis
- **Format Optimization**: Converts to mono MP3 at optimal bitrate for lip-sync
- **Speaker Voice Map**: Maintains `speaker_voice_map.json` for consistency

### 📐 **3. Timestamp Extraction** (35-45%)
**Duration**: 10-15 seconds | **Models**: Whisper | **Output**: `subtitles.srt`

- **Word-Level Timing**: Extracts precise start/end times for each word
- **Segment Alignment**: Maps timestamps to script segments for synchronization
- **Audio Duration Analysis**: Calculates total audio length for animation planning
- **Script-Timestamp Sync**: Aligns generated script with extracted timing data

### 🎨 **4. Storyboard Generation** (45-48%)
**Duration**: 3-5 seconds | **Models**: GPT-4o | **Output**: `storyboard.json`

- **Spatial Tracking**: Plans object placement and movement across scenes
- **Visual Context**: Maintains continuity between sequential diagrams
- **Scene Layout**: Defines spatial relationships and element positioning
- **Animation Sequences**: Prepares data for LayoutEngine processing

### 🎬 **5. Animation Rendering** (50-60%)
**Duration**: 45-90 seconds | **Models**: Manim or Remotion | **Output**: `remotion_output.mp4` or `manim_output/`

- **Code Generation**: Auto-generates animation code from storyboard
- **Self-Healing**: Automatically fixes rendering errors with retry logic
- **Quality Rendering**: Produces 9:8 aspect ratio videos (1080x960)
- **Dual Engine Support**: Manim (Python) or Remotion (React/TypeScript)

### 🎭 **6. Celebrity Video Generation** (60-75%)
**Duration**: 60-90 seconds | **Models**: Seedance, Kling, TMappDev | **Output**: `celebrity_videos/`

- **Image-to-Video**: Converts celebrity images to talking head videos
- **Prompt Engineering**: Uses varied expressions (natural, animated, energetic)
- **Parallel Processing**: Generates videos for all segments simultaneously
- **Duration Precision**: Trims videos to exact audio segment lengths
- **Lip-Sync Preparation**: Creates base videos for lip-sync processing

### 💬 **7. Lip-Sync Processing** (75-90%)
**Duration**: 60-90 seconds | **Models**: TMappDev, Kling, Pixverse | **Output**: `lipsynced_videos/`

- **Audio-Video Sync**: Aligns celebrity mouth movements with audio
- **Parallel Processing**: Lip-syncs all segments simultaneously with rate limiting
- **Precision Trimming**: Ensures exact duration match with audio segments
- **Concatenation**: Combines all lip-synced segments into full video

### 🎞️ **8. Video Compositing** (90-95%)
**Duration**: 15-20 seconds | **Tools**: FFmpeg | **Output**: `composite_video.mp4`

- **Top-Bottom Layout**: Combines animation (top 9:8) with celebrity video (bottom 9:16)
- **Audio Preservation**: Maintains lip-synced audio from bottom video
- **Duration Verification**: Ensures perfect synchronization
- **Format Optimization**: Produces 9:16 final video format

### 📝 **9. Subtitle Addition** (95-100%)
**Duration**: 5-10 seconds | **Tools**: FFmpeg | **Output**: `final_video.mp4`

- **Lip-Sync Re-Timing**: Re-extracts timestamps from final lip-synced audio
- **SRT Generation**: Creates synchronized subtitle file
- **Burn-In Rendering**: Embeds subtitles directly into video
- **Quality Preservation**: Maintains video quality during subtitle addition

## Key Technologies

### AI Models
- **GPT-4o**: Script generation, character profiles, storyboard planning
- **Whisper**: Audio transcription and timestamp extraction
- **OpenAI TTS**: Natural voice synthesis
- **Replicate Models**: Celebrity video generation, lip-sync, image-to-video
- **MiniMax**: Voice cloning and speech synthesis

### Rendering Engines
- **Manim**: Mathematical animations and educational diagrams
- **Remotion**: Web-based animation alternative
- **FFmpeg**: Video processing, compositing, subtitle rendering

### Infrastructure
- **FastAPI**: Async Python web framework
- **WebSocket**: Real-time progress updates
- **Parallel Processing**: Concurrent API calls with rate limiting
- **Resume Functionality**: Step-by-step pipeline recovery

## Pipeline Features

### 🔄 **Resume & Recovery**
- Detects completed steps on restart
- Skips redundant processing
- Maintains job metadata across sessions
- Supports partial pipeline continuation

### ⚡ **Performance Optimization**
- Parallel celebrity video generation (6 concurrent max)
- Parallel lip-sync processing (6 concurrent max)
- Rate limiting to prevent API throttling
- Async processing with progress callbacks

### 🎯 **Quality Assurance**
- Duration verification at each step
- Automatic retry logic for failed renders
- Audio/video synchronization checks
- Error handling and graceful degradation

### 🎭 **Customization**
- Multiple celebrity presets (Drake, Sydney Sweeney, Goku, etc.)
- Custom photo/audio uploads for voice cloning
- Dual animation engines (Manim/Remotion)
- Configurable quality settings

## Output Files Structure
```
job_id/
├── script.json                 # Generated dialogue script
├── narration.mp3              # Full audio narration
├── subtitles.srt              # Timing data for subtitles
├── storyboard.json            # Visual scene planning
├── job_metadata.json          # Pipeline configuration
├── audio_segments/            # Individual audio clips
├── celebrity_videos/          # Generated talking head videos
├── lipsynced_videos/          # Lip-synced video segments
├── remotion_output.mp4        # Animation video (9:8)
├── manim_output/              # Manim render directory
├── composite_video.mp4        # Combined video (9:16)
└── final_video.mp4            # Final video with subtitles
```

## Error Handling & Recovery

- **Manim/Remotion**: 3-attempt retry with code regeneration
- **API Failures**: Graceful fallback to alternative models
- **Duration Mismatches**: Automatic trimming and re-syncing
- **WebSocket Disconnection**: Continues processing in background
- **Rate Limiting**: Built-in delays and concurrent request limits

## Performance Metrics

- **Total Time**: 3-5 minutes for 60-second video
- **API Calls**: 15-25 Replicate API calls per video
- **Concurrent Operations**: Up to 6 parallel video generation tasks
- **Success Rate**: 95%+ with automatic error recovery
- **Output Quality**: 1080p 9:16 vertical video format
