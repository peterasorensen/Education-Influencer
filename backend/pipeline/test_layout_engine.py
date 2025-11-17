"""
Test Suite for Layout Engine

Tests spatial tracking, object placement, and Manim code generation.
"""

import unittest
from layout_engine import (
    LayoutEngine,
    SpatialTracker,
    BoundingBox,
    LayoutStrategy,
    ManimCodeTemplate
)


class TestBoundingBox(unittest.TestCase):
    """Test BoundingBox class."""

    def test_bounding_box_properties(self):
        """Test bounding box properties."""
        bbox = BoundingBox(x=0, y=0, width=2, height=1)

        self.assertEqual(bbox.left, -1.0)
        self.assertEqual(bbox.right, 1.0)
        self.assertEqual(bbox.top, 0.5)
        self.assertEqual(bbox.bottom, -0.5)

    def test_bounding_box_overlap(self):
        """Test overlap detection."""
        bbox1 = BoundingBox(x=0, y=0, width=2, height=2)
        bbox2 = BoundingBox(x=1, y=0, width=2, height=2)
        bbox3 = BoundingBox(x=5, y=0, width=2, height=2)

        # bbox1 and bbox2 overlap
        self.assertTrue(bbox1.overlaps(bbox2))
        self.assertTrue(bbox2.overlaps(bbox1))

        # bbox1 and bbox3 don't overlap
        self.assertFalse(bbox1.overlaps(bbox3))
        self.assertFalse(bbox3.overlaps(bbox1))

    def test_contains_point(self):
        """Test point containment."""
        bbox = BoundingBox(x=0, y=0, width=2, height=2)

        self.assertTrue(bbox.contains_point(0, 0))
        self.assertTrue(bbox.contains_point(0.5, 0.5))
        self.assertFalse(bbox.contains_point(2, 2))
        self.assertFalse(bbox.contains_point(-2, 0))


class TestSpatialTracker(unittest.TestCase):
    """Test SpatialTracker class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tracker = SpatialTracker()

    def test_register_object(self):
        """Test object registration."""
        bbox = BoundingBox(x=0, y=0, width=2, height=1)
        success = self.tracker.register_object("obj1", bbox)

        self.assertTrue(success)
        self.assertEqual(len(self.tracker.occupied_boxes), 1)
        self.assertIn("obj1", self.tracker.object_registry)

    def test_register_overlapping_object(self):
        """Test registering overlapping objects."""
        bbox1 = BoundingBox(x=0, y=0, width=2, height=2)
        bbox2 = BoundingBox(x=0.5, y=0, width=2, height=2)

        self.tracker.register_object("obj1", bbox1)
        success = self.tracker.register_object("obj2", bbox2)

        self.assertFalse(success)
        self.assertEqual(len(self.tracker.occupied_boxes), 1)

    def test_unregister_object(self):
        """Test object unregistration."""
        bbox = BoundingBox(x=0, y=0, width=2, height=1)
        self.tracker.register_object("obj1", bbox)

        success = self.tracker.unregister_object("obj1")

        self.assertTrue(success)
        self.assertEqual(len(self.tracker.occupied_boxes), 0)
        self.assertNotIn("obj1", self.tracker.object_registry)

    def test_find_available_position(self):
        """Test finding available positions."""
        # Center should be available initially
        x, y = self.tracker.find_available_position(
            width=2.0,
            height=1.0,
            strategy=LayoutStrategy.CENTER_FOCUSED
        )

        # Center position
        self.assertAlmostEqual(x, 0.0, places=1)
        self.assertAlmostEqual(y, 0.0, places=1)

        # Register an object at center
        bbox = BoundingBox(x=0, y=0, width=2, height=1)
        self.tracker.register_object("center", bbox)

        # Next position should be different
        x2, y2 = self.tracker.find_available_position(
            width=2.0,
            height=1.0,
            strategy=LayoutStrategy.CENTER_FOCUSED
        )

        # Should not be at center anymore
        self.assertFalse(abs(x2) < 0.1 and abs(y2) < 0.1)

    def test_clear(self):
        """Test clearing all objects."""
        bbox1 = BoundingBox(x=0, y=0, width=2, height=1)
        bbox2 = BoundingBox(x=3, y=0, width=2, height=1)

        self.tracker.register_object("obj1", bbox1)
        self.tracker.register_object("obj2", bbox2)

        self.tracker.clear()

        self.assertEqual(len(self.tracker.occupied_boxes), 0)
        self.assertEqual(len(self.tracker.object_registry), 0)


class TestManimCodeTemplate(unittest.TestCase):
    """Test ManimCodeTemplate class."""

    def test_get_imports(self):
        """Test import generation."""
        imports = ManimCodeTemplate.get_imports()

        self.assertIn("from manim import *", imports)
        self.assertIn("import random", imports)
        self.assertIn("import math", imports)

    def test_get_class_header(self):
        """Test class header generation."""
        header = ManimCodeTemplate.get_class_header()

        self.assertIn("class EducationalScene(Scene):", header)
        self.assertIn("def construct(self):", header)
        self.assertIn("elapsed_time = 0", header)

    def test_create_text(self):
        """Test text creation code."""
        code = ManimCodeTemplate.create_text(
            obj_id="title",
            text="Hello World",
            x=0, y=2,
            color="BLUE",
            font_size=48
        )

        self.assertIn('title = Text("Hello World"', code)
        self.assertIn("font_size=48", code)
        self.assertIn("color=BLUE", code)
        self.assertIn("[0.00, 2.00, 0]", code)

    def test_create_math_tex(self):
        """Test equation creation code."""
        code = ManimCodeTemplate.create_math_tex(
            obj_id="eq1",
            latex=r"\frac{1}{2}",
            x=1, y=-1,
            color="YELLOW"
        )

        self.assertIn('eq1 = MathTex(r"', code)
        self.assertIn("color=YELLOW", code)
        self.assertIn("[1.00, -1.00, 0]", code)

    def test_create_shape(self):
        """Test shape creation code."""
        code = ManimCodeTemplate.create_shape(
            obj_id="rect1",
            shape_type="rectangle",
            x=0, y=0,
            width=3.0,
            height=2.0,
            color="RED"
        )

        self.assertIn("rect1 = Rectangle(width=3.00, height=2.00)", code)
        self.assertIn("set_color(RED)", code)
        self.assertIn("set_fill(RED", code)

    def test_animate_fade_in(self):
        """Test fade in animation code."""
        code = ManimCodeTemplate.animate_fade_in(
            obj_id="obj1",
            duration=1.5,
            start_time=2.0
        )

        self.assertIn("FadeIn(obj1)", code)
        self.assertIn("run_time=1.50", code)
        self.assertIn("2.00 - elapsed_time", code)

    def test_animate_move(self):
        """Test move animation code."""
        code = ManimCodeTemplate.animate_move(
            obj_id="circle",
            target_x=3.0,
            target_y=-2.0,
            duration=2.0,
            start_time=5.0
        )

        self.assertIn("circle.animate.move_to", code)
        self.assertIn("[3.00, -2.00, 0]", code)
        self.assertIn("run_time=2.00", code)


class TestLayoutEngine(unittest.TestCase):
    """Test LayoutEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = LayoutEngine()

    def test_estimate_dimensions_text(self):
        """Test dimension estimation for text."""
        obj_spec = {
            "type": "text",
            "content": "Hello World",
            "properties": {"font_size": 36}
        }

        dims = self.engine._estimate_dimensions(obj_spec)

        self.assertIn("width", dims)
        self.assertIn("height", dims)
        self.assertGreater(dims["width"], 0)
        self.assertGreater(dims["height"], 0)

    def test_estimate_dimensions_shape(self):
        """Test dimension estimation for shapes."""
        obj_spec = {
            "type": "rectangle",
            "properties": {"width": 4.0, "height": 2.5}
        }

        dims = self.engine._estimate_dimensions(obj_spec)

        self.assertEqual(dims["width"], 4.0)
        self.assertEqual(dims["height"], 2.5)

    def test_place_object(self):
        """Test object placement."""
        obj_spec = {
            "id": "test_obj",
            "type": "text",
            "content": "Test",
            "position": {"x": 1.0, "y": 2.0},
            "properties": {}
        }

        x, y = self.engine._place_object(obj_spec)

        self.assertEqual(x, 1.0)
        self.assertEqual(y, 2.0)
        self.assertIn("test_obj", self.engine.placed_objects)

    def test_place_object_auto(self):
        """Test automatic object placement."""
        obj_spec = {
            "id": "auto_obj",
            "type": "text",
            "content": "Auto",
            "position": "auto",
            "layout_strategy": "center_focused",
            "properties": {}
        }

        x, y = self.engine._place_object(obj_spec)

        # Should be placed somewhere (x and y are numeric)
        self.assertIsInstance(x, (int, float))
        self.assertIsInstance(y, (int, float))

    def test_generate_object_code_text(self):
        """Test generating code for text object."""
        obj_info = {
            "id": "title",
            "type": "text",
            "spec": {
                "content": "Test Title",
                "properties": {"color": "BLUE", "font_size": 48}
            },
            "position": {"x": 0, "y": 2},
            "dimensions": {"width": 2.0, "height": 0.5}
        }

        code = self.engine._generate_object_code(obj_info)

        self.assertIn("title = Text(", code)
        self.assertIn("Test Title", code)
        self.assertIn("color=BLUE", code)

    def test_generate_animation_code_fade_in(self):
        """Test generating fade in animation code."""
        anim = {
            "type": "fade_in",
            "target": "obj1",
            "start_time": 1.0,
            "duration": 1.5
        }

        code = self.engine._generate_animation_code(anim)

        self.assertIn("FadeIn(obj1)", code)
        self.assertIn("run_time=1.50", code)

    def test_process_storyboard_simple(self):
        """Test processing a simple storyboard."""
        storyboard = {
            "objects": [
                {
                    "id": "text1",
                    "type": "text",
                    "content": "Hello",
                    "position": {"x": 0, "y": 0},
                    "properties": {}
                }
            ],
            "animations": [
                {
                    "type": "fade_in",
                    "target": "text1",
                    "start_time": 0.0,
                    "duration": 1.0
                }
            ]
        }

        code = self.engine.process_storyboard(storyboard)

        # Check structure
        self.assertIn("from manim import *", code)
        self.assertIn("class EducationalScene(Scene):", code)
        self.assertIn("def construct(self):", code)
        self.assertIn('text1 = Text("Hello"', code)
        self.assertIn("FadeIn(text1)", code)

    def test_get_object_position(self):
        """Test getting object position."""
        obj_spec = {
            "id": "obj1",
            "type": "text",
            "content": "Test",
            "position": {"x": 2.5, "y": -1.0},
            "properties": {}
        }

        self.engine._place_object(obj_spec)
        pos = self.engine.get_object_position("obj1")

        self.assertIsNotNone(pos)
        self.assertEqual(pos[0], 2.5)
        self.assertEqual(pos[1], -1.0)

    def test_get_object_position_not_found(self):
        """Test getting position of non-existent object."""
        pos = self.engine.get_object_position("nonexistent")
        self.assertIsNone(pos)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
