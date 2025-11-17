"""
Unit tests for the Spatial Tracker system.

Run with: python -m pytest pipeline/test_spatial_tracker.py -v
Or directly: python pipeline/test_spatial_tracker.py
"""

import unittest
from spatial_tracker import (
    SpatialTracker,
    ObjectType,
    Region,
    BoundingBox,
    TrackedObject
)


class TestBoundingBox(unittest.TestCase):
    """Test BoundingBox class functionality."""

    def test_bounding_box_creation(self):
        """Test basic bounding box creation."""
        box = BoundingBox(x_min=-1, x_max=1, y_min=-2, y_max=2)
        self.assertEqual(box.width, 2)
        self.assertEqual(box.height, 4)
        self.assertEqual(box.center, (0, 0))
        self.assertEqual(box.area, 8)

    def test_bounding_box_invalid(self):
        """Test that invalid bounding boxes raise errors."""
        with self.assertRaises(ValueError):
            BoundingBox(x_min=1, x_max=-1, y_min=-2, y_max=2)

        with self.assertRaises(ValueError):
            BoundingBox(x_min=-1, x_max=1, y_min=2, y_max=-2)

    def test_overlap_detection(self):
        """Test bounding box overlap detection."""
        box1 = BoundingBox(x_min=0, x_max=2, y_min=0, y_max=2)
        box2 = BoundingBox(x_min=1, x_max=3, y_min=1, y_max=3)
        box3 = BoundingBox(x_min=5, x_max=7, y_min=5, y_max=7)

        self.assertTrue(box1.overlaps(box2))
        self.assertTrue(box2.overlaps(box1))
        self.assertFalse(box1.overlaps(box3))
        self.assertFalse(box3.overlaps(box1))

    def test_contains_point(self):
        """Test point containment."""
        box = BoundingBox(x_min=-1, x_max=1, y_min=-1, y_max=1)

        self.assertTrue(box.contains_point(0, 0))
        self.assertTrue(box.contains_point(-1, -1))
        self.assertTrue(box.contains_point(1, 1))
        self.assertFalse(box.contains_point(2, 0))
        self.assertFalse(box.contains_point(0, 2))

    def test_expand(self):
        """Test bounding box expansion."""
        box = BoundingBox(x_min=-1, x_max=1, y_min=-1, y_max=1)
        expanded = box.expand(0.5)

        self.assertEqual(expanded.width, box.width + 1)
        self.assertEqual(expanded.height, box.height + 1)


class TestSpatialTracker(unittest.TestCase):
    """Test SpatialTracker class functionality."""

    def setUp(self):
        """Set up test tracker."""
        self.tracker = SpatialTracker()

    def tearDown(self):
        """Clean up after each test."""
        self.tracker.clear()

    def test_add_object(self):
        """Test adding objects to tracker."""
        obj = self.tracker.add_object(
            object_id="test_1",
            object_type=ObjectType.TITLE,
            content="Test Title",
            position=(0, 4.0),
            dimensions=(3.0, 0.8),
            start_time=0.0,
            end_time=3.0
        )

        self.assertIsInstance(obj, TrackedObject)
        self.assertEqual(obj.id, "test_1")
        self.assertEqual(obj.object_type, ObjectType.TITLE)
        self.assertEqual(len(self.tracker.objects), 1)

    def test_add_duplicate_id(self):
        """Test that duplicate IDs raise an error."""
        self.tracker.add_object(
            object_id="test_1",
            object_type=ObjectType.TITLE,
            content="Test",
            position=(0, 0),
            dimensions=(1, 1),
            start_time=0.0,
            end_time=1.0
        )

        with self.assertRaises(ValueError):
            self.tracker.add_object(
                object_id="test_1",
                object_type=ObjectType.TEXT,
                content="Test 2",
                position=(0, 0),
                dimensions=(1, 1),
                start_time=0.0,
                end_time=1.0
            )

    def test_invalid_time_range(self):
        """Test that invalid time ranges raise an error."""
        with self.assertRaises(ValueError):
            self.tracker.add_object(
                object_id="test_1",
                object_type=ObjectType.TITLE,
                content="Test",
                position=(0, 0),
                dimensions=(1, 1),
                start_time=5.0,
                end_time=3.0  # Invalid: end before start
            )

    def test_remove_object(self):
        """Test removing objects from tracker."""
        self.tracker.add_object(
            object_id="test_1",
            object_type=ObjectType.TITLE,
            content="Test",
            position=(0, 0),
            dimensions=(1, 1),
            start_time=0.0,
            end_time=1.0
        )

        self.assertEqual(len(self.tracker.objects), 1)
        success = self.tracker.remove_object("test_1")
        self.assertTrue(success)
        self.assertEqual(len(self.tracker.objects), 0)

        # Try to remove non-existent object
        success = self.tracker.remove_object("test_1")
        self.assertFalse(success)

    def test_check_overlap(self):
        """Test overlap detection."""
        self.tracker.add_object(
            object_id="test_1",
            object_type=ObjectType.TITLE,
            content="Test",
            position=(0, 0),
            dimensions=(2, 2),
            start_time=0.0,
            end_time=10.0
        )

        # Test overlapping box
        overlap_box = BoundingBox(x_min=-0.5, x_max=0.5, y_min=-0.5, y_max=0.5)
        overlaps = self.tracker.check_overlap(overlap_box, time=5.0)
        self.assertEqual(len(overlaps), 1)

        # Test non-overlapping box
        no_overlap_box = BoundingBox(x_min=5, x_max=6, y_min=5, y_max=6)
        overlaps = self.tracker.check_overlap(no_overlap_box, time=5.0)
        self.assertEqual(len(overlaps), 0)

        # Test time outside object's lifetime
        overlaps = self.tracker.check_overlap(overlap_box, time=15.0)
        self.assertEqual(len(overlaps), 0)

    def test_check_overlap_time_range(self):
        """Test overlap detection over time range."""
        self.tracker.add_object(
            object_id="test_1",
            object_type=ObjectType.TITLE,
            content="Test",
            position=(0, 0),
            dimensions=(2, 2),
            start_time=5.0,
            end_time=10.0
        )

        overlap_box = BoundingBox(x_min=-0.5, x_max=0.5, y_min=-0.5, y_max=0.5)

        # Test overlapping time range
        overlaps = self.tracker.check_overlap_time_range(
            overlap_box, start_time=7.0, end_time=12.0
        )
        self.assertEqual(len(overlaps), 1)

        # Test non-overlapping time range
        overlaps = self.tracker.check_overlap_time_range(
            overlap_box, start_time=0.0, end_time=3.0
        )
        self.assertEqual(len(overlaps), 0)

    def test_get_active_objects_at_time(self):
        """Test querying active objects at specific time."""
        self.tracker.add_object(
            "obj1", ObjectType.TITLE, "Title", (0, 0), (1, 1), 0.0, 3.0
        )
        self.tracker.add_object(
            "obj2", ObjectType.EQUATION, "Eq", (0, 0), (1, 1), 2.0, 5.0
        )
        self.tracker.add_object(
            "obj3", ObjectType.DIAGRAM, "Diagram", (0, 0), (1, 1), 6.0, 10.0
        )

        # At t=1.0, only obj1 is active
        active = self.tracker.get_active_objects_at_time(1.0)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, "obj1")

        # At t=2.5, both obj1 and obj2 are active
        active = self.tracker.get_active_objects_at_time(2.5)
        self.assertEqual(len(active), 2)

        # At t=7.0, only obj3 is active
        active = self.tracker.get_active_objects_at_time(7.0)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, "obj3")

    def test_find_available_space(self):
        """Test finding available space."""
        # Add object in center
        self.tracker.add_object(
            "center_obj",
            ObjectType.EQUATION,
            "Eq",
            position=(0, 0),
            dimensions=(2, 2),
            start_time=0.0,
            end_time=10.0
        )

        # Try to find space at same time
        position = self.tracker.find_available_space(
            dimensions=(1.5, 1.5),
            time=5.0
        )

        self.assertIsNotNone(position)
        # Position should not be at center (0, 0)
        self.assertNotEqual(position, (0, 0))

    def test_get_objects_in_region(self):
        """Test getting objects in a specific region."""
        # Add object in top center
        self.tracker.add_object(
            "top_obj",
            ObjectType.TITLE,
            "Title",
            position=(0, 3.5),
            dimensions=(2, 0.8),
            start_time=0.0,
            end_time=10.0
        )

        # Add object in bottom center
        self.tracker.add_object(
            "bottom_obj",
            ObjectType.DIAGRAM,
            "Diagram",
            position=(0, -3.0),
            dimensions=(2, 1),
            start_time=0.0,
            end_time=10.0
        )

        # Query top region
        top_objects = self.tracker.get_objects_in_region(Region.TOP_CENTER, time=5.0)
        self.assertEqual(len(top_objects), 1)
        self.assertEqual(top_objects[0].id, "top_obj")

        # Query bottom region
        bottom_objects = self.tracker.get_objects_in_region(Region.BOTTOM_CENTER, time=5.0)
        self.assertEqual(len(bottom_objects), 1)
        self.assertEqual(bottom_objects[0].id, "bottom_obj")

    def test_suggest_layout(self):
        """Test layout suggestion system."""
        objects_to_place = [
            {"dimensions": (3.0, 0.8), "type": ObjectType.TITLE, "content": "Title"},
            {"dimensions": (3.0, 2.0), "type": ObjectType.EQUATION, "content": "Eq"},
            {"dimensions": (2.0, 1.5), "type": ObjectType.DIAGRAM, "content": "Diagram"},
        ]

        suggestions = self.tracker.suggest_layout(
            objects_to_place,
            time_range=(0.0, 10.0)
        )

        self.assertEqual(len(suggestions), 3)

        # Title should be suggested for top region
        title_suggestion = suggestions[0]
        self.assertIn('suggested_position', title_suggestion)
        self.assertIn('region', title_suggestion)
        self.assertIn('top', title_suggestion['region'])

    def test_get_occupancy_grid(self):
        """Test occupancy grid generation."""
        # Add object
        self.tracker.add_object(
            "test_obj",
            ObjectType.EQUATION,
            "Eq",
            position=(0, 0),
            dimensions=(2, 2),
            start_time=0.0,
            end_time=10.0
        )

        grid = self.tracker.get_occupancy_grid(5.0)

        # Grid should be 8 rows x 9 cols
        self.assertEqual(len(grid), self.tracker.GRID_ROWS)
        self.assertEqual(len(grid[0]), self.tracker.GRID_COLS)

        # Some cells should be occupied (value > 0)
        total_occupied = sum(sum(row) for row in grid)
        self.assertGreater(total_occupied, 0)

    def test_get_statistics(self):
        """Test statistics generation."""
        # Empty tracker
        stats = self.tracker.get_statistics()
        self.assertEqual(stats['total_objects'], 0)

        # Add some objects
        self.tracker.add_object(
            "obj1", ObjectType.TITLE, "Title", (0, 0), (1, 1), 0.0, 3.0
        )
        self.tracker.add_object(
            "obj2", ObjectType.EQUATION, "Eq", (0, 0), (1, 1), 3.0, 6.0
        )

        stats = self.tracker.get_statistics()
        self.assertEqual(stats['total_objects'], 2)
        self.assertIn('title', stats['object_types'])
        self.assertIn('equation', stats['object_types'])
        self.assertEqual(stats['time_range'], (0.0, 6.0))
        self.assertEqual(stats['average_duration'], 3.0)

    def test_export_timeline(self):
        """Test timeline export."""
        # Add objects in non-chronological order
        self.tracker.add_object(
            "obj2", ObjectType.EQUATION, "Eq", (0, 0), (1, 1), 5.0, 10.0
        )
        self.tracker.add_object(
            "obj1", ObjectType.TITLE, "Title", (0, 0), (1, 1), 0.0, 3.0
        )
        self.tracker.add_object(
            "obj3", ObjectType.DIAGRAM, "Diagram", (0, 0), (1, 1), 3.0, 7.0
        )

        timeline = self.tracker.export_timeline()

        # Should be sorted by start_time
        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0]['id'], 'obj1')
        self.assertEqual(timeline[1]['id'], 'obj3')
        self.assertEqual(timeline[2]['id'], 'obj2')

    def test_clear(self):
        """Test clearing all objects."""
        self.tracker.add_object(
            "obj1", ObjectType.TITLE, "Title", (0, 0), (1, 1), 0.0, 3.0
        )
        self.tracker.add_object(
            "obj2", ObjectType.EQUATION, "Eq", (0, 0), (1, 1), 3.0, 6.0
        )

        self.assertEqual(len(self.tracker.objects), 2)

        self.tracker.clear()
        self.assertEqual(len(self.tracker.objects), 0)


class TestTrackedObject(unittest.TestCase):
    """Test TrackedObject class functionality."""

    def test_is_active_at(self):
        """Test activity time checking."""
        box = BoundingBox(x_min=-1, x_max=1, y_min=-1, y_max=1)
        obj = TrackedObject(
            id="test",
            object_type=ObjectType.TITLE,
            content="Test",
            bounding_box=box,
            start_time=5.0,
            end_time=10.0
        )

        self.assertFalse(obj.is_active_at(4.9))
        self.assertTrue(obj.is_active_at(5.0))
        self.assertTrue(obj.is_active_at(7.5))
        self.assertTrue(obj.is_active_at(9.9))
        self.assertFalse(obj.is_active_at(10.0))

    def test_to_dict(self):
        """Test dictionary conversion."""
        box = BoundingBox(x_min=-1, x_max=1, y_min=-1, y_max=1)
        obj = TrackedObject(
            id="test",
            object_type=ObjectType.TITLE,
            content="Test",
            bounding_box=box,
            start_time=0.0,
            end_time=10.0,
            metadata={"color": "RED"}
        )

        obj_dict = obj.to_dict()

        self.assertEqual(obj_dict['id'], "test")
        self.assertEqual(obj_dict['type'], "title")
        self.assertEqual(obj_dict['content'], "Test")
        self.assertEqual(obj_dict['start_time'], 0.0)
        self.assertEqual(obj_dict['end_time'], 10.0)
        self.assertEqual(obj_dict['metadata']['color'], "RED")
        self.assertIn('bounding_box', obj_dict)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBoundingBox))
    suite.addTests(loader.loadTestsFromTestCase(TestSpatialTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestTrackedObject))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
