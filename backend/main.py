"""
FastAPI Backend for Educational Video Generation Pipeline

Provides REST API and WebSocket endpoints for generating educational videos
with multi-voice narration, Manim animations, and audio synthesis.
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import os
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from pipeline import (
    ScriptGenerator,
    AudioGenerator,
    TimestampExtractor,
    VisualScriptGenerator,
    ManimGenerator,
    VideoStitcher,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Educational Video Generation API",
    description="Generate educational videos with AI-powered narration and Manim animations",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://yourdomain.com",  # Replace with your Vercel domain
        "https://*.vercel.app",  # Allow Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set. API calls will fail.")

# Output directories
BASE_OUTPUT_DIR = Path("./output")
BASE_OUTPUT_DIR.mkdir(exist_ok=True)

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Job status tracking
job_status: Dict[str, Dict[str, Any]] = {}


# Request/Response Models
class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""

    topic: str = Field(..., description="Educational topic for the video")
    duration_seconds: int = Field(
        default=60, ge=30, le=300, description="Target video duration in seconds"
    )
    quality: str = Field(
        default="medium_quality",
        description="Video quality (low_quality, medium_quality, high_quality)",
    )
    enable_subtitles: bool = Field(
        default=True, description="Whether to add subtitles to the final video"
    )


class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""

    job_id: str = Field(..., alias="jobId", description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")

    class Config:
        populate_by_name = True
        by_alias = True


class JobStatusResponse(BaseModel):
    """Response model for job status."""

    job_id: str
    status: str
    progress: int
    message: str
    video_url: Optional[str] = None
    error: Optional[str] = None


# Helper Functions
def get_pipeline_step_from_progress(progress: int) -> str:
    """Map progress percentage to pipeline step."""
    if progress < 20:
        return "generating_script"
    elif progress < 45:
        return "creating_audio"
    elif progress < 55:
        return "extracting_timestamps"
    elif progress < 60:
        return "planning_visuals"
    elif progress < 85:
        return "generating_animations"
    else:
        return "stitching_video"


def get_step_status(progress: int, step: str) -> str:
    """Determine status of a step based on current progress."""
    current_step = get_pipeline_step_from_progress(progress)
    steps_order = [
        "generating_script",
        "creating_audio",
        "extracting_timestamps",
        "planning_visuals",
        "generating_animations",
        "stitching_video"
    ]

    if steps_order.index(step) < steps_order.index(current_step):
        return "completed"
    elif step == current_step:
        return "in_progress"
    else:
        return "pending"


def calculate_step_progress(overall_progress: int, step: str) -> int:
    """Calculate individual step progress (0-100) based on overall progress."""
    step_ranges = {
        "generating_script": (0, 20),
        "creating_audio": (20, 45),
        "extracting_timestamps": (45, 55),
        "planning_visuals": (55, 60),
        "generating_animations": (60, 85),
        "stitching_video": (85, 100)
    }

    if step not in step_ranges:
        return 0

    start, end = step_ranges[step]

    if overall_progress < start:
        return 0
    elif overall_progress >= end:
        return 100
    else:
        # Calculate progress within this step's range
        step_range = end - start
        progress_in_step = overall_progress - start
        return int((progress_in_step / step_range) * 100)


async def send_progress_update(job_id: str, message: str, progress: int):
    """
    Send progress update via WebSocket.

    Args:
        job_id: Job identifier
        message: Progress message
        progress: Progress percentage (0-100)
    """
    # Update job status
    if job_id in job_status:
        job_status[job_id]["progress"] = progress
        job_status[job_id]["message"] = message
        job_status[job_id]["status"] = "processing"

    # Send WebSocket update if connected
    if job_id in active_connections:
        try:
            steps_order = [
                "generating_script",
                "creating_audio",
                "extracting_timestamps",
                "planning_visuals",
                "generating_animations",
                "stitching_video"
            ]

            # Send progress for ALL steps with their individual progress
            for step in steps_order:
                step_progress = calculate_step_progress(progress, step)
                current_step = get_pipeline_step_from_progress(progress)

                if step_progress == 100:
                    status = "completed"
                elif step == current_step:
                    status = "in_progress"
                else:
                    status = "pending"

                await active_connections[job_id].send_json({
                    "type": "progress",
                    "data": {
                        "step": step,
                        "status": status,
                        "message": message if step == current_step else "",
                        "progress": step_progress
                    }
                })
        except Exception as e:
            logger.error(f"Failed to send WebSocket update: {e}")


async def send_completion(job_id: str, video_url: str, topic: str = "", duration: float = 0):
    """Send completion notification via WebSocket."""
    if job_id in job_status:
        job_status[job_id]["status"] = "completed"
        job_status[job_id]["progress"] = 100
        job_status[job_id]["video_url"] = video_url

    if job_id in active_connections:
        try:
            # Mark all steps as completed
            steps_order = [
                "generating_script",
                "creating_audio",
                "extracting_timestamps",
                "planning_visuals",
                "generating_animations",
                "stitching_video"
            ]

            for step in steps_order:
                await active_connections[job_id].send_json({
                    "type": "progress",
                    "data": {
                        "step": step,
                        "status": "completed",
                        "message": f"{step.replace('_', ' ').title()} complete",
                        "progress": 100
                    }
                })

            # Send final completion message
            await active_connections[job_id].send_json({
                "type": "complete",
                "data": {
                    "videoUrl": video_url,
                    "duration": duration,
                    "topic": topic
                }
            })
        except Exception as e:
            logger.error(f"Failed to send completion: {e}")


async def send_error(job_id: str, error: str):
    """Send error notification via WebSocket."""
    if job_id in job_status:
        job_status[job_id]["status"] = "failed"
        job_status[job_id]["error"] = error

    if job_id in active_connections:
        try:
            await active_connections[job_id].send_json(
                {"type": "error", "message": error}
            )
        except Exception as e:
            logger.error(f"Failed to send error: {e}")


async def generate_video_pipeline(
    job_id: str,
    topic: str,
    duration_seconds: int,
    quality: str,
    enable_subtitles: bool,
):
    """
    Main video generation pipeline.

    Args:
        job_id: Unique job identifier
        topic: Educational topic
        duration_seconds: Target duration
        quality: Video quality setting
        enable_subtitles: Whether to add subtitles
    """
    try:
        logger.info(f"Starting video generation for job {job_id}: {topic}")

        # Create job output directory
        job_dir = BASE_OUTPUT_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Initialize pipeline modules
        script_gen = ScriptGenerator(OPENAI_API_KEY)
        audio_gen = AudioGenerator(OPENAI_API_KEY)
        timestamp_ext = TimestampExtractor(OPENAI_API_KEY)
        visual_gen = VisualScriptGenerator(OPENAI_API_KEY)
        manim_gen = ManimGenerator(OPENAI_API_KEY)
        video_stitcher = VideoStitcher()

        # Step 1: Generate Script
        await send_progress_update(job_id, "Generating script...", 5)
        script = await script_gen.generate_script(
            topic=topic,
            duration_seconds=duration_seconds,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )
        logger.info(f"Script generated with {len(script)} segments")

        # Save script
        script_path = job_dir / "script.json"
        import json
        script_path.write_text(json.dumps(script, indent=2), encoding="utf-8")

        # Step 2: Generate Audio
        await send_progress_update(job_id, "Generating audio...", 20)
        audio_dir = job_dir / "audio_segments"
        final_audio_path = job_dir / "narration.mp3"
        await audio_gen.generate_full_audio(
            script=script,
            output_dir=audio_dir,
            final_output_path=final_audio_path,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )
        logger.info(f"Audio generated: {final_audio_path}")

        # Step 3: Extract Timestamps
        await send_progress_update(job_id, "Extracting timestamps...", 45)
        srt_path = job_dir / "subtitles.srt"
        timestamp_data = await timestamp_ext.extract_timestamps(
            audio_path=final_audio_path,
            output_srt_path=srt_path,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )
        logger.info(f"Timestamps extracted: {len(timestamp_data['segments'])} segments")

        # Align script with timestamps
        aligned_script = await timestamp_ext.align_script_with_timestamps(
            script=script,
            timestamp_data=timestamp_data,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )

        # Step 4: Generate Visual Instructions
        await send_progress_update(job_id, "Generating visual instructions...", 55)
        visual_instructions = await visual_gen.generate_visual_instructions(
            script=script,
            topic=topic,
            aligned_timestamps=aligned_script,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )
        logger.info(f"Visual instructions generated: {len(visual_instructions)} segments")

        # Save visual instructions
        visual_path = job_dir / "visual_instructions.json"
        visual_path.write_text(
            json.dumps(visual_instructions, indent=2), encoding="utf-8"
        )

        # Step 5: Generate Manim Code
        await send_progress_update(job_id, "Generating Manim code...", 60)
        manim_file = job_dir / "animation.py"
        audio_duration = timestamp_data.get('duration', 60.0)
        await manim_gen.generate_manim_code(
            visual_instructions=visual_instructions,
            topic=topic,
            output_path=manim_file,
            target_duration=audio_duration,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )
        logger.info(f"Manim code generated: {manim_file}")

        # Step 6: Render Manim Video
        await send_progress_update(job_id, "Rendering Manim animation...", 75)
        manim_output_dir = job_dir / "manim_output"
        manim_video = await manim_gen.render_manim_video(
            manim_file=manim_file,
            output_dir=manim_output_dir,
            quality=quality,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )
        logger.info(f"Manim video rendered: {manim_video}")

        # Step 7: Stitch Video and Audio
        await send_progress_update(job_id, "Combining video and audio...", 85)
        stitched_video = job_dir / "video_no_subs.mp4"
        await video_stitcher.stitch_video(
            video_path=manim_video,
            audio_path=final_audio_path,
            output_path=stitched_video,
            progress_callback=lambda msg, prog: asyncio.create_task(
                send_progress_update(job_id, msg, prog)
            ),
        )
        logger.info(f"Video stitched: {stitched_video}")

        # Step 8: Add Subtitles (if enabled)
        if enable_subtitles:
            await send_progress_update(job_id, "Adding subtitles...", 90)
            final_video = job_dir / "final_video.mp4"
            await video_stitcher.add_subtitles(
                video_path=stitched_video,
                srt_path=srt_path,
                output_path=final_video,
                progress_callback=lambda msg, prog: asyncio.create_task(
                    send_progress_update(job_id, msg, prog)
                ),
            )
        else:
            final_video = stitched_video

        logger.info(f"Final video ready: {final_video}")

        # Send completion
        video_url = f"/api/videos/{job_id}/{final_video.name}"
        video_duration = timestamp_data.get('duration', 0) if 'timestamp_data' in locals() else 0
        await send_completion(job_id, video_url, topic=topic, duration=video_duration)

        logger.info(f"Video generation complete for job {job_id}")

    except Exception as e:
        logger.error(f"Video generation failed for job {job_id}: {e}", exc_info=True)
        await send_error(job_id, str(e))


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Educational Video Generation API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest, background_tasks: BackgroundTasks
):
    """
    Generate an educational video.

    Args:
        request: Video generation parameters

    Returns:
        Job information including job_id for tracking progress
    """
    try:
        # Validate API key
        if not OPENAI_API_KEY:
            raise HTTPException(
                status_code=500, detail="OpenAI API key not configured"
            )

        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Initialize job status
        job_status[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Job queued",
            "topic": request.topic,
            "created_at": datetime.now().isoformat(),
        }

        # Start background task
        background_tasks.add_task(
            generate_video_pipeline,
            job_id=job_id,
            topic=request.topic,
            duration_seconds=request.duration_seconds,
            quality=request.quality,
            enable_subtitles=request.enable_subtitles,
        )

        logger.info(f"Video generation job created: {job_id}")

        return VideoGenerationResponse(
            job_id=job_id,
            status="queued",
            message="Video generation job started. Connect to WebSocket for progress updates.",
        )

    except Exception as e:
        logger.error(f"Failed to create video generation job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a video generation job.

    Args:
        job_id: Job identifier

    Returns:
        Current job status
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    status = job_status[job_id]
    return JobStatusResponse(
        job_id=status["job_id"],
        status=status["status"],
        progress=status.get("progress", 0),
        message=status.get("message", ""),
        video_url=status.get("video_url"),
        error=status.get("error"),
    )


@app.get("/api/videos/{job_id}/{filename}")
async def get_video(job_id: str, filename: str):
    """
    Download generated video.

    Args:
        job_id: Job identifier
        filename: Video filename

    Returns:
        Video file
    """
    video_path = BASE_OUTPUT_DIR / job_id / filename

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=f"{job_id}_{filename}",
    )


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time progress updates.

    Args:
        websocket: WebSocket connection
        job_id: Job identifier to track
    """
    await websocket.accept()
    active_connections[job_id] = websocket

    try:
        logger.info(f"WebSocket connected for job {job_id}")

        # Send current status if job exists
        if job_id in job_status:
            status = job_status[job_id]
            await websocket.send_json(
                {
                    "type": "status",
                    "status": status["status"],
                    "progress": status.get("progress", 0),
                    "message": status.get("message", ""),
                }
            )

        # Keep connection alive
        while True:
            try:
                # Wait for messages with timeout to keep connection alive
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                # No message received, just continue
                continue
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {e}")
    finally:
        if job_id in active_connections:
            del active_connections[job_id]


# Run application
if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    logger.info(f"Starting Educational Video Generation API on port {port}")

    import os
    is_production = os.getenv("ENVIRONMENT") == "production"

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,
        reload_dirs=["pipeline"] if not is_production else None,
        log_level="info",
    )
