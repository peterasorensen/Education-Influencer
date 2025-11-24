"""
Visual Context System

Tracks cumulative visual state across scenes to enable progressive diagram building
and visual continuity in educational videos. Each scene is aware of all previous
visual elements and can build upon them.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class VisualElementType(str, Enum):
    """Types of visual elements that can appear in scenes."""
    DIAGRAM = "diagram"
    EQUATION = "equation"
    CHART = "chart"
    ANIMATION = "animation"
    TEXT_OVERLAY = "text_overlay"
    CHARACTER = "character"
    BACKGROUND = "background"


@dataclass
class VisualElement:
    """Represents a visual element that appears in a scene."""

    element_id: str
    element_type: VisualElementType
    description: str
    introduced_in_scene: int
    still_visible: bool = True
    position: Optional[str] = None  # "center", "left", "right", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "description": self.description,
            "introduced_in_scene": self.introduced_in_scene,
            "still_visible": self.still_visible,
            "position": self.position,
            "metadata": self.metadata
        }


@dataclass
class SceneVisualState:
    """Visual state for a specific scene."""

    scene_number: int
    elements_introduced: List[VisualElement] = field(default_factory=list)
    elements_modified: List[str] = field(default_factory=list)  # Element IDs
    elements_removed: List[str] = field(default_factory=list)  # Element IDs
    teaching_focus: str = ""
    visual_theme: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "scene_number": self.scene_number,
            "elements_introduced": [e.to_dict() for e in self.elements_introduced],
            "elements_modified": self.elements_modified,
            "elements_removed": self.elements_removed,
            "teaching_focus": self.teaching_focus,
            "visual_theme": self.visual_theme
        }


class VisualContext:
    """
    Maintains cumulative visual context across all scenes.

    This enables:
    - Progressive diagram building (each scene builds on previous)
    - Visual callbacks to earlier explanations
    - Consistent visual language throughout video
    - Awareness of what's already on screen
    """

    def __init__(self, topic: str):
        """Initialize visual context."""
        self.topic = topic
        self.scenes: List[SceneVisualState] = []
        self.all_elements: Dict[str, VisualElement] = {}
        self.current_scene_number = 0
        self.visual_themes: List[str] = []

    def add_scene(self, scene_state: SceneVisualState):
        """Add a new scene's visual state."""
        self.scenes.append(scene_state)
        self.current_scene_number += 1

        # Track new elements
        for element in scene_state.elements_introduced:
            self.all_elements[element.element_id] = element

        # Update modified elements
        for element_id in scene_state.elements_modified:
            if element_id in self.all_elements:
                # Element was modified - could update metadata here
                pass

        # Remove elements
        for element_id in scene_state.elements_removed:
            if element_id in self.all_elements:
                self.all_elements[element_id].still_visible = False

    def get_currently_visible_elements(self) -> List[VisualElement]:
        """Get all visual elements currently on screen."""
        return [e for e in self.all_elements.values() if e.still_visible]

    def get_scene_history(self, current_scene: int) -> List[SceneVisualState]:
        """Get all scenes up to (but not including) current scene."""
        return self.scenes[:current_scene]

    def get_visual_summary(self, up_to_scene: Optional[int] = None) -> str:
        """
        Get a summary of visual state for prompt injection.

        Args:
            up_to_scene: Only include scenes up to this number (for progressive generation)

        Returns:
            String summary of visual context
        """
        scenes_to_include = self.scenes[:up_to_scene] if up_to_scene else self.scenes

        if not scenes_to_include:
            return "No previous visual elements. This is the first scene."

        summary = "=== VISUAL CONTEXT (Previous Scenes) ===\n\n"

        # Summarize each previous scene
        for scene in scenes_to_include:
            summary += f"Scene {scene.scene_number}:\n"
            summary += f"  Teaching Focus: {scene.teaching_focus}\n"

            if scene.elements_introduced:
                summary += "  Introduced:\n"
                for elem in scene.elements_introduced:
                    summary += f"    - {elem.element_type}: {elem.description}\n"

            if scene.elements_modified:
                summary += f"  Modified: {', '.join(scene.elements_modified)}\n"

            if scene.elements_removed:
                summary += f"  Removed: {', '.join(scene.elements_removed)}\n"

            summary += "\n"

        # Current visual state
        visible = self.get_currently_visible_elements()
        if visible:
            summary += "Currently Visible Elements:\n"
            for elem in visible:
                summary += f"  - {elem.element_type} ({elem.element_id}): {elem.description}\n"
                if elem.position:
                    summary += f"    Position: {elem.position}\n"

        summary += "\n=== INSTRUCTIONS FOR NEXT SCENE ===\n"
        summary += "- Build upon existing visual elements when appropriate\n"
        summary += "- Maintain visual continuity with previous scenes\n"
        summary += "- Reference earlier diagrams/concepts when relevant\n"
        summary += "- Create progressive complexity (simple → complex)\n"
        summary += "- Reuse and extend diagrams rather than creating new ones\n"

        return summary

    def suggest_next_visual_progression(self, next_teaching_focus: str) -> str:
        """
        Suggest how to visually progress to the next concept.

        Args:
            next_teaching_focus: What the next scene will teach

        Returns:
            Suggestions for visual progression
        """
        visible = self.get_currently_visible_elements()

        if not visible:
            return f"Start fresh with visual representation of: {next_teaching_focus}"

        suggestions = f"Next teaching focus: {next_teaching_focus}\n\n"
        suggestions += "Visual Progression Options:\n"

        # Find relevant existing elements to build upon
        diagrams = [e for e in visible if e.element_type == VisualElementType.DIAGRAM]
        equations = [e for e in visible if e.element_type == VisualElementType.EQUATION]

        if diagrams:
            suggestions += f"- Extend existing diagram: {diagrams[0].description}\n"
            suggestions += "- Animate additions to current diagram\n"

        if equations:
            suggestions += f"- Build upon equation: {equations[0].description}\n"
            suggestions += "- Show mathematical derivation step\n"

        suggestions += "- Connect new concept to previously shown visuals\n"
        suggestions += "- Use visual callback to earlier scene\n"

        return suggestions

    def to_dict(self) -> Dict[str, Any]:
        """Convert entire context to dictionary for serialization."""
        return {
            "topic": self.topic,
            "current_scene_number": self.current_scene_number,
            "scenes": [s.to_dict() for s in self.scenes],
            "all_elements": {k: v.to_dict() for k, v in self.all_elements.items()},
            "visual_themes": self.visual_themes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualContext":
        """Reconstruct VisualContext from dictionary."""
        context = cls(topic=data["topic"])
        context.current_scene_number = data["current_scene_number"]
        context.visual_themes = data.get("visual_themes", [])

        # Reconstruct elements
        for elem_id, elem_data in data.get("all_elements", {}).items():
            element = VisualElement(
                element_id=elem_data["element_id"],
                element_type=VisualElementType(elem_data["element_type"]),
                description=elem_data["description"],
                introduced_in_scene=elem_data["introduced_in_scene"],
                still_visible=elem_data["still_visible"],
                position=elem_data.get("position"),
                metadata=elem_data.get("metadata", {})
            )
            context.all_elements[elem_id] = element

        # Reconstruct scenes
        for scene_data in data.get("scenes", []):
            scene = SceneVisualState(
                scene_number=scene_data["scene_number"],
                teaching_focus=scene_data["teaching_focus"],
                visual_theme=scene_data.get("visual_theme")
            )
            # Reconstruct introduced elements
            for elem_data in scene_data.get("elements_introduced", []):
                element = VisualElement(
                    element_id=elem_data["element_id"],
                    element_type=VisualElementType(elem_data["element_type"]),
                    description=elem_data["description"],
                    introduced_in_scene=elem_data["introduced_in_scene"],
                    still_visible=elem_data["still_visible"],
                    position=elem_data.get("position"),
                    metadata=elem_data.get("metadata", {})
                )
                scene.elements_introduced.append(element)

            scene.elements_modified = scene_data.get("elements_modified", [])
            scene.elements_removed = scene_data.get("elements_removed", [])
            context.scenes.append(scene)

        return context
