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
            progress_callback("Generating Manim code...", 50)

        manim_code = None
        last_error = None
        error_history = []  # Track all previous errors for context

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Manim code generation attempt {attempt + 1}/{self.MAX_RETRIES}")

                if progress_callback:
                    progress_callback(
                        f"Generating Manim code (attempt {attempt + 1}/{self.MAX_RETRIES})...",
                        50 + (attempt * 3),
                    )

                # Generate code
                if attempt == 0:
                    manim_code = await self._generate_initial_code(
                        visual_instructions, topic, target_duration
                    )
                else:
                    # Fix previous code based on error with full context
                    manim_code = await self._fix_code(
                        manim_code, last_error, visual_instructions, topic, attempt, error_history
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
                    # Add to error history for context in next attempt
                    error_history.append({
                        "attempt": attempt + 1,
                        "error": error_message,
                        "stage": "syntax_validation"
                    })
                    continue

                # Test render to catch runtime errors
                test_valid, test_error = await self._test_render(output_path)

                if test_valid:
                    logger.info("Manim code generated and validated successfully")
                    if progress_callback:
                        progress_callback("Manim code validated successfully", 59)
                    return output_path

                logger.warning(
                    f"Runtime validation failed (attempt {attempt + 1}): {test_error}"
                )
                last_error = test_error
                # Add to error history for context in next attempt
                error_history.append({
                    "attempt": attempt + 1,
                    "error": test_error,
                    "stage": "runtime_validation"
                })

            except Exception as e:
                # Catch exceptions during this attempt but continue loop
                logger.warning(f"Exception during attempt {attempt + 1}: {e}")
                last_error = str(e)
                # Add to error history
                error_history.append({
                    "attempt": attempt + 1,
                    "error": str(e),
                    "stage": "exception"
                })
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
- AnnularSector (has parameter issues, use Sector or Arc instead)
- Surface.set_fill_by_value (use basic set_fill instead)
- ParametricSurface without proper setup (stick to basic shapes)
- ThreeDScene.set_camera_orientation with complex configs (use simple angles only)
- SVGMobject or any external file references (SVG, PNG, images) - NEVER use these
- ImageMobject - NEVER use external images
- Sparkle (does not exist, use Flash or Indicate instead)
- ParticleSystem (does not exist, use VGroup of Dots with animations instead)
- set_width/set_height with stretch=True parameter - DEPRECATED/REMOVED (use scale_to_fit_width/height)
- ONLY use shapes you can create with code (Circle, Square, Polygon, etc.)

REQUIRED IMPORTS AT TOP OF FILE:
```python
from manim import *
import random
import math
```

SAFE VISUAL TECHNIQUES:
1. Basic shapes: Circle, Square, Rectangle, Triangle, Line, Arc, Sector, Polygon, Dot, Ellipse
2. Text/Math: Text("..."), MathTex(r"...")
3. Grouping: VGroup(obj1, obj2, obj3)
4. Colors: .set_color(RED), .set_fill(BLUE, opacity=0.5), random.choice([RED, BLUE, GREEN])
5. Positioning: .move_to(UP), .next_to(other, RIGHT), .shift(LEFT * 2)
6. Basic animations: Create, FadeIn, FadeOut, Write, Transform, ReplacementTransform
7. Movement: obj.animate.shift(RIGHT), obj.animate.rotate(PI/4)
8. Random positioning: random.uniform(-3, 3) for coordinates
9. Pie slices: Use Sector(angle=PI/4) instead of AnnularSector
10. SIZING - NEVER use deprecated stretch parameter:
   - Use obj.scale(0.5) to make 50% size
   - Use obj.scale_to_fit_width(2) for specific width
   - Use obj.scale_to_fit_height(2) for specific height
   - BANNED: .set_width(val, stretch=True) or .set_height(val, stretch=True)

CRITICAL - ARRAY/LIST ACCESS (MUST FOLLOW):
- NEVER access list/VGroup indices without checking length first
- ALWAYS use: if len(items) > index: items[index]
- NEVER use: items[4] directly (will crash if less than 5 items)
- For iteration: use for item in items: ... (safe, no indexing needed)
- Example SAFE: for i, obj in enumerate(group): obj.set_color(BLUE)
- Example UNSAFE: group[2].set_color(BLUE)  # WRONG! Check length first!

VISUAL CREATIVITY (encouraged!):
- Compound shapes: VGroup multiple shapes together, layer them creatively
- Colors: Use gradients (.set_color_by_gradient), rainbow effects, color transitions
- Animations: Chain animations, use rate_func for easing, create smooth transitions
- Effects: Indicate, Flash, Wiggle, FocusOn, Circumscribe, ShowPassingFlash
- 3D: Rotate objects in 3D space, use Cube/Sphere/Prism, add depth with layering
- Particle effects: Create VGroups of Dots with random positions/colors
  Example: VGroup(*[Dot(color=random.choice([RED,BLUE])).shift(UP*random.uniform(-2,2)) for _ in range(10)])
           Animate with LaggedStart for staggered effect
- Motion: Use obj.animate.shift/rotate/scale, create paths with TracedPath
- Transformations: Morph shapes with Transform, create visual metaphors
- Emphasis: Surround important elements, add glowing effects with multiple layers
- Dynamic layouts: Arrange objects creatively, use .arrange(), .next_to() with buffers

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

CRITICAL BANS - THESE WILL CRASH (DO NOT USE):
- AnnularSector → BANNED! Use Sector(angle=PI/3) or Annulus(inner_radius=0.5, outer_radius=1)
- ShowCreation → BANNED! Use Create instead
- GrowArrow → BANNED! Use Create or FadeIn
- ParticleSystem → BANNED! Does not exist. Use VGroup of Dots with LaggedStart animations
- set_width/set_height with stretch=True → BANNED! Use .scale() or .scale_to_fit_width() instead
- align_to() after set_width/set_height → Can cause errors, do positioning separately

IMPLEMENT THE VISUAL INSTRUCTIONS CREATIVELY:
- Read the "description" field and bring it to life with engaging animations
- Follow the "cleanup" field to remove old content (critical for avoiding overlaps!)
- Use the suggested "manim_elements" but add creative flair
- Make animations smooth and visually interesting
- Use colors, gradients, and effects to enhance visual appeal
- Add particle effects, glowing, highlighting where appropriate
- Chain animations together smoothly

CONTENT CLEANUP (READ "cleanup" FIELD):
- If cleanup says "fade out intro title" → self.play(FadeOut(title_object))
- If cleanup says "remove previous diagram" → self.play(FadeOut(old_diagram)); self.remove(old_diagram)
- If cleanup says "clear screen" → fade out all previous objects
- Keep track of all created objects so you can remove them later

Examples of creative implementation:
- "draw fraction 1/2" → MathTex(r"\\frac{{1}}{{2}}") with Write animation, maybe add color
- "fraction bar divided in half" → Colorful Rectangle with Line, animate the division
- "show multiplication" → MathTex with smooth fade-in, maybe highlight the operation
- "water molecule" → Colored circles (H=white, O=red) with labels, show bonds as lines
- "pie slice" → Sector(angle=PI/4, color=BLUE) NOT AnnularSector
- "ring/donut" → Annulus(inner_radius=0.5, outer_radius=1.5) NOT AnnularSector

SPATIAL POSITIONING (CRITICAL - KEEP ON SCREEN & MANAGE OLD CONTENT):
- Screen boundaries: -7 to +7 horizontal, -4 to +4 vertical
- SAFE positioning: .to_edge(UP/DOWN/LEFT/RIGHT), .move_to(ORIGIN), .shift(UP/DOWN/LEFT/RIGHT)
- UNSAFE: Large multipliers like DOWN*3, UP*4, LEFT*5 will go OFF SCREEN!
- Layout zones: TOP (.to_edge(UP)), CENTER (ORIGIN), BOTTOM (DOWN*1 max)

REMOVE OLD CONTENT (CRITICAL):
- Intro titles: FadeOut after 2-3 seconds, don't let them stay forever
- Old diagrams: FadeOut or move off-screen when no longer needed
- Keep screen clean: self.play(FadeOut(old_obj)) before adding new content
- If building on previous: move old content aside (shift LEFT/UP) or fade to low opacity
- Example: self.play(FadeOut(title)); self.remove(title) after intro

AVOID OVERLAPS:
- Before adding new content, remove or move old content
- Use .next_to(other, DOWN, buff=0.5) to position relative to existing objects
- Scale objects if needed: obj.scale(0.7) to make room
- Clear the screen periodically: self.play(*[FadeOut(obj) for obj in [obj1, obj2, obj3]])

TIMING (CRITICAL):
1. Track elapsed_time variable
2. Before each animation: wait_time = timestamp["start"] - elapsed_time; self.wait(wait_time)
3. Use run_time in self.play() for precise duration control
4. Update elapsed_time after each animation

BE CREATIVE with visual implementation while following the core concept!

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
        attempt: int,
        error_history: List[Dict],
    ) -> str:
        """Fix Manim code based on error feedback with context from previous attempts."""
        system_prompt = """Fix this Manim code based on the error. Return ONLY fixed code.

COMMON FIXES:
- NameError 'ShowCreation' → Replace with Create
- NameError 'GrowArrow' → Replace with Create or FadeIn
- NameError 'Sparkle' → Replace with Flash or Indicate for emphasis effects
- NameError 'ParticleSystem' → Replace with VGroup of Dots animated individually
  Example: particles = VGroup(*[Dot().shift(random_point) for _ in range(20)])
           self.play(LaggedStart(*[FadeIn(p) for p in particles]))
- NameError 'random' → Add imports at top: from manim import *; import random; import math
- TypeError with AnnularSector → Use Sector or Arc instead
- TypeError with Surface/ParametricSurface → Use basic shapes instead
- TypeError with set_fill_by_value → Use .set_fill(color, opacity)
- TypeError 'unexpected keyword argument stretch' → CRITICAL! Remove stretch parameter from set_width/set_height
  OLD: rect.set_width(value, stretch=True, about_edge=LEFT)
  NEW: rect.scale_to_fit_width(value).align_to(original, LEFT)
- OSError with SVG/image files → NEVER use external files, draw with shapes instead
- Missing imports → ALWAYS include at top: from manim import *; import random; import math

CRITICAL - IndexError 'list index out of range' FIX:
This is THE MOST COMMON ERROR. Fix ALL array/list accesses:
1. Find ALL instances of direct indexing: items[0], group[3], objects[i], etc.
2. Replace with safe access patterns:
   - OLD: group[2].set_color(RED)
   - NEW: if len(group) > 2: group[2].set_color(RED)
   - BETTER: for obj in group: obj.set_color(RED)  # iterate instead
3. For loops with indices:
   - OLD: for i in range(5): group[i].shift(UP*i)
   - NEW: for i, obj in enumerate(group): obj.shift(UP*i)
4. NEVER assume a VGroup/list has any specific length!

SAFE REPLACEMENTS:
- AnnularSector → Sector(angle=PI/4) or Arc
- Complex 3D surfaces → Cube(), Sphere(), Prism()
- Parametric functions → Basic shapes with positioning
- Advanced camera → Simple scene without camera manipulation
- SVGMobject("file.svg") → Draw the shape using Circle, Polygon, VGroup, etc.
- ImageMobject → Not allowed, use shapes only
- group[index] → if len(group) > index: group[index] OR use enumerate/iteration
- obj.set_width(val, stretch=True) → obj.scale_to_fit_width(val)
- obj.set_height(val, stretch=True) → obj.scale_to_fit_height(val)
- For half-width: obj.copy().scale(0.5) instead of set_width(width/2, stretch=True)

IMPORTANT - YOU ARE IN A FIX LOOP:
The code you're seeing has already been attempted and FAILED. This is a RETRY attempt.
You must analyze what went wrong and try a DIFFERENT approach than before.
Don't just make the same fix again - the error shows your previous fix didn't work."""

        # Build context about previous attempts
        context_lines = []
        if error_history:
            context_lines.append("\n=== PREVIOUS FIX ATTEMPTS (THESE ALL FAILED) ===")
            for i, err_info in enumerate(error_history, 1):
                context_lines.append(
                    f"Attempt {err_info['attempt']} ({err_info['stage']}): {err_info['error']}"
                )
            context_lines.append("=== END PREVIOUS ATTEMPTS ===\n")
            context_lines.append(
                f"This is now attempt {attempt + 1}. The previous {len(error_history)} attempt(s) failed."
            )
            context_lines.append(
                "CRITICAL: You must try a DIFFERENT fix than before. The current code below is the result of your previous fix that FAILED."
            )

        previous_context = "\n".join(context_lines) if context_lines else ""

        user_prompt = f"""{previous_context}

CURRENT ERROR (from your previous fix attempt):
{error_message}

CURRENT CODE (this is your PREVIOUS fix that failed):
```python
{broken_code}
```

INSTRUCTIONS:
1. Analyze what you tried before (if this is a retry)
2. Understand why that fix didn't work
3. Try a DIFFERENT approach this time
4. Make sure to address the CURRENT error, not just repeat the same fix
5. Return ONLY the fixed Python code, no explanations

Fix the error using safe Manim patterns. Keep visuals similar but use reliable methods."""

        logger.info(f"Fixing Manim code based on error feedback (attempt {attempt + 1}, {len(error_history)} previous errors)")

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

        logger.debug(f"Fixed code attempt {attempt + 1}, length: {len(fixed_code)} characters")
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
        aspect_ratio: str = "16:9",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Render Manim code to video.

        Args:
            manim_file: Path to the Manim Python file
            output_dir: Directory to save rendered video
            scene_name: Name of the scene class to render
            quality: Quality flag (low_quality, medium_quality, high_quality)
            aspect_ratio: Video aspect ratio (default: 16:9, use 9:16 for mobile)
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

            # Calculate resolution based on aspect ratio
            # For 9:16 (mobile portrait), we'll use 1080x1920 for high quality
            # For 16:9 (standard), we'll use the default manim resolutions
            resolution_args = []
            if aspect_ratio == "9:16":
                # Mobile portrait resolution
                if quality == "high_quality":
                    resolution_args = ["-r", "1080,1920"]
                elif quality == "medium_quality":
                    resolution_args = ["-r", "720,1280"]
                else:  # low_quality
                    resolution_args = ["-r", "480,854"]

            # Run manim render command
            cmd = [
                "manim",
                quality_flag,
                str(manim_file),
                scene_name,
                "-o", "manim_output.mp4",
                "--media_dir", str(output_dir),
            ]

            # Add resolution if specified
            if resolution_args:
                cmd.extend(resolution_args)

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
