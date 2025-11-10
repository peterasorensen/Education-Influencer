"""
Manim Generator Module

Generates Manim code from visual instructions with self-fixing capabilities.
Validates generated code and retries with error feedback up to 3 times.
"""

import logging
from typing import Callable, Optional, List, Dict, Tuple
from pathlib import Path
import asyncio
import subprocess
import re
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class ManimGenerator:
    """Generate and validate Manim code with self-fixing loop."""

    MAX_RETRIES = 3

    def __init__(self, api_key: str):
        """
        Initialize the Manim generator.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"

    async def generate_manim_code(
        self,
        visual_instructions: List[Dict],
        topic: str,
        output_path: Path,
        target_duration: float = 60.0,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Generate Manim code from visual instructions with self-fixing.

        Args:
            visual_instructions: List of visual instruction segments
            topic: Educational topic
            output_path: Path to save the generated Manim Python file
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the generated and validated Manim file

        Raises:
            Exception: If code generation fails after max retries
        """
        if progress_callback:
            progress_callback("Generating Manim code...", 60)

        manim_code = None
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Manim code generation attempt {attempt + 1}/{self.MAX_RETRIES}")

                if progress_callback:
                    progress_callback(
                        f"Generating Manim code (attempt {attempt + 1}/{self.MAX_RETRIES})...",
                        60 + (attempt * 5),
                    )

                # Generate code
                if attempt == 0:
                    manim_code = await self._generate_initial_code(
                        visual_instructions, topic, target_duration
                    )
                else:
                    # Fix previous code based on error
                    manim_code = await self._fix_code(
                        manim_code, last_error, visual_instructions, topic
                    )

                # Save code
                output_path.parent.mkdir(parents=True, exist_ok=True)
                await asyncio.to_thread(
                    output_path.write_text, manim_code, encoding="utf-8"
                )

                # Validate code (syntax check)
                is_valid, error_message = await self._validate_code(output_path)

                if not is_valid:
                    logger.warning(
                        f"Syntax validation failed (attempt {attempt + 1}): {error_message}"
                    )
                    last_error = error_message
                    continue

                # Test render to catch runtime errors
                test_valid, test_error = await self._test_render(output_path)

                if test_valid:
                    logger.info("Manim code generated and validated successfully")
                    if progress_callback:
                        progress_callback("Manim code validated successfully", 75)
                    return output_path

                logger.warning(
                    f"Runtime validation failed (attempt {attempt + 1}): {test_error}"
                )
                last_error = test_error

            except Exception as e:
                # Catch exceptions during this attempt but continue loop
                logger.warning(f"Exception during attempt {attempt + 1}: {e}")
                last_error = str(e)
                continue

        # Max retries exceeded
        error_msg = f"Failed to generate valid Manim code after {self.MAX_RETRIES} attempts. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def _generate_initial_code(
        self, visual_instructions: List[Dict], topic: str, target_duration: float = 60.0
    ) -> str:
        """Generate initial Manim code from visual instructions."""
        system_prompt = """Generate Manim code for an educational animation.

CRITICAL TIMING REQUIREMENTS:
Track elapsed time properly:
```python
elapsed_time = 0  # Track total elapsed time

# For each timestamped instruction:
target_start = instruction["timestamp"]["start"]
wait_time = target_start - elapsed_time
if wait_time > 0:
    self.wait(wait_time)
    elapsed_time = target_start

# Play animation with run_time to control duration
duration = instruction["timestamp"]["end"] - instruction["timestamp"]["start"]
self.play(Animation, run_time=duration)
elapsed_time += duration
```

CRITICAL - FORBIDDEN/DEPRECATED (DO NOT USE):
- ShowCreation (use Create instead)
- GrowArrow (use Create or FadeIn instead)
- Surface.set_fill_by_value (use basic set_fill instead)
- ParametricSurface without proper setup (stick to basic shapes)
- ThreeDScene.set_camera_orientation with complex configs (use simple angles only)
- SVGMobject or any external file references (SVG, PNG, images) - NEVER use these
- ImageMobject - NEVER use external images
- ONLY use shapes you can create with code (Circle, Square, Polygon, etc.)

SAFE VISUAL TECHNIQUES:
1. Basic shapes: Circle, Square, Rectangle, Triangle, Line, Arc, Polygon
2. Text/Math: Text("..."), MathTex(r"...")
3. Grouping: VGroup(obj1, obj2, obj3)
4. Colors: .set_color(RED), .set_fill(BLUE, opacity=0.5)
5. Positioning: .move_to(UP), .next_to(other, RIGHT), .shift(LEFT * 2)
6. Basic animations: Create, FadeIn, FadeOut, Write, Transform, ReplacementTransform
7. Movement: obj.animate.shift(RIGHT), obj.animate.rotate(PI/4)

VISUAL SOPHISTICATION (use these safely):
- Compound shapes with VGroup: VGroup(Circle(), Square()).arrange(RIGHT)
- Layering: Create multiple objects at same position with different colors/sizes
- Gradients: .set_color_by_gradient(BLUE, PURPLE)
- Highlights: Indicate(obj), Flash(obj), Wiggle(obj)
- 3D basics: Cube(), Sphere(), Prism() with simple .rotate() and .shift()
- Arrows: Arrow(start, end), CurvedArrow(start, end)

CRITICAL - TEXT/MATH RENDERING:
- For equations/math: ALWAYS use MathTex(r"...") with raw strings
- For chemical formulas: Use MathTex(r"H_2O") NOT Tex("H_2O")
- For plain text: Use Text("...") NOT Tex
- MathTex handles LaTeX math mode automatically
- Example: MathTex(r"E = mc^2"), MathTex(r"6CO_2 + 6H_2O")

Return ONLY Python code."""

        # Format instructions with clear timestamp information
        instructions_with_timing = []
        for inst in visual_instructions:
            timing_info = {
                "timestamp": inst.get("timestamp", {}),
                "narration": inst.get("narration", ""),
                "visual_type": inst.get("visual_type", ""),
                "description": inst.get("description", ""),
                "manim_elements": inst.get("manim_elements", []),
                "builds_on": inst.get("builds_on", ""),
            }
            instructions_with_timing.append(timing_info)

        instructions_json = json.dumps(instructions_with_timing, indent=2)

        user_prompt = f"""Topic: {topic}
Total duration: {target_duration} seconds

Timestamped visual instructions:
{instructions_json}

CRITICAL: Follow the visual instructions EXACTLY.
- If instruction says "draw fraction 1/2" → draw MathTex(r"\\frac{{1}}{{2}}")
- If instruction says "draw fraction bar divided in half" → draw Rectangle divided by a Line
- If instruction says "show multiplication 2×3" → draw MathTex(r"2 \\times 3")
- If instruction says "draw water molecule" → draw circles for H and O atoms with labels
- Read the "description" field and implement EXACTLY what it says

SPATIAL POSITIONING (CRITICAL - KEEP EVERYTHING ON SCREEN):
- DEFAULT MANIM COORDINATES: Origin (0,0,0) is CENTER of screen
- Screen boundaries: approximately -7 to +7 horizontal, -4 to +4 vertical
- NEVER position objects beyond these bounds or they'll be off-screen
- WARNING: Objects positioned at DOWN*3 or DOWN*4 will likely be cut off at bottom!
- Follow "positioning" field instructions (TOP, UP, DOWN, LEFT, RIGHT, center)
- Safe positioning methods:
  * .to_edge(UP) - moves to top edge with padding (SAFE)
  * .to_edge(DOWN) - moves to bottom edge with padding (SAFE)
  * .to_corner(UL) - upper left corner with padding (SAFE)
  * .shift(UP) or .shift(UP*2) - move upward (SAFE)
  * .shift(DOWN) - small move down (SAFE)
  * .shift(DOWN*2) - medium move down (CHECK if too low!)
  * .next_to(other, DOWN, buff=0.5) - position below with spacing
- Layout strategy for multiple objects:
  * Top area: .to_edge(UP) or UP*2 for titles/equations
  * Center: ORIGIN or UP*0.5 or DOWN*0.5 for main content
  * Bottom area: DOWN or DOWN*1.5 MAX (don't go lower!)
  * Use .arrange(DOWN, buff=0.5) to auto-space vertically with safe spacing
- When new objects are added, make sure old ones don't cover them:
  * Move old objects: obj.animate.shift(UP*2) or obj.animate.shift(LEFT*3)
  * Fade old objects: obj.animate.set_opacity(0.3)
  * Scale down old objects: obj.animate.scale(0.5)
- Keep titles/equations small: .scale(0.7) or .scale(0.8)
- Example: VGroup(title, content, footer).arrange(DOWN, buff=0.8).move_to(ORIGIN)

Generate code with:
1. elapsed_time variable to track current time
2. Calculate wait_time = timestamp["start"] - elapsed_time before each animation
3. Use run_time parameter in self.play() for precise duration control
4. Follow visual_type and description fields precisely - don't improvise
5. Build on previous objects as described in "builds_on" field
6. Position objects according to "positioning" field to avoid overlaps

Class name: EducationalScene"""

        logger.info("Generating initial Manim code")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        code = response.choices[0].message.content

        # Extract code from markdown if present
        code = self._extract_code_from_markdown(code)

        logger.debug(f"Generated code length: {len(code)} characters")
        return code

    async def _fix_code(
        self,
        broken_code: str,
        error_message: str,
        visual_instructions: List[Dict],
        topic: str,
    ) -> str:
        """Fix Manim code based on error feedback."""
        system_prompt = """Fix this Manim code based on the error. Return ONLY fixed code.

COMMON FIXES:
- NameError 'ShowCreation' → Replace with Create
- NameError 'GrowArrow' → Replace with Create or FadeIn
- TypeError with Surface/ParametricSurface → Use basic shapes instead
- TypeError with set_fill_by_value → Use .set_fill(color, opacity)
- OSError with SVG/image files → NEVER use external files, draw with shapes instead
- Missing imports → Add: from manim import *

SAFE REPLACEMENTS:
- Complex 3D surfaces → Cube(), Sphere(), Prism()
- Parametric functions → Basic shapes with positioning
- Advanced camera → Simple scene without camera manipulation
- SVGMobject("file.svg") → Draw the shape using Circle, Polygon, VGroup, etc.
- ImageMobject → Not allowed, use shapes only"""

        user_prompt = f"""Error: {error_message}

Code:
```python
{broken_code}
```

Fix the error using safe Manim patterns. Keep visuals similar but use reliable methods."""

        logger.info("Fixing Manim code based on error feedback")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        fixed_code = response.choices[0].message.content
        fixed_code = self._extract_code_from_markdown(fixed_code)

        return fixed_code

    async def _validate_code(self, code_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate Manim code by checking syntax and imports.

        Args:
            code_path: Path to the Manim Python file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # First check: Python syntax
            result = await asyncio.to_thread(
                subprocess.run,
                ["python", "-m", "py_compile", str(code_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                error_msg = f"Syntax error: {result.stderr}"
                logger.warning(error_msg)
                return False, error_msg

            # Second check: Try importing the module
            # This checks for import errors and basic runtime issues
            code_content = code_path.read_text(encoding="utf-8")

            # Check for required Manim imports
            if "from manim import" not in code_content and "import manim" not in code_content:
                return False, "Missing Manim imports"

            # Check for Scene class
            if "class" not in code_content or "Scene" not in code_content:
                return False, "Missing Scene class definition"

            # Check for construct method
            if "def construct" not in code_content:
                return False, "Missing construct() method"

            logger.info("Code validation passed")
            return True, None

        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, f"Validation error: {str(e)}"

    async def _test_render(self, code_path: Path) -> Tuple[bool, str]:
        """
        Test render Manim code to catch runtime errors.

        Args:
            code_path: Path to the Manim Python file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Quick render test - just generate first frame
            cmd = [
                "manim",
                str(code_path),
                "EducationalScene",
                "-ql",  # Low quality for fast test
                "--format=png",  # Just render an image
                "-n", "0,1",  # Only first frame
            ]

            logger.info(f"Test rendering: {' '.join(cmd)}")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout for test
            )

            if result.returncode != 0:
                error_output = result.stderr or result.stdout
                # Extract the actual error message
                error_lines = error_output.split('\n')
                # Find the most relevant error line
                for line in reversed(error_lines):
                    if 'Error' in line or 'Exception' in line or 'TypeError' in line:
                        return False, line.strip()
                return False, f"Render test failed: {error_output[-500:]}"  # Last 500 chars

            logger.info("Test render passed")
            return True, None

        except subprocess.TimeoutExpired:
            return False, "Test render timeout"
        except Exception as e:
            logger.error(f"Test render error: {e}")
            return False, f"Test render error: {str(e)}"

    def _extract_code_from_markdown(self, text: str) -> str:
        """
        Extract Python code from markdown code blocks if present.

        Args:
            text: Text that may contain markdown code blocks

        Returns:
            Extracted code or original text
        """
        # Try to find code between ```python and ```
        pattern = r"```(?:python)?\s*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            # Return the first code block found
            return matches[0].strip()

        # No code blocks found, return original
        return text.strip()

    async def render_manim_video(
        self,
        manim_file: Path,
        output_dir: Path,
        scene_name: str = "EducationalScene",
        quality: str = "medium_quality",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Render Manim code to video.

        Args:
            manim_file: Path to the Manim Python file
            output_dir: Directory to save rendered video
            scene_name: Name of the scene class to render
            quality: Quality flag (low_quality, medium_quality, high_quality)
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the rendered video file

        Raises:
            Exception: If rendering fails
        """
        try:
            if progress_callback:
                progress_callback("Rendering Manim animation...", 75)

            logger.info(f"Rendering Manim scene: {scene_name}")

            # Quality to resolution mapping
            quality_flags = {
                "low_quality": "-ql",
                "medium_quality": "-qm",
                "high_quality": "-qh",
            }

            quality_flag = quality_flags.get(quality, "-qm")

            # Run manim render command
            cmd = [
                "manim",
                quality_flag,
                str(manim_file),
                scene_name,
                "-o", "manim_output.mp4",
                "--media_dir", str(output_dir),
            ]

            logger.info(f"Running command: {' '.join(cmd)}")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Log output for debugging
            if result.stdout:
                logger.info(f"Manim stdout: {result.stdout[-1000:]}")  # Last 1000 chars
            if result.stderr:
                logger.warning(f"Manim stderr: {result.stderr[-1000:]}")  # Last 1000 chars

            if result.returncode != 0:
                error_msg = f"Manim rendering failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Search for the output video file more comprehensively
            import os
            video_path = None

            # Search all subdirectories for manim_output.mp4
            for root, dirs, files in os.walk(output_dir):
                if "manim_output.mp4" in files:
                    video_path = Path(root) / "manim_output.mp4"
                    logger.info(f"Found video at: {video_path}")
                    break

            if not video_path or not video_path.exists():
                # Log directory structure for debugging
                logger.error(f"Video not found. Directory structure of {output_dir}:")
                for root, dirs, files in os.walk(output_dir):
                    logger.error(f"  {root}: {files}")
                raise Exception(f"Rendered video not found after searching {output_dir}")

            logger.info(f"Video rendered successfully: {video_path}")

            if progress_callback:
                progress_callback("Manim rendering complete", 85)

            return video_path

        except subprocess.TimeoutExpired:
            error_msg = "Manim rendering timeout (5 minutes)"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Manim rendering failed: {e}")
            raise Exception(f"Failed to render Manim video: {e}")
