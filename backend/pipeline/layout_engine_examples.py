"""
Layout Engine Examples

Demonstrates how to use the layout engine to convert storyboard JSON to Manim code.
"""

import json
from layout_engine import LayoutEngine


# Example 1: Simple text with animations
def example_1_simple_text():
    """Simple example: Title and subtitle with fade animations."""
    print("=" * 80)
    print("EXAMPLE 1: Simple Text with Fade Animations")
    print("=" * 80)

    storyboard = {
        "objects": [
            {
                "id": "title",
                "type": "text",
                "content": "Introduction to Fractions",
                "position": "auto",
                "layout_strategy": "center_focused",
                "properties": {
                    "color": "BLUE",
                    "font_size": 48
                }
            },
            {
                "id": "subtitle",
                "type": "text",
                "content": "Understanding 1/2 and 2/3",
                "position": "auto",
                "layout_strategy": "center_focused",
                "properties": {
                    "color": "WHITE",
                    "font_size": 36
                }
            }
        ],
        "animations": [
            {
                "type": "write",
                "target": "title",
                "start_time": 0.0,
                "duration": 1.5
            },
            {
                "type": "fade_in",
                "target": "subtitle",
                "start_time": 2.0,
                "duration": 1.0
            },
            {
                "type": "fade_out",
                "target": "title",
                "start_time": 5.0,
                "duration": 0.5
            },
            {
                "type": "fade_out",
                "target": "subtitle",
                "start_time": 5.5,
                "duration": 0.5
            }
        ]
    }

    engine = LayoutEngine()
    manim_code = engine.process_storyboard(storyboard)

    print("\nGenerated Manim Code:")
    print("-" * 80)
    print(manim_code)
    print("-" * 80)

    return manim_code


# Example 2: Mathematical equation with shapes
def example_2_equation_with_shapes():
    """Example with equation and visual shapes."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Equation with Visual Shapes")
    print("=" * 80)

    storyboard = {
        "objects": [
            {
                "id": "equation",
                "type": "equation",
                "content": r"\frac{1}{2} \times \frac{2}{3} = \frac{2}{6}",
                "position": {"x": 0, "y": 2.5},
                "properties": {
                    "color": "YELLOW",
                    "font_size": 44
                }
            },
            {
                "id": "fraction1",
                "type": "rectangle",
                "position": "auto",
                "layout_strategy": "horizontal_stack",
                "properties": {
                    "width": 2.0,
                    "height": 1.0,
                    "color": "BLUE",
                    "fill_opacity": 0.6
                }
            },
            {
                "id": "fraction2",
                "type": "rectangle",
                "position": "auto",
                "layout_strategy": "horizontal_stack",
                "properties": {
                    "width": 2.0,
                    "height": 1.0,
                    "color": "RED",
                    "fill_opacity": 0.6
                }
            },
            {
                "id": "result",
                "type": "rectangle",
                "position": "auto",
                "layout_strategy": "horizontal_stack",
                "properties": {
                    "width": 2.0,
                    "height": 1.0,
                    "color": "GREEN",
                    "fill_opacity": 0.6
                }
            }
        ],
        "animations": [
            {
                "type": "write",
                "target": "equation",
                "start_time": 0.0,
                "duration": 2.0
            },
            {
                "type": "create",
                "target": "fraction1",
                "start_time": 2.5,
                "duration": 1.0
            },
            {
                "type": "create",
                "target": "fraction2",
                "start_time": 3.0,
                "duration": 1.0
            },
            {
                "type": "highlight",
                "target": "fraction1",
                "start_time": 4.0,
                "duration": 0.5,
                "effect": "indicate"
            },
            {
                "type": "highlight",
                "target": "fraction2",
                "start_time": 4.5,
                "duration": 0.5,
                "effect": "indicate"
            },
            {
                "type": "create",
                "target": "result",
                "start_time": 5.5,
                "duration": 1.0
            }
        ]
    }

    engine = LayoutEngine()
    manim_code = engine.process_storyboard(storyboard)

    print("\nGenerated Manim Code:")
    print("-" * 80)
    print(manim_code)
    print("-" * 80)

    return manim_code


# Example 3: Complex scene with multiple object types
def example_3_complex_scene():
    """Complex example with multiple object types and animations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Complex Scene with Multiple Object Types")
    print("=" * 80)

    storyboard = {
        "objects": [
            {
                "id": "title",
                "type": "text",
                "content": "The Pythagorean Theorem",
                "position": {"x": 0, "y": 3.0},
                "properties": {
                    "color": "BLUE",
                    "font_size": 52
                }
            },
            {
                "id": "theorem",
                "type": "equation",
                "content": r"a^2 + b^2 = c^2",
                "position": {"x": 0, "y": 1.5},
                "properties": {
                    "color": "YELLOW",
                    "font_size": 48
                }
            },
            {
                "id": "square_a",
                "type": "square",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {
                    "width": 1.5,
                    "height": 1.5,
                    "color": "RED",
                    "fill_opacity": 0.5
                }
            },
            {
                "id": "square_b",
                "type": "square",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {
                    "width": 1.5,
                    "height": 1.5,
                    "color": "GREEN",
                    "fill_opacity": 0.5
                }
            },
            {
                "id": "square_c",
                "type": "square",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {
                    "width": 2.1,
                    "height": 2.1,
                    "color": "BLUE",
                    "fill_opacity": 0.5
                }
            },
            {
                "id": "label_a",
                "type": "text",
                "content": "a",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {
                    "color": "RED",
                    "font_size": 36
                }
            },
            {
                "id": "label_b",
                "type": "text",
                "content": "b",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {
                    "color": "GREEN",
                    "font_size": 36
                }
            },
            {
                "id": "label_c",
                "type": "text",
                "content": "c",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {
                    "color": "BLUE",
                    "font_size": 36
                }
            }
        ],
        "animations": [
            # Intro
            {
                "type": "write",
                "target": "title",
                "start_time": 0.0,
                "duration": 1.5
            },
            {
                "type": "write",
                "target": "theorem",
                "start_time": 2.0,
                "duration": 2.0
            },
            # Show squares
            {
                "type": "create",
                "target": "square_a",
                "start_time": 5.0,
                "duration": 1.0
            },
            {
                "type": "fade_in",
                "target": "label_a",
                "start_time": 5.5,
                "duration": 0.5
            },
            {
                "type": "create",
                "target": "square_b",
                "start_time": 6.5,
                "duration": 1.0
            },
            {
                "type": "fade_in",
                "target": "label_b",
                "start_time": 7.0,
                "duration": 0.5
            },
            {
                "type": "create",
                "target": "square_c",
                "start_time": 8.5,
                "duration": 1.0
            },
            {
                "type": "fade_in",
                "target": "label_c",
                "start_time": 9.0,
                "duration": 0.5
            },
            # Highlight relationship
            {
                "type": "highlight",
                "target": "square_a",
                "start_time": 11.0,
                "duration": 0.8,
                "effect": "indicate"
            },
            {
                "type": "highlight",
                "target": "square_b",
                "start_time": 11.3,
                "duration": 0.8,
                "effect": "indicate"
            },
            {
                "type": "highlight",
                "target": "square_c",
                "start_time": 12.5,
                "duration": 1.0,
                "effect": "circumscribe"
            }
        ]
    }

    engine = LayoutEngine()
    manim_code = engine.process_storyboard(storyboard)

    print("\nGenerated Manim Code:")
    print("-" * 80)
    print(manim_code)
    print("-" * 80)

    return manim_code


# Example 4: Animation transformations and movements
def example_4_transformations():
    """Example with transform and move animations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Transformations and Movements")
    print("=" * 80)

    storyboard = {
        "objects": [
            {
                "id": "circle1",
                "type": "circle",
                "position": {"x": -3, "y": 0},
                "properties": {
                    "width": 1.5,
                    "height": 1.5,
                    "color": "BLUE",
                    "fill_opacity": 0.7
                }
            },
            {
                "id": "square1",
                "type": "square",
                "position": {"x": 3, "y": 0},
                "properties": {
                    "width": 1.5,
                    "height": 1.5,
                    "color": "RED",
                    "fill_opacity": 0.7
                }
            },
            {
                "id": "text1",
                "type": "text",
                "content": "Watch the transformation!",
                "position": {"x": 0, "y": 3},
                "properties": {
                    "color": "WHITE",
                    "font_size": 40
                }
            }
        ],
        "animations": [
            {
                "type": "fade_in",
                "target": "text1",
                "start_time": 0.0,
                "duration": 1.0
            },
            {
                "type": "create",
                "target": "circle1",
                "start_time": 1.5,
                "duration": 1.0
            },
            {
                "type": "create",
                "target": "square1",
                "start_time": 2.0,
                "duration": 1.0
            },
            # Move circle to center
            {
                "type": "move",
                "target": "circle1",
                "target_position": {"x": 0, "y": 0},
                "start_time": 4.0,
                "duration": 1.5
            },
            # Scale up
            {
                "type": "scale",
                "target": "circle1",
                "scale_factor": 1.5,
                "start_time": 6.0,
                "duration": 1.0
            },
            # Scale down
            {
                "type": "scale",
                "target": "circle1",
                "scale_factor": 0.67,
                "start_time": 7.5,
                "duration": 1.0
            },
            # Highlight
            {
                "type": "highlight",
                "target": "square1",
                "start_time": 9.0,
                "duration": 1.0,
                "effect": "flash"
            }
        ]
    }

    engine = LayoutEngine()
    manim_code = engine.process_storyboard(storyboard)

    print("\nGenerated Manim Code:")
    print("-" * 80)
    print(manim_code)
    print("-" * 80)

    return manim_code


# Example 5: Grid layout with multiple shapes
def example_5_grid_layout():
    """Example demonstrating automatic grid layout."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Automatic Grid Layout")
    print("=" * 80)

    storyboard = {
        "objects": [
            {
                "id": "title",
                "type": "text",
                "content": "Grid Layout Demo",
                "position": {"x": 0, "y": 3.5},
                "properties": {
                    "color": "PURPLE",
                    "font_size": 48
                }
            }
        ],
        "animations": [
            {
                "type": "write",
                "target": "title",
                "start_time": 0.0,
                "duration": 1.0
            }
        ]
    }

    # Add 9 circles in a grid
    colors = ["RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "PURPLE", "PINK", "TEAL", "GOLD"]
    for i in range(9):
        storyboard["objects"].append({
            "id": f"shape_{i}",
            "type": "circle",
            "position": "auto",
            "layout_strategy": "grid",
            "properties": {
                "width": 1.0,
                "height": 1.0,
                "color": colors[i],
                "fill_opacity": 0.6
            }
        })
        storyboard["animations"].append({
            "type": "create",
            "target": f"shape_{i}",
            "start_time": 2.0 + i * 0.2,
            "duration": 0.5
        })

    engine = LayoutEngine()
    manim_code = engine.process_storyboard(storyboard)

    print("\nGenerated Manim Code:")
    print("-" * 80)
    print(manim_code)
    print("-" * 80)

    return manim_code


# Example 6: Complete educational scene
def example_6_educational_scene():
    """Complete educational scene example."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Complete Educational Scene - Multiplying Fractions")
    print("=" * 80)

    storyboard = {
        "objects": [
            # Title
            {
                "id": "title",
                "type": "text",
                "content": "Multiplying Fractions",
                "position": {"x": 0, "y": 3.5},
                "properties": {
                    "color": "BLUE",
                    "font_size": 52
                }
            },
            # Problem
            {
                "id": "problem",
                "type": "equation",
                "content": r"\frac{1}{2} \times \frac{2}{3}",
                "position": {"x": 0, "y": 2.0},
                "properties": {
                    "color": "YELLOW",
                    "font_size": 44
                }
            },
            # Step 1: Numerators
            {
                "id": "step1_label",
                "type": "text",
                "content": "Step 1: Multiply numerators",
                "position": {"x": -3, "y": 0.5},
                "properties": {
                    "color": "WHITE",
                    "font_size": 28
                }
            },
            {
                "id": "step1_calc",
                "type": "equation",
                "content": r"1 \times 2 = 2",
                "position": {"x": -3, "y": -0.5},
                "properties": {
                    "color": "GREEN",
                    "font_size": 36
                }
            },
            # Step 2: Denominators
            {
                "id": "step2_label",
                "type": "text",
                "content": "Step 2: Multiply denominators",
                "position": {"x": 3, "y": 0.5},
                "properties": {
                    "color": "WHITE",
                    "font_size": 28
                }
            },
            {
                "id": "step2_calc",
                "type": "equation",
                "content": r"2 \times 3 = 6",
                "position": {"x": 3, "y": -0.5},
                "properties": {
                    "color": "GREEN",
                    "font_size": 36
                }
            },
            # Result
            {
                "id": "result",
                "type": "equation",
                "content": r"\frac{2}{6} = \frac{1}{3}",
                "position": {"x": 0, "y": -2.5},
                "properties": {
                    "color": "GOLD",
                    "font_size": 48
                }
            },
            # Visual rectangle
            {
                "id": "visual_rect",
                "type": "rectangle",
                "position": {"x": 0, "y": -2.5},
                "properties": {
                    "width": 3.0,
                    "height": 1.5,
                    "color": "BLUE",
                    "fill_opacity": 0.3
                }
            }
        ],
        "animations": [
            # Introduction
            {
                "type": "write",
                "target": "title",
                "start_time": 0.0,
                "duration": 1.5
            },
            {
                "type": "write",
                "target": "problem",
                "start_time": 2.0,
                "duration": 2.0
            },
            # Fade out title
            {
                "type": "fade_out",
                "target": "title",
                "start_time": 5.0,
                "duration": 0.5
            },
            # Step 1
            {
                "type": "fade_in",
                "target": "step1_label",
                "start_time": 6.0,
                "duration": 1.0
            },
            {
                "type": "write",
                "target": "step1_calc",
                "start_time": 7.0,
                "duration": 1.5
            },
            {
                "type": "highlight",
                "target": "step1_calc",
                "start_time": 8.5,
                "duration": 0.8,
                "effect": "indicate"
            },
            # Step 2
            {
                "type": "fade_in",
                "target": "step2_label",
                "start_time": 9.5,
                "duration": 1.0
            },
            {
                "type": "write",
                "target": "step2_calc",
                "start_time": 10.5,
                "duration": 1.5
            },
            {
                "type": "highlight",
                "target": "step2_calc",
                "start_time": 12.0,
                "duration": 0.8,
                "effect": "indicate"
            },
            # Show result
            {
                "type": "write",
                "target": "result",
                "start_time": 13.5,
                "duration": 2.0
            },
            {
                "type": "highlight",
                "target": "result",
                "start_time": 15.5,
                "duration": 1.0,
                "effect": "circumscribe"
            }
        ]
    }

    engine = LayoutEngine()
    manim_code = engine.process_storyboard(storyboard)

    print("\nGenerated Manim Code:")
    print("-" * 80)
    print(manim_code)
    print("-" * 80)

    # Also save to file
    output_file = "/Users/Apple/workspace/gauntlet/educational-influencer/backend/output/example_6_manim_code.py"
    try:
        with open(output_file, 'w') as f:
            f.write(manim_code)
        print(f"\nCode saved to: {output_file}")
    except Exception as e:
        print(f"\nCould not save to file: {e}")

    return manim_code


def run_all_examples():
    """Run all examples."""
    print("\n")
    print("*" * 80)
    print("LAYOUT ENGINE EXAMPLES - JSON TO MANIM CODE CONVERSION")
    print("*" * 80)

    example_1_simple_text()
    example_2_equation_with_shapes()
    example_3_complex_scene()
    example_4_transformations()
    example_5_grid_layout()
    example_6_educational_scene()

    print("\n" + "*" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("*" * 80)


if __name__ == "__main__":
    # Run all examples
    run_all_examples()
