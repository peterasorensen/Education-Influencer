"""
Script Generator Module

Generates multi-voice conversational scripts using OpenAI GPT-4o.
Creates engaging educational content with multiple characters (boy and girl voices).
"""

import logging
from typing import Callable, Optional, List, Dict
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generate multi-voice educational scripts using OpenAI GPT-4o."""

    def __init__(self, api_key: str):
        """
        Initialize the script generator.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"

    async def generate_script(
        self,
        topic: str,
        duration_seconds: int = 60,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict[str, str]]:
        """
        Generate a multi-voice educational script.

        Args:
            topic: The educational topic to create a script about
            duration_seconds: Target duration in seconds
            progress_callback: Optional callback for progress updates

        Returns:
            List of script segments with speaker and text
            Format: [{"speaker": "Alex", "text": "..."}, ...]

        Raises:
            Exception: If script generation fails
        """
        try:
            if progress_callback:
                progress_callback("Generating conversational script...", 10)

            system_prompt = """Create an educational script with 2-3 voices for a short animated video.

Keep it simple:
- Use different speakers (give them names)
- Reference visuals when explaining
- Make it engaging for the topic
- Keep segments short (1-2 sentences each)

Return JSON array with:
- "speaker": name of speaker
- "text": what they say"""

            user_prompt = f"""Topic: {topic}
Duration: ~{duration_seconds} seconds
Target segments: {max(8, duration_seconds // 5)}

Create an engaging script."""

            logger.info(f"Generating script for topic: {topic}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            logger.debug(f"Raw response: {content}")

            # Parse JSON response
            parsed = json.loads(content)

            # Handle different possible JSON structures
            if "script" in parsed:
                script = parsed["script"]
            elif "dialogue" in parsed:
                script = parsed["dialogue"]
            elif isinstance(parsed, list):
                script = parsed
            else:
                # Try to find the first list in the parsed object
                for value in parsed.values():
                    if isinstance(value, list):
                        script = value
                        break
                else:
                    raise ValueError("Could not find script array in response")

            # Validate script format
            if not isinstance(script, list) or len(script) == 0:
                raise ValueError("Script must be a non-empty list")

            for segment in script:
                if "speaker" not in segment or "text" not in segment:
                    raise ValueError(
                        "Each script segment must have 'speaker' and 'text' fields"
                    )

            logger.info(f"Generated script with {len(script)} segments")

            if progress_callback:
                progress_callback(
                    f"Script generated with {len(script)} dialogue segments", 20
                )

            return script

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise Exception(f"Invalid JSON response from OpenAI: {e}")
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise Exception(f"Failed to generate script: {e}")

    async def refine_script(
        self,
        original_script: List[Dict[str, str]],
        feedback: str,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> List[Dict[str, str]]:
        """
        Refine an existing script based on feedback.

        Args:
            original_script: The original script to refine
            feedback: Feedback or instructions for refinement
            progress_callback: Optional callback for progress updates

        Returns:
            Refined script in the same format

        Raises:
            Exception: If refinement fails
        """
        try:
            if progress_callback:
                progress_callback("Refining script based on feedback...", 10)

            system_prompt = """You are an expert educational content editor. Refine scripts while maintaining the conversational, engaging style between Alex and Maya."""

            user_prompt = f"""Here is the original script:
{json.dumps(original_script, indent=2)}

Feedback: {feedback}

Please refine the script based on this feedback. Return the refined script in the same JSON format as the original."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            # Extract script from response
            if "script" in parsed:
                refined_script = parsed["script"]
            elif "dialogue" in parsed:
                refined_script = parsed["dialogue"]
            elif isinstance(parsed, list):
                refined_script = parsed
            else:
                for value in parsed.values():
                    if isinstance(value, list):
                        refined_script = value
                        break
                else:
                    raise ValueError("Could not find refined script in response")

            logger.info(f"Refined script with {len(refined_script)} segments")

            if progress_callback:
                progress_callback("Script refinement complete", 20)

            return refined_script

        except Exception as e:
            logger.error(f"Script refinement failed: {e}")
            raise Exception(f"Failed to refine script: {e}")
