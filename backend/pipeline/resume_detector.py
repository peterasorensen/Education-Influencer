"""
Resume Detector Module

Detects which pipeline steps have been completed by analyzing output directory.
Allows resuming from the last successful step instead of starting over.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, List
import json

logger = logging.getLogger(__name__)


class ResumeDetector:
    """Detect completed pipeline steps from output directory."""

    def __init__(self, job_dir: Path):
        """
        Initialize the resume detector.

        Args:
            job_dir: Path to job output directory
        """
        self.job_dir = job_dir

    def detect_completed_steps(self) -> Dict[str, bool]:
        """
        Analyze output directory to detect which steps are complete.

        Returns:
            Dictionary mapping step names to completion status
        """
        steps = {
            "script": False,
            "audio": False,
            "timestamps": False,
            "visual_instructions": False,  # Legacy
            "storyboard": False,  # NEW
            "manim_code": False,
            "manim_render": False,
            "celebrity_videos": False,
            "lipsynced_videos": False,
            "composite": False,
            "final": False,
        }

        if not self.job_dir.exists():
            logger.info(f"Job directory does not exist: {self.job_dir}")
            return steps

        # Check script
        script_path = self.job_dir / "script.json"
        if script_path.exists() and script_path.stat().st_size > 0:
            steps["script"] = True
            logger.info("✓ Script found")

        # Check audio
        audio_path = self.job_dir / "narration.mp3"
        audio_dir = self.job_dir / "audio_segments"
        voice_map_path = self.job_dir / "speaker_voice_map.json"
        if (audio_path.exists() and audio_path.stat().st_size > 0 and
            audio_dir.exists() and len(list(audio_dir.glob("segment_*.mp3"))) > 0):
            steps["audio"] = True
            if voice_map_path.exists():
                logger.info("✓ Audio found (with speaker voice map)")
            else:
                logger.info("✓ Audio found (legacy - no speaker voice map)")

        # Check timestamps
        srt_path = self.job_dir / "subtitles.srt"
        if srt_path.exists() and srt_path.stat().st_size > 0:
            steps["timestamps"] = True
            logger.info("✓ Timestamps found")

        # Check visual instructions (legacy)
        visual_path = self.job_dir / "visual_instructions.json"
        if visual_path.exists() and visual_path.stat().st_size > 0:
            steps["visual_instructions"] = True
            logger.info("✓ Visual instructions found (legacy)")

        # Check storyboard (NEW)
        storyboard_path = self.job_dir / "storyboard.json"
        if storyboard_path.exists() and storyboard_path.stat().st_size > 0:
            steps["storyboard"] = True
            logger.info("✓ Storyboard found")

        # Check manim code
        manim_path = self.job_dir / "animation.py"
        if manim_path.exists() and manim_path.stat().st_size > 0:
            steps["manim_code"] = True
            logger.info("✓ Manim code found")

        # Check manim render
        manim_output_dir = self.job_dir / "manim_output"
        if manim_output_dir.exists():
            # Find manim_output.mp4 anywhere in manim_output directory
            manim_videos = list(manim_output_dir.rglob("manim_output.mp4"))
            if manim_videos and manim_videos[0].stat().st_size > 0:
                steps["manim_render"] = True
                logger.info("✓ Manim render found")

        # Check celebrity videos
        celebrity_dir = self.job_dir / "celebrity_videos"
        if celebrity_dir.exists():
            celebrity_videos = list(celebrity_dir.glob("segment_*.mp4"))
            if len(celebrity_videos) > 0:
                steps["celebrity_videos"] = True
                logger.info(f"✓ Celebrity videos found ({len(celebrity_videos)} segments)")

        # Check lip-synced videos
        lipsynced_dir = self.job_dir / "lipsynced_videos"
        if lipsynced_dir.exists():
            lipsynced_videos = list(lipsynced_dir.glob("lipsynced_*.mp4"))
            if len(lipsynced_videos) > 0:
                steps["lipsynced_videos"] = True
                logger.info(f"✓ Lip-synced videos found ({len(lipsynced_videos)} segments)")

        # Check composite
        composite_path = self.job_dir / "composite_video.mp4"
        if composite_path.exists() and composite_path.stat().st_size > 0:
            steps["composite"] = True
            logger.info("✓ Composite video found")

        # Check final
        final_path = self.job_dir / "final_video.mp4"
        if final_path.exists() and final_path.stat().st_size > 0:
            steps["final"] = True
            logger.info("✓ Final video found")

        return steps

    def get_resume_point(self) -> str:
        """
        Determine which step to resume from.

        Returns:
            Step name to resume from, or "start" if no progress
        """
        steps = self.detect_completed_steps()

        # Resume from first incomplete step
        if not steps["script"]:
            return "script"
        elif not steps["audio"]:
            return "audio"
        elif not steps["timestamps"]:
            return "timestamps"
        # Check for new storyboard system first, fallback to legacy
        elif not steps["storyboard"] and not steps["visual_instructions"]:
            return "storyboard"  # or "visual_instructions" for legacy
        elif not steps["manim_code"]:
            return "manim_code"
        elif not steps["manim_render"]:
            return "manim_render"
        elif not steps["celebrity_videos"]:
            return "celebrity_videos"
        elif not steps["lipsynced_videos"]:
            return "lipsynced_videos"
        elif not steps["composite"]:
            return "composite"
        elif not steps["final"]:
            return "final"
        else:
            return "complete"

    def load_script(self) -> Optional[List[Dict]]:
        """Load script from file if it exists."""
        script_path = self.job_dir / "script.json"
        if script_path.exists():
            try:
                return json.loads(script_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Failed to load script: {e}")
        return None

    def load_visual_instructions(self) -> Optional[List[Dict]]:
        """Load visual instructions from file if they exist (legacy)."""
        visual_path = self.job_dir / "visual_instructions.json"
        if visual_path.exists():
            try:
                return json.loads(visual_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Failed to load visual instructions: {e}")
        return None

    def load_storyboard(self) -> Optional[Dict]:
        """Load storyboard from file if it exists (NEW)."""
        storyboard_path = self.job_dir / "storyboard.json"
        if storyboard_path.exists():
            try:
                return json.loads(storyboard_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Failed to load storyboard: {e}")
        return None

    def load_speaker_voice_map(self) -> Optional[Dict]:
        """Load speaker-to-voice mapping from file if it exists."""
        voice_map_path = self.job_dir / "speaker_voice_map.json"
        if voice_map_path.exists():
            try:
                return json.loads(voice_map_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Failed to load speaker voice map: {e}")
        return None

    def get_paths(self) -> Dict[str, Path]:
        """Get all relevant file paths for the job."""
        return {
            "script": self.job_dir / "script.json",
            "audio": self.job_dir / "narration.mp3",
            "audio_segments": self.job_dir / "audio_segments",
            "speaker_voice_map": self.job_dir / "speaker_voice_map.json",
            "srt": self.job_dir / "subtitles.srt",
            "visual_instructions": self.job_dir / "visual_instructions.json",  # Legacy
            "storyboard": self.job_dir / "storyboard.json",  # NEW
            "manim_file": self.job_dir / "animation.py",
            "manim_output": self.job_dir / "manim_output",
            "celebrity_videos": self.job_dir / "celebrity_videos",
            "lipsynced_videos": self.job_dir / "lipsynced_videos",
            "composite": self.job_dir / "composite_video.mp4",
            "final": self.job_dir / "final_video.mp4",
        }

    def get_summary(self) -> str:
        """Get a human-readable summary of completed steps."""
        steps = self.detect_completed_steps()
        resume_point = self.get_resume_point()

        completed_count = sum(1 for v in steps.values() if v)
        total_count = len(steps)

        summary = f"Progress: {completed_count}/{total_count} steps complete\n"
        summary += f"Resume from: {resume_point}\n\n"
        summary += "Steps:\n"

        step_names = {
            "script": "1. Script Generation",
            "audio": "2. Audio Generation",
            "timestamps": "3. Timestamp Extraction",
            "visual_instructions": "4a. Visual Instructions (legacy)",
            "storyboard": "4b. Storyboard Generation (NEW)",
            "manim_code": "5. Manim Code",
            "manim_render": "6. Manim Render",
            "celebrity_videos": "7. Celebrity Videos",
            "lipsynced_videos": "8. Lip-synced Videos",
            "composite": "9. Composite Video",
            "final": "10. Final Video",
        }

        for key, name in step_names.items():
            status = "✓" if steps[key] else "✗"
            summary += f"  {status} {name}\n"

        return summary
