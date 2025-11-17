"""
Storyboard Utilities

Helper functions for creating, manipulating, and converting storyboards.
"""

import json
from typing import Dict, List, Any, Optional, Union
from copy import deepcopy


class StoryboardBuilder:
    """Builder class for creating storyboards programmatically."""

    def __init__(self, title: str, topic: str, category: str):
        """
        Initialize a new storyboard.

        Args:
            title: Video title
            topic: Main topic
            category: Educational category
        """
        self.storyboard = {
            "metadata": {
                "title": title,
                "topic": topic,
                "category": category,
                "difficulty": "intermediate",
                "duration": 0.0,
                "target_audience": "",
                "learning_objectives": [],
                "prerequisites": []
            },
            "global_settings": {
                "background_color": "#0F1419",
                "theme": "dark",
                "font_family": "Arial",
                "voice_settings": {
                    "voice_id": "default",
                    "speed": 1.0,
                    "pitch": 1.0
                },
                "camera": {
                    "width": 1920,
                    "height": 1080,
                    "fps": 60
                }
            },
            "segments": []
        }

    def set_difficulty(self, difficulty: str) -> 'StoryboardBuilder':
        """Set difficulty level."""
        self.storyboard["metadata"]["difficulty"] = difficulty
        return self

    def set_target_audience(self, audience: str) -> 'StoryboardBuilder':
        """Set target audience."""
        self.storyboard["metadata"]["target_audience"] = audience
        return self

    def add_learning_objective(self, objective: str) -> 'StoryboardBuilder':
        """Add a learning objective."""
        self.storyboard["metadata"]["learning_objectives"].append(objective)
        return self

    def add_prerequisite(self, prerequisite: str) -> 'StoryboardBuilder':
        """Add a prerequisite."""
        self.storyboard["metadata"]["prerequisites"].append(prerequisite)
        return self

    def set_theme(self, theme: str, background_color: Optional[str] = None) -> 'StoryboardBuilder':
        """Set visual theme."""
        self.storyboard["global_settings"]["theme"] = theme
        if background_color:
            self.storyboard["global_settings"]["background_color"] = background_color
        return self

    def set_voice(self, voice_id: str, speed: float = 1.0, pitch: float = 1.0) -> 'StoryboardBuilder':
        """Set voice settings."""
        self.storyboard["global_settings"]["voice_settings"] = {
            "voice_id": voice_id,
            "speed": speed,
            "pitch": pitch
        }
        return self

    def add_segment(self, segment: Dict[str, Any]) -> 'StoryboardBuilder':
        """Add a segment to the storyboard."""
        self.storyboard["segments"].append(segment)
        # Update total duration
        if segment.get("end_time", 0) > self.storyboard["metadata"]["duration"]:
            self.storyboard["metadata"]["duration"] = segment["end_time"]
        return self

    def build(self) -> Dict[str, Any]:
        """Return the completed storyboard."""
        return self.storyboard

    def save(self, filepath: str):
        """Save storyboard to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.storyboard, f, indent=2)


class SegmentBuilder:
    """Builder class for creating individual segments."""

    def __init__(self, segment_id: str, start_time: float, end_time: float):
        """
        Initialize a new segment.

        Args:
            segment_id: Unique segment identifier
            start_time: Start time in seconds
            end_time: End time in seconds
        """
        self.segment = {
            "id": segment_id,
            "start_time": start_time,
            "end_time": end_time,
            "visual_states": []
        }

    def add_narration(
        self,
        text: str,
        emphasis_words: Optional[List[str]] = None,
        pause_after: float = 0.0,
        speed: float = 1.0
    ) -> 'SegmentBuilder':
        """Add narration to the segment."""
        self.segment["narration"] = {
            "text": text,
            "emphasis_words": emphasis_words or [],
            "pause_after": pause_after,
            "speed": speed
        }
        return self

    def add_visual_state(self, visual_state: Dict[str, Any]) -> 'SegmentBuilder':
        """Add a visual state to the segment."""
        self.segment["visual_states"].append(visual_state)
        return self

    def add_camera_movement(
        self,
        movement_type: str,
        duration: float,
        target: Optional[Union[str, Dict[str, float]]] = None,
        zoom_level: float = 1.0
    ) -> 'SegmentBuilder':
        """Add camera movement to the segment."""
        self.segment["camera_movement"] = {
            "type": movement_type,
            "duration": duration
        }
        if target:
            self.segment["camera_movement"]["target"] = target
        if movement_type == "zoom":
            self.segment["camera_movement"]["zoom_level"] = zoom_level
        return self

    def add_notes(self, notes: str) -> 'SegmentBuilder':
        """Add internal notes to the segment."""
        self.segment["notes"] = notes
        return self

    def build(self) -> Dict[str, Any]:
        """Return the completed segment."""
        return self.segment


class VisualStateBuilder:
    """Builder class for creating visual states."""

    def __init__(
        self,
        object_id: str,
        object_type: str,
        content: Any,
        action: str
    ):
        """
        Initialize a new visual state.

        Args:
            object_id: Unique object identifier
            object_type: Type of visual element
            content: Content of the element
            action: Animation action
        """
        self.visual_state = {
            "object_id": object_id,
            "type": object_type,
            "content": content,
            "action": action,
            "timing": 0.0,
            "duration": 1.0
        }

    def set_position(self, position: Union[str, Dict[str, float]]) -> 'VisualStateBuilder':
        """Set object position."""
        self.visual_state["position"] = position
        return self

    def set_size(self, size: Union[str, Dict[str, float]]) -> 'VisualStateBuilder':
        """Set object size."""
        self.visual_state["size"] = size
        return self

    def set_timing(self, timing: float, duration: float = 1.0) -> 'VisualStateBuilder':
        """Set animation timing."""
        self.visual_state["timing"] = timing
        self.visual_state["duration"] = duration
        return self

    def set_style(self, **style_props) -> 'VisualStateBuilder':
        """Set style properties."""
        self.visual_state["style"] = style_props
        return self

    def set_action_params(self, **params) -> 'VisualStateBuilder':
        """Set action parameters."""
        self.visual_state["action_params"] = params
        return self

    def set_transition(self, transition_type: str, lag_ratio: float = 0.0) -> 'VisualStateBuilder':
        """Set transition easing."""
        self.visual_state["transition"] = {
            "type": transition_type,
            "lag_ratio": lag_ratio
        }
        return self

    def set_layer(self, layer: int) -> 'VisualStateBuilder':
        """Set rendering layer."""
        self.visual_state["layer"] = layer
        return self

    def set_persist(self, persist: bool) -> 'VisualStateBuilder':
        """Set whether object persists after segment."""
        self.visual_state["persist"] = persist
        return self

    def set_remove_time(self, remove_time: float) -> 'VisualStateBuilder':
        """Set when to remove object."""
        self.visual_state["remove_time"] = remove_time
        return self

    def build(self) -> Dict[str, Any]:
        """Return the completed visual state."""
        return self.visual_state


# Convenience functions for common visual state patterns

def create_text(
    object_id: str,
    text: str,
    position: Union[str, Dict] = "center",
    size: str = "medium",
    color: str = "#FFFFFF",
    action: str = "fade_in",
    timing: float = 0.0,
    duration: float = 1.0
) -> Dict[str, Any]:
    """Create a text visual state."""
    return (
        VisualStateBuilder(object_id, "text", text, action)
        .set_position(position)
        .set_size(size)
        .set_timing(timing, duration)
        .set_style(color=color, font_size=48)
        .build()
    )


def create_equation(
    object_id: str,
    latex: str,
    position: Union[str, Dict] = "center",
    size: str = "large",
    color: str = "#FFFFFF",
    action: str = "write",
    timing: float = 0.0,
    duration: float = 2.0
) -> Dict[str, Any]:
    """Create an equation visual state."""
    return (
        VisualStateBuilder(object_id, "equation", latex, action)
        .set_position(position)
        .set_size(size)
        .set_timing(timing, duration)
        .set_style(color=color, font_size=64)
        .set_transition("smooth", lag_ratio=0.1)
        .build()
    )


def create_shape(
    object_id: str,
    shape_type: str,
    position: Union[str, Dict] = "center",
    fill_color: str = "#FF6B6B",
    stroke_color: str = "#FFFFFF",
    action: str = "create",
    timing: float = 0.0,
    duration: float = 1.5,
    **shape_params
) -> Dict[str, Any]:
    """Create a shape visual state."""
    content = {"shape_type": shape_type}
    content.update(shape_params)

    return (
        VisualStateBuilder(object_id, "shape", content, action)
        .set_position(position)
        .set_timing(timing, duration)
        .set_style(
            fill_color=fill_color,
            stroke_color=stroke_color,
            stroke_width=3
        )
        .build()
    )


def create_vector(
    object_id: str,
    start: Dict[str, float],
    end: Dict[str, float],
    color: str = "#58A6FF",
    action: str = "create",
    timing: float = 0.0,
    duration: float = 1.0
) -> Dict[str, Any]:
    """Create a vector (arrow) visual state."""
    return (
        VisualStateBuilder(
            object_id,
            "vector",
            {"start": start, "end": end},
            action
        )
        .set_timing(timing, duration)
        .set_style(stroke_color=color, stroke_width=4)
        .build()
    )


def create_highlight(
    object_id: str,
    target_position: Union[str, Dict],
    color: str = "#FFD700",
    timing: float = 0.0,
    duration: float = 1.5
) -> Dict[str, Any]:
    """Create a highlight annotation."""
    return (
        VisualStateBuilder(object_id, "annotation", "", "indicate")
        .set_position(target_position)
        .set_timing(timing, duration)
        .set_action_params(color=color)
        .build()
    )


class StoryboardTransformer:
    """Transform and manipulate existing storyboards."""

    @staticmethod
    def shift_timing(storyboard: Dict[str, Any], shift_seconds: float) -> Dict[str, Any]:
        """
        Shift all timing in the storyboard by a number of seconds.

        Args:
            storyboard: Source storyboard
            shift_seconds: Seconds to shift (positive or negative)

        Returns:
            New storyboard with shifted timing
        """
        result = deepcopy(storyboard)

        for segment in result.get("segments", []):
            segment["start_time"] += shift_seconds
            segment["end_time"] += shift_seconds

            for visual_state in segment.get("visual_states", []):
                if "remove_time" in visual_state:
                    visual_state["remove_time"] += shift_seconds

        result["metadata"]["duration"] += shift_seconds

        return result

    @staticmethod
    def scale_timing(storyboard: Dict[str, Any], scale_factor: float) -> Dict[str, Any]:
        """
        Scale all timing in the storyboard by a factor.

        Args:
            storyboard: Source storyboard
            scale_factor: Factor to scale by (e.g., 1.5 = 50% slower)

        Returns:
            New storyboard with scaled timing
        """
        result = deepcopy(storyboard)

        for segment in result.get("segments", []):
            segment["start_time"] *= scale_factor
            segment["end_time"] *= scale_factor

            for visual_state in segment.get("visual_states", []):
                visual_state["timing"] *= scale_factor
                visual_state["duration"] *= scale_factor
                if "remove_time" in visual_state:
                    visual_state["remove_time"] *= scale_factor

        result["metadata"]["duration"] *= scale_factor

        return result

    @staticmethod
    def merge_storyboards(
        storyboard1: Dict[str, Any],
        storyboard2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two storyboards sequentially.

        Args:
            storyboard1: First storyboard
            storyboard2: Second storyboard (will be appended)

        Returns:
            Merged storyboard
        """
        result = deepcopy(storyboard1)
        shift_time = result["metadata"]["duration"]

        # Shift and append segments from second storyboard
        for segment in storyboard2.get("segments", []):
            shifted_segment = deepcopy(segment)
            shifted_segment["start_time"] += shift_time
            shifted_segment["end_time"] += shift_time

            for visual_state in shifted_segment.get("visual_states", []):
                if "remove_time" in visual_state:
                    visual_state["remove_time"] += shift_time

            result["segments"].append(shifted_segment)

        # Update duration
        result["metadata"]["duration"] = shift_time + storyboard2["metadata"]["duration"]

        # Merge learning objectives
        result["metadata"]["learning_objectives"].extend(
            storyboard2["metadata"].get("learning_objectives", [])
        )

        return result

    @staticmethod
    def extract_segment_range(
        storyboard: Dict[str, Any],
        start_segment_id: str,
        end_segment_id: str
    ) -> Dict[str, Any]:
        """
        Extract a range of segments into a new storyboard.

        Args:
            storyboard: Source storyboard
            start_segment_id: ID of first segment to include
            end_segment_id: ID of last segment to include

        Returns:
            New storyboard with only specified segments
        """
        result = deepcopy(storyboard)
        result["segments"] = []

        in_range = False
        min_time = float('inf')

        for segment in storyboard.get("segments", []):
            if segment["id"] == start_segment_id:
                in_range = True
                min_time = segment["start_time"]

            if in_range:
                result["segments"].append(deepcopy(segment))

            if segment["id"] == end_segment_id:
                break

        # Shift timing to start from 0
        if result["segments"]:
            result = StoryboardTransformer.shift_timing(result, -min_time)

        return result

    @staticmethod
    def change_theme(
        storyboard: Dict[str, Any],
        theme: str,
        color_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Change the visual theme of a storyboard.

        Args:
            storyboard: Source storyboard
            theme: New theme name
            color_mapping: Optional mapping of old colors to new colors

        Returns:
            New storyboard with updated theme
        """
        result = deepcopy(storyboard)
        result["global_settings"]["theme"] = theme

        # Apply theme-specific defaults
        theme_colors = {
            "dark": {"background": "#0F1419", "text": "#FFFFFF"},
            "light": {"background": "#FFFFFF", "text": "#000000"},
            "blue": {"background": "#1E3A5F", "text": "#FFFFFF"},
            "green": {"background": "#1B4332", "text": "#FFFFFF"}
        }

        if theme in theme_colors:
            result["global_settings"]["background_color"] = theme_colors[theme]["background"]

        # Apply color mapping if provided
        if color_mapping:
            for segment in result.get("segments", []):
                for visual_state in segment.get("visual_states", []):
                    style = visual_state.get("style", {})
                    for key, value in style.items():
                        if value in color_mapping:
                            style[key] = color_mapping[value]

        return result


def storyboard_to_markdown(storyboard: Dict[str, Any]) -> str:
    """
    Convert a storyboard to a readable markdown format.

    Args:
        storyboard: Storyboard dictionary

    Returns:
        Markdown string
    """
    md = []

    # Header
    md.append(f"# {storyboard['metadata']['title']}\n")
    md.append(f"**Topic:** {storyboard['metadata']['topic']}\n")
    md.append(f"**Category:** {storyboard['metadata']['category']}\n")
    md.append(f"**Duration:** {storyboard['metadata']['duration']}s\n")
    md.append("")

    # Learning objectives
    if storyboard['metadata'].get('learning_objectives'):
        md.append("## Learning Objectives\n")
        for obj in storyboard['metadata']['learning_objectives']:
            md.append(f"- {obj}")
        md.append("")

    # Segments
    md.append("## Timeline\n")
    for segment in storyboard.get('segments', []):
        md.append(f"### {segment['id']} ({segment['start_time']}s - {segment['end_time']}s)\n")

        # Narration
        if 'narration' in segment:
            md.append(f"**Narration:** {segment['narration']['text']}\n")

        # Visual states
        if segment.get('visual_states'):
            md.append("**Visuals:**")
            for vs in segment['visual_states']:
                md.append(
                    f"- `{vs['object_id']}` ({vs['type']}): "
                    f"{vs['action']} at {vs.get('timing', 0)}s"
                )
            md.append("")

    return "\n".join(md)


# Example usage
if __name__ == "__main__":
    # Build a simple storyboard
    builder = StoryboardBuilder(
        title="Introduction to Derivatives",
        topic="Calculus - Derivatives",
        category="mathematics"
    )

    builder.set_difficulty("intermediate")
    builder.set_target_audience("college students")
    builder.add_learning_objective("Understand the concept of a derivative")
    builder.add_prerequisite("Basic algebra")

    # Create a segment
    seg = SegmentBuilder("seg_intro", 0.0, 5.0)
    seg.add_narration(
        "A derivative represents the rate of change of a function.",
        emphasis_words=["derivative", "rate of change"]
    )

    # Add visuals
    title = create_text(
        "title",
        "Introduction to Derivatives",
        position="top",
        size="large",
        color="#58A6FF"
    )
    seg.add_visual_state(title)

    formula = create_equation(
        "derivative_def",
        "f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}",
        timing=2.0
    )
    seg.add_visual_state(formula)

    builder.add_segment(seg.build())

    # Save
    storyboard = builder.build()
    print(json.dumps(storyboard, indent=2))
