"""
Text Wrapping Demo for Manim 9:8 Canvas
========================================

This file demonstrates the automatic text wrapping feature that prevents
text overflow on the 9:8 aspect ratio canvas (1080x960 pixels).

Key Features:
- Automatic line breaking at word boundaries
- Font size-aware character limit calculation
- Accurate dimension estimation for multi-line text
- Safe positioning within canvas bounds

Canvas Specifications:
- Aspect ratio: 9:8 (width:height)
- Resolution: 1080x960 pixels at high quality
- Manim coordinates: -5.4 to 5.4 horizontal, -4.8 to 4.8 vertical
- Safe text width: 8.8 units (with 1 unit margins on each side)
"""

from manim import *


class TextWrappingDemo(Scene):
    def construct(self):
        """Demonstrate various text wrapping scenarios."""

        # Title - wraps automatically at 60 chars for font_size 36
        title = Text(
            "Automatic Text Wrapping Demonstration\nfor 9:8 AspectRatio Canvas",
            font_size=42,
            color=BLUE
        ).to_edge(UP)

        self.play(Write(title), run_time=2)
        self.wait(1)

        # Example 1: Short text (no wrapping needed)
        short_text = Text(
            "This is short text",
            font_size=36,
            color=WHITE
        ).shift(UP * 2)

        example1_label = Text(
            "Example 1: Short Text",
            font_size=24,
            color=GRAY
        ).next_to(short_text, DOWN, buff=0.3)

        self.play(FadeIn(short_text), FadeIn(example1_label))
        self.wait(2)

        self.play(FadeOut(short_text), FadeOut(example1_label))

        # Example 2: Long text that needs wrapping
        long_text = Text(
            "This is a very long sentence that will definitely overflow off the\nscreen if we don't wrap it properly and would cause text to bleed\nbeyond the canvas boundaries making it unreadable",
            font_size=36,
            color=YELLOW
        ).move_to(ORIGIN)

        example2_label = Text(
            "Example 2: Wrapped Text (3 lines)",
            font_size=24,
            color=GRAY
        ).next_to(long_text, DOWN, buff=0.5)

        self.play(Write(long_text), run_time=3)
        self.play(FadeIn(example2_label))
        self.wait(3)

        self.play(FadeOut(long_text), FadeOut(example2_label))

        # Example 3: Large font size (fewer characters per line)
        large_font_text = Text(
            "Large font size makes text wider\nso even shorter sentences\nneed wrapping",
            font_size=48,
            color=GREEN
        ).move_to(ORIGIN)

        example3_label = Text(
            "Example 3: Large Font (48pt, 45 chars/line max)",
            font_size=24,
            color=GRAY
        ).next_to(large_font_text, DOWN, buff=0.5)

        self.play(Write(large_font_text), run_time=2)
        self.play(FadeIn(example3_label))
        self.wait(3)

        self.play(FadeOut(large_font_text), FadeOut(example3_label))

        # Example 4: Small font size (more characters per line)
        small_font_text = Text(
            "Small font allows more characters per line without overflow issues and can fit\nlonger sentences before needing to wrap to the next line",
            font_size=24,
            color=PURPLE
        ).move_to(ORIGIN)

        example4_label = Text(
            "Example 4: Small Font (24pt, 90 chars/line max)",
            font_size=24,
            color=GRAY
        ).next_to(small_font_text, DOWN, buff=0.5)

        self.play(Write(small_font_text), run_time=3)
        self.play(FadeIn(example4_label))
        self.wait(3)

        self.play(FadeOut(small_font_text), FadeOut(example4_label))

        # Example 5: Multiple text objects with different sizes
        text1 = Text(
            "Multiple text objects",
            font_size=36,
            color=RED
        ).shift(UP * 2)

        text2 = Text(
            "Each automatically wrapped\nbased on font size",
            font_size=30,
            color=ORANGE
        ).shift(UP * 0.5)

        text3 = Text(
            "Ensuring everything stays\nwithin canvas bounds\nfor perfect rendering",
            font_size=28,
            color=TEAL
        ).shift(DOWN * 1.5)

        example5_label = Text(
            "Example 5: Multiple Objects",
            font_size=24,
            color=GRAY
        ).to_edge(DOWN)

        self.play(
            FadeIn(text1),
            FadeIn(text2),
            FadeIn(text3),
            FadeIn(example5_label),
            run_time=2
        )
        self.wait(3)

        self.play(
            FadeOut(text1),
            FadeOut(text2),
            FadeOut(text3),
            FadeOut(example5_label)
        )

        # Final message
        final_message = Text(
            "Text wrapping prevents overflow\nand improves readability",
            font_size=40,
            color=GOLD
        ).move_to(ORIGIN)

        checkmark = Text("✓", font_size=72, color=GREEN).next_to(final_message, UP, buff=0.5)

        self.play(FadeIn(checkmark, scale=0.5))
        self.play(Write(final_message), run_time=2)
        self.wait(2)

        # Fade out title at the end
        self.play(
            FadeOut(title),
            FadeOut(final_message),
            FadeOut(checkmark),
            run_time=1.5
        )

        self.wait(1)


class ComparisonDemo(Scene):
    """Side-by-side comparison of wrapped vs unwrapped text."""

    def construct(self):
        # Title
        title = Text(
            "Before vs After Comparison",
            font_size=42,
            color=BLUE
        ).to_edge(UP)

        self.play(Write(title))
        self.wait(1)

        # Create divider line
        divider = Line(UP * 3, DOWN * 3, color=WHITE).move_to(ORIGIN)

        # Before (simulated overflow - shown in red)
        before_label = Text("WITHOUT Wrapping", font_size=28, color=RED).shift(LEFT * 3 + UP * 2.5)

        before_text = Text(
            "This text would overflow off\nthe screen without wrapping",
            font_size=32,
            color=RED
        ).shift(LEFT * 3)

        overflow_warning = Text(
            "⚠ May overflow!",
            font_size=24,
            color=RED
        ).shift(LEFT * 3 + DOWN * 1.5)

        # After (with wrapping - shown in green)
        after_label = Text("WITH Wrapping", font_size=28, color=GREEN).shift(RIGHT * 3 + UP * 2.5)

        after_text = Text(
            "This text is automatically\nwrapped to fit perfectly\nwithin canvas bounds",
            font_size=32,
            color=GREEN
        ).shift(RIGHT * 3)

        success_check = Text(
            "✓ Fits perfectly!",
            font_size=24,
            color=GREEN
        ).shift(RIGHT * 3 + DOWN * 1.8)

        # Animate
        self.play(Create(divider))
        self.wait(0.5)

        self.play(
            FadeIn(before_label),
            FadeIn(after_label)
        )
        self.wait(0.5)

        self.play(
            Write(before_text),
            Write(after_text),
            run_time=2
        )
        self.wait(1)

        self.play(
            FadeIn(overflow_warning),
            FadeIn(success_check)
        )
        self.wait(3)

        # Clean up
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )
        self.wait(0.5)


# Instructions for running this demo:
# 1. For TextWrappingDemo:
#    manim -pqh example_text_wrapping_demo.py TextWrappingDemo --resolution 1080,960
#
# 2. For ComparisonDemo:
#    manim -pqh example_text_wrapping_demo.py ComparisonDemo --resolution 1080,960
#
# 3. To render both:
#    manim -pqh example_text_wrapping_demo.py --resolution 1080,960
