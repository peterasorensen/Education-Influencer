"""
Spatial Tracking System for Manim Objects

Manages object placement and tracks spatial occupancy over time on a 9:8 canvas.
Prevents overlapping objects and provides intelligent layout suggestions.

Canvas Specifications:
- Aspect ratio: 9:8 (width:height)
- Resolution: 1080x960 for high quality
- Coordinate system: Manim center at (0, 0)
- Horizontal range: approximately -5.4 to 5.4
- Vertical range: approximately -4.8 to 4.8
"""

import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ObjectType(Enum):
    """Types of objects that can be tracked."""
    TEXT = "text"
    EQUATION = "equation"
    SHAPE = "shape"
    IMAGE = "image"
    DIAGRAM = "diagram"
    ANIMATION = "animation"
    LABEL = "label"
    TITLE = "title"


class Region(Enum):
    """Predefined regions on the canvas for layout suggestions."""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


@dataclass
class BoundingBox:
    """Represents a rectangular bounding box in Manim coordinates."""
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    def __post_init__(self):
        """Validate bounding box coordinates."""
        if self.x_min >= self.x_max:
            raise ValueError(f"Invalid x coordinates: {self.x_min} >= {self.x_max}")
        if self.y_min >= self.y_max:
            raise ValueError(f"Invalid y coordinates: {self.y_min} >= {self.y_max}")

    @property
    def width(self) -> float:
        """Get the width of the bounding box."""
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        """Get the height of the bounding box."""
        return self.y_max - self.y_min

    @property
    def center(self) -> Tuple[float, float]:
        """Get the center point of the bounding box."""
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)

    @property
    def area(self) -> float:
        """Get the area of the bounding box."""
        return self.width * self.height

    def overlaps(self, other: 'BoundingBox') -> bool:
        """
        Check if this bounding box overlaps with another.

        Args:
            other: Another bounding box

        Returns:
            True if the boxes overlap, False otherwise
        """
        # No overlap if one box is to the left/right of the other
        if self.x_max <= other.x_min or other.x_max <= self.x_min:
            return False

        # No overlap if one box is above/below the other
        if self.y_max <= other.y_min or other.y_max <= self.y_min:
            return False

        return True

    def contains_point(self, x: float, y: float) -> bool:
        """
        Check if a point is inside this bounding box.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if the point is inside, False otherwise
        """
        return (self.x_min <= x <= self.x_max and
                self.y_min <= y <= self.y_max)

    def expand(self, margin: float) -> 'BoundingBox':
        """
        Create a new bounding box expanded by a margin.

        Args:
            margin: Amount to expand in all directions

        Returns:
            New expanded bounding box
        """
        return BoundingBox(
            x_min=self.x_min - margin,
            x_max=self.x_max + margin,
            y_min=self.y_min - margin,
            y_max=self.y_max + margin
        )

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation."""
        return {
            "x_min": self.x_min,
            "x_max": self.x_max,
            "y_min": self.y_min,
            "y_max": self.y_max,
            "width": self.width,
            "height": self.height,
            "center_x": self.center[0],
            "center_y": self.center[1]
        }


@dataclass
class TrackedObject:
    """Represents a tracked object on the canvas."""
    id: str
    object_type: ObjectType
    content: str
    bounding_box: BoundingBox
    start_time: float
    end_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_active_at(self, time: float) -> bool:
        """
        Check if this object is active at a given time.

        Args:
            time: Time in seconds

        Returns:
            True if the object is active at the given time
        """
        return self.start_time <= time < self.end_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "type": self.object_type.value,
            "content": self.content,
            "bounding_box": self.bounding_box.to_dict(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metadata": self.metadata
        }


class SpatialTracker:
    """
    Tracks spatial occupancy of Manim objects on a 9:8 canvas over time.

    Manages object placement, detects overlaps, and provides intelligent
    layout suggestions to prevent spatial conflicts.
    """

    # Canvas dimensions in Manim coordinates (9:8 aspect ratio)
    CANVAS_WIDTH = 10.8  # -5.4 to 5.4
    CANVAS_HEIGHT = 9.6  # -4.8 to 4.8
    CANVAS_X_MIN = -5.4
    CANVAS_X_MAX = 5.4
    CANVAS_Y_MIN = -4.8
    CANVAS_Y_MAX = 4.8

    # Grid resolution for spatial indexing
    GRID_COLS = 9
    GRID_ROWS = 8

    def __init__(self):
        """Initialize the spatial tracker."""
        self.objects: Dict[str, TrackedObject] = {}
        self.grid_cell_width = self.CANVAS_WIDTH / self.GRID_COLS
        self.grid_cell_height = self.CANVAS_HEIGHT / self.GRID_ROWS

        logger.info(
            f"SpatialTracker initialized: "
            f"{self.CANVAS_WIDTH}x{self.CANVAS_HEIGHT} canvas, "
            f"{self.GRID_COLS}x{self.GRID_ROWS} grid"
        )

    def add_object(
        self,
        object_id: str,
        object_type: ObjectType,
        content: str,
        position: Tuple[float, float],
        dimensions: Tuple[float, float],
        start_time: float,
        end_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TrackedObject:
        """
        Add an object to the spatial tracker.

        Args:
            object_id: Unique identifier for the object
            object_type: Type of object (text, equation, shape, etc.)
            content: Content description or text
            position: (x, y) center position in Manim coordinates
            dimensions: (width, height) of the object
            start_time: Time when object appears (seconds)
            end_time: Time when object disappears (seconds)
            metadata: Optional additional metadata

        Returns:
            The created TrackedObject

        Raises:
            ValueError: If object_id already exists or parameters are invalid
        """
        if object_id in self.objects:
            raise ValueError(f"Object with id '{object_id}' already exists")

        if start_time >= end_time:
            raise ValueError(f"Invalid time range: start_time ({start_time}) must be < end_time ({end_time})")

        x, y = position
        width, height = dimensions

        # Create bounding box
        bounding_box = BoundingBox(
            x_min=x - width / 2,
            x_max=x + width / 2,
            y_min=y - height / 2,
            y_max=y + height / 2
        )

        # Validate that object is within canvas bounds
        if not self._is_within_canvas(bounding_box):
            logger.warning(
                f"Object '{object_id}' extends beyond canvas bounds: "
                f"{bounding_box.to_dict()}"
            )

        # Create tracked object
        tracked_obj = TrackedObject(
            id=object_id,
            object_type=object_type,
            content=content,
            bounding_box=bounding_box,
            start_time=start_time,
            end_time=end_time,
            metadata=metadata or {}
        )

        self.objects[object_id] = tracked_obj

        logger.info(
            f"Added object '{object_id}' ({object_type.value}): "
            f"pos={position}, dims={dimensions}, "
            f"time=[{start_time:.2f}, {end_time:.2f}]"
        )

        return tracked_obj

    def remove_object(self, object_id: str) -> bool:
        """
        Remove an object from the tracker.

        Args:
            object_id: ID of the object to remove

        Returns:
            True if object was removed, False if not found
        """
        if object_id in self.objects:
            del self.objects[object_id]
            logger.info(f"Removed object '{object_id}'")
            return True

        logger.warning(f"Object '{object_id}' not found")
        return False

    def check_overlap(
        self,
        bounding_box: BoundingBox,
        time: float,
        exclude_ids: Optional[Set[str]] = None
    ) -> List[TrackedObject]:
        """
        Check if a bounding box overlaps with any active objects at a given time.

        Args:
            bounding_box: The bounding box to check
            time: Time in seconds
            exclude_ids: Optional set of object IDs to exclude from check

        Returns:
            List of overlapping TrackedObjects
        """
        exclude_ids = exclude_ids or set()
        overlapping = []

        for obj_id, obj in self.objects.items():
            if obj_id in exclude_ids:
                continue

            if obj.is_active_at(time) and obj.bounding_box.overlaps(bounding_box):
                overlapping.append(obj)

        return overlapping

    def check_overlap_time_range(
        self,
        bounding_box: BoundingBox,
        start_time: float,
        end_time: float,
        exclude_ids: Optional[Set[str]] = None
    ) -> List[TrackedObject]:
        """
        Check if a bounding box overlaps with any objects during a time range.

        Args:
            bounding_box: The bounding box to check
            start_time: Start of time range (seconds)
            end_time: End of time range (seconds)
            exclude_ids: Optional set of object IDs to exclude from check

        Returns:
            List of overlapping TrackedObjects
        """
        exclude_ids = exclude_ids or set()
        overlapping = []

        for obj_id, obj in self.objects.items():
            if obj_id in exclude_ids:
                continue

            # Check if time ranges overlap
            time_overlap = not (obj.end_time <= start_time or obj.start_time >= end_time)

            if time_overlap and obj.bounding_box.overlaps(bounding_box):
                overlapping.append(obj)

        return overlapping

    def get_active_objects_at_time(self, time: float) -> List[TrackedObject]:
        """
        Get all objects that are active at a specific time.

        Args:
            time: Time in seconds

        Returns:
            List of active TrackedObjects
        """
        return [obj for obj in self.objects.values() if obj.is_active_at(time)]

    def get_objects_in_region(
        self,
        region: Region,
        time: Optional[float] = None
    ) -> List[TrackedObject]:
        """
        Get all objects in a specific region.

        Args:
            region: The region to query
            time: Optional time filter (only return objects active at this time)

        Returns:
            List of TrackedObjects in the region
        """
        region_box = self._get_region_bounding_box(region)

        objects_in_region = []
        for obj in self.objects.values():
            if time is not None and not obj.is_active_at(time):
                continue

            # Check if object's bounding box overlaps with region
            if obj.bounding_box.overlaps(region_box):
                objects_in_region.append(obj)

        return objects_in_region

    def find_available_space(
        self,
        dimensions: Tuple[float, float],
        time: float,
        preferred_regions: Optional[List[Region]] = None,
        margin: float = 0.3
    ) -> Optional[Tuple[float, float]]:
        """
        Find available space for an object of given dimensions at a specific time.

        Args:
            dimensions: (width, height) of the object to place
            time: Time in seconds
            preferred_regions: Optional list of preferred regions to try first
            margin: Minimum margin between objects (default 0.3)

        Returns:
            (x, y) center position if space found, None otherwise
        """
        width, height = dimensions

        # Try preferred regions first
        if preferred_regions:
            for region in preferred_regions:
                position = self._find_space_in_region(
                    region, width, height, time, margin
                )
                if position:
                    logger.info(f"Found space in preferred region {region.value}: {position}")
                    return position

        # Try all regions
        for region in Region:
            position = self._find_space_in_region(
                region, width, height, time, margin
            )
            if position:
                logger.info(f"Found space in region {region.value}: {position}")
                return position

        logger.warning(f"No available space found for dimensions {dimensions} at time {time}")
        return None

    def suggest_layout(
        self,
        objects_to_place: List[Dict[str, Any]],
        time_range: Tuple[float, float]
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal layout for multiple objects.

        Args:
            objects_to_place: List of objects with 'dimensions' and optional 'type'
            time_range: (start_time, end_time) for the objects

        Returns:
            List of objects with added 'suggested_position' and 'region' fields
        """
        start_time, end_time = time_range
        suggestions = []

        # Sort objects by priority (titles first, then larger objects)
        sorted_objects = sorted(
            objects_to_place,
            key=lambda x: (
                0 if x.get('type') == ObjectType.TITLE else 1,
                -x['dimensions'][0] * x['dimensions'][1]  # Sort by area descending
            )
        )

        used_regions = set()

        for obj in sorted_objects:
            width, height = obj['dimensions']
            obj_type = obj.get('type', ObjectType.DIAGRAM)

            # Determine preferred regions based on type
            preferred_regions = self._get_preferred_regions_for_type(
                obj_type, used_regions
            )

            # Find available space
            position = self._find_space_in_region_list(
                preferred_regions, width, height, start_time, margin=0.3
            )

            if position:
                # Determine which region this position is in
                region = self._position_to_region(position)
                used_regions.add(region)

                suggestion = {
                    **obj,
                    'suggested_position': position,
                    'region': region.value
                }
            else:
                # Fallback: suggest scaling down or using center
                suggestion = {
                    **obj,
                    'suggested_position': (0, 0),
                    'region': Region.CENTER.value,
                    'warning': 'No ideal space found, may need to scale down'
                }

            suggestions.append(suggestion)

        return suggestions

    def get_occupancy_grid(self, time: float) -> List[List[int]]:
        """
        Get a grid representation of canvas occupancy at a specific time.

        Args:
            time: Time in seconds

        Returns:
            2D grid (rows x cols) where each cell contains count of objects
        """
        grid = [[0 for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]

        active_objects = self.get_active_objects_at_time(time)

        for obj in active_objects:
            # Determine which grid cells this object occupies
            cells = self._get_grid_cells_for_box(obj.bounding_box)
            for row, col in cells:
                if 0 <= row < self.GRID_ROWS and 0 <= col < self.GRID_COLS:
                    grid[row][col] += 1

        return grid

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about tracked objects.

        Returns:
            Dictionary with various statistics
        """
        if not self.objects:
            return {
                "total_objects": 0,
                "object_types": {},
                "time_range": None,
                "average_duration": 0,
                "canvas_utilization": 0
            }

        # Count objects by type
        type_counts = {}
        for obj in self.objects.values():
            obj_type = obj.object_type.value
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

        # Calculate time range
        min_time = min(obj.start_time for obj in self.objects.values())
        max_time = max(obj.end_time for obj in self.objects.values())

        # Calculate average duration
        total_duration = sum(
            obj.end_time - obj.start_time for obj in self.objects.values()
        )
        avg_duration = total_duration / len(self.objects)

        # Calculate canvas utilization (approximate)
        canvas_area = self.CANVAS_WIDTH * self.CANVAS_HEIGHT
        avg_object_area = sum(
            obj.bounding_box.area for obj in self.objects.values()
        ) / len(self.objects)
        utilization = (avg_object_area / canvas_area) * 100

        return {
            "total_objects": len(self.objects),
            "object_types": type_counts,
            "time_range": (min_time, max_time),
            "average_duration": avg_duration,
            "canvas_utilization_percent": utilization
        }

    def export_timeline(self) -> List[Dict[str, Any]]:
        """
        Export timeline of all objects sorted by start time.

        Returns:
            List of object dictionaries sorted by start_time
        """
        timeline = [obj.to_dict() for obj in self.objects.values()]
        timeline.sort(key=lambda x: x['start_time'])
        return timeline

    def clear(self):
        """Clear all tracked objects."""
        self.objects.clear()
        logger.info("Cleared all tracked objects")

    # Private helper methods

    def _is_within_canvas(self, bounding_box: BoundingBox) -> bool:
        """Check if a bounding box is fully within canvas bounds."""
        return (
            bounding_box.x_min >= self.CANVAS_X_MIN and
            bounding_box.x_max <= self.CANVAS_X_MAX and
            bounding_box.y_min >= self.CANVAS_Y_MIN and
            bounding_box.y_max <= self.CANVAS_Y_MAX
        )

    def _get_region_bounding_box(self, region: Region) -> BoundingBox:
        """Get the bounding box for a region."""
        # Divide canvas into 9 regions (3x3 grid)
        third_width = self.CANVAS_WIDTH / 3
        third_height = self.CANVAS_HEIGHT / 3

        region_map = {
            Region.TOP_LEFT: (0, 1, 2, 3),
            Region.TOP_CENTER: (1, 2, 2, 3),
            Region.TOP_RIGHT: (2, 3, 2, 3),
            Region.CENTER_LEFT: (0, 1, 1, 2),
            Region.CENTER: (1, 2, 1, 2),
            Region.CENTER_RIGHT: (2, 3, 1, 2),
            Region.BOTTOM_LEFT: (0, 1, 0, 1),
            Region.BOTTOM_CENTER: (1, 2, 0, 1),
            Region.BOTTOM_RIGHT: (2, 3, 0, 1),
        }

        x_start, x_end, y_start, y_end = region_map[region]

        return BoundingBox(
            x_min=self.CANVAS_X_MIN + x_start * third_width,
            x_max=self.CANVAS_X_MIN + x_end * third_width,
            y_min=self.CANVAS_Y_MIN + y_start * third_height,
            y_max=self.CANVAS_Y_MIN + y_end * third_height
        )

    def _find_space_in_region(
        self,
        region: Region,
        width: float,
        height: float,
        time: float,
        margin: float
    ) -> Optional[Tuple[float, float]]:
        """Try to find space in a specific region."""
        region_box = self._get_region_bounding_box(region)

        # Check if object fits in region at all
        if width + 2 * margin > region_box.width or height + 2 * margin > region_box.height:
            return None

        # Try center of region first
        center_x, center_y = region_box.center
        test_box = BoundingBox(
            x_min=center_x - width / 2 - margin,
            x_max=center_x + width / 2 + margin,
            y_min=center_y - height / 2 - margin,
            y_max=center_y + height / 2 + margin
        )

        if not self.check_overlap(test_box, time):
            return (center_x, center_y)

        # Try a grid of positions within the region
        steps = 5
        x_step = (region_box.width - width - 2 * margin) / steps
        y_step = (region_box.height - height - 2 * margin) / steps

        for i in range(steps):
            for j in range(steps):
                test_x = region_box.x_min + margin + width / 2 + i * x_step
                test_y = region_box.y_min + margin + height / 2 + j * y_step

                test_box = BoundingBox(
                    x_min=test_x - width / 2 - margin,
                    x_max=test_x + width / 2 + margin,
                    y_min=test_y - height / 2 - margin,
                    y_max=test_y + height / 2 + margin
                )

                if not self.check_overlap(test_box, time):
                    return (test_x, test_y)

        return None

    def _find_space_in_region_list(
        self,
        regions: List[Region],
        width: float,
        height: float,
        time: float,
        margin: float
    ) -> Optional[Tuple[float, float]]:
        """Try to find space in a list of regions."""
        for region in regions:
            position = self._find_space_in_region(region, width, height, time, margin)
            if position:
                return position
        return None

    def _position_to_region(self, position: Tuple[float, float]) -> Region:
        """Determine which region a position is in."""
        x, y = position

        third_width = self.CANVAS_WIDTH / 3
        third_height = self.CANVAS_HEIGHT / 3

        # Determine column
        if x < self.CANVAS_X_MIN + third_width:
            col = 0
        elif x < self.CANVAS_X_MIN + 2 * third_width:
            col = 1
        else:
            col = 2

        # Determine row (note: higher y is top)
        if y < self.CANVAS_Y_MIN + third_height:
            row = 0  # bottom
        elif y < self.CANVAS_Y_MIN + 2 * third_height:
            row = 1  # middle
        else:
            row = 2  # top

        region_matrix = [
            [Region.BOTTOM_LEFT, Region.BOTTOM_CENTER, Region.BOTTOM_RIGHT],
            [Region.CENTER_LEFT, Region.CENTER, Region.CENTER_RIGHT],
            [Region.TOP_LEFT, Region.TOP_CENTER, Region.TOP_RIGHT]
        ]

        return region_matrix[row][col]

    def _get_preferred_regions_for_type(
        self,
        obj_type: ObjectType,
        used_regions: Set[Region]
    ) -> List[Region]:
        """Get preferred regions for an object type, excluding used regions."""
        type_preferences = {
            ObjectType.TITLE: [Region.TOP_CENTER, Region.TOP_LEFT, Region.TOP_RIGHT],
            ObjectType.EQUATION: [Region.CENTER, Region.TOP_CENTER, Region.CENTER_LEFT],
            ObjectType.TEXT: [Region.CENTER_LEFT, Region.CENTER, Region.BOTTOM_LEFT],
            ObjectType.DIAGRAM: [Region.CENTER, Region.CENTER_RIGHT, Region.BOTTOM_CENTER],
            ObjectType.LABEL: [Region.TOP_RIGHT, Region.BOTTOM_RIGHT, Region.CENTER_RIGHT],
        }

        # Default preferences if type not specified
        default_preferences = [
            Region.CENTER, Region.TOP_CENTER, Region.CENTER_LEFT,
            Region.CENTER_RIGHT, Region.BOTTOM_CENTER
        ]

        preferences = type_preferences.get(obj_type, default_preferences)

        # Filter out used regions
        available = [r for r in preferences if r not in used_regions]

        # If all preferred regions are used, use any unused region
        if not available:
            all_regions = list(Region)
            available = [r for r in all_regions if r not in used_regions]

        return available if available else list(Region)

    def _get_grid_cells_for_box(self, box: BoundingBox) -> List[Tuple[int, int]]:
        """Get list of (row, col) grid cells that a bounding box occupies."""
        cells = []

        # Convert bounding box coordinates to grid cells
        col_start = int((box.x_min - self.CANVAS_X_MIN) / self.grid_cell_width)
        col_end = int((box.x_max - self.CANVAS_X_MIN) / self.grid_cell_width)
        row_start = int((box.y_min - self.CANVAS_Y_MIN) / self.grid_cell_height)
        row_end = int((box.y_max - self.CANVAS_Y_MIN) / self.grid_cell_height)

        # Clamp to grid bounds
        col_start = max(0, min(col_start, self.GRID_COLS - 1))
        col_end = max(0, min(col_end, self.GRID_COLS - 1))
        row_start = max(0, min(row_start, self.GRID_ROWS - 1))
        row_end = max(0, min(row_end, self.GRID_ROWS - 1))

        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):
                cells.append((row, col))

        return cells


def create_example_usage():
    """
    Example usage of the SpatialTracker system.

    Demonstrates tracking objects, checking overlaps, and finding available space.
    """
    print("=" * 70)
    print("MANIM SPATIAL TRACKER - Example Usage")
    print("=" * 70)

    # Initialize tracker
    tracker = SpatialTracker()
    print(f"\nCanvas: {tracker.CANVAS_WIDTH} x {tracker.CANVAS_HEIGHT}")
    print(f"X range: [{tracker.CANVAS_X_MIN}, {tracker.CANVAS_X_MAX}]")
    print(f"Y range: [{tracker.CANVAS_Y_MIN}, {tracker.CANVAS_Y_MAX}]")
    print(f"Grid: {tracker.GRID_ROWS} rows x {tracker.GRID_COLS} cols")

    # Example 1: Add a title at the top
    print("\n" + "=" * 70)
    print("Example 1: Adding a title")
    print("=" * 70)

    title = tracker.add_object(
        object_id="title_1",
        object_type=ObjectType.TITLE,
        content="Introduction to Fractions",
        position=(0, 4.0),  # Top center
        dimensions=(4.0, 0.8),
        start_time=0.0,
        end_time=3.0,
        metadata={"color": "YELLOW", "animation": "Write"}
    )
    print(f"Added: {title.to_dict()}")

    # Example 2: Try to add overlapping object (should detect overlap)
    print("\n" + "=" * 70)
    print("Example 2: Checking for overlaps")
    print("=" * 70)

    test_box = BoundingBox(x_min=-1, x_max=1, y_min=3.5, y_max=4.5)
    overlaps = tracker.check_overlap(test_box, time=1.5)
    print(f"Test box: {test_box.to_dict()}")
    print(f"Overlapping objects at t=1.5s: {len(overlaps)}")
    if overlaps:
        for obj in overlaps:
            print(f"  - {obj.id}: {obj.content}")

    # Example 3: Find available space
    print("\n" + "=" * 70)
    print("Example 3: Finding available space")
    print("=" * 70)

    available_pos = tracker.find_available_space(
        dimensions=(3.0, 2.0),
        time=1.5,
        preferred_regions=[Region.CENTER, Region.CENTER_LEFT]
    )
    print(f"Available position for 3.0x2.0 object at t=1.5s: {available_pos}")

    # Example 4: Add equation in center
    print("\n" + "=" * 70)
    print("Example 4: Adding equation in available space")
    print("=" * 70)

    if available_pos:
        equation = tracker.add_object(
            object_id="equation_1",
            object_type=ObjectType.EQUATION,
            content=r"\frac{1}{2} \times \frac{2}{3}",
            position=available_pos,
            dimensions=(3.0, 2.0),
            start_time=3.0,
            end_time=10.0,
            metadata={"latex": True}
        )
        print(f"Added: {equation.id} at position {available_pos}")

    # Example 5: Add multiple objects over time
    print("\n" + "=" * 70)
    print("Example 5: Adding multiple objects")
    print("=" * 70)

    diagram = tracker.add_object(
        object_id="diagram_1",
        object_type=ObjectType.DIAGRAM,
        content="Fraction bars visualization",
        position=(0, -2.0),  # Bottom center
        dimensions=(4.0, 1.5),
        start_time=5.0,
        end_time=15.0
    )

    label = tracker.add_object(
        object_id="label_1",
        object_type=ObjectType.LABEL,
        content="Step 1",
        position=(4.0, 3.0),
        dimensions=(1.5, 0.5),
        start_time=4.0,
        end_time=8.0
    )

    print(f"Added diagram: {diagram.id}")
    print(f"Added label: {label.id}")

    # Example 6: Query active objects at different times
    print("\n" + "=" * 70)
    print("Example 6: Querying active objects at different times")
    print("=" * 70)

    for time in [1.5, 5.0, 10.0]:
        active = tracker.get_active_objects_at_time(time)
        print(f"\nActive objects at t={time}s:")
        for obj in active:
            print(f"  - {obj.id} ({obj.object_type.value}): {obj.content}")

    # Example 7: Get occupancy grid
    print("\n" + "=" * 70)
    print("Example 7: Canvas occupancy grid at t=6.0s")
    print("=" * 70)

    grid = tracker.get_occupancy_grid(6.0)
    print("\nGrid (each cell shows number of objects):")
    print("Top")
    for row in reversed(grid):  # Print from top to bottom
        print(" ".join(str(cell) for cell in row))
    print("Bottom")

    # Example 8: Layout suggestion
    print("\n" + "=" * 70)
    print("Example 8: Layout suggestions for multiple objects")
    print("=" * 70)

    objects_to_place = [
        {"dimensions": (3.0, 0.8), "type": ObjectType.TITLE, "content": "New Title"},
        {"dimensions": (3.5, 2.0), "type": ObjectType.EQUATION, "content": "Main equation"},
        {"dimensions": (2.0, 1.5), "type": ObjectType.DIAGRAM, "content": "Visual aid"},
    ]

    suggestions = tracker.suggest_layout(objects_to_place, time_range=(15.0, 20.0))
    print("\nLayout suggestions:")
    for i, suggestion in enumerate(suggestions):
        print(f"\n  Object {i + 1}: {suggestion.get('content', 'unnamed')}")
        print(f"    Suggested position: {suggestion.get('suggested_position')}")
        print(f"    Region: {suggestion.get('region')}")
        if 'warning' in suggestion:
            print(f"    Warning: {suggestion['warning']}")

    # Example 9: Statistics
    print("\n" + "=" * 70)
    print("Example 9: Tracker statistics")
    print("=" * 70)

    stats = tracker.get_statistics()
    print(f"\nTotal objects tracked: {stats['total_objects']}")
    print(f"Object types: {stats['object_types']}")
    print(f"Time range: {stats['time_range']}")
    print(f"Average duration: {stats['average_duration']:.2f}s")
    print(f"Canvas utilization: {stats['canvas_utilization_percent']:.2f}%")

    # Example 10: Export timeline
    print("\n" + "=" * 70)
    print("Example 10: Export timeline")
    print("=" * 70)

    timeline = tracker.export_timeline()
    print("\nObject timeline (chronological order):")
    for obj in timeline:
        print(f"  [{obj['start_time']:.1f}s - {obj['end_time']:.1f}s] "
              f"{obj['id']}: {obj['content']}")

    print("\n" + "=" * 70)
    print("Example usage complete!")
    print("=" * 70)

    return tracker


if __name__ == "__main__":
    # Run example usage
    create_example_usage()
