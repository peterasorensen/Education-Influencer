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

Key points:
- Minimize text, maximize visuals
- Use 3D objects and diagrams
- Build cumulatively (keep things on screen)
- Use ThreeDScene for 3D
- Use self.wait() to control timing - total animation should match target duration

Return ONLY Python code."""

        instructions_json = json.dumps(visual_instructions, indent=2)

        user_prompt = f"""Topic: {topic}
Target duration: {target_duration} seconds

Instructions:
{instructions_json}

Generate code. Use self.wait() to make animation last {target_duration} seconds total. Class name: EducationalScene"""

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
        system_prompt = """Fix this Manim code based on the error. Return ONLY fixed code."""

        user_prompt = f"""Error: {error_message}

Code:
```python
{broken_code}
```

Fix it."""

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

            if result.returncode != 0:
                error_msg = f"Manim rendering failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            # Find the output video file
            video_path = output_dir / "videos" / manim_file.stem / quality / "manim_output.mp4"

            if not video_path.exists():
                # Try alternative path structure
                for quality_dir in ["1080p60", "720p30", "480p15"]:
                    alt_path = output_dir / "videos" / manim_file.stem / quality_dir / "manim_output.mp4"
                    if alt_path.exists():
                        video_path = alt_path
                        break

            if not video_path.exists():
                raise Exception(f"Rendered video not found. Expected at: {video_path}")

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
