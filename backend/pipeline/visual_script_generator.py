"""
Visual Script Generator Module

Generates Manim-aware visual instructions based on the script and timestamps.
Creates detailed scene descriptions for mathematical animations and visual explanations.
"""

import logging
from typing import Callable, Optional, List, Dict
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class VisualScriptGenerator:
    """Generate Manim-aware visual instructions for educational content."""

    def __init__(self, api_key: str):
        """
        Initialize the visual script generator.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"

    async def generate_visual_instructions(
        self,
        script: List[Dict[str, str]],
        topic: str,
        aligned_timestamps: Optional[List[Dict]] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict]:
        """
        Generate visual instructions for Manim animations.

        Args:
            script: List of script segments with speaker and text
            topic: The educational topic
            aligned_timestamps: Optional list of script segments with timing
            progress_callback: Optional callback for progress updates

        Returns:
            List of visual instruction segments:
            [{
                "timestamp": {"start": 0.5, "end": 3.2},
                "narration": "...",
                "visual_type": "equation|diagram|graph|text|animation",
                "description": "Detailed description of what to show",
                "manim_elements": ["MathTex", "Circle", etc.],
                "transitions": ["FadeIn", "Transform", etc.]
            }, ...]

        Raises:
            Exception: If visual instruction generation fails
        """
        try:
            if progress_callback:
                progress_callback("Generating visual instructions...", 55)

            # Prepare script text with timestamps if available
            script_text = self._format_script_for_prompt(script, aligned_timestamps)

            system_prompt = """Design visual instructions for an educational animation using Manim.

For math/equations:
- Always include the mathematical notation being discussed
- Show step-by-step transformations of equations
- If helpful, use visual models (fraction bars, number lines, grids) to represent operations
- Highlight the parts being manipulated

For science:
- Draw the actual structures/objects being discussed (molecules, cells, atoms, planets)
- Label important parts
- Show processes with arrows and transformations

SPATIAL MANAGEMENT (CRITICAL):
- Use different screen positions: UP, DOWN, LEFT, RIGHT, TOP, BOTTOM
- Move old objects out of the way: shift them UP/LEFT, fade opacity, or scale down
- Position new content where there's space
- For titles/equations at top: keep them small or move them aside when drawing below
- For step-by-step: arrange vertically or horizontally with clear spacing

Return JSON with "instructions" key containing array of objects. Each object must have:
- "narration": the text being spoken
- "visual_type": equation, fraction_model, diagram, molecular_structure, etc. (be specific)
- "description": EXACTLY what to draw AND where to position it (UP, DOWN, LEFT, RIGHT, center, etc.)
- "manim_elements": MathTex for equations, specific shapes for models
- "builds_on": how this adds to previous visual without covering it
- "positioning": explicit positioning instructions to avoid overlaps

Example for "Let's multiply one half by two thirds":
{"instructions": [{
  "narration": "Let's multiply one half by two thirds",
  "visual_type": "equation",
  "description": "Write the equation 1/2 × 2/3 using MathTex at the top of screen",
  "manim_elements": ["MathTex for the multiplication expression"],
  "builds_on": "Starting point for the problem",
  "positioning": "Place at TOP, leaving center area free for visual model"
}]}"""

            user_prompt = f"""Topic: {topic}

Timestamped script:
{script_text}

For EACH line of narration, analyze what concept is being explained and design the appropriate visual:

MATH EXAMPLES:
- "multiply 1/2 by 3/4" → Show MathTex equation "1/2 × 3/4", then draw TWO fraction bars: one split in 2 parts (shade 1), one split in 4 parts (shade 3)
- "what is 25% of 80" → Show MathTex "25% × 80", draw a bar representing 100, divide it into 4 parts (25% each), show 80 inside
- "solve x + 5 = 12" → Show the equation, then show step-by-step: subtract 5 from both sides, show x = 7

SCIENCE EXAMPLES:
- "photosynthesis uses CO2 and water" → Draw the chemical equation, then draw representations of CO2 molecules (C with two Os) and H2O molecules
- "the earth orbits the sun" → Draw a large yellow sphere (sun) in center, smaller blue sphere (earth) moving in elliptical path around it

Design visuals that DIRECTLY illustrate the specific concept being discussed in that narration line."""

            logger.info(f"Generating visual instructions for topic: {topic}")

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
            logger.info(f"Visual instructions response (first 500 chars): {content[:500]}")

            parsed = json.loads(content)
            logger.info(f"Parsed JSON keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'not a dict'}")

            # Extract visual instructions with flexible key matching
            instructions = None

            if isinstance(parsed, list):
                instructions = parsed
            elif isinstance(parsed, dict):
                # Try common keys
                for key in ["visual_instructions", "instructions", "scenes", "visuals", "segments", "timeline"]:
                    if key in parsed:
                        instructions = parsed[key]
                        logger.info(f"Found instructions under key: {key}")
                        break

                # If still not found, try to find ANY list in the response
                if instructions is None:
                    for key, value in parsed.items():
                        if isinstance(value, list) and len(value) > 0:
                            instructions = value
                            logger.info(f"Found instructions list under key: {key}")
                            break

            if instructions is None or not isinstance(instructions, list):
                logger.error(f"Failed to extract instructions. Full response: {content}")
                logger.error(f"Parsed structure: {json.dumps(parsed, indent=2)[:1000]}")
                raise ValueError(f"Could not find visual instructions array in response. Keys found: {list(parsed.keys()) if isinstance(parsed, dict) else 'not a dict'}")

            # Validate and enrich instructions
            validated_instructions = self._validate_instructions(
                instructions, script, aligned_timestamps
            )

            logger.info(
                f"Generated {len(validated_instructions)} visual instruction segments"
            )

            if progress_callback:
                progress_callback(
                    f"Created {len(validated_instructions)} visual segments", 60
                )

            return validated_instructions

        except Exception as e:
            logger.error(f"Visual instruction generation failed: {e}")
            raise Exception(f"Failed to generate visual instructions: {e}")

    def _format_script_for_prompt(
        self,
        script: List[Dict[str, str]],
        aligned_timestamps: Optional[List[Dict]] = None,
    ) -> str:
        """Format script for the prompt."""
        lines = []

        if aligned_timestamps:
            for segment in aligned_timestamps:
                speaker = segment.get("speaker", "Unknown")
                text = segment.get("text", "")
                start = segment.get("start", 0)
                end = segment.get("end", 0)
                lines.append(
                    f"[{start:.2f}s - {end:.2f}s] {speaker}: {text}"
                )
        else:
            for idx, segment in enumerate(script):
                speaker = segment.get("speaker", "Unknown")
                text = segment.get("text", "")
                lines.append(f"{idx + 1}. {speaker}: {text}")

        return "\n".join(lines)

    def _validate_instructions(
        self,
        instructions: List[Dict],
        script: List[Dict[str, str]],
        aligned_timestamps: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """
        Validate and enrich visual instructions.

        Ensures all required fields are present and adds timing information.
        """
        validated = []

        for idx, instruction in enumerate(instructions):
            # Ensure required fields
            validated_instruction = {
                "id": idx,
                "narration": instruction.get("narration", ""),
                "visual_type": instruction.get("visual_type", "diagram"),
                "description": instruction.get("description", ""),
                "manim_elements": instruction.get("manim_elements", []),
                "builds_on": instruction.get("builds_on", ""),
            }

            # Add timestamp - CRITICAL for syncing
            if aligned_timestamps and idx < len(aligned_timestamps):
                segment = aligned_timestamps[idx]
                validated_instruction["timestamp"] = {
                    "start": segment.get("start", 0.0),
                    "end": segment.get("end", 0.0),
                }
                # Use actual narration text from aligned timestamps
                if not validated_instruction["narration"]:
                    validated_instruction["narration"] = segment.get("text", "")
            elif "timestamp" in instruction:
                validated_instruction["timestamp"] = instruction["timestamp"]
            else:
                # Estimate timing if no timestamps available
                estimated_start = idx * 3
                estimated_end = (idx + 1) * 3
                validated_instruction["timestamp"] = {
                    "start": estimated_start,
                    "end": estimated_end,
                }

            validated.append(validated_instruction)

        return validated

    async def refine_visual_instructions(
        self,
        original_instructions: List[Dict],
        feedback: str,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict]:
        """
        Refine visual instructions based on feedback.

        Args:
            original_instructions: Original visual instructions
            feedback: Feedback for refinement
            progress_callback: Optional callback for progress updates

        Returns:
            Refined visual instructions

        Raises:
            Exception: If refinement fails
        """
        try:
            if progress_callback:
                progress_callback("Refining visual instructions...", 55)

            system_prompt = """You are an expert at designing educational animations with Manim. Refine visual instructions based on feedback while maintaining clarity and educational value."""

            user_prompt = f"""Original visual instructions:
{json.dumps(original_instructions, indent=2)}

Feedback: {feedback}

Please refine the visual instructions based on this feedback. Return the refined instructions in the same JSON format."""

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

            # Extract refined instructions
            if "visual_instructions" in parsed:
                refined = parsed["visual_instructions"]
            elif "instructions" in parsed:
                refined = parsed["instructions"]
            elif isinstance(parsed, list):
                refined = parsed
            else:
                for value in parsed.values():
                    if isinstance(value, list):
                        refined = value
                        break
                else:
                    raise ValueError("Could not find refined instructions in response")

            logger.info(f"Refined {len(refined)} visual instructions")

            if progress_callback:
                progress_callback("Visual instruction refinement complete", 60)

            return refined

        except Exception as e:
            logger.error(f"Visual instruction refinement failed: {e}")
            raise Exception(f"Failed to refine visual instructions: {e}")
