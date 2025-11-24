"""
Storyboard Generator Module

Generates structured storyboard JSON with spatial tracking from script and timestamps.
Replaces VisualScriptGenerator with enhanced spatial awareness and layout planning.
Supports cumulative visual context for progressive diagram building.
"""

import logging
from typing import Callable, Optional, List, Dict, Any
from openai import AsyncOpenAI
import json

# Import visual context system
try:
    from .visual_context import VisualContext, SceneVisualState, VisualElement, VisualElementType
except ImportError:
    VisualContext = None
    SceneVisualState = None
    VisualElement = None
    VisualElementType = None

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
        word_timestamps: Optional[Dict] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        visual_context: Optional[Any] = None,  # VisualContext
    ) -> Dict[str, Any]:
        """
        Generate storyboard JSON from script with spatial tracking and word-sync actions.

        Args:
            script: List of script segments with speaker and text
            topic: The educational topic
            aligned_timestamps: Optional list of script segments with timing
            word_timestamps: Optional dict with word-level timing from Whisper
            progress_callback: Optional callback for progress updates
            visual_context: Optional VisualContext for scene continuity

        Returns:
            Storyboard dictionary with metadata, scenes, and word-sync actions

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

            system_prompt = """Generate a detailed storyboard JSON for an educational animation with WORD-SYNCHRONIZED ANIMATIONS.

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
      "properties": {"font_size": 36, "color": "BLUE"},
      "word_sync": [
        {"word": "equation", "time": 1.2, "action": "indicate", "target": "eq_main"},
        {"word": "Einstein", "time": 2.1, "action": "flash", "target": "title"},
        {"word": "energy", "time": 3.5, "action": "circumscribe", "target": "e_var"}
      ]
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

WORD-SYNC ACTIONS (CRITICAL FOR ENGAGEMENT):
Use word-level timestamps to create DYNAMIC, SYNCHRONIZED animations that POP!

Available actions:
- "indicate": Pulse/scale effect when word is spoken (great for emphasis)
- "flash": Bright flash effect (use for "look at this!")
- "circumscribe": Draw circle/box around object (highlight important parts)
- "wiggle": Small wiggle motion (playful emphasis)
- "focus": Brief zoom focus effect (direct attention)
- "color_pulse": Temporary color change (visual variety)
- "scale_pop": Quick scale up and down (makes it POP!)
- "write_word": Write text word-by-word as spoken (perfect sync)

WORD-SYNC STRATEGY:
1. When narration mentions a mathematical term → indicate/circumscribe the equation
2. When introducing a concept → flash or scale_pop the title/object
3. When saying "this" or "here" → focus/indicate the referenced object
4. When listing items → indicate each item as it's spoken
5. When emphasizing → use flash or color_pulse
6. For step-by-step explanations → write_word to reveal text progressively

Example: "Einstein's famous equation E equals M C squared"
- "Einstein" → flash portrait/title
- "equation" → circumscribe equation
- "E" → indicate E variable
- "equals" → indicate equals sign
- "M" → indicate M variable
- "C" → indicate C variable
- "squared" → indicate exponent with scale_pop

Return valid JSON with "metadata" and "scenes" keys."""

            # Format word timestamps if available
            word_sync_info = ""
            if word_timestamps and "segments" in word_timestamps:
                word_sync_info = "\n\nWORD-LEVEL TIMESTAMPS (use these for word_sync actions):\n"
                for seg in word_timestamps["segments"][:5]:  # Show first 5 segments as examples
                    if "words" in seg and seg["words"]:
                        word_sync_info += f"\nSegment {seg.get('id', 0)}: \"{seg.get('text', '')}\"\n"
                        for w in seg["words"][:10]:  # Show up to 10 words per segment
                            word_sync_info += f"  - \"{w.get('word', '')}\" at {w.get('start', 0):.2f}s\n"

            # Inject visual context if provided
            visual_context_prompt = ""
            if visual_context:
                visual_context_prompt = "\n\n" + visual_context.get_visual_summary() + "\n"
                logger.info(f"Including visual context from {len(visual_context.scenes)} previous scenes")
            else:
                logger.info("No visual context - this is the first scene or context not provided")

            user_prompt = f"""EDUCATIONAL TOPIC: {topic}
Duration: {total_duration:.1f}s

SCRIPT (what's being taught):
{script_text}
{word_sync_info}
{visual_context_prompt}

YOUR JOB: Create visuals that TEACH this concept, not generic diagrams!

TEACHING VISUALS:
- For math/physics → Show actual equations, formulas, relationships
- For processes → Show step-by-step flow with labeled stages
- For concepts → Illustrate with concrete examples/analogies
- For data → Plot actual graphs/charts that demonstrate the point
- For systems → Diagram real components and how they connect

EXAMPLE GOOD: Topic "Pythagorean theorem"
- visual_type: "shape", description: "Draw right triangle with sides labeled a, b, c"
- visual_type: "equation", description: "Show equation a² + b² = c²"
- visual_type: "diagram", description: "Illustrate squares on each side to prove theorem"

EXAMPLE BAD: Generic boxes labeled "Input → Process → Output" (too vague!)

Make visuals that directly teach {topic} based on what's in the script!
Add word_sync for dynamic emphasis."""

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
                "word_sync": scene.get("word_sync", []),  # NEW: Word-synchronized actions
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
