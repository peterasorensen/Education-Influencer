#!/usr/bin/env python3
"""
Layout Engine Demo

Interactive demonstration of layout engine capabilities.
Shows JSON input and generated Manim code output.
"""

import json
from layout_engine import LayoutEngine, LayoutStrategy


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_basic_usage():
    """Demonstrate basic usage."""
    print_section("DEMO 1: Basic Usage")

    # Simple storyboard
    storyboard = {
        "objects": [
            {
                "id": "greeting",
                "type": "text",
                "content": "Welcome to Layout Engine!",
                "position": "auto",
                "layout_strategy": "center_focused",
                "properties": {
                    "color": "BLUE",
                    "font_size": 48
                }
            }
        ],
        "animations": [
            {
                "type": "write",
                "target": "greeting",
                "start_time": 0.0,
                "duration": 2.0
            },
            {
                "type": "highlight",
                "target": "greeting",
                "start_time": 3.0,
                "duration": 1.0,
                "effect": "indicate"
            }
        ]
    }

    print("INPUT JSON:")
    print(json.dumps(storyboard, indent=2))

    engine = LayoutEngine()
    code = engine.process_storyboard(storyboard)

    print("\nGENERATED MANIM CODE:")
    print("-" * 80)
    print(code)
    print("-" * 80)


def demo_spatial_awareness():
    """Demonstrate spatial awareness and collision detection."""
    print_section("DEMO 2: Spatial Awareness & Collision Detection")

    storyboard = {
        "objects": [
            # Place 3 circles with auto-placement
            {
                "id": "circle1",
                "type": "circle",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {"width": 1.5, "height": 1.5, "color": "RED", "fill_opacity": 0.6}
            },
            {
                "id": "circle2",
                "type": "circle",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {"width": 1.5, "height": 1.5, "color": "GREEN", "fill_opacity": 0.6}
            },
            {
                "id": "circle3",
                "type": "circle",
                "position": "auto",
                "layout_strategy": "grid",
                "properties": {"width": 1.5, "height": 1.5, "color": "BLUE", "fill_opacity": 0.6}
            }
        ],
        "animations": [
            {"type": "create", "target": "circle1", "start_time": 0.0, "duration": 0.5},
            {"type": "create", "target": "circle2", "start_time": 0.5, "duration": 0.5},
            {"type": "create", "target": "circle3", "start_time": 1.0, "duration": 0.5}
        ]
    }

    print("The engine automatically places objects to avoid overlaps:")
    print(json.dumps(storyboard, indent=2))

    engine = LayoutEngine()
    code = engine.process_storyboard(storyboard)

    # Show positions
    print("\nCOMPUTED POSITIONS:")
    for obj_id in ["circle1", "circle2", "circle3"]:
        pos = engine.get_object_position(obj_id)
        if pos:
            print(f"  {obj_id}: ({pos[0]:.2f}, {pos[1]:.2f})")

    print("\nNote: Objects are placed in grid pattern without overlapping!")


def demo_all_animation_types():
    """Demonstrate all animation types."""
    print_section("DEMO 3: All Animation Types")

    animations_demo = {
        "objects": [
            {"id": "obj1", "type": "text", "content": "Fade In", "position": {"x": -5, "y": 3}, "properties": {}},
            {"id": "obj2", "type": "text", "content": "Write", "position": {"x": -5, "y": 1.5}, "properties": {}},
            {"id": "obj3", "type": "circle", "position": {"x": -5, "y": 0}, "properties": {"width": 1, "height": 1, "color": "RED", "fill_opacity": 0.5}},
            {"id": "obj4", "type": "square", "position": {"x": -5, "y": -1.5}, "properties": {"width": 1, "height": 1, "color": "BLUE", "fill_opacity": 0.5}},
            {"id": "obj5", "type": "text", "content": "Scale Me!", "position": {"x": 2, "y": 0}, "properties": {"font_size": 24}},
            {"id": "obj6", "type": "text", "content": "Highlight", "position": {"x": 5, "y": 0}, "properties": {}},
        ],
        "animations": [
            {"type": "fade_in", "target": "obj1", "start_time": 0.0, "duration": 1.0},
            {"type": "write", "target": "obj2", "start_time": 1.0, "duration": 1.0},
            {"type": "create", "target": "obj3", "start_time": 2.0, "duration": 1.0},
            {"type": "create", "target": "obj4", "start_time": 3.0, "duration": 1.0},
            {"type": "move", "target": "obj3", "target_position": {"x": 0, "y": 0}, "start_time": 4.0, "duration": 1.5},
            {"type": "scale", "target": "obj5", "scale_factor": 2.0, "start_time": 5.0, "duration": 1.0},
            {"type": "highlight", "target": "obj6", "start_time": 6.0, "duration": 0.8, "effect": "flash"},
            {"type": "fade_out", "target": "obj1", "start_time": 7.0, "duration": 0.5},
        ]
    }

    print("Supported animation types:")
    print("- fade_in, fade_out")
    print("- write (for text/equations)")
    print("- create (for shapes)")
    print("- move, scale")
    print("- highlight (indicate, flash, circumscribe, wiggle)")
    print("- transform")

    print("\nSample animations:")
    print(json.dumps(animations_demo["animations"], indent=2))


def demo_layout_strategies():
    """Demonstrate different layout strategies."""
    print_section("DEMO 4: Layout Strategies")

    strategies = [
        ("center_focused", "Spiral outward from center"),
        ("grid", "Arrange in grid pattern"),
        ("flow", "Left-to-right, top-to-bottom"),
        ("vertical_stack", "Stack vertically"),
        ("horizontal_stack", "Stack horizontally"),
    ]

    print("Available layout strategies:\n")
    for strategy, description in strategies:
        print(f"  {strategy:20} - {description}")

    # Demo grid layout
    print("\n" + "-" * 80)
    print("Example: Grid Layout with 6 objects")
    print("-" * 80)

    grid_demo = {
        "objects": [],
        "animations": []
    }

    colors = ["RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "PURPLE"]
    for i, color in enumerate(colors):
        grid_demo["objects"].append({
            "id": f"box_{i}",
            "type": "square",
            "position": "auto",
            "layout_strategy": "grid",
            "properties": {
                "width": 1.2,
                "height": 1.2,
                "color": color,
                "fill_opacity": 0.7
            }
        })

    engine = LayoutEngine()
    code = engine.process_storyboard(grid_demo)

    print("\nComputed positions (grid layout):")
    for i in range(6):
        obj_id = f"box_{i}"
        pos = engine.get_object_position(obj_id)
        if pos:
            print(f"  {obj_id}: ({pos[0]:+6.2f}, {pos[1]:+6.2f})")


def demo_educational_equation():
    """Demonstrate educational equation example."""
    print_section("DEMO 5: Educational Equation with Visuals")

    equation_demo = {
        "objects": [
            {
                "id": "title",
                "type": "text",
                "content": "Quadratic Formula",
                "position": {"x": 0, "y": 3.5},
                "properties": {"color": "BLUE", "font_size": 52}
            },
            {
                "id": "formula",
                "type": "equation",
                "content": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
                "position": {"x": 0, "y": 2.0},
                "properties": {"color": "YELLOW", "font_size": 44}
            },
            {
                "id": "a_label",
                "type": "text",
                "content": "a: coefficient of x²",
                "position": {"x": 0, "y": 0.5},
                "properties": {"font_size": 28}
            },
            {
                "id": "b_label",
                "type": "text",
                "content": "b: coefficient of x",
                "position": {"x": 0, "y": -0.5},
                "properties": {"font_size": 28}
            },
            {
                "id": "c_label",
                "type": "text",
                "content": "c: constant term",
                "position": {"x": 0, "y": -1.5},
                "properties": {"font_size": 28}
            }
        ],
        "animations": [
            {"type": "write", "target": "title", "start_time": 0.0, "duration": 1.5},
            {"type": "write", "target": "formula", "start_time": 2.0, "duration": 2.5},
            {"type": "fade_in", "target": "a_label", "start_time": 5.0, "duration": 0.8},
            {"type": "fade_in", "target": "b_label", "start_time": 5.5, "duration": 0.8},
            {"type": "fade_in", "target": "c_label", "start_time": 6.0, "duration": 0.8},
            {"type": "highlight", "target": "formula", "start_time": 7.5, "duration": 1.0, "effect": "circumscribe"}
        ]
    }

    print("Educational content with equations and explanations:")
    print(json.dumps(equation_demo, indent=2))


def demo_timing_control():
    """Demonstrate precise timing control."""
    print_section("DEMO 6: Timing Control")

    timing_demo = {
        "objects": [
            {"id": "obj1", "type": "text", "content": "First (0-2s)", "position": {"x": 0, "y": 2}, "properties": {}},
            {"id": "obj2", "type": "text", "content": "Second (2-4s)", "position": {"x": 0, "y": 0}, "properties": {}},
            {"id": "obj3", "type": "text", "content": "Third (5-7s)", "position": {"x": 0, "y": -2}, "properties": {}},
        ],
        "animations": [
            {"type": "fade_in", "target": "obj1", "start_time": 0.0, "duration": 1.0},
            {"type": "fade_out", "target": "obj1", "start_time": 1.5, "duration": 0.5},
            {"type": "fade_in", "target": "obj2", "start_time": 2.0, "duration": 1.0},
            {"type": "fade_out", "target": "obj2", "start_time": 3.5, "duration": 0.5},
            {"type": "fade_in", "target": "obj3", "start_time": 5.0, "duration": 1.0},
            {"type": "fade_out", "target": "obj3", "start_time": 6.5, "duration": 0.5},
        ]
    }

    print("The layout engine handles precise timing:")
    print("- Automatic wait times between animations")
    print("- Elapsed time tracking")
    print("- Synchronized animations")

    print("\nTimeline:")
    for anim in timing_demo["animations"]:
        start = anim["start_time"]
        duration = anim["duration"]
        end = start + duration
        print(f"  {start:4.1f}s - {end:4.1f}s: {anim['type']:12} {anim['target']}")


def demo_canvas_info():
    """Show canvas information."""
    print_section("Canvas Coordinate System")

    print("""
Manim Canvas Layout:

        Y
        ^
        |
  +4    |------------------------+
        |                        |
        |         TOP            |
  +2    |                        |
        |                        |
  0     |-------CENTER-----------|------> X
        |                        |
  -2    |                        |
        |        BOTTOM          |
  -4    |                        |
        |                        |
  -7    +------------------------+ +7
        LEFT                   RIGHT

Dimensions:
  - Width:  14 units (-7 to +7)
  - Height:  8 units (-4 to +4)
  - Center: (0, 0)

Safe zones:
  - Title area:    y = 2.5 to 3.5
  - Content area:  y = -2.0 to 2.0
  - Footer area:   y = -3.5 to -2.5
    """)


def run_all_demos():
    """Run all demonstrations."""
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "  LAYOUT ENGINE - INTERACTIVE DEMONSTRATION".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)

    demo_basic_usage()
    demo_spatial_awareness()
    demo_all_animation_types()
    demo_layout_strategies()
    demo_educational_equation()
    demo_timing_control()
    demo_canvas_info()

    print("\n" + "*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "  DEMONSTRATION COMPLETE".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)

    print("\nNext steps:")
    print("  1. Check out layout_engine_examples.py for working code")
    print("  2. Run tests: python test_layout_engine.py")
    print("  3. Read docs: LAYOUT_ENGINE_README.md")
    print("  4. Try your own storyboards!\n")


if __name__ == "__main__":
    run_all_demos()
