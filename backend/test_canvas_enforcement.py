#!/usr/bin/env python3
"""
Test script to demonstrate canvas constraint enforcement.

This script shows:
1. Code that violates 9:8 canvas constraints (before enforcement)
2. Code after automatic enforcement (helper functions added, positions fixed)
3. Validation errors that would trigger regeneration
"""

import sys
import re
from pathlib import Path

# Add parent directory to path to import pipeline modules
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.manim_generator import ManimGenerator


# Example of BAD code that LLM might generate (violates constraints)
BAD_CODE = '''from manim import *
import random
import math

class EducationalScene(Scene):
    def construct(self):
        elapsed_time = 0

        # PROBLEM 1: Long text without wrapping - WILL GO OFF SCREEN!
        question_text = Text("Yeah, I always wondered how you know what each slice is worth.").to_edge(DOWN)
        self.play(Write(question_text), run_time=4.34)
        elapsed_time += 4.34

        # PROBLEM 2: Using .to_corner() - can go off-screen on 9:8 canvas!
        title = Text("Introduction to Fractions").to_corner(UP + LEFT)
        self.play(FadeIn(title))

        # PROBLEM 3: Using .to_edge() - unsafe on 9:8 canvas!
        subtitle = Text("Let's explore fractions together").to_edge(RIGHT)
        self.play(Write(subtitle))

        # PROBLEM 4: Multiple objects with no spatial tracking - WILL OVERLAP!
        obj1 = Circle().move_to(UP * 2)
        obj2 = Square().move_to(UP * 2)  # Same position as obj1!
        self.play(Create(obj1), Create(obj2))

        # PROBLEM 5: Long text without wrap_text function
        explanation = Text("This is a very long explanation that will definitely overflow the canvas boundaries because it's too wide for a 9:8 aspect ratio")
        self.play(Write(explanation))
'''


def test_validation():
    """Test that validation catches constraint violations."""
    print("=" * 80)
    print("TEST 1: VALIDATION - Detecting Canvas Constraint Violations")
    print("=" * 80)

    generator = ManimGenerator(api_key="dummy")  # Don't need real API key for validation

    is_valid, errors = generator._validate_canvas_constraints(BAD_CODE)

    print(f"\nValidation Result: {'PASS' if is_valid else 'FAIL'}")
    print(f"\nErrors Found: {len(errors)}")
    print("\nDetailed Errors:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

    print("\n" + "-" * 80)
    print("These errors would trigger code regeneration with stricter prompts.")
    print("-" * 80)


def test_enforcement():
    """Test that enforcement automatically fixes code."""
    print("\n\n" + "=" * 80)
    print("TEST 2: ENFORCEMENT - Automatic Code Fixing")
    print("=" * 80)

    generator = ManimGenerator(api_key="dummy")

    print("\n--- BEFORE ENFORCEMENT ---")
    print(BAD_CODE)

    print("\n\n--- APPLYING ENFORCEMENT ---")
    fixed_code = generator._enforce_canvas_bounds(BAD_CODE)

    print("\n--- AFTER ENFORCEMENT ---")
    print(fixed_code)

    print("\n\n" + "=" * 80)
    print("CHANGES MADE:")
    print("=" * 80)

    changes = []

    # Check what was added/changed
    if 'def wrap_text' in fixed_code and 'def wrap_text' not in BAD_CODE:
        changes.append("✓ Added wrap_text() helper function")

    if 'import numpy as np' in fixed_code and 'import numpy as np' not in BAD_CODE:
        changes.append("✓ Added numpy import")

    if 'def clamp_position' in fixed_code:
        changes.append("✓ Added clamp_position() helper function")

    # Count replacements (excluding comments)
    # Remove comments before counting
    code_no_comments = re.sub(r'#.*$', '', BAD_CODE, flags=re.MULTILINE)
    fixed_no_comments = re.sub(r'#.*$', '', fixed_code, flags=re.MULTILINE)

    to_edge_before = len(re.findall(r'\.to_edge\(', code_no_comments))
    to_edge_after = len(re.findall(r'\.to_edge\(', fixed_no_comments))
    if to_edge_after < to_edge_before:
        changes.append(f"✓ Replaced {to_edge_before - to_edge_after} .to_edge() calls with safe coordinates")

    to_corner_before = len(re.findall(r'\.to_corner\(', code_no_comments))
    to_corner_after = len(re.findall(r'\.to_corner\(', fixed_no_comments))
    if to_corner_after < to_corner_before:
        changes.append(f"✓ Replaced {to_corner_before - to_corner_after} .to_corner() calls with safe coordinates")

    wrap_text_usage = len(re.findall(r'wrap_text\(', fixed_code))
    if wrap_text_usage > 1:  # More than just the function definition
        changes.append(f"✓ Auto-wrapped {wrap_text_usage - 1} long Text() calls")

    for change in changes:
        print(f"  {change}")

    # Validate the fixed code
    print("\n\n--- VALIDATING FIXED CODE ---")
    is_valid, errors = generator._validate_canvas_constraints(fixed_code)
    print(f"Validation Result: {'PASS ✓' if is_valid else 'FAIL ✗'}")
    if errors:
        print("Remaining Issues:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("No constraint violations found! Code is now safe for 9:8 canvas.")


def test_specific_fixes():
    """Test specific code transformation examples."""
    print("\n\n" + "=" * 80)
    print("TEST 3: SPECIFIC TRANSFORMATION EXAMPLES")
    print("=" * 80)

    generator = ManimGenerator(api_key="dummy")

    examples = [
        {
            "name": "Long text wrapping",
            "before": 'Text("This is a very long sentence that will overflow the canvas boundaries on a 9:8 aspect ratio")',
            "pattern": r'wrap_text\(',
        },
        {
            "name": "to_edge(DOWN) replacement",
            "before": 'some_obj.to_edge(DOWN)',
            "pattern": r'move_to\(np\.array\(\[0, -3\.5, 0\]\)\)',
        },
        {
            "name": "to_corner(UP + LEFT) replacement",
            "before": 'title.to_corner(UP + LEFT)',
            "pattern": r'move_to\(np\.array\(\[-4\.0, 3\.5, 0\]\)\)',
        },
    ]

    for example in examples:
        code = f"from manim import *\nimport random\nimport math\n\nclass EducationalScene(Scene):\n    def construct(self):\n        {example['before']}"
        fixed = generator._enforce_canvas_bounds(code)

        print(f"\n{example['name']}:")
        print(f"  Before: {example['before']}")
        if re.search(example['pattern'], fixed):
            print(f"  After:  ✓ Fixed correctly")
        else:
            print(f"  After:  ✗ Not fixed (expected pattern not found)")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MANIM CANVAS CONSTRAINT ENFORCEMENT TEST SUITE")
    print("Testing 9:8 Aspect Ratio Safety Measures")
    print("=" * 80)

    test_validation()
    test_enforcement()
    test_specific_fixes()

    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("""
The enforcement system provides THREE layers of protection:

1. VALIDATION: Detects constraint violations and triggers regeneration
   - Checks for missing helper functions
   - Detects long text without wrapping
   - Identifies dangerous positioning methods
   - Validates spatial tracking implementation

2. POST-PROCESSING: Automatically fixes common issues
   - Adds wrap_text() and clamp_position() helper functions
   - Auto-wraps long Text() strings
   - Replaces .to_edge() with safe coordinates
   - Replaces .to_corner() with safe coordinates
   - Ensures numpy import is present

3. REGENERATION: If validation fails, LLM gets specific error feedback
   - Strict prompt tells LLM exactly what went wrong
   - Multiple retry attempts with increasing strictness
   - Full conversation context maintained for coherent fixes

This ensures text never goes off-screen and objects don't overlap,
even if the LLM doesn't follow the initial prompt instructions.
""")
    print("=" * 80)
