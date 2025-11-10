"""
Educational Video Generation Pipeline

This package contains modules for generating educational videos with:
- Multi-voice script generation
- Audio synthesis
- Timestamp extraction
- Visual instruction generation
- Manim video generation
- Video stitching
"""

from .script_generator import ScriptGenerator
from .audio_generator import AudioGenerator
from .timestamp_extractor import TimestampExtractor
from .visual_script_generator import VisualScriptGenerator
from .manim_generator import ManimGenerator
from .video_stitcher import VideoStitcher

__all__ = [
    "ScriptGenerator",
    "AudioGenerator",
    "TimestampExtractor",
    "VisualScriptGenerator",
    "ManimGenerator",
    "VideoStitcher",
]
