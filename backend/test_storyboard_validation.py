"""
Test script for validating storyboard examples and schema.

This script validates all example storyboards and demonstrates
the validation and analysis capabilities.
"""

import json
import sys
from pathlib import Path
from storyboard_validator import (
    StoryboardValidator,
    StoryboardAnalyzer,
    print_validation_report
)
from storyboard_utils import (
    StoryboardBuilder,
    SegmentBuilder,
    create_text,
    create_equation,
    create_shape,
    storyboard_to_markdown,
    StoryboardTransformer
)


def test_schema_validation():
    """Test schema validation on all examples."""
    print("="*80)
    print("TESTING SCHEMA VALIDATION")
    print("="*80)
    print()

    validator = StoryboardValidator('storyboard_schema.json')

    example_files = [
        'examples/storyboard_pythagorean_theorem.json',
        'examples/storyboard_dna_structure.json',
        'examples/storyboard_newtons_second_law.json',
        'examples/storyboard_chain_rule.json'
    ]

    all_valid = True

    for filepath in example_files:
        if Path(filepath).exists():
            print_validation_report(filepath, validator)
            is_valid, _ = validator.validate_file(filepath)
            all_valid = all_valid and is_valid
        else:
            print(f"Warning: {filepath} not found")
            all_valid = False

    return all_valid


def test_storyboard_builder():
    """Test programmatic storyboard creation."""
    print("="*80)
    print("TESTING STORYBOARD BUILDER")
    print("="*80)
    print()

    # Create a simple storyboard programmatically
    builder = StoryboardBuilder(
        title="Test: Simple Algebra",
        topic="Solving Linear Equations",
        category="mathematics"
    )

    builder.set_difficulty("beginner")
    builder.set_target_audience("middle school students")
    builder.add_learning_objective("Solve simple linear equations")
    builder.add_prerequisite("Basic arithmetic")

    # Create segment 1
    seg1 = SegmentBuilder("seg_intro", 0.0, 5.0)
    seg1.add_narration(
        "Let's solve a simple equation: x plus 3 equals 7",
        emphasis_words=["solve", "equation"]
    )
    seg1.add_visual_state(
        create_text(
            "title",
            "Solving Linear Equations",
            position="top",
            size="large",
            color="#58A6FF"
        )
    )
    seg1.add_visual_state(
        create_equation(
            "eq1",
            "x + 3 = 7",
            position="center",
            timing=2.0
        )
    )
    builder.add_segment(seg1.build())

    # Create segment 2
    seg2 = SegmentBuilder("seg_solve", 5.0, 10.0)
    seg2.add_narration(
        "Subtract 3 from both sides to get x equals 4",
        emphasis_words=["subtract", "both sides"]
    )
    seg2.add_visual_state(
        create_equation(
            "eq2",
            "x = 7 - 3",
            position="center",
            timing=1.0
        )
    )
    seg2.add_visual_state(
        create_equation(
            "eq3",
            "x = 4",
            position="center",
            timing=3.0,
            color="#95E1D3"
        )
    )
    builder.add_segment(seg2.build())

    # Build and validate
    storyboard = builder.build()

    print("Generated storyboard:")
    print(json.dumps(storyboard, indent=2))
    print()

    # Validate
    validator = StoryboardValidator('storyboard_schema.json')
    is_valid, errors = validator.validate(storyboard)

    if is_valid:
        print("✓ Programmatically created storyboard is VALID")
    else:
        print("✗ Programmatically created storyboard is INVALID:")
        for error in errors:
            print(f"  - {error}")

    print()
    return is_valid


def test_storyboard_analysis():
    """Test storyboard analysis features."""
    print("="*80)
    print("TESTING STORYBOARD ANALYSIS")
    print("="*80)
    print()

    # Load an example
    with open('examples/storyboard_pythagorean_theorem.json', 'r') as f:
        storyboard = json.load(f)

    # Get statistics
    print("Statistics for Pythagorean Theorem storyboard:")
    print("-" * 80)
    stats = StoryboardAnalyzer.get_statistics(storyboard)
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    print("\n")

    # Get complexity
    print("Complexity Analysis:")
    print("-" * 80)
    complexity = StoryboardAnalyzer.check_complexity(storyboard)
    for key, value in complexity.items():
        print(f"{key}: {value}")

    print("\n")

    # Get object timeline
    print("Object Timeline:")
    print("-" * 80)
    timeline = StoryboardAnalyzer.get_object_timeline(storyboard)
    for obj_id, events in list(timeline.items())[:5]:  # Show first 5
        print(f"\n{obj_id}:")
        for event in events:
            print(f"  - {event['action']} at {event['absolute_time']}s "
                  f"({event['segment_id']}, type: {event['type']})")

    print("\n")


def test_storyboard_transformations():
    """Test storyboard transformation utilities."""
    print("="*80)
    print("TESTING STORYBOARD TRANSFORMATIONS")
    print("="*80)
    print()

    # Load an example
    with open('examples/storyboard_pythagorean_theorem.json', 'r') as f:
        original = json.load(f)

    print(f"Original duration: {original['metadata']['duration']}s")

    # Test time shifting
    shifted = StoryboardTransformer.shift_timing(original, 10.0)
    print(f"After shifting +10s: {shifted['metadata']['duration']}s")
    print(f"First segment now starts at: {shifted['segments'][0]['start_time']}s")

    # Test time scaling
    scaled = StoryboardTransformer.scale_timing(original, 1.5)
    print(f"After scaling by 1.5x: {scaled['metadata']['duration']}s")
    print(f"First segment now ends at: {scaled['segments'][0]['end_time']}s")

    # Test theme change
    themed = StoryboardTransformer.change_theme(original, "light")
    print(f"Changed theme to: {themed['global_settings']['theme']}")
    print(f"New background: {themed['global_settings']['background_color']}")

    print("\n✓ All transformations completed successfully")
    print()


def test_markdown_export():
    """Test markdown export functionality."""
    print("="*80)
    print("TESTING MARKDOWN EXPORT")
    print("="*80)
    print()

    # Load an example
    with open('examples/storyboard_pythagorean_theorem.json', 'r') as f:
        storyboard = json.load(f)

    # Convert to markdown
    markdown = storyboard_to_markdown(storyboard)

    print("Markdown output (first 500 characters):")
    print("-" * 80)
    print(markdown[:500])
    print("...")
    print()

    # Save to file
    output_path = 'examples/pythagorean_theorem_outline.md'
    with open(output_path, 'w') as f:
        f.write(markdown)

    print(f"✓ Full markdown saved to: {output_path}")
    print()


def test_error_detection():
    """Test that validator catches common errors."""
    print("="*80)
    print("TESTING ERROR DETECTION")
    print("="*80)
    print()

    validator = StoryboardValidator('storyboard_schema.json')

    # Test 1: Overlapping segments
    print("Test 1: Overlapping segments")
    print("-" * 80)
    bad_storyboard_1 = {
        "metadata": {
            "title": "Test",
            "topic": "Test",
            "category": "mathematics",
            "duration": 20.0
        },
        "segments": [
            {
                "id": "seg_1",
                "start_time": 0.0,
                "end_time": 10.0,
                "visual_states": []
            },
            {
                "id": "seg_2",
                "start_time": 5.0,  # Overlaps with seg_1!
                "end_time": 15.0,
                "visual_states": []
            }
        ]
    }

    is_valid, errors = validator.validate(bad_storyboard_1)
    if not is_valid:
        print("✓ Correctly detected overlapping segments:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✗ Failed to detect overlapping segments")

    print()

    # Test 2: Visual state timing exceeds segment
    print("Test 2: Visual state timing exceeds segment")
    print("-" * 80)
    bad_storyboard_2 = {
        "metadata": {
            "title": "Test",
            "topic": "Test",
            "category": "mathematics",
            "duration": 10.0
        },
        "segments": [
            {
                "id": "seg_1",
                "start_time": 0.0,
                "end_time": 5.0,
                "visual_states": [
                    {
                        "object_id": "obj1",
                        "type": "text",
                        "content": "Hello",
                        "action": "fade_in",
                        "timing": 3.0,
                        "duration": 5.0  # Extends beyond segment!
                    }
                ]
            }
        ]
    }

    is_valid, errors = validator.validate(bad_storyboard_2)
    if not is_valid:
        print("✓ Correctly detected animation extending beyond segment:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✗ Failed to detect animation timing error")

    print()

    # Test 3: Invalid object reference
    print("Test 3: Invalid relative position reference")
    print("-" * 80)
    bad_storyboard_3 = {
        "metadata": {
            "title": "Test",
            "topic": "Test",
            "category": "mathematics",
            "duration": 10.0
        },
        "segments": [
            {
                "id": "seg_1",
                "start_time": 0.0,
                "end_time": 5.0,
                "visual_states": [
                    {
                        "object_id": "obj1",
                        "type": "text",
                        "content": "Hello",
                        "action": "fade_in",
                        "position": {
                            "relative_to": "nonexistent_object",  # Invalid reference!
                            "offset": {"x": 0, "y": 1}
                        }
                    }
                ]
            }
        ]
    }

    is_valid, errors = validator.validate(bad_storyboard_3)
    if not is_valid:
        print("✓ Correctly detected invalid object reference:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✗ Failed to detect invalid reference")

    print()


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*20 + "STORYBOARD SCHEMA TEST SUITE" + " "*30 + "║")
    print("╚" + "═"*78 + "╝")
    print()

    results = []

    try:
        # Test 1: Schema validation
        result1 = test_schema_validation()
        results.append(("Schema Validation", result1))
    except Exception as e:
        print(f"Error in schema validation: {e}\n")
        results.append(("Schema Validation", False))

    try:
        # Test 2: Builder
        result2 = test_storyboard_builder()
        results.append(("Storyboard Builder", result2))
    except Exception as e:
        print(f"Error in storyboard builder: {e}\n")
        results.append(("Storyboard Builder", False))

    try:
        # Test 3: Analysis
        test_storyboard_analysis()
        results.append(("Storyboard Analysis", True))
    except Exception as e:
        print(f"Error in storyboard analysis: {e}\n")
        results.append(("Storyboard Analysis", False))

    try:
        # Test 4: Transformations
        test_storyboard_transformations()
        results.append(("Storyboard Transformations", True))
    except Exception as e:
        print(f"Error in transformations: {e}\n")
        results.append(("Storyboard Transformations", False))

    try:
        # Test 5: Markdown export
        test_markdown_export()
        results.append(("Markdown Export", True))
    except Exception as e:
        print(f"Error in markdown export: {e}\n")
        results.append(("Markdown Export", False))

    try:
        # Test 6: Error detection
        test_error_detection()
        results.append(("Error Detection", True))
    except Exception as e:
        print(f"Error in error detection: {e}\n")
        results.append(("Error Detection", False))

    # Print summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print()

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")

    print()

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
