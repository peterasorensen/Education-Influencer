"""
Test script to verify Manim text wrapping and spatial tracking fixes.

This script demonstrates that:
1. Text wrapping prevents text from going off screen on 9:8 canvas
2. Spatial tracking prevents objects from overlapping
3. Canvas boundaries are respected (9:8 aspect ratio)

Run with: python test_manim_fixes.py
"""

from manim import *
import random
import math
import numpy as np


# Helper function for text wrapping (will be included in generated code)
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

    return "\n".join(lines)


class TestWrappingAndSpatialTracking(Scene):
    """Test scene demonstrating text wrapping and spatial tracking on 9:8 canvas."""

    def is_position_clear(self, x, y, width, height, margin=0.3):
        """Check if position is clear (no overlaps)."""
        for obj_bbox in self.placed_objects:
            # Check if bounding boxes overlap (with margin)
            if (abs(x - obj_bbox['x']) < (width + obj_bbox['width']) / 2 + margin and
                abs(y - obj_bbox['y']) < (height + obj_bbox['height']) / 2 + margin):
                return False
        return True

    def place_object(self, obj, x, y, width, height):
        """Place object and register in spatial tracker."""
        obj.move_to(np.array([x, y, 0]))
        self.placed_objects.append({
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'obj': obj
        })
        return obj

    def construct(self):
        # Initialize tracking lists
        self.placed_objects = []
        active_objects = []

        # Canvas boundaries for 9:8 aspect ratio
        canvas_width = 10.8  # -5.4 to 5.4
        canvas_height = 9.6  # -4.8 to 4.8

        # Draw canvas boundary (for visual reference)
        boundary = Rectangle(
            width=canvas_width,
            height=canvas_height,
            color=GRAY,
            stroke_width=2
        ).move_to(ORIGIN)
        self.add(boundary)

        # Test 1: Text wrapping with long text
        long_text = "This is a very long sentence that would normally go off the screen without proper text wrapping functionality implemented for the 9:8 aspect ratio canvas"

        # Without wrapping (BAD - commented out as it would go off screen)
        # bad_text = Text(long_text, font_size=36, color=RED)

        # With wrapping (GOOD)
        wrapped = wrap_text(long_text, font_size=36)
        good_text = Text(wrapped, font_size=36, color=GREEN)
        self.place_object(good_text, 0, 3.5, 7, 2)
        active_objects.append(good_text)

        self.play(Write(good_text, run_time=2))
        self.wait(1)

        # Test 2: Multiple objects with spatial tracking
        # Title
        title = Text(wrap_text("Educational Content", font_size=48), font_size=48, color=YELLOW)
        if self.is_position_clear(0, 1.5, 6, 1):
            self.place_object(title, 0, 1.5, 6, 1)
            active_objects.append(title)
            self.play(FadeIn(title))

        # Equation (should not overlap with title)
        equation = MathTex(r"E = mc^2", font_size=48, color=BLUE)
        if self.is_position_clear(0, -0.5, 3, 1):
            self.place_object(equation, 0, -0.5, 3, 1)
            active_objects.append(equation)
            self.play(Write(equation))

        # Diagram (should not overlap with equation)
        circle1 = Circle(radius=0.8, color=RED, fill_opacity=0.5)
        if self.is_position_clear(-2, -3, 1.6, 1.6):
            self.place_object(circle1, -2, -3, 1.6, 1.6)
            active_objects.append(circle1)
            self.play(Create(circle1))

        circle2 = Circle(radius=0.8, color=BLUE, fill_opacity=0.5)
        if self.is_position_clear(2, -3, 1.6, 1.6):
            self.place_object(circle2, 2, -3, 1.6, 1.6)
            active_objects.append(circle2)
            self.play(Create(circle2))

        self.wait(2)

        # Test 3: Cleanup old content before adding new
        # Remove all previous content
        self.play(*[FadeOut(obj) for obj in active_objects])
        for obj in active_objects:
            self.remove(obj)
        active_objects.clear()
        self.placed_objects.clear()

        # Add new content
        new_title = Text(wrap_text("New Section: Spatial Tracking Works!", font_size=42), font_size=42, color=PURPLE)
        self.place_object(new_title, 0, 2, 7, 1.5)
        active_objects.append(new_title)
        self.play(FadeIn(new_title))

        # Add explanation text with wrapping
        explanation = "Spatial tracking ensures objects don't overlap and text wrapping prevents content from going off screen on our 9:8 aspect ratio canvas"
        wrapped_explanation = wrap_text(explanation, font_size=32)
        explanation_text = Text(wrapped_explanation, font_size=32, color=WHITE)
        self.place_object(explanation_text, 0, -1, 8, 2.5)
        active_objects.append(explanation_text)
        self.play(Write(explanation_text, run_time=3))

        self.wait(2)

        # Final cleanup
        self.play(*[FadeOut(obj) for obj in active_objects])
        self.play(FadeOut(boundary))
        self.wait(1)


if __name__ == "__main__":
    print("=" * 70)
    print("TEST: Manim Text Wrapping and Spatial Tracking Fixes")
    print("=" * 70)
    print()
    print("This test demonstrates:")
    print("1. Text wrapping prevents overflow on 9:8 canvas")
    print("2. Spatial tracking prevents object overlaps")
    print("3. Canvas boundaries are respected (-5.4 to 5.4, -4.8 to 4.8)")
    print()
    print("To render this test:")
    print("  manim test_manim_fixes.py TestWrappingAndSpatialTracking -qh -r 1080,960")
    print()
    print("Expected output:")
    print("- Text should wrap and stay within canvas bounds")
    print("- Objects should not overlap each other")
    print("- Content should be clearly visible and well-positioned")
    print("=" * 70)
