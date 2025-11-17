"""
Quick Start Guide for Spatial Tracker

This file demonstrates practical usage patterns for integrating
the spatial tracker into the Manim generation pipeline.
"""

from spatial_tracker import SpatialTracker, ObjectType, Region, BoundingBox
from typing import List, Dict, Any, Tuple, Optional


# ============================================================================
# EXAMPLE 1: Basic Usage
# ============================================================================

def example_basic_tracking():
    """Basic object tracking example."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Object Tracking")
    print("=" * 70)
    
    tracker = SpatialTracker()
    
    # Add a title
    tracker.add_object(
        object_id="intro_title",
        object_type=ObjectType.TITLE,
        content="Introduction to Fractions",
        position=(0, 4.0),  # Top center
        dimensions=(4.0, 0.8),
        start_time=0.0,
        end_time=3.0,
        metadata={"animation": "Write", "color": "YELLOW"}
    )
    
    # Add an equation
    tracker.add_object(
        object_id="main_equation",
        object_type=ObjectType.EQUATION,
        content=r"\frac{1}{2} + \frac{1}{3}",
        position=(0, 1.0),
        dimensions=(3.0, 1.5),
        start_time=3.0,
        end_time=10.0,
        metadata={"latex": True}
    )
    
    # Query active objects
    print("\nActive objects at t=5.0s:")
    for obj in tracker.get_active_objects_at_time(5.0):
        print(f"  - {obj.id}: {obj.content}")
    
    return tracker


# ============================================================================
# EXAMPLE 2: Preventing Overlaps
# ============================================================================

def example_overlap_prevention():
    """Demonstrate overlap detection and prevention."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Overlap Prevention")
    print("=" * 70)
    
    tracker = SpatialTracker()
    
    # Add first object
    tracker.add_object(
        "obj1",
        ObjectType.EQUATION,
        "First equation",
        position=(0, 0),
        dimensions=(3.0, 2.0),
        start_time=0.0,
        end_time=10.0
    )
    
    # Try to place second object - check for overlap first
    desired_position = (0.5, 0.5)
    desired_dims = (2.0, 1.5)
    
    # Create bounding box for desired position
    test_box = BoundingBox(
        x_min=desired_position[0] - desired_dims[0]/2,
        x_max=desired_position[0] + desired_dims[0]/2,
        y_min=desired_position[1] - desired_dims[1]/2,
        y_max=desired_position[1] + desired_dims[1]/2
    )
    
    # Check for overlaps
    overlaps = tracker.check_overlap(test_box, time=5.0)
    
    if overlaps:
        print(f"\nDesired position {desired_position} would overlap!")
        print("Finding alternative position...")
        
        # Find available space
        alt_position = tracker.find_available_space(
            dimensions=desired_dims,
            time=5.0,
            preferred_regions=[Region.CENTER_RIGHT, Region.BOTTOM_CENTER]
        )
        
        if alt_position:
            print(f"Alternative position found: {alt_position}")
            
            tracker.add_object(
                "obj2",
                ObjectType.EQUATION,
                "Second equation",
                position=alt_position,
                dimensions=desired_dims,
                start_time=5.0,
                end_time=15.0
            )
    
    return tracker


# ============================================================================
# EXAMPLE 3: Smart Layout for Multiple Objects
# ============================================================================

def example_smart_layout():
    """Demonstrate intelligent layout suggestions."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Smart Layout")
    print("=" * 70)
    
    tracker = SpatialTracker()
    
    # Define objects to place
    objects_to_place = [
        {
            "id": "title",
            "type": ObjectType.TITLE,
            "content": "Understanding Quadratic Equations",
            "dimensions": (5.0, 0.8)
        },
        {
            "id": "equation",
            "type": ObjectType.EQUATION,
            "content": r"ax^2 + bx + c = 0",
            "dimensions": (3.5, 1.2)
        },
        {
            "id": "graph",
            "type": ObjectType.DIAGRAM,
            "content": "Parabola visualization",
            "dimensions": (3.0, 3.0)
        },
        {
            "id": "label",
            "type": ObjectType.LABEL,
            "content": "Standard Form",
            "dimensions": (2.0, 0.5)
        }
    ]
    
    # Get layout suggestions
    suggestions = tracker.suggest_layout(
        objects_to_place,
        time_range=(0.0, 20.0)
    )
    
    print("\nLayout Suggestions:")
    for suggestion in suggestions:
        print(f"\n  {suggestion['id']} ({suggestion['type'].value}):")
        print(f"    Position: {suggestion['suggested_position']}")
        print(f"    Region: {suggestion['region']}")
        if 'warning' in suggestion:
            print(f"    Warning: {suggestion['warning']}")
        
        # Add to tracker
        if 'warning' not in suggestion:
            tracker.add_object(
                object_id=suggestion['id'],
                object_type=suggestion['type'],
                content=suggestion['content'],
                position=suggestion['suggested_position'],
                dimensions=suggestion['dimensions'],
                start_time=0.0,
                end_time=20.0
            )
    
    return tracker


# ============================================================================
# EXAMPLE 4: Timeline Management
# ============================================================================

def example_timeline_management():
    """Demonstrate timeline and temporal tracking."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Timeline Management")
    print("=" * 70)
    
    tracker = SpatialTracker()
    
    # Add objects at different times
    timeline_objects = [
        ("title", ObjectType.TITLE, "Introduction", (0, 4), (4, 0.8), 0.0, 3.0),
        ("eq1", ObjectType.EQUATION, "Equation 1", (0, 1), (3, 1.5), 3.0, 8.0),
        ("diagram", ObjectType.DIAGRAM, "Visualization", (0, -2), (3, 2), 5.0, 12.0),
        ("eq2", ObjectType.EQUATION, "Equation 2", (0, 1), (3, 1.5), 8.0, 15.0),
        ("label", ObjectType.LABEL, "Summary", (3, 3), (2, 0.5), 12.0, 15.0),
    ]
    
    for obj_id, obj_type, content, pos, dims, start, end in timeline_objects:
        tracker.add_object(obj_id, obj_type, content, pos, dims, start, end)
    
    # Export and display timeline
    timeline = tracker.export_timeline()
    
    print("\nObject Timeline:")
    for obj in timeline:
        print(f"  [{obj['start_time']:5.1f}s - {obj['end_time']:5.1f}s] "
              f"{obj['id']:10s} ({obj['type']:8s}): {obj['content']}")
    
    # Show what's active at key times
    key_times = [2.0, 6.0, 10.0, 14.0]
    print("\nActive Objects at Key Times:")
    for time in key_times:
        active = tracker.get_active_objects_at_time(time)
        print(f"\n  t={time}s: {len(active)} objects")
        for obj in active:
            print(f"    - {obj.id}")
    
    return tracker


# ============================================================================
# EXAMPLE 5: Occupancy Visualization
# ============================================================================

def example_occupancy_grid():
    """Demonstrate occupancy grid usage."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Occupancy Grid")
    print("=" * 70)
    
    tracker = SpatialTracker()
    
    # Add several objects
    tracker.add_object("top_left", ObjectType.TEXT, "TL", (-3, 3), (2, 1.5), 0, 10)
    tracker.add_object("center", ObjectType.EQUATION, "C", (0, 0), (2.5, 2), 0, 10)
    tracker.add_object("bottom_right", ObjectType.DIAGRAM, "BR", (3, -3), (2, 1.5), 0, 10)
    
    # Get occupancy grid
    grid = tracker.get_occupancy_grid(5.0)
    
    print("\nCanvas Occupancy Grid (t=5.0s):")
    print("(Each cell shows number of objects)\n")
    print("     0 1 2 3 4 5 6 7 8")
    print("   ┌─────────────────────┐")
    
    for i, row in enumerate(reversed(grid)):
        row_num = len(grid) - i - 1
        print(f" {row_num} │", " ".join(str(cell) for cell in row), "│")
    
    print("   └─────────────────────┘")
    print("     Bottom → Top")
    
    return tracker


# ============================================================================
# EXAMPLE 6: Integration with Visual Instructions
# ============================================================================

def example_visual_instruction_integration():
    """Example of integrating with visual instruction generation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Visual Instruction Integration")
    print("=" * 70)
    
    tracker = SpatialTracker()
    
    # Simulated visual instructions
    visual_instructions = [
        {
            "id": 0,
            "narration": "Welcome to fractions",
            "visual_type": "title",
            "description": "Show intro title",
            "timestamp": {"start": 0.0, "end": 3.0}
        },
        {
            "id": 1,
            "narration": "Here's one half",
            "visual_type": "equation_with_diagram",
            "description": "Show 1/2 equation with visual representation",
            "timestamp": {"start": 3.0, "end": 7.0}
        },
        {
            "id": 2,
            "narration": "And two thirds",
            "visual_type": "equation_with_diagram",
            "description": "Show 2/3 equation with visual representation",
            "timestamp": {"start": 7.0, "end": 11.0}
        },
    ]
    
    # Process instructions and assign positions
    processed_instructions = []
    
    for instruction in visual_instructions:
        # Determine object type and dimensions
        visual_type = instruction['visual_type']
        
        if 'title' in visual_type:
            obj_type = ObjectType.TITLE
            dims = (4.0, 0.8)
            preferred_regions = [Region.TOP_CENTER]
        elif 'equation' in visual_type:
            obj_type = ObjectType.EQUATION
            dims = (3.0, 2.0)
            preferred_regions = [Region.CENTER, Region.TOP_CENTER]
        else:
            obj_type = ObjectType.DIAGRAM
            dims = (3.0, 2.0)
            preferred_regions = [Region.CENTER, Region.BOTTOM_CENTER]
        
        # Find available space
        position = tracker.find_available_space(
            dimensions=dims,
            time=instruction['timestamp']['start'],
            preferred_regions=preferred_regions
        )
        
        if position:
            # Add to tracker
            obj = tracker.add_object(
                object_id=f"obj_{instruction['id']}",
                object_type=obj_type,
                content=instruction['narration'],
                position=position,
                dimensions=dims,
                start_time=instruction['timestamp']['start'],
                end_time=instruction['timestamp']['end']
            )
            
            # Add position info to instruction
            instruction['position'] = position
            instruction['dimensions'] = dims
            instruction['region'] = tracker._position_to_region(position).value
            
            print(f"\nInstruction {instruction['id']}:")
            print(f"  Narration: {instruction['narration']}")
            print(f"  Type: {visual_type}")
            print(f"  Position: {position}")
            print(f"  Region: {instruction['region']}")
        else:
            print(f"\nWarning: No space found for instruction {instruction['id']}")
        
        processed_instructions.append(instruction)
    
    return tracker, processed_instructions


# ============================================================================
# EXAMPLE 7: Statistics and Analysis
# ============================================================================

def example_statistics():
    """Demonstrate statistics and analysis features."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Statistics and Analysis")
    print("=" * 70)
    
    tracker = SpatialTracker()
    
    # Add various objects
    tracker.add_object("t1", ObjectType.TITLE, "Title 1", (0, 4), (3, 0.8), 0, 5)
    tracker.add_object("e1", ObjectType.EQUATION, "Eq 1", (0, 1), (2.5, 1.5), 3, 10)
    tracker.add_object("e2", ObjectType.EQUATION, "Eq 2", (-2, -1), (2, 1.2), 7, 12)
    tracker.add_object("d1", ObjectType.DIAGRAM, "Diagram", (2, 0), (2.5, 2), 8, 15)
    tracker.add_object("l1", ObjectType.LABEL, "Label", (3, 3), (1.5, 0.5), 10, 14)
    
    # Get statistics
    stats = tracker.get_statistics()
    
    print("\nTracker Statistics:")
    print(f"  Total Objects: {stats['total_objects']}")
    print(f"  Object Types: {stats['object_types']}")
    print(f"  Time Range: {stats['time_range'][0]:.1f}s to {stats['time_range'][1]:.1f}s")
    print(f"  Average Duration: {stats['average_duration']:.2f}s")
    print(f"  Canvas Utilization: {stats['canvas_utilization_percent']:.2f}%")
    
    # Check coverage by region
    print("\nRegion Coverage:")
    for region in Region:
        objects = tracker.get_objects_in_region(region)
        print(f"  {region.value:15s}: {len(objects)} objects")
    
    return tracker


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("SPATIAL TRACKER - QUICK START EXAMPLES")
    print("=" * 70)
    
    examples = [
        ("Basic Tracking", example_basic_tracking),
        ("Overlap Prevention", example_overlap_prevention),
        ("Smart Layout", example_smart_layout),
        ("Timeline Management", example_timeline_management),
        ("Occupancy Grid", example_occupancy_grid),
        ("Visual Instruction Integration", example_visual_instruction_integration),
        ("Statistics and Analysis", example_statistics),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
    
    print("\n" + "=" * 70)
    print("All examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
