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

Rules:
- Show don't tell - minimal text, maximum visuals
- Use 3D objects, diagrams, shapes to demonstrate concepts
- Build cumulatively - keep adding to the scene
- Use transformations to show change

Return JSON with "visual_instructions" array."""

            user_prompt = f"""Topic: {topic}

Script:
{script_text}

Design visuals for this script."""

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
            logger.debug(f"Visual instructions response: {content[:500]}...")

            parsed = json.loads(content)

            # Extract visual instructions
            if "visual_instructions" in parsed:
                instructions = parsed["visual_instructions"]
            elif "instructions" in parsed:
                instructions = parsed["instructions"]
            elif "scenes" in parsed:
                instructions = parsed["scenes"]
            elif isinstance(parsed, list):
                instructions = parsed
            else:
                # Try to find the first list in the response
                for value in parsed.values():
                    if isinstance(value, list):
                        instructions = value
                        break
                else:
                    raise ValueError("Could not find visual instructions in response")

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
                "visual_type": instruction.get("visual_type", "text"),
                "description": instruction.get("description", ""),
                "manim_elements": instruction.get("manim_elements", []),
                "transitions": instruction.get("transitions", ["FadeIn", "FadeOut"]),
            }

            # Add timestamp if available
            if aligned_timestamps and idx < len(aligned_timestamps):
                segment = aligned_timestamps[idx]
                validated_instruction["timestamp"] = {
                    "start": segment.get("start", idx * 3),
                    "end": segment.get("end", (idx + 1) * 3),
                }
            elif "timestamp" in instruction:
                validated_instruction["timestamp"] = instruction["timestamp"]
            else:
                # Estimate timing
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
