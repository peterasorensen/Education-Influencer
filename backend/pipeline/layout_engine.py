"""
Layout Engine Module

Converts storyboard JSON to Manim code with spatial awareness and collision detection.
Automatically places objects to prevent overlaps and generates clean, working Manim code.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import math

logger = logging.getLogger(__name__)


class LayoutStrategy(Enum):
    """Layout strategies for object placement."""
    AUTO = "auto"  # Automatically choose best strategy
    GRID = "grid"  # Grid layout
    FLOW = "flow"  # Flow layout (left to right, top to bottom)
    CENTER_FOCUSED = "center_focused"  # Center with surrounding elements
    VERTICAL_STACK = "vertical_stack"  # Stack vertically
    HORIZONTAL_STACK = "horizontal_stack"  # Stack horizontally
    MANUAL = "manual"  # Use exact coordinates


@dataclass
class BoundingBox:
    """Represents a rectangular bounding box in Manim coordinate space."""
    x: float  # Center x coordinate
    y: float  # Center y coordinate
    width: float  # Total width
    height: float  # Total height

    @property
    def left(self) -> float:
        return self.x - self.width / 2

    @property
    def right(self) -> float:
        return self.x + self.width / 2

    @property
    def top(self) -> float:
        return self.y + self.height / 2

    @property
    def bottom(self) -> float:
        return self.y - self.height / 2

    def overlaps(self, other: 'BoundingBox', buffer: float = 0.3) -> bool:
        """Check if this box overlaps with another, with optional buffer."""
        return not (
            self.right + buffer < other.left or
            self.left - buffer > other.right or
            self.top + buffer < other.bottom or
            self.bottom - buffer > other.top
        )

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside this bounding box."""
        return self.left <= x <= self.right and self.bottom <= y <= self.top


class SpatialTracker:
    """Tracks occupied space in the Manim canvas to prevent overlaps."""

    # Canvas bounds for 9:8 aspect ratio (1080x960)
    CANVAS_WIDTH = 10.8  # -5.4 to 5.4
    CANVAS_HEIGHT = 9.6  # -4.8 to 4.8

    def __init__(self, canvas_width: float = CANVAS_WIDTH, canvas_height: float = CANVAS_HEIGHT):
        """
        Initialize spatial tracker.

        Args:
            canvas_width: Canvas width in Manim units (default: 10.8)
            canvas_height: Canvas height in Manim units (default: 9.6)
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.occupied_boxes: List[BoundingBox] = []
        self.object_registry: Dict[str, BoundingBox] = {}

    def register_object(self, obj_id: str, bbox: BoundingBox) -> bool:
        """
        Register an object's bounding box.

        Args:
            obj_id: Unique identifier for the object
            bbox: Bounding box of the object

        Returns:
            True if registration successful, False if overlaps detected
        """
        # Check for overlaps
        for existing_bbox in self.occupied_boxes:
            if bbox.overlaps(existing_bbox):
                logger.warning(f"Object {obj_id} overlaps with existing object")
                return False

        # Register the object
        self.occupied_boxes.append(bbox)
        self.object_registry[obj_id] = bbox
        logger.debug(f"Registered object {obj_id} at ({bbox.x}, {bbox.y})")
        return True

    def unregister_object(self, obj_id: str) -> bool:
        """
        Unregister an object (e.g., when it's removed from scene).

        Args:
            obj_id: Unique identifier for the object

        Returns:
            True if unregistration successful, False if object not found
        """
        if obj_id not in self.object_registry:
            return False

        bbox = self.object_registry[obj_id]
        self.occupied_boxes.remove(bbox)
        del self.object_registry[obj_id]
        logger.debug(f"Unregistered object {obj_id}")
        return True

    def find_available_position(
        self,
        width: float,
        height: float,
        preferred_x: Optional[float] = None,
        preferred_y: Optional[float] = None,
        strategy: LayoutStrategy = LayoutStrategy.CENTER_FOCUSED
    ) -> Tuple[float, float]:
        """
        Find an available position for an object with given dimensions.

        Args:
            width: Object width in Manim units
            height: Object height in Manim units
            preferred_x: Preferred x coordinate (if None, search automatically)
            preferred_y: Preferred y coordinate (if None, search automatically)
            strategy: Layout strategy to use

        Returns:
            Tuple of (x, y) coordinates for the object center
        """
        # If preferred position is given and available, use it
        if preferred_x is not None and preferred_y is not None:
            test_bbox = BoundingBox(preferred_x, preferred_y, width, height)
            if self._is_position_valid(test_bbox):
                return preferred_x, preferred_y

        # Otherwise, search for position based on strategy
        if strategy == LayoutStrategy.CENTER_FOCUSED:
            return self._find_center_focused_position(width, height)
        elif strategy == LayoutStrategy.GRID:
            return self._find_grid_position(width, height)
        elif strategy == LayoutStrategy.FLOW:
            return self._find_flow_position(width, height)
        elif strategy == LayoutStrategy.VERTICAL_STACK:
            return self._find_vertical_stack_position(width, height)
        elif strategy == LayoutStrategy.HORIZONTAL_STACK:
            return self._find_horizontal_stack_position(width, height)
        else:
            return self._find_center_focused_position(width, height)

    def _is_position_valid(self, bbox: BoundingBox) -> bool:
        """Check if a position is valid (in bounds and no overlaps)."""
        # Check canvas bounds
        if (bbox.left < -self.canvas_width / 2 or
            bbox.right > self.canvas_width / 2 or
            bbox.bottom < -self.canvas_height / 2 or
            bbox.top > self.canvas_height / 2):
            return False

        # Check overlaps
        for existing_bbox in self.occupied_boxes:
            if bbox.overlaps(existing_bbox):
                return False

        return True

    def _find_center_focused_position(self, width: float, height: float) -> Tuple[float, float]:
        """Find position using center-focused strategy (spiral outward from center)."""
        # Try center first
        center_bbox = BoundingBox(0, 0, width, height)
        if self._is_position_valid(center_bbox):
            return 0, 0

        # Spiral outward from center
        max_radius = min(self.canvas_width, self.canvas_height) / 2
        step = 0.5

        for radius in [i * step for i in range(1, int(max_radius / step))]:
            # Try positions in a circle around center
            num_positions = max(8, int(radius * 4))
            for i in range(num_positions):
                angle = 2 * math.pi * i / num_positions
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)

                test_bbox = BoundingBox(x, y, width, height)
                if self._is_position_valid(test_bbox):
                    return x, y

        # Fallback: return center (may overlap)
        logger.warning("Could not find non-overlapping position, using center")
        return 0, 0

    def _find_grid_position(self, width: float, height: float) -> Tuple[float, float]:
        """Find position using grid layout."""
        # Define grid
        grid_cols = 3
        grid_rows = 2

        cell_width = self.canvas_width / grid_cols
        cell_height = self.canvas_height / grid_rows

        # Try each grid cell
        for row in range(grid_rows):
            for col in range(grid_cols):
                x = -self.canvas_width / 2 + cell_width * (col + 0.5)
                y = self.canvas_height / 2 - cell_height * (row + 0.5)

                test_bbox = BoundingBox(x, y, width, height)
                if self._is_position_valid(test_bbox):
                    return x, y

        # Fallback to center-focused
        return self._find_center_focused_position(width, height)

    def _find_flow_position(self, width: float, height: float) -> Tuple[float, float]:
        """Find position using flow layout (left to right, top to bottom)."""
        margin = 0.5
        start_x = -self.canvas_width / 2 + margin
        start_y = self.canvas_height / 2 - margin

        x = start_x
        y = start_y

        row_height = height + margin

        while y > -self.canvas_height / 2:
            while x < self.canvas_width / 2 - margin:
                test_bbox = BoundingBox(x + width / 2, y - height / 2, width, height)
                if self._is_position_valid(test_bbox):
                    return x + width / 2, y - height / 2
                x += width + margin

            # Move to next row
            x = start_x
            y -= row_height

        # Fallback to center-focused
        return self._find_center_focused_position(width, height)

    def _find_vertical_stack_position(self, width: float, height: float) -> Tuple[float, float]:
        """Find position by stacking vertically from top."""
        margin = 0.5
        x = 0  # Center horizontally
        y = self.canvas_height / 2 - height / 2 - margin

        while y > -self.canvas_height / 2:
            test_bbox = BoundingBox(x, y, width, height)
            if self._is_position_valid(test_bbox):
                return x, y
            y -= height + margin

        # Fallback to center-focused
        return self._find_center_focused_position(width, height)

    def _find_horizontal_stack_position(self, width: float, height: float) -> Tuple[float, float]:
        """Find position by stacking horizontally from left."""
        margin = 0.5
        x = -self.canvas_width / 2 + width / 2 + margin
        y = 0  # Center vertically

        while x < self.canvas_width / 2:
            test_bbox = BoundingBox(x, y, width, height)
            if self._is_position_valid(test_bbox):
                return x, y
            x += width + margin

        # Fallback to center-focused
        return self._find_center_focused_position(width, height)

    def clear(self):
        """Clear all registered objects."""
        self.occupied_boxes.clear()
        self.object_registry.clear()
        logger.debug("Cleared spatial tracker")


class ManimCodeTemplate:
    """Templates for generating Manim code for different object types."""

    # Canvas specifications for 9:8 aspect ratio
    CANVAS_WIDTH = 10.8  # -5.4 to 5.4
    CANVAS_HEIGHT = 9.6  # -4.8 to 4.8
    SAFE_TEXT_WIDTH = 8.8  # Leave 1 unit margin on each side

    @staticmethod
    def wrap_text(text: str, font_size: int = 36, max_width: float = None) -> str:
        """
        Wrap text to prevent overflow off screen.

        Args:
            text: Text to wrap
            font_size: Font size in points
            max_width: Maximum width in Manim units (default: SAFE_TEXT_WIDTH)

        Returns:
            Text with \\n line breaks inserted at word boundaries
        """
        if max_width is None:
            max_width = ManimCodeTemplate.SAFE_TEXT_WIDTH

        # Target readable line length: 50-70 characters for font_size 36
        # Longer lines become hard to read, shorter lines waste space
        # Scale based on font size (larger fonts = fewer chars, smaller fonts = more chars)

        # Base calculation on font_size 36 = 60 chars per line
        # Adjust proportionally: font_size 48 = 45 chars, font_size 24 = 90 chars
        base_chars_at_36 = 60
        max_chars_per_line = int(base_chars_at_36 * (36 / font_size))

        # Ensure we don't exceed canvas width even with wide characters
        # Worst case: 0.08 units per character (wide font)
        absolute_max = int(max_width / (0.08 * font_size / 36))
        max_chars_per_line = min(max_chars_per_line, absolute_max)

        # If text fits on one line, return as-is
        if len(text) <= max_chars_per_line:
            return text

        # Break text into words
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            # +1 for space before word (except first word)
            space_needed = word_length + (1 if current_line else 0)

            if current_length + space_needed <= max_chars_per_line:
                current_line.append(word)
                current_length += space_needed
            else:
                # Start new line
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length

        # Add last line
        if current_line:
            lines.append(" ".join(current_line))

        # Join with \\n for Manim text
        return "\\n".join(lines)

    @staticmethod
    def estimate_text_dimensions(text: str, font_size: int = 36) -> Tuple[float, float]:
        """
        Estimate text dimensions after wrapping.

        Args:
            text: Text content (may contain \\n)
            font_size: Font size in points

        Returns:
            Tuple of (width, height) in Manim units
        """
        # Split by newlines to count lines
        lines = text.split("\\n")
        num_lines = len(lines)

        # Find longest line
        max_line_length = max(len(line) for line in lines) if lines else 0

        # Estimate dimensions (use same estimate as wrapping)
        char_width = 0.06 * (font_size / 48)
        line_height = 0.7 * (font_size / 48)  # Include line spacing

        width = max_line_length * char_width
        height = num_lines * line_height

        return width, height

    @staticmethod
    def get_imports() -> str:
        """Get required imports for Manim code."""
        return """from manim import *
import random
import math"""

    @staticmethod
    def get_class_header(class_name: str = "EducationalScene") -> str:
        """Get class definition header."""
        return f"""

class {class_name}(Scene):
    def construct(self):
        # Initialize elapsed time tracker
        elapsed_time = 0
"""

    @staticmethod
    def create_text(obj_id: str, text: str, x: float, y: float,
                   color: str = "WHITE", font_size: int = 36) -> str:
        """Generate code to create text object with automatic wrapping."""
        # Wrap text to prevent overflow
        wrapped_text = ManimCodeTemplate.wrap_text(text, font_size)

        return f"""        # Create text: {obj_id}
        {obj_id} = Text("{wrapped_text}", font_size={font_size}, color={color})
        {obj_id}.move_to(np.array([{x:.2f}, {y:.2f}, 0]))
"""

    @staticmethod
    def create_math_tex(obj_id: str, latex: str, x: float, y: float,
                       color: str = "WHITE", font_size: int = 36) -> str:
        """Generate code to create math equation."""
        # Escape backslashes for Python string
        escaped_latex = latex.replace("\\", "\\\\")
        return f"""        # Create equation: {obj_id}
        {obj_id} = MathTex(r"{escaped_latex}", font_size={font_size}, color={color})
        {obj_id}.move_to(np.array([{x:.2f}, {y:.2f}, 0]))
"""

    @staticmethod
    def create_shape(obj_id: str, shape_type: str, x: float, y: float,
                    width: float = 2.0, height: float = 1.0,
                    color: str = "BLUE", fill_opacity: float = 0.5) -> str:
        """Generate code to create shape."""
        shapes_map = {
            "rectangle": f"Rectangle(width={width:.2f}, height={height:.2f})",
            "square": f"Square(side_length={min(width, height):.2f})",
            "circle": f"Circle(radius={min(width, height)/2:.2f})",
            "triangle": f"Triangle()",
            "ellipse": f"Ellipse(width={width:.2f}, height={height:.2f})"
        }

        shape_code = shapes_map.get(shape_type.lower(), f"Rectangle(width={width:.2f}, height={height:.2f})")

        return f"""        # Create shape: {obj_id}
        {obj_id} = {shape_code}
        {obj_id}.move_to(np.array([{x:.2f}, {y:.2f}, 0]))
        {obj_id}.set_color({color})
        {obj_id}.set_fill({color}, opacity={fill_opacity:.2f})
"""

    @staticmethod
    def create_diagram(obj_id: str, diagram_type: str, x: float, y: float,
                      description: str = "") -> str:
        """Generate code to create diagram (compound object)."""
        # For now, create a placeholder group
        return f"""        # Create diagram: {obj_id}
        # {description}
        {obj_id} = VGroup()
        # TODO: Add diagram elements based on type: {diagram_type}
        {obj_id}.move_to(np.array([{x:.2f}, {y:.2f}, 0]))
"""

    @staticmethod
    def animate_fade_in(obj_id: str, duration: float, start_time: float,
                       elapsed_var: str = "elapsed_time") -> str:
        """Generate code for fade in animation."""
        return f"""        # Fade in: {obj_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play(FadeIn({obj_id}), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
"""

    @staticmethod
    def animate_fade_out(obj_id: str, duration: float, start_time: float,
                        elapsed_var: str = "elapsed_time") -> str:
        """Generate code for fade out animation."""
        return f"""        # Fade out: {obj_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play(FadeOut({obj_id}), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
        self.remove({obj_id})
"""

    @staticmethod
    def animate_write(obj_id: str, duration: float, start_time: float,
                     elapsed_var: str = "elapsed_time") -> str:
        """Generate code for write animation (for text/equations)."""
        return f"""        # Write: {obj_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play(Write({obj_id}), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
"""

    @staticmethod
    def animate_create(obj_id: str, duration: float, start_time: float,
                      elapsed_var: str = "elapsed_time") -> str:
        """Generate code for create animation (for shapes)."""
        return f"""        # Create: {obj_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play(Create({obj_id}), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
"""

    @staticmethod
    def animate_transform(from_id: str, to_id: str, duration: float,
                         start_time: float, elapsed_var: str = "elapsed_time") -> str:
        """Generate code for transform animation."""
        return f"""        # Transform: {from_id} -> {to_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play(Transform({from_id}, {to_id}), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
"""

    @staticmethod
    def animate_move(obj_id: str, target_x: float, target_y: float,
                    duration: float, start_time: float,
                    elapsed_var: str = "elapsed_time") -> str:
        """Generate code for move animation."""
        return f"""        # Move: {obj_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play({obj_id}.animate.move_to(np.array([{target_x:.2f}, {target_y:.2f}, 0])), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
"""

    @staticmethod
    def animate_scale(obj_id: str, scale_factor: float, duration: float,
                     start_time: float, elapsed_var: str = "elapsed_time") -> str:
        """Generate code for scale animation."""
        return f"""        # Scale: {obj_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play({obj_id}.animate.scale({scale_factor:.2f}), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
"""

    @staticmethod
    def animate_highlight(obj_id: str, duration: float, start_time: float,
                         elapsed_var: str = "elapsed_time",
                         effect: str = "Indicate") -> str:
        """Generate code for highlight animation."""
        effects_map = {
            "indicate": "Indicate",
            "circumscribe": "Circumscribe",
            "flash": "Flash",
            "wiggle": "Wiggle",
            "focus": "FocusOn"
        }
        effect_func = effects_map.get(effect.lower(), "Indicate")

        return f"""        # Highlight: {obj_id}
        wait_time = {start_time:.2f} - {elapsed_var}
        if wait_time > 0:
            self.wait(wait_time)
            {elapsed_var} = {start_time:.2f}
        self.play({effect_func}({obj_id}), run_time={duration:.2f})
        {elapsed_var} += {duration:.2f}
"""


class LayoutEngine:
    """
    Layout engine that converts storyboard JSON to Manim code with spatial awareness.

    Features:
    - Smart positioning with overlap prevention
    - Multiple layout strategies
    - Automatic object placement
    - Animation code generation
    - Clean, working Manim code output
    """

    def __init__(self, canvas_width: float = 10.8, canvas_height: float = 9.6):
        """
        Initialize layout engine.

        Args:
            canvas_width: Canvas width in Manim units (default: 10.8 for 9:8 aspect ratio)
            canvas_height: Canvas height in Manim units (default: 9.6 for 9:8 aspect ratio)
        """
        self.tracker = SpatialTracker(canvas_width, canvas_height)
        self.template = ManimCodeTemplate()
        self.placed_objects: Dict[str, Dict[str, Any]] = {}
        self.animations: List[Dict[str, Any]] = []
        self.current_time = 0.0

        logger.info(f"Initialized LayoutEngine with canvas {canvas_width}x{canvas_height}")

    def process_storyboard(self, storyboard: Dict[str, Any]) -> str:
        """
        Convert storyboard JSON to Manim code.

        Args:
            storyboard: Storyboard JSON with objects and animations

        Returns:
            Complete Manim Python code as string

        Example storyboard format:
        {
            "objects": [
                {
                    "id": "title",
                    "type": "text",
                    "content": "Hello World",
                    "position": "auto" or {"x": 0, "y": 2},
                    "layout_strategy": "center_focused",
                    "properties": {"color": "BLUE", "font_size": 48}
                }
            ],
            "animations": [
                {
                    "type": "fade_in",
                    "target": "title",
                    "start_time": 0.0,
                    "duration": 1.0
                }
            ]
        }
        """
        try:
            logger.info("Processing storyboard to Manim code")

            # Reset state
            self.tracker.clear()
            self.placed_objects.clear()
            self.animations.clear()
            self.current_time = 0.0

            # Extract objects and animations
            objects = storyboard.get("objects", [])
            animations = storyboard.get("animations", [])

            logger.info(f"Processing {len(objects)} objects and {len(animations)} animations")

            # Phase 1: Place all objects
            for obj_spec in objects:
                self._place_object(obj_spec)

            # Phase 2: Store animations
            self.animations = sorted(animations, key=lambda a: a.get("start_time", 0))

            # Phase 3: Generate Manim code
            code = self._generate_manim_code()

            logger.info(f"Generated Manim code: {len(code)} characters")
            return code

        except Exception as e:
            logger.error(f"Failed to process storyboard: {e}")
            raise

    def _place_object(self, obj_spec: Dict[str, Any]) -> Tuple[float, float]:
        """
        Place an object in the scene, finding position if needed.

        Args:
            obj_spec: Object specification from storyboard

        Returns:
            Tuple of (x, y) coordinates where object was placed
        """
        obj_id = obj_spec.get("id", f"obj_{len(self.placed_objects)}")
        obj_type = obj_spec.get("type", "text")

        # Get dimensions
        dimensions = self._estimate_dimensions(obj_spec)
        width, height = dimensions["width"], dimensions["height"]

        # Get position
        position = obj_spec.get("position", "auto")

        if position == "auto":
            # Automatic positioning
            strategy_name = obj_spec.get("layout_strategy", "center_focused")
            strategy = LayoutStrategy[strategy_name.upper()]

            x, y = self.tracker.find_available_position(
                width, height, strategy=strategy
            )
        elif isinstance(position, dict):
            # Manual positioning
            x = position.get("x", 0)
            y = position.get("y", 0)
        else:
            # Fallback to center
            x, y = 0, 0

        # Register with spatial tracker
        bbox = BoundingBox(x, y, width, height)
        success = self.tracker.register_object(obj_id, bbox)

        if not success:
            logger.warning(f"Object {obj_id} overlaps, but placing anyway")

        # Store placed object info
        self.placed_objects[obj_id] = {
            "id": obj_id,
            "type": obj_type,
            "position": {"x": x, "y": y},
            "dimensions": dimensions,
            "bbox": bbox,
            "spec": obj_spec
        }

        logger.debug(f"Placed {obj_type} '{obj_id}' at ({x:.2f}, {y:.2f})")
        return x, y

    def _estimate_dimensions(self, obj_spec: Dict[str, Any]) -> Dict[str, float]:
        """
        Estimate object dimensions based on type and content.

        Args:
            obj_spec: Object specification

        Returns:
            Dict with "width" and "height" keys
        """
        obj_type = obj_spec.get("type", "text")
        props = obj_spec.get("properties", {})

        # Check if dimensions are explicitly provided
        if "width" in props and "height" in props:
            return {"width": props["width"], "height": props["height"]}

        # Estimate based on type
        if obj_type == "text":
            content = obj_spec.get("content", "")
            font_size = props.get("font_size", 36)
            # Wrap text and calculate dimensions
            wrapped_text = self.template.wrap_text(content, font_size)
            width, height = self.template.estimate_text_dimensions(wrapped_text, font_size)
            return {"width": width, "height": height}

        elif obj_type == "equation":
            latex = obj_spec.get("content", "")
            font_size = props.get("font_size", 36)
            # LaTeX typically wider than text
            char_width = 0.08 * (font_size / 36)
            width = len(latex) * char_width
            height = 0.6 * (font_size / 36)
            return {"width": width, "height": height}

        elif obj_type in ["rectangle", "square", "circle", "triangle", "ellipse"]:
            width = props.get("width", 2.0)
            height = props.get("height", 1.0)
            return {"width": width, "height": height}

        elif obj_type == "diagram":
            # Diagrams are typically larger
            width = props.get("width", 4.0)
            height = props.get("height", 3.0)
            return {"width": width, "height": height}

        else:
            # Default size
            return {"width": 2.0, "height": 1.0}

    def _generate_manim_code(self) -> str:
        """
        Generate complete Manim Python code from placed objects and animations.

        Returns:
            Complete Manim code as string
        """
        code_parts = []

        # Add imports
        code_parts.append(self.template.get_imports())

        # Add class header
        code_parts.append(self.template.get_class_header())

        # Create all objects
        code_parts.append("        # Create all objects")
        for obj_id, obj_info in self.placed_objects.items():
            obj_code = self._generate_object_code(obj_info)
            code_parts.append(obj_code)

        code_parts.append("\n        # Animations")

        # Add animations in chronological order
        for anim in self.animations:
            anim_code = self._generate_animation_code(anim)
            code_parts.append(anim_code)

        # Join all parts
        return "\n".join(code_parts)

    def _generate_object_code(self, obj_info: Dict[str, Any]) -> str:
        """
        Generate Manim code to create an object.

        Args:
            obj_info: Placed object information

        Returns:
            Manim code to create the object
        """
        obj_id = obj_info["id"]
        obj_type = obj_info["type"]
        spec = obj_info["spec"]
        pos = obj_info["position"]
        props = spec.get("properties", {})

        x, y = pos["x"], pos["y"]

        if obj_type == "text":
            return self.template.create_text(
                obj_id,
                spec.get("content", ""),
                x, y,
                color=props.get("color", "WHITE"),
                font_size=props.get("font_size", 36)
            )

        elif obj_type == "equation":
            return self.template.create_math_tex(
                obj_id,
                spec.get("content", ""),
                x, y,
                color=props.get("color", "WHITE"),
                font_size=props.get("font_size", 36)
            )

        elif obj_type in ["rectangle", "square", "circle", "triangle", "ellipse"]:
            dims = obj_info["dimensions"]
            return self.template.create_shape(
                obj_id,
                obj_type,
                x, y,
                width=dims["width"],
                height=dims["height"],
                color=props.get("color", "BLUE"),
                fill_opacity=props.get("fill_opacity", 0.5)
            )

        elif obj_type == "diagram":
            return self.template.create_diagram(
                obj_id,
                spec.get("diagram_type", "custom"),
                x, y,
                description=spec.get("description", "")
            )

        else:
            # Fallback: create as text
            return self.template.create_text(
                obj_id,
                str(spec.get("content", obj_id)),
                x, y
            )

    def _generate_animation_code(self, anim: Dict[str, Any]) -> str:
        """
        Generate Manim code for an animation.

        Args:
            anim: Animation specification

        Returns:
            Manim code for the animation
        """
        anim_type = anim.get("type", "fade_in")
        target = anim.get("target", "")
        start_time = anim.get("start_time", 0.0)
        duration = anim.get("duration", 1.0)

        if anim_type == "fade_in":
            return self.template.animate_fade_in(target, duration, start_time)

        elif anim_type == "fade_out":
            # Unregister object after fade out
            if target in self.placed_objects:
                self.tracker.unregister_object(target)
            return self.template.animate_fade_out(target, duration, start_time)

        elif anim_type == "write":
            return self.template.animate_write(target, duration, start_time)

        elif anim_type == "create":
            return self.template.animate_create(target, duration, start_time)

        elif anim_type == "transform":
            from_obj = anim.get("from", "")
            to_obj = anim.get("to", "")
            return self.template.animate_transform(from_obj, to_obj, duration, start_time)

        elif anim_type == "move":
            target_pos = anim.get("target_position", {"x": 0, "y": 0})
            return self.template.animate_move(
                target,
                target_pos["x"],
                target_pos["y"],
                duration,
                start_time
            )

        elif anim_type == "scale":
            scale_factor = anim.get("scale_factor", 1.0)
            return self.template.animate_scale(target, scale_factor, duration, start_time)

        elif anim_type == "highlight":
            effect = anim.get("effect", "indicate")
            return self.template.animate_highlight(target, duration, start_time, effect=effect)

        else:
            # Unknown animation type, return comment
            return f"        # Unknown animation type: {anim_type} for {target}\n"

    def get_object_position(self, obj_id: str) -> Optional[Tuple[float, float]]:
        """
        Get the position of a placed object.

        Args:
            obj_id: Object identifier

        Returns:
            Tuple of (x, y) or None if object not found
        """
        if obj_id in self.placed_objects:
            pos = self.placed_objects[obj_id]["position"]
            return pos["x"], pos["y"]
        return None

    def get_available_space(self) -> List[BoundingBox]:
        """
        Get list of available (unoccupied) spaces in the canvas.

        Returns:
            List of BoundingBox objects representing available space
        """
        # This is a simplified implementation
        # Could be enhanced with more sophisticated space partitioning
        available = []

        # Sample grid of potential positions
        for x in range(-6, 7, 2):
            for y in range(-3, 4, 2):
                test_box = BoundingBox(x, y, 1.0, 1.0)
                is_free = True
                for occupied in self.tracker.occupied_boxes:
                    if test_box.overlaps(occupied):
                        is_free = False
                        break
                if is_free:
                    available.append(test_box)

        return available
