"""
Test script demonstrating text wrapping functionality.

This script shows how the text wrapping feature prevents text overflow
on the 9:8 aspect ratio canvas (1080x960).
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.layout_engine import LayoutEngine, ManimCodeTemplate


def test_text_wrapping():
    """Test text wrapping with various text lengths and font sizes."""

    print("=" * 80)
    print("TEXT WRAPPING TEST - Manim 9:8 Canvas (1080x960)")
    print("=" * 80)

    # Canvas specifications
    print(f"\nCanvas Width: {ManimCodeTemplate.CANVAS_WIDTH} units (-5.4 to 5.4)")
    print(f"Canvas Height: {ManimCodeTemplate.CANVAS_HEIGHT} units (-4.8 to 4.8)")
    print(f"Safe Text Width: {ManimCodeTemplate.SAFE_TEXT_WIDTH} units (with 1 unit margins)")

    # Test cases
    test_cases = [
        {
            "text": "Short text",
            "font_size": 36,
            "description": "Short text that fits on one line"
        },
        {
            "text": "This is a moderately long sentence that might need wrapping depending on the font size",
            "font_size": 36,
            "description": "Medium length text at standard font size"
        },
        {
            "text": "This is a very long sentence that will definitely overflow off the screen if we don't wrap it properly and would cause text to bleed beyond the canvas boundaries",
            "font_size": 36,
            "description": "Long text requiring multiple lines"
        },
        {
            "text": "Large font size makes text wider so even shorter sentences need wrapping",
            "font_size": 48,
            "description": "Medium text at large font size"
        },
        {
            "text": "Small font allows more characters per line without overflow issues",
            "font_size": 24,
            "description": "Text at small font size"
        },
    ]

    print("\n" + "=" * 80)
    print("TEST CASES")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        text = test["text"]
        font_size = test["font_size"]
        description = test["description"]

        print(f"\n--- Test Case {i}: {description} ---")
        print(f"Original text ({len(text)} chars): {text}")
        print(f"Font size: {font_size}")

        # Wrap the text
        wrapped = ManimCodeTemplate.wrap_text(text, font_size)

        # Calculate dimensions
        width, height = ManimCodeTemplate.estimate_text_dimensions(wrapped, font_size)

        # Check if it fits
        fits_width = width <= ManimCodeTemplate.SAFE_TEXT_WIDTH
        fits_height = height <= ManimCodeTemplate.CANVAS_HEIGHT

        print(f"\nWrapped text:")
        lines = wrapped.split("\\n")
        for line_num, line in enumerate(lines, 1):
            print(f"  Line {line_num}: {line}")

        print(f"\nEstimated dimensions:")
        print(f"  Width:  {width:.2f} units (limit: {ManimCodeTemplate.SAFE_TEXT_WIDTH} units) - {'✓ FITS' if fits_width else '✗ OVERFLOW'}")
        print(f"  Height: {height:.2f} units (limit: {ManimCodeTemplate.CANVAS_HEIGHT} units) - {'✓ FITS' if fits_height else '✗ OVERFLOW'}")
        print(f"  Lines:  {len(lines)}")


def test_layout_engine_integration():
    """Test the full layout engine with text wrapping."""

    print("\n\n" + "=" * 80)
    print("LAYOUT ENGINE INTEGRATION TEST")
    print("=" * 80)

    # Create layout engine
    engine = LayoutEngine()

    # Create a storyboard with long text
    storyboard = {
        "objects": [
            {
                "id": "title",
                "type": "text",
                "content": "Introduction to Mathematical Concepts and Their Applications",
                "position": "auto",
                "layout_strategy": "center_focused",
                "properties": {"color": "BLUE", "font_size": 48}
            },
            {
                "id": "description",
                "type": "text",
                "content": "This is a very long description that explains the concept in detail and would normally overflow off the screen if we didn't have automatic text wrapping enabled",
                "position": "auto",
                "layout_strategy": "center_focused",
                "properties": {"color": "WHITE", "font_size": 36}
            },
            {
                "id": "small_note",
                "type": "text",
                "content": "Small footnote",
                "position": "auto",
                "layout_strategy": "center_focused",
                "properties": {"color": "GRAY", "font_size": 24}
            },
        ],
        "animations": [
            {
                "type": "write",
                "target": "title",
                "start_time": 0.0,
                "duration": 2.0
            },
            {
                "type": "fade_in",
                "target": "description",
                "start_time": 2.5,
                "duration": 1.5
            },
            {
                "type": "fade_in",
                "target": "small_note",
                "start_time": 4.5,
                "duration": 1.0
            },
        ]
    }

    # Generate Manim code
    print("\nGenerating Manim code with automatic text wrapping...")
    code = engine.process_storyboard(storyboard)

    # Extract and display text creation sections
    print("\nGenerated text objects with wrapping:")
    print("-" * 80)

    for obj_id in ["title", "description", "small_note"]:
        if obj_id in engine.placed_objects:
            obj_info = engine.placed_objects[obj_id]
            spec = obj_info["spec"]
            original_text = spec["content"]
            font_size = spec["properties"]["font_size"]

            wrapped_text = ManimCodeTemplate.wrap_text(original_text, font_size)
            width, height = ManimCodeTemplate.estimate_text_dimensions(wrapped_text, font_size)

            lines = wrapped_text.split("\\n")
            print(f"\nObject: {obj_id}")
            print(f"  Original ({len(original_text)} chars): {original_text}")
            print(f"  Font size: {font_size}")
            print(f"  Wrapped ({len(lines)} lines):")
            for line_num, line in enumerate(lines, 1):
                print(f"    Line {line_num}: {line}")
            print(f"  Dimensions: {width:.2f}x{height:.2f} units")
            print(f"  Position: ({obj_info['position']['x']:.2f}, {obj_info['position']['y']:.2f})")

    print("\n" + "-" * 80)
    print("\nFull generated Manim code:")
    print("=" * 80)
    print(code)
    print("=" * 80)

    # Save to file for testing
    output_file = Path(__file__).parent / "test_wrapped_text.py"
    output_file.write_text(code)
    print(f"\n✓ Saved to: {output_file}")
    print("\nYou can test this with: manim -pql test_wrapped_text.py EducationalScene")


def demonstrate_comparison():
    """Show before/after comparison."""

    print("\n\n" + "=" * 80)
    print("BEFORE vs AFTER COMPARISON")
    print("=" * 80)

    long_text = "This is a very long sentence that will definitely overflow off the screen without proper text wrapping"
    font_size = 36

    print(f"\nOriginal text: {long_text}")
    print(f"Font size: {font_size}")

    # Before (no wrapping)
    print("\n--- BEFORE (No Wrapping) ---")
    print("Manim code:")
    print(f'  Text("{long_text}", font_size={font_size})')

    char_width = 0.05 * (font_size / 36)
    width_before = len(long_text) * char_width
    print(f"\nEstimated width: {width_before:.2f} units")
    print(f"Canvas safe width: {ManimCodeTemplate.SAFE_TEXT_WIDTH} units")
    print(f"Result: {'✗ OVERFLOWS by {:.2f} units'.format(width_before - ManimCodeTemplate.SAFE_TEXT_WIDTH) if width_before > ManimCodeTemplate.SAFE_TEXT_WIDTH else '✓ Fits'}")

    # After (with wrapping)
    print("\n--- AFTER (With Wrapping) ---")
    wrapped = ManimCodeTemplate.wrap_text(long_text, font_size)
    print("Manim code:")
    print(f'  Text("{wrapped}", font_size={font_size})')

    width_after, height_after = ManimCodeTemplate.estimate_text_dimensions(wrapped, font_size)
    print(f"\nEstimated dimensions: {width_after:.2f}x{height_after:.2f} units")
    print(f"Canvas safe width: {ManimCodeTemplate.SAFE_TEXT_WIDTH} units")
    print(f"Result: {'✓ Fits within canvas bounds' if width_after <= ManimCodeTemplate.SAFE_TEXT_WIDTH else '✗ Still overflows'}")

    print("\nWrapped text preview:")
    lines = wrapped.split("\\n")
    for line_num, line in enumerate(lines, 1):
        print(f"  Line {line_num}: {line}")


if __name__ == "__main__":
    test_text_wrapping()
    test_layout_engine_integration()
    demonstrate_comparison()

    print("\n\n" + "=" * 80)
    print("✓ TEXT WRAPPING TESTS COMPLETE")
    print("=" * 80)
