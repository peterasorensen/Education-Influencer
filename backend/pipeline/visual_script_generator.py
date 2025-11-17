"""
Visual Script Generator Module (DEPRECATED - Use StoryboardGenerator)

This module is maintained for backward compatibility.
Please use storyboard_generator.StoryboardGenerator for new code.

Generates Manim-aware visual instructions based on the script and timestamps.
Creates detailed scene descriptions for mathematical animations and visual explanations.
"""

import logging
from typing import Callable, Optional, List, Dict
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)

# Import from new module for backward compatibility
from .storyboard_generator import StoryboardGenerator as _StoryboardGenerator


class VisualScriptGenerator(_StoryboardGenerator):
    """Generate Manim-aware visual instructions for educational content.

    This class now inherits from StoryboardGenerator and maintains the old API
    for backward compatibility.
    """

    def __init__(self, api_key: str):
        """
        Initialize the visual script generator.

        Args:
            api_key: OpenAI API key
        """
        # Initialize parent StoryboardGenerator
        super().__init__(api_key)

    async def generate_visual_instructions(
        self,
        script: List[Dict[str, str]],
        topic: str,
        aligned_timestamps: Optional[List[Dict]] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict]:
        """
        Generate visual instructions for Manim animations.

        This method now delegates to the new generate_storyboard method
        for improved educational quality.

        Args:
            script: List of script segments with speaker and text
            topic: The educational topic
            aligned_timestamps: Optional list of script segments with timing
            progress_callback: Optional callback for progress updates

        Returns:
            List of visual instruction segments (storyboard frames)

        Raises:
            Exception: If visual instruction generation fails
        """
        # Delegate to new storyboard generation method
        return await self.generate_storyboard(
            script=script,
            topic=topic,
            aligned_timestamps=aligned_timestamps,
            progress_callback=progress_callback,
        )

    async def refine_visual_instructions(
        self,
        original_instructions: List[Dict],
        feedback: str,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict]:
        """
        Refine visual instructions based on feedback.

        This method delegates to the parent's refine_storyboard method.

        Args:
            original_instructions: Original visual instructions
            feedback: Feedback for refinement
            progress_callback: Optional callback for progress updates

        Returns:
            Refined visual instructions

        Raises:
            Exception: If refinement fails
        """
        # Delegate to new storyboard refinement method
        return await self.refine_storyboard(
            original_storyboard=original_instructions,
            feedback=feedback,
            progress_callback=progress_callback,
        )
