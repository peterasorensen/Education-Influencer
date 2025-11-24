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
        conversation_history = []  # Maintain full conversation with LLM

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Manim code generation attempt {attempt + 1}/{self.MAX_RETRIES}")

                if progress_callback:
                    progress_callback(
                        f"Generating Manim code (attempt {attempt + 1}/{self.MAX_RETRIES})...",
                        50 + (attempt * 3),
                    )

                # Generate code (passes conversation history for context)
                if attempt == 0:
                    manim_code, conversation_history = await self._generate_initial_code(
                        visual_instructions, topic, target_duration
                    )
                else:
                    # Fix previous code based on error with FULL conversation context
                    manim_code, conversation_history = await self._fix_code(
                        manim_code, last_error, conversation_history, attempt
                    )

                # ENFORCE canvas bounds - post-process code to add safety measures
                logger.info("Applying canvas bounds enforcement...")
                manim_code = self._enforce_canvas_bounds(manim_code)

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
                    last_error = f"Syntax Error:\n{error_message}"
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
                last_error = f"Runtime Error:\n{test_error}"

            except Exception as e:
                # Catch exceptions during this attempt but continue loop
                logger.warning(f"Exception during attempt {attempt + 1}: {e}")
                last_error = f"Exception:\n{str(e)}"
                continue

        # Max retries exceeded
        error_msg = f"Failed to generate valid Manim code after {self.MAX_RETRIES} attempts. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def _generate_initial_code(
        self, visual_instructions: List[Dict], topic: str, target_duration: float = 60.0
    ) -> Tuple[str, List[Dict]]:
        """Generate initial Manim code from visual instructions.

        Returns:
            Tuple of (generated_code, conversation_history)
        """
        system_prompt = """Generate Manim code for an educational animation.

CRITICAL - NO TEXT OBJECTS (SUBTITLES HANDLE NARRATION):
- ⛔ NEVER use Text() objects for narration or explanations - subtitles already show spoken words!
- ⛔ NEVER create Text objects with dialogue, descriptions, or explanations
- ✅ ONLY use MathTex() for mathematical equations and formulas (E = mc², x² + y² = r², etc.)
- ✅ ONLY use Text() for SHORT labels on diagrams (max 1-3 words like "Input", "CPU", "Output")
- The video has SUBTITLES that show everything being said - DO NOT duplicate this as Text!
- Focus on VISUAL elements: shapes, diagrams, equations, arrows, graphs, animations
- Example WRONG: Text("Let's multiply these fractions") ← FORBIDDEN! Subtitle already shows this
- Example CORRECT: MathTex(r"\\frac{2}{3} \\times \\frac{4}{5}") ← This is a visual element

CRITICAL - 9:8 ASPECT RATIO CANVAS (NOT 16:9!):
- Resolution: 1080x960 (high quality) - This is a 9:8 aspect ratio, NOT 16:9!
- Canvas width: ~10.8 Manim units (from -5.4 to +5.4)
- Canvas height: ~9.6 Manim units (from -4.8 to +4.8)
- SAFE TEXT WIDTH: Maximum 8.8 units (leave 1 unit margin on each side)
- Horizontal boundaries: -5.4 to +5.4 (NEVER exceed these!)
- Vertical boundaries: -4.8 to +4.8 (NEVER exceed these!)

TEXT WRAPPING (CRITICAL - PREVENTS TEXT GOING OFF SCREEN):
ALWAYS wrap text to prevent overflow. Use this Python helper function at the top of your code:

```python
def wrap_text(text, font_size=36, max_width=8.8):
    '''Wrap text to prevent off-screen overflow on 9:8 canvas'''
    # Calculate max characters per line based on font size
    # Font size 36 = ~60 chars, font size 48 = ~45 chars, font size 24 = ~90 chars
    base_chars_at_36 = 60
    max_chars_per_line = int(base_chars_at_36 * (36 / font_size))

    # Ensure we don't exceed canvas width (worst case: 0.08 units per char)
    absolute_max = int(max_width / (0.08 * font_size / 36))
    max_chars_per_line = min(max_chars_per_line, absolute_max)

    # If text fits on one line, return as-is
    if len(text) <= max_chars_per_line:
        return text

    # Break text into words and wrap
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        space_needed = word_length + (1 if current_line else 0)

        if current_length + space_needed <= max_chars_per_line:
            current_line.append(word)
            current_length += space_needed
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(" ".join(current_line))

    return "\\n".join(lines)
```

Then wrap ALL text before creating Text objects:
```python
# BAD - text might go off screen:
text = Text("This is a long sentence that might overflow the canvas boundaries", font_size=36)

# GOOD - text is wrapped to fit:
wrapped = wrap_text("This is a long sentence that might overflow the canvas boundaries", font_size=36)
text = Text(wrapped, font_size=36)
```

SPATIAL AWARENESS (MANDATORY - PREVENT OVERLAPS):
CRITICAL: Helper functions will be automatically injected into your code.
You MUST use place_object_safe() for ALL object placement.

```python
# These functions are AUTOMATICALLY available (don't redefine them):
# - placed_objects = []  (global list tracking all objects)
# - is_position_clear(x, y, width, height, buffer=0.3)
# - place_object_safe(obj, x, y, width, height)
# - remove_object_tracking(obj)

# MANDATORY: Use place_object_safe() instead of obj.move_to()
# BAD (will cause overlaps):
title = Text(wrap_text("Introduction", font_size=48), font_size=48)
title.move_to(np.array([0, 3.5, 0]))  # WRONG - no tracking!

# GOOD (enforces boundaries and tracks position):
title = Text(wrap_text("Introduction", font_size=48), font_size=48)
place_object_safe(title, 0, 3.5, 4.0, 0.8)  # Automatically clamps and tracks!

# When removing objects, update tracking:
self.play(FadeOut(title))
remove_object_tracking(title)
self.remove(title)

# Optional: Check if position is clear before creating complex objects
if is_position_clear(0, 0, 3, 2):
    diagram = VGroup(...)  # Create diagram
    place_object_safe(diagram, 0, 0, 3, 2)
else:
    # Find alternative position or skip
    pass
```

CRITICAL RULES:
1. ALWAYS use place_object_safe() instead of .move_to()
2. ALWAYS wrap text with wrap_text() before creating Text objects
3. ALWAYS remove_object_tracking() before FadeOut/self.remove()
4. NEVER use .to_edge() or .to_corner() (will go off-screen on 9:8 canvas)
5. NEVER use direct .move_to() without place_object_safe()

POSITIONING GUIDELINES FOR 9:8 CANVAS:
- Top region: y = 3.5 to 4.5 (use for titles)
- Upper middle: y = 1.5 to 3.0 (use for equations/main content)
- Center: y = -1.0 to 1.5 (use for diagrams)
- Lower middle: y = -3.0 to -1.0 (use for explanations)
- Bottom: y = -4.5 to -3.0 (use for labels/notes)
- Left side: x = -4.0 to -2.0
- Center: x = -2.0 to 2.0
- Right side: x = 2.0 to 4.0

OBJECT CLEANUP (CRITICAL - PREVENTS OVERCROWDING):
- Remove old objects before adding new ones in the same region
- Use FadeOut + self.remove() to completely remove objects
- Track what's on screen and clean up regularly:
```python
# Keep list of active objects
active_objects = []

# When adding new content, remove old if in same region
if active_objects:
    self.play(*[FadeOut(obj) for obj in active_objects])
    for obj in active_objects:
        self.remove(obj)
    active_objects.clear()

# Add new content and track it
new_obj = Text(wrap_text("New content", font_size=36), font_size=36)
place_object(new_obj, 0, 2, 3, 0.8)
active_objects.append(new_obj)
self.play(FadeIn(new_obj))
```

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

WORD-SYNCHRONIZED ANIMATIONS (CRITICAL FOR ENGAGEMENT - MAKES ANIMATIONS POP!):
You will receive word_sync data showing EXACTLY when each word is spoken.
Use these to create DYNAMIC, SYNCHRONIZED animations that engage viewers!

CRITICAL - Word-sync timing pattern (MUST USE THIS EXACT PATTERN):
```python
# PATTERN: Wait to word time, then play animation, then update elapsed_time
# This ensures animations sync perfectly with audio!

# "indicate" - Pulse/scale effect (MOST COMMON - use for any emphasis)
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(Indicate(target_object, scale_factor=1.3), run_time=0.4)
elapsed_time += 0.4

# "flash" - Bright flash effect (great for "look at this!")
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(Flash(target_object, color=YELLOW, line_length=0.5), run_time=0.3)
elapsed_time += 0.3

# "circumscribe" - Draw attention box (highlight important parts)
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(Circumscribe(target_object, color=RED, fade_out=True), run_time=0.6)
elapsed_time += 0.6

# "wiggle" - Playful wiggle (fun emphasis)
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(Wiggle(target_object, scale_value=1.2), run_time=0.4)
elapsed_time += 0.4

# "focus" - Zoom focus effect (direct attention)
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(FocusOn(target_object), run_time=0.3)
elapsed_time += 0.3

# "color_pulse" - Temporary color change
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(target_object.animate.set_color(YELLOW), run_time=0.2)
self.play(target_object.animate.set_color(original_color), run_time=0.2)
elapsed_time += 0.4

# "scale_pop" - Quick scale up/down (makes it POP!)
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(target_object.animate.scale(1.3), run_time=0.15)
self.play(target_object.animate.scale(1/1.3), run_time=0.15)
elapsed_time += 0.3

# "write_word" - Write text word-by-word (perfect for progressive reveal)
if word_time > elapsed_time:
    self.wait(word_time - elapsed_time)
    elapsed_time = word_time
self.play(AddTextWordByWord(text_object), run_time=0.5)
elapsed_time += 0.5
```

WORD-SYNC IMPLEMENTATION PATTERN:
```python
def construct(self):
    elapsed_time = 0

    # Scene setup
    title = Text("Einstein's Equation")
    equation = MathTex(r"E = mc^2")

    # Position objects
    title.move_to(UP * 2)
    equation.move_to(ORIGIN)

    # Initial animations
    self.play(FadeIn(title))
    elapsed_time += 1.0
    self.play(Write(equation))
    elapsed_time += 1.5

    # WORD-SYNCHRONIZED ANIMATIONS from word_sync data
    # Example: word_sync = [
    #   {"word": "Einstein", "time": 2.5, "action": "flash", "target": "title"},
    #   {"word": "equation", "time": 3.2, "action": "circumscribe", "target": "equation"},
    #   {"word": "energy", "time": 4.1, "action": "indicate", "target": "e_part"}
    # ]

    # When "Einstein" is spoken at 2.5s - WAIT then ANIMATE
    if 2.5 > elapsed_time:
        self.wait(2.5 - elapsed_time)
        elapsed_time = 2.5
    self.play(Flash(title, color=YELLOW, line_length=0.5), run_time=0.3)
    elapsed_time += 0.3

    # When "equation" is spoken at 3.2s - WAIT then ANIMATE
    if 3.2 > elapsed_time:
        self.wait(3.2 - elapsed_time)
        elapsed_time = 3.2
    self.play(Circumscribe(equation, color=RED, fade_out=True), run_time=0.6)
    elapsed_time += 0.6

    # When "energy" is spoken at 4.1s - WAIT then ANIMATE
    if 4.1 > elapsed_time:
        self.wait(4.1 - elapsed_time)
        elapsed_time = 4.1
    self.play(Indicate(equation, scale_factor=1.5), run_time=0.4)
    elapsed_time += 0.4
```

ACCESSING EQUATION PARTS FOR WORD-SYNC:
```python
# MathTex allows indexing individual parts
equation = MathTex(r"E", "=", "m", "c", "^2")
# equation[0] = "E"
# equation[1] = "="
# equation[2] = "m"
# equation[3] = "c"
# equation[4] = "^2"

# When narration says "E" - highlight E
self.play(Indicate(equation[0], scale_factor=1.5), run_time=0.4)

# When narration says "mass" - highlight m
self.play(Indicate(equation[2], scale_factor=1.5), run_time=0.4)

# When narration says "speed of light" - highlight c
self.play(Circumscribe(equation[3], color=BLUE), run_time=0.5)
```

SYNCHRONIZATION STRATEGY:
1. Mathematical terms spoken → Indicate/Circumscribe the equation part
2. "This" or "here" → FocusOn or Indicate the referenced object
3. Concept introduction → Flash or scale_pop the main object
4. Step-by-step listing → Indicate each item as mentioned
5. Emphasis words → color_pulse or wiggle
6. Progressive explanation → write_word for text reveal

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
import numpy as np
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

CRITICAL - TRANSFORM + INDEXING (CAUSES BROADCAST ERRORS):
- NEVER access submobjects by index after Transform()
- WRONG: self.play(Transform(obj1, obj2)) followed by obj1[0] or obj1[2]
- This causes "ValueError: could not broadcast input array from shape (4,3) into shape (12,3)"
- Solutions:
  1. Use ReplacementTransform instead: self.play(ReplacementTransform(obj1, obj2)) then obj2[0]
  2. Create new objects instead of transforming
  3. Don't index into transformed objects - use them as a whole
- Example SAFE: obj = new_obj; self.play(Indicate(obj))
- Example UNSAFE: self.play(Transform(eq, eq_new)); self.play(Indicate(eq[2]))  # WRONG!

CRITICAL - ARRAY/LIST ACCESS (MUST FOLLOW):
- NEVER access MathTex/VGroup submobjects by index without checking length
- WRONG: eq[0], eq[2], eq[4] (will crash if eq doesn't have 5+ submobjects!)
- SAFE OPTION 1: Use whole object: self.play(Indicate(eq)) instead of Indicate(eq[0])
- SAFE OPTION 2: Check length first: if len(eq) > 2: self.play(Indicate(eq[2]))
- SAFE OPTION 3: Iterate: for part in eq: self.play(Indicate(part))
- MathTex submobjects are UNPREDICTABLE - don't assume specific indices exist!
- Example UNSAFE: final_eq = MathTex(r"x^2 + 5x + 6"); self.play(Indicate(final_eq[0]))  # CRASHES!
- Example SAFE: final_eq = MathTex(r"x^2 + 5x + 6"); self.play(Indicate(final_eq))  # WORKS!

CRITICAL - OBJECT LIFECYCLE (MUST FOLLOW):
- NEVER use objects after they've been removed from the scene
- WRONG: Remove obj → then use it in ReplacementTransform(obj, new_obj)
- If you need to transform between scenes, DON'T remove the source object first
- Example UNSAFE:
  self.play(FadeOut(eq1))
  self.remove(eq1)
  active_objects.clear()  # eq1 is GONE now
  self.play(ReplacementTransform(eq1, eq2))  # CRASHES! eq1 doesn't exist!
- Example SAFE:
  # Don't remove eq1 if you need it for transform
  self.play(ReplacementTransform(eq1, eq2))  # Transform THEN remove
  # OR just create new object:
  self.play(FadeOut(eq1))
  self.play(Create(eq2))

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
            # Support both legacy (manim_elements) and new storyboard (elements) formats
            timing_info = {
                "timestamp": inst.get("timestamp", {}),
                "narration": inst.get("narration", ""),
                "visual_type": inst.get("visual_type", ""),
                "description": inst.get("description", ""),
                "manim_elements": inst.get("manim_elements") or inst.get("elements", []),
                "builds_on": inst.get("builds_on", ""),
                "region": inst.get("region", ""),
                "cleanup": inst.get("cleanup", []),
                "transitions": inst.get("transitions", []),
                "properties": inst.get("properties", {}),
                "word_sync": inst.get("word_sync", []),
            }
            instructions_with_timing.append(timing_info)

        instructions_json = json.dumps(instructions_with_timing, indent=2)

        # Extract word_sync data from instructions
        has_word_sync = any(inst.get("word_sync") for inst in visual_instructions)
        word_sync_note = ""
        if has_word_sync:
            word_sync_note = "\n\nWORD-SYNC DATA PROVIDED - IMPLEMENT ALL WORD-SYNCHRONIZED ANIMATIONS!"
            word_sync_note += "\nEach scene includes 'word_sync' array with precise timing for dynamic effects."
            word_sync_note += "\nYou MUST implement these synchronized animations to make content POP!"

        user_prompt = f"""Generate Manim code for this educational animation.

Topic: {topic}
Duration: {target_duration} seconds
Total Scenes: {len(visual_instructions)}

VISUAL INSTRUCTIONS:
{instructions_json}
{word_sync_note}

REQUIREMENTS:
1. Implement ALL {len(visual_instructions)} scenes from start to finish
2. Each scene builds on previous content - don't remove objects unless "cleanup" says so
3. Track elapsed_time for timestamp synchronization
4. Use wrap_text() for all text
5. Use place_object_safe() for positioning
6. Implement word_sync actions if present

Technical specs:
- 9:8 canvas (x: -5.4 to 5.4, y: -4.8 to 4.8)
- Class name: EducationalScene
- Follow the "description" and "manim_elements" for each scene"""

        logger.info("Generating initial Manim code")

        # Build conversation history
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )

        code = response.choices[0].message.content

        # Add assistant response to conversation history
        messages.append({"role": "assistant", "content": code})

        # Extract code from markdown if present
        code = self._extract_code_from_markdown(code)

        logger.debug(f"Generated code length: {len(code)} characters")
        return code, messages

    async def _fix_code(
        self,
        broken_code: str,
        error_message: str,
        conversation_history: List[Dict],
        attempt: int,
    ) -> Tuple[str, List[Dict]]:
        """Fix Manim code based on error feedback with full conversation context.

        Args:
            broken_code: The code that failed
            error_message: The error that occurred
            conversation_history: Full conversation with LLM (maintains context)
            attempt: Current attempt number

        Returns:
            Tuple of (fixed_code, updated_conversation_history)
        """
        # Continue the conversation with the error as user feedback
        error_prompt = f"""The code you generated has an error. Here's what happened:

ERROR:
{error_message}

FAILED CODE:
```python
{broken_code}
```

This is attempt {attempt + 1}/3. Please analyze the error carefully and fix the code.

CRITICAL DEBUGGING TIPS FOR THIS ERROR:
- If IndexError "list index out of range": You're accessing MathTex/VGroup submobjects that don't exist (e.g., eq[0], eq[2]). MathTex doesn't always split into predictable submobjects! FIXES: (1) Use whole object: Indicate(eq) instead of Indicate(eq[0]), OR (2) Don't access by index at all - just animate the whole object, OR (3) Use Create/FadeIn instead of trying to access parts.
- If error mentions object after active_objects.clear(): You removed an object then tried to use it! NEVER use ReplacementTransform(old_obj, new_obj) after removing old_obj. FIX: Either don't remove the old object before transform, OR just use Create(new_obj) instead of transforming.
- If ValueError "could not broadcast input array": This is caused by accessing submobjects after Transform. NEVER use indexing after Transform (e.g., obj[0], obj[2]). Instead: (1) Use ReplacementTransform instead of Transform, OR (2) Create a new object instead of transforming, OR (3) Don't index into transformed objects.
- If NameError: You used a deprecated/non-existent function. Check the system prompt for replacements (ShowCreation→Create, GrowArrow→Create, etc).
- If TypeError with 'stretch': Remove the stretch parameter from set_width/set_height. Use .scale_to_fit_width() instead.
- If AttributeError: The method doesn't exist. Use basic Manim methods only.

SIMPLEST FIX FOR MOST ERRORS: Don't use indexing (obj[0], obj[2]) or Transform at all. Just use Create, FadeIn, FadeOut on whole objects!

Return ONLY the fixed Python code, no explanations."""

        logger.info(f"Fixing Manim code based on error (attempt {attempt + 1})")

        # Add error feedback to conversation history (continue the conversation)
        conversation_history.append({"role": "user", "content": error_prompt})

        # Continue conversation with full context
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=conversation_history,  # Full conversation history!
            temperature=0.7,
        )

        fixed_code = response.choices[0].message.content

        # Add assistant's fix to conversation history
        conversation_history.append({"role": "assistant", "content": fixed_code})

        # Extract code from markdown if present
        fixed_code = self._extract_code_from_markdown(fixed_code)

        logger.debug(f"Fixed code attempt {attempt + 1}, length: {len(fixed_code)} characters")
        return fixed_code, conversation_history

    def _validate_canvas_constraints(self, code: str) -> Tuple[bool, List[str]]:
        """
        Validate that code respects 9:8 canvas constraints.

        Args:
            code: The generated Manim code

        Returns:
            Tuple of (is_valid, list_of_errors)
            Only CRITICAL errors cause validation to fail
        """
        errors = []
        critical_errors = []

        # Strip comments for validation (to avoid false positives from commented code)
        code_no_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

        # Check 1: wrap_text function should be included
        if 'def wrap_text' not in code:
            critical_errors.append("CRITICAL: wrap_text() helper function not included - text WILL go off screen!")

        # Check 2: Find long text strings that should be wrapped
        # Find Text() calls with long strings (>50 chars)
        text_pattern = r'Text\(["\']([^"\']{50,})["\']'
        long_texts = re.findall(text_pattern, code_no_comments)
        if long_texts:
            # Check if wrap_text is actually being used
            if 'wrap_text(' not in code_no_comments:
                critical_errors.append(f"CRITICAL: Found {len(long_texts)} long Text() strings without wrap_text() usage. Examples: {long_texts[:2]}")

        # Check 3: Dangerous positioning methods that can go off-screen on 9:8 canvas
        dangerous_methods = [
            (r'\.to_edge\(', 'to_edge() can place objects off-screen on 9:8 canvas'),
            (r'\.to_corner\(', 'to_corner() can place objects off-screen on 9:8 canvas'),
        ]
        for pattern, warning in dangerous_methods:
            if re.search(pattern, code_no_comments):
                critical_errors.append(f"CRITICAL: Using {warning}. Use explicit coordinates instead.")

        # Check 4: Check for extreme position values
        # Look for move_to, shift with large values
        position_pattern = r'(?:move_to|shift)\([^)]*?([-\d.]+)\s*\*\s*(?:UP|DOWN|LEFT|RIGHT)'
        position_multipliers = re.findall(position_pattern, code)
        for multiplier in position_multipliers:
            try:
                val = abs(float(multiplier))
                if val > 5.0:
                    critical_errors.append(f"CRITICAL: Position multiplier {multiplier} exceeds safe bounds for 9:8 canvas (max ±4.5)")
            except:
                pass

        # Check 5: Spatial tracking functions (warnings only - not critical)
        if 'def is_position_clear' not in code:
            errors.append("INFO: is_position_clear() helper function not included - objects may overlap")

        if 'def place_object' not in code:
            errors.append("INFO: place_object() helper function not included - no spatial tracking")

        # Check 6: Active objects tracking (warnings only - not critical)
        if 'active_objects = []' not in code and 'active_objects=[]' not in code:
            errors.append("INFO: active_objects list not initialized - no object lifecycle management")

        # Combine all messages for logging
        all_messages = critical_errors + errors

        # Only fail validation if there are CRITICAL errors
        # Warnings/Info are logged but don't cause failure
        return len(critical_errors) == 0, all_messages

    def _enforce_canvas_bounds(self, code: str) -> str:
        """
        Post-process generated code to enforce 9:8 canvas constraints.
        Adds safety wrappers and helper functions if missing.

        Args:
            code: The generated Manim code

        Returns:
            Code with enforced canvas constraints
        """
        logger.info("Enforcing canvas bounds on generated code")

        # Template for helper functions that should ALWAYS be included
        HELPER_FUNCTIONS = '''
def wrap_text(text, font_size=36, max_width=8.8):
    """Wrap text to prevent off-screen overflow on 9:8 canvas"""
    base_chars_at_36 = 60
    max_chars_per_line = int(base_chars_at_36 * (36 / font_size))
    absolute_max = int(max_width / (0.08 * font_size / 36))
    max_chars_per_line = min(max_chars_per_line, absolute_max)

    if len(text) <= max_chars_per_line:
        return text

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        space_needed = word_length + (1 if current_line else 0)

        if current_length + space_needed <= max_chars_per_line:
            current_line.append(word)
            current_length += space_needed
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(" ".join(current_line))

    return "\\n".join(lines)

def clamp_position(x, y, max_x=4.5, max_y=4.0):
    """Clamp position to safe canvas bounds"""
    return (
        max(-max_x, min(max_x, x)),
        max(-max_y, min(max_y, y))
    )

# CRITICAL: Runtime spatial tracking to prevent overlaps
placed_objects = []

def is_position_clear(x, y, width, height, buffer=0.3):
    """Check if a position is free from overlaps with existing objects."""
    for obj_info in placed_objects:
        # Check if bounding boxes overlap (with buffer)
        if (abs(x - obj_info['x']) < (width + obj_info['width']) / 2 + buffer and
            abs(y - obj_info['y']) < (height + obj_info['height']) / 2 + buffer):
            return False
    return True

def place_object_safe(obj, x, y, width, height):
    """Place object safely - clamps to bounds and registers position."""
    # Clamp to canvas bounds (9:8 aspect ratio)
    x = max(-5.4 + width/2, min(5.4 - width/2, x))
    y = max(-4.8 + height/2, min(4.8 - height/2, y))

    # Move object to clamped position
    obj.move_to(np.array([x, y, 0]))

    # Register this object's position
    placed_objects.append({
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'obj': obj
    })

    return obj

def remove_object_tracking(obj):
    """Remove object from spatial tracking when it's removed from scene."""
    global placed_objects
    placed_objects = [info for info in placed_objects if info['obj'] != obj]
'''

        # Step 1: Ensure numpy is imported (needed for np.array in position replacements)
        if 'import numpy as np' not in code:
            logger.info("Adding numpy import")
            # Add after other imports
            import_match = re.search(r'(import (?:random|math))', code)
            if import_match:
                insert_pos = import_match.end()
                code = code[:insert_pos] + '\nimport numpy as np' + code[insert_pos:]

        # Step 2: Add helper functions if not present
        # Check for any of the critical helper functions
        needs_helpers = (
            'def wrap_text' not in code or
            'def remove_object_tracking' not in code or
            'def place_object_safe' not in code or
            'placed_objects = []' not in code
        )

        if needs_helpers:
            logger.info("Adding helper functions (wrap_text, place_object_safe, remove_object_tracking, placed_objects, etc.)")
            # Insert after imports and before class definition
            class_match = re.search(r'(class \w+\(Scene\):)', code)
            if class_match:
                insert_pos = class_match.start()
                # Remove any partial helper function definitions first to avoid duplicates
                code = re.sub(r'def wrap_text\(.*?\):.*?(?=\ndef [a-z_]|\nclass )', '', code, flags=re.DOTALL)
                code = re.sub(r'def remove_object_tracking\(.*?\):.*?(?=\ndef [a-z_]|\nclass )', '', code, flags=re.DOTALL)
                code = re.sub(r'def place_object_safe\(.*?\):.*?(?=\ndef [a-z_]|\nclass )', '', code, flags=re.DOTALL)
                code = re.sub(r'placed_objects\s*=\s*\[\]', '', code, flags=re.DOTALL)
                # Add complete helper functions
                code = code[:insert_pos] + HELPER_FUNCTIONS + '\n' + code[insert_pos:]
            else:
                logger.warning("Could not find class definition to insert helper functions!")
        else:
            logger.info("Helper functions already present in code")

        # Step 3: Auto-wrap long Text() calls
        # Find Text("long string", ...) and wrap with wrap_text()
        def wrap_long_text(match):
            text_content = match.group(1)
            rest = match.group(2)

            # Only wrap if text is longer than 50 chars
            if len(text_content) > 50:
                # Extract font_size if present
                font_size_match = re.search(r'font_size\s*=\s*(\d+)', rest)
                font_size = font_size_match.group(1) if font_size_match else '36'

                logger.info(f"Auto-wrapping long text: {text_content[:50]}...")
                # Keep the rest of the parameters intact
                if rest.strip():
                    return f'Text(wrap_text("{text_content}", font_size={font_size}), {rest.lstrip(", ")})'
                else:
                    return f'Text(wrap_text("{text_content}", font_size={font_size}))'
            return match.group(0)

        # Pattern: Text("any text"[, other_params])
        # Use non-greedy match and handle optional parameters
        code = re.sub(
            r'Text\("([^"]+)"((?:\s*,\s*[^)]*)?)\)',
            wrap_long_text,
            code
        )

        # Step 4: Replace dangerous positioning methods
        # Replace .to_edge() with explicit safe coordinates
        def replace_to_edge(match):
            direction = match.group(1)
            logger.info(f"Replacing .to_edge({direction}) with safe coordinates")

            # Map to safe coordinates on 9:8 canvas
            safe_positions = {
                'UP': '.move_to(np.array([0, 3.5, 0]))',
                'DOWN': '.move_to(np.array([0, -3.5, 0]))',
                'LEFT': '.move_to(np.array([-4.0, 0, 0]))',
                'RIGHT': '.move_to(np.array([4.0, 0, 0]))',
            }
            return safe_positions.get(direction, match.group(0))

        code = re.sub(r'\.to_edge\((UP|DOWN|LEFT|RIGHT)\)', replace_to_edge, code)

        # Replace .to_corner() with explicit safe coordinates
        def replace_to_corner(match):
            corner = match.group(1)
            logger.info(f"Replacing .to_corner({corner}) with safe coordinates")

            safe_corners = {
                'UP + LEFT': '.move_to(np.array([-4.0, 3.5, 0]))',
                'UP + RIGHT': '.move_to(np.array([4.0, 3.5, 0]))',
                'DOWN + LEFT': '.move_to(np.array([-4.0, -3.5, 0]))',
                'DOWN + RIGHT': '.move_to(np.array([4.0, -3.5, 0]))',
                'UL': '.move_to(np.array([-4.0, 3.5, 0]))',
                'UR': '.move_to(np.array([4.0, 3.5, 0]))',
                'DL': '.move_to(np.array([-4.0, -3.5, 0]))',
                'DR': '.move_to(np.array([4.0, -3.5, 0]))',
            }
            return safe_corners.get(corner, match.group(0))

        code = re.sub(r'\.to_corner\((UP \+ LEFT|UP \+ RIGHT|DOWN \+ LEFT|DOWN \+ RIGHT|UL|UR|DL|DR)\)', replace_to_corner, code)

        # Step 5: Fix dangerous indexing patterns (causes IndexError)
        # Pattern: obj[0], obj[2], obj[4] without length checks
        # This is EXTREMELY common and causes "IndexError: list index out of range"

        # Find all direct indexing patterns: variable_name[number]
        indexing_pattern = r'(\w+)\[(\d+)\]'
        indexing_matches = re.findall(indexing_pattern, code)

        if indexing_matches:
            logger.info("Detected direct indexing - wrapping with length checks...")

            # Group by variable name
            indexed_vars = {}
            for var_name, index in indexing_matches:
                if var_name not in indexed_vars:
                    indexed_vars[var_name] = []
                indexed_vars[var_name].append(int(index))

            # For each variable that's indexed, wrap accesses in safe checks
            for var_name, indices in indexed_vars.items():
                max_index = max(indices)
                # Only fix if indexing > 0 (common for MathTex submobjects)
                if max_index > 0:
                    logger.info(f"Variable '{var_name}' is indexed up to [{max_index}] - replacing with safe iteration")

                    # Replace pattern: self.play(Indicate(var[0])) with safe version
                    # Find all Indicate/Flash/etc calls with indexing
                    for idx in indices:
                        unsafe_pattern = rf'self\.play\((Indicate|Flash|Circumscribe|FocusOn)\({var_name}\[{idx}\]([^)]*)\)\)'
                        safe_replacement = rf'# Safely access {var_name}[{idx}] if it exists\n        if len({var_name}) > {idx}: self.play(\1({var_name}[{idx}]\2))'
                        code = re.sub(unsafe_pattern, safe_replacement, code)

        # Step 6: Remove ReplacementTransform/Transform using objects that don't exist
        # Pattern: object was removed from scene, then used in ReplacementTransform
        # This causes various errors

        # Find all variable assignments and tracking
        lines = code.split('\n')
        removed_vars = set()
        new_lines = []

        for i, line in enumerate(lines):
            # Track objects that get removed
            if 'self.remove(' in line or 'active_objects.clear()' in line:
                # Mark that variables might be invalid after this point
                pass

            # Check for ReplacementTransform/Transform with potentially removed objects
            transform_match = re.search(r'self\.play\((Replacement)?Transform\((\w+),\s*(\w+)\)', line)
            if transform_match:
                source_obj = transform_match.group(2)
                target_obj = transform_match.group(3)

                # Check if source_obj was created in this scene or previous
                # If it looks like it was removed, comment it out and just create target
                if i > 100:  # Arbitrary - if deep in code, likely cross-scene reference
                    # Look back to see if source was defined recently
                    lookback = '\n'.join(lines[max(0, i-30):i])
                    if source_obj not in lookback and 'active_objects.clear()' in lookback:
                        logger.warning(f"Line {i}: {source_obj} likely removed before Transform - replacing with direct Create")
                        # Replace with direct creation
                        indent = len(line) - len(line.lstrip())
                        new_line = ' ' * indent + f'self.play(Create({target_obj}))'
                        new_lines.append(new_line)
                        continue

            new_lines.append(line)

        code = '\n'.join(new_lines)

        # Step 7: Fix any legacy sync_to_word usage (broken pattern that doesn't call self.wait)
        # Pattern: elapsed_time = sync_to_word(X.X, elapsed_time)
        # Fix: if X.X > elapsed_time: self.wait(X.X - elapsed_time); elapsed_time = X.X
        sync_pattern = r'elapsed_time\s*=\s*sync_to_word\(([0-9.]+),\s*elapsed_time\)'
        sync_matches = re.findall(sync_pattern, code)

        if sync_matches:
            logger.warning(f"Found {len(sync_matches)} legacy sync_to_word calls - converting to inline wait pattern")
            for time_value in sync_matches:
                old_pattern = rf'elapsed_time\s*=\s*sync_to_word\({time_value},\s*elapsed_time\)'
                # Replace with correct inline pattern that calls self.wait()
                new_pattern = f'''if {time_value} > elapsed_time:
        self.wait({time_value} - elapsed_time)
        elapsed_time = {time_value}'''
                code = re.sub(old_pattern, new_pattern, code)
                logger.info(f"Converted sync_to_word({time_value}) to inline wait pattern")

        logger.info("Canvas bounds enforcement complete")
        return code

    def _validate_actual_positions(self, code: str) -> Tuple[bool, List[str]]:
        """
        Extract actual object positions from code and validate boundaries/overlaps.

        Args:
            code: The generated Manim code

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Extract move_to() calls: obj.move_to(np.array([x, y, 0]))
        move_pattern = r'(\w+)\.move_to\((?:np\.array\()?[\[\(]([^,\]]+),\s*([^,\]]+)(?:,\s*[^\]]+)?[\]\)]'
        moves = re.findall(move_pattern, code)

        positions = {}
        for match in moves:
            obj_id = match[0]
            try:
                x_str = match[1].strip()
                y_str = match[2].strip()

                # Evaluate simple expressions (e.g., "3.5", "-2.0")
                # Skip complex expressions (variables, functions)
                if re.match(r'^[-+]?\d+\.?\d*$', x_str) and re.match(r'^[-+]?\d+\.?\d*$', y_str):
                    x = float(x_str)
                    y = float(y_str)

                    # Estimate dimensions (conservative: 3x1 for text, 2x2 for shapes)
                    # This is a heuristic - real dimensions depend on object type
                    width = 3.0
                    height = 1.0

                    positions[obj_id] = (x, y, width, height)
            except (ValueError, IndexError):
                continue

        # Check boundaries
        for obj_id, (x, y, width, height) in positions.items():
            left = x - width/2
            right = x + width/2
            top = y + height/2
            bottom = y - height/2

            if left < -5.4:
                errors.append(f"BOUNDARY VIOLATION: {obj_id} extends beyond left boundary ({left:.2f} < -5.4)")
            if right > 5.4:
                errors.append(f"BOUNDARY VIOLATION: {obj_id} extends beyond right boundary ({right:.2f} > 5.4)")
            if top > 4.8:
                errors.append(f"BOUNDARY VIOLATION: {obj_id} extends beyond top boundary ({top:.2f} > 4.8)")
            if bottom < -4.8:
                errors.append(f"BOUNDARY VIOLATION: {obj_id} extends beyond bottom boundary ({bottom:.2f} < -4.8)")

        # Check for overlaps (simplified - only checks objects with explicit positions)
        obj_list = list(positions.items())
        for i in range(len(obj_list)):
            for j in range(i + 1, len(obj_list)):
                id1, (x1, y1, w1, h1) = obj_list[i]
                id2, (x2, y2, w2, h2) = obj_list[j]

                # Check if bounding boxes overlap
                if (abs(x1 - x2) < (w1 + w2)/2 and abs(y1 - y2) < (h1 + h2)/2):
                    errors.append(f"OVERLAP DETECTED: {id1} overlaps with {id2}")

        return len(errors) == 0, errors

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

            # CRITICAL: Validate canvas constraints (9:8 aspect ratio)
            is_valid, constraint_errors = self._validate_canvas_constraints(code_content)
            if not is_valid:
                error_msg = "Canvas constraint violations:\n" + "\n".join(constraint_errors)
                logger.warning(error_msg)
                return False, error_msg

            # NEW: Validate actual positions extracted from code
            is_valid_positions, position_errors = self._validate_actual_positions(code_content)
            if not is_valid_positions:
                error_msg = "Spatial violations detected:\n" + "\n".join(position_errors)
                logger.warning(error_msg)
                return False, error_msg

            logger.info("Code validation passed (syntax, constraints, and spatial checks)")
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
            # Quick render test - render FULL animation at low quality to catch all runtime errors
            # Previously only rendered first frame "-n 0,1" which missed errors later in animation
            cmd = [
                "manim",
                str(code_path),
                "EducationalScene",
                "-ql",  # Low quality for speed
                "--format=mp4",  # Full video to test all frames
            ]

            logger.info(f"Test rendering: {' '.join(cmd)}")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for full animation test (was 30s for single frame)
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
            aspect_ratio: Video aspect ratio (default: 16:9, use 9:16 for full mobile, 9:8 for half-screen top/bottom split)
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
            # For 9:8 (half-screen for top/bottom split), we'll use 1080x960
            # For 16:9 (standard), we'll use the default manim resolutions
            resolution_args = []
            if aspect_ratio == "9:16":
                # Mobile portrait resolution (full screen)
                if quality == "high_quality":
                    resolution_args = ["-r", "1080,1920"]
                elif quality == "medium_quality":
                    resolution_args = ["-r", "720,1280"]
                else:  # low_quality
                    resolution_args = ["-r", "480,854"]
            elif aspect_ratio == "9:8":
                # Half-screen portrait (for top/bottom compositing)
                if quality == "high_quality":
                    resolution_args = ["-r", "1080,960"]
                elif quality == "medium_quality":
                    resolution_args = ["-r", "720,640"]
                else:  # low_quality
                    resolution_args = ["-r", "480,427"]

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
