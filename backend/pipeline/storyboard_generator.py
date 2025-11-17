"""
Storyboard Generator Module

Generates structured storyboard JSON with spatial tracking from script and timestamps.
Replaces VisualScriptGenerator with enhanced spatial awareness and layout planning.
"""

import logging
from typing import Callable, Optional, List, Dict, Any
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class StoryboardGenerator:
    """
    Generate structured storyboards with spatial tracking for educational content.

    Features:
    - Creates scene-by-scene storyboard JSON
    - Includes spatial layout information
    - Plans object placement and lifecycle
    - Generates animation sequences
    - Prepares data for LayoutEngine
    """

    def __init__(self, api_key: str):
        """
        Initialize the storyboard generator.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"

    async def generate_storyboard(
        self,
        script: List[Dict[str, str]],
        topic: str,
        aligned_timestamps: Optional[List[Dict]] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Generate storyboard JSON from script with spatial tracking.

        Args:
            script: List of script segments with speaker and text
            topic: The educational topic
            aligned_timestamps: Optional list of script segments with timing
            progress_callback: Optional callback for progress updates

        Returns:
            Storyboard dictionary with metadata and scenes

        Raises:
            Exception: If storyboard generation fails
        """
        try:
            if progress_callback:
                progress_callback("Generating storyboard with spatial tracking...", 45)

            # Prepare script text with timestamps if available
            script_text = self._format_script_for_prompt(script, aligned_timestamps)

            # Calculate total duration
            total_duration = 60.0  # default
            if aligned_timestamps and len(aligned_timestamps) > 0:
                last_segment = aligned_timestamps[-1]
                total_duration = last_segment.get("end", 60.0)

            system_prompt = """Generate a detailed storyboard JSON for an educational animation.

OUTPUT FORMAT (REQUIRED):
{
  "metadata": {
    "topic": "Topic name",
    "duration": 60.0,
    "num_scenes": 10
  },
  "scenes": [
    {
      "id": "scene_0",
      "timestamp": {"start": 0.0, "end": 3.0},
      "narration": "Text being spoken",
      "visual_type": "equation|text|diagram|shape|graph",
      "description": "What to show",
      "elements": ["MathTex", "Text"],
      "region": "center|top|bottom|top_left|etc",
      "cleanup": ["previous_object_ids"],
      "transitions": ["FadeIn", "Write"],
      "properties": {"font_size": 36, "color": "BLUE"}
    }
  ]
}

SCREEN REGIONS:
- center, top, bottom, top_left, top_right, center_left, center_right, bottom_left, bottom_right

VISUAL TYPES:
- equation: Math equations
- text: Plain text
- title: Title text
- diagram: Visual diagrams
- shape: Geometric shapes
- graph: Charts/plots

CLEANUP: List IDs of objects to remove before this scene
TRANSITIONS: Animation types (FadeIn, Write, Create, Transform)
ELEMENTS: Manim objects to use (MathTex, Text, Circle, etc.)

Return valid JSON with "metadata" and "scenes" keys."""

            user_prompt = f"""Topic: {topic}
Duration: {total_duration:.1f}s

Script:
{script_text}

Generate storyboard JSON. Match visuals to narration. Use proper regions and cleanup."""

            logger.info(f"Generating storyboard for: {topic}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            # Validate and extract storyboard
            storyboard = self._validate_storyboard(parsed, script, aligned_timestamps)

            logger.info(f"Generated storyboard with {len(storyboard.get('scenes', []))} scenes")

            if progress_callback:
                progress_callback(f"Storyboard created with {len(storyboard['scenes'])} scenes", 48)

            return storyboard

        except Exception as e:
            logger.error(f"Storyboard generation failed: {e}")
            raise Exception(f"Failed to generate storyboard: {e}")

    def _format_script_for_prompt(
        self,
        script: List[Dict[str, str]],
        aligned_timestamps: Optional[List[Dict]] = None,
    ) -> str:
        """Format script for prompt."""
        lines = []
        if aligned_timestamps:
            for seg in aligned_timestamps:
                lines.append(f"[{seg.get('start', 0):.2f}s-{seg.get('end', 0):.2f}s] {seg.get('speaker', 'Speaker')}: {seg.get('text', '')}")
        else:
            for idx, seg in enumerate(script):
                lines.append(f"{idx + 1}. {seg.get('speaker', 'Speaker')}: {seg.get('text', '')}")
        return "\n".join(lines)

    def _validate_storyboard(
        self,
        parsed: Dict,
        script: List[Dict[str, str]],
        aligned_timestamps: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Validate and enrich storyboard."""
        scenes = parsed.get("scenes", [])
        
        if not scenes:
            raise ValueError("No scenes found in storyboard")

        validated_scenes = []
        for idx, scene in enumerate(scenes):
            validated = {
                "id": scene.get("id", f"scene_{idx}"),
                "narration": scene.get("narration", ""),
                "visual_type": scene.get("visual_type", "text"),
                "description": scene.get("description", ""),
                "elements": scene.get("elements", ["Text"]),
                "region": scene.get("region", "center"),
                "cleanup": scene.get("cleanup", []),
                "transitions": scene.get("transitions", ["FadeIn"]),
                "properties": scene.get("properties", {}),
            }

            # Add timestamps
            if aligned_timestamps and idx < len(aligned_timestamps):
                seg = aligned_timestamps[idx]
                validated["timestamp"] = {"start": seg.get("start", 0.0), "end": seg.get("end", 0.0)}
            elif "timestamp" in scene:
                validated["timestamp"] = scene["timestamp"]
            else:
                validated["timestamp"] = {"start": idx * 3, "end": (idx + 1) * 3}

            validated_scenes.append(validated)

        return {
            "metadata": parsed.get("metadata", {"topic": "Unknown", "duration": 60.0, "num_scenes": len(validated_scenes)}),
            "scenes": validated_scenes
        }
