"""
Test script for the new educational content generation prompts.

This script demonstrates the improved quality and pedagogical depth
of the redesigned ScriptGenerator and StoryboardGenerator.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from pipeline import ScriptGenerator, StoryboardGenerator, VisualScriptGenerator

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")


async def test_script_generation():
    """Test the new world-class script generation."""
    print("\n" + "="*80)
    print("TESTING NEW SCRIPT GENERATION")
    print("="*80 + "\n")

    generator = ScriptGenerator(api_key=OPENAI_API_KEY)

    topic = "Why does multiplying fractions work?"
    print(f"Topic: {topic}")
    print(f"Generating script with world-class pedagogy...\n")

    script = await generator.generate_script(
        topic=topic,
        duration_seconds=60
    )

    print(f"✓ Generated {len(script)} dialogue segments\n")
    print("Sample segments:")
    print("-" * 80)

    # Show first 3 segments
    for i, segment in enumerate(script[:3]):
        speaker = segment.get('speaker', 'Unknown')
        text = segment.get('text', '')
        print(f"\n[{i+1}] {speaker}:")
        print(f"    {text}")

    print("\n" + "-" * 80)
    print(f"\nFull script saved to: test_output_script.json")

    with open("test_output_script.json", "w") as f:
        json.dump({"dialogue": script}, f, indent=2)

    return script


async def test_storyboard_generation(script):
    """Test the new comprehensive storyboard generation."""
    print("\n" + "="*80)
    print("TESTING NEW STORYBOARD GENERATION")
    print("="*80 + "\n")

    generator = StoryboardGenerator(api_key=OPENAI_API_KEY)

    topic = "Why does multiplying fractions work?"
    print(f"Topic: {topic}")
    print(f"Generating comprehensive visual storyboard...\n")

    storyboard = await generator.generate_storyboard(
        script=script,
        topic=topic
    )

    print(f"✓ Generated {len(storyboard)} storyboard frames\n")
    print("Sample frame:")
    print("-" * 80)

    # Show first frame in detail
    if storyboard:
        frame = storyboard[0]
        print(f"\nFrame 1:")
        print(f"  Narration: {frame.get('narration', 'N/A')[:100]}...")
        print(f"  Teaching Moment: {frame.get('teaching_moment', 'N/A')}")
        print(f"  Visual Focus: {frame.get('visual_focus', 'N/A')}")
        print(f"  Scene Description: {frame.get('scene_description', 'N/A')[:150]}...")
        print(f"  Objects: {len(frame.get('objects', []))} visual elements")
        print(f"  Animations: {len(frame.get('animations', []))} animations")
        print(f"  Cleanup: {frame.get('cleanup', 'N/A')}")

    print("\n" + "-" * 80)
    print(f"\nFull storyboard saved to: test_output_storyboard.json")

    with open("test_output_storyboard.json", "w") as f:
        json.dump({"storyboard": storyboard}, f, indent=2)

    return storyboard


async def test_backward_compatibility(script):
    """Test that VisualScriptGenerator still works (backward compatibility)."""
    print("\n" + "="*80)
    print("TESTING BACKWARD COMPATIBILITY")
    print("="*80 + "\n")

    generator = VisualScriptGenerator(api_key=OPENAI_API_KEY)

    print("Using old API (VisualScriptGenerator.generate_visual_instructions)...")
    print("This should delegate to new StoryboardGenerator internally.\n")

    instructions = await generator.generate_visual_instructions(
        script=script,
        topic="Why does multiplying fractions work?"
    )

    print(f"✓ Generated {len(instructions)} visual instruction frames")
    print("✓ Backward compatibility confirmed!")

    # Verify it has the new comprehensive structure
    if instructions and len(instructions) > 0:
        frame = instructions[0]
        has_teaching_moment = 'teaching_moment' in frame
        has_visual_focus = 'visual_focus' in frame
        has_objects = 'objects' in frame

        print(f"\nNew storyboard fields present:")
        print(f"  - teaching_moment: {'✓' if has_teaching_moment else '✗'}")
        print(f"  - visual_focus: {'✓' if has_visual_focus else '✗'}")
        print(f"  - objects array: {'✓' if has_objects else '✗'}")

    return instructions


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("TESTING NEW EDUCATIONAL CONTENT GENERATION PROMPTS")
    print("="*80)

    try:
        # Test 1: Script Generation
        script = await test_script_generation()

        # Test 2: Storyboard Generation
        storyboard = await test_storyboard_generation(script)

        # Test 3: Backward Compatibility
        await test_backward_compatibility(script)

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")

        print("Output files:")
        print("  - test_output_script.json (world-class dialogue)")
        print("  - test_output_storyboard.json (comprehensive visual storyboard)")
        print("\nReview these files to see the improved quality!")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
