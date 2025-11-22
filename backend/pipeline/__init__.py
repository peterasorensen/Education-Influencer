"""
Educational Video Generation Pipeline

This package contains modules for generating educational videos with:
- Multi-voice script generation
- Audio synthesis
- Timestamp extraction
- Visual instruction generation
- Manim video generation
- Layout engine with spatial awareness
- Image to video generation (celebrity animations)
- Lipsync generation
- Video stitching and compositing
"""

from .script_generator import ScriptGenerator
from .audio_generator import AudioGenerator
from .timestamp_extractor import TimestampExtractor
from .visual_script_generator import VisualScriptGenerator  # Legacy - backward compatibility
from .storyboard_generator import StoryboardGenerator  # NEW
from .spatial_tracker import SpatialTracker, ObjectType, Region, BoundingBox, TrackedObject  # NEW
from .manim_generator import ManimGenerator
from .remotion_generator import RemotionGenerator  # NEW - Alternative to Manim
from .layout_engine import LayoutEngine, LayoutStrategy, ManimCodeTemplate  # NEW
from .image_to_video_generator import ImageToVideoGenerator
from .lipsync_generator import LipsyncGenerator
from .video_stitcher import VideoStitcher
from .resume_detector import ResumeDetector

__all__ = [
    "ScriptGenerator",
    "AudioGenerator",
    "TimestampExtractor",
    "VisualScriptGenerator",  # Legacy - backward compatibility
    "StoryboardGenerator",  # NEW
    "SpatialTracker",  # NEW
    "ObjectType",  # NEW
    "Region",  # NEW
    "BoundingBox",  # NEW
    "TrackedObject",  # NEW
    "LayoutEngine",  # NEW
    "LayoutStrategy",  # NEW
    "ManimCodeTemplate",  # NEW
    "ManimGenerator",
    "RemotionGenerator",  # NEW - Alternative to Manim
    "ImageToVideoGenerator",
    "LipsyncGenerator",
    "VideoStitcher",
    "ResumeDetector",
]
