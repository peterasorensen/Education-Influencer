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
        speaker_names: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, str]]:
        """
        Generate a multi-voice educational script.

        Args:
            topic: The educational topic to create a script about
            duration_seconds: Target duration in seconds
            progress_callback: Optional callback for progress updates
            speaker_names: Optional dict with 'teacher' and 'student' names
                          e.g., {"teacher": "Drake", "student": "Sydney"}
                          Defaults to {"teacher": "Teacher", "student": "Student"}

        Returns:
            List of script segments with speaker and text
            Format: [{"speaker": "Alex", "text": "..."}, ...]

        Raises:
            Exception: If script generation fails
        """
        try:
            if progress_callback:
                progress_callback("Generating conversational script...", 10)

            # Set speaker names
            if speaker_names is None:
                speaker_names = {"teacher": "Teacher", "student": "Student"}

            teacher_name = speaker_names.get("teacher", "Teacher")
            student_name = speaker_names.get("student", "Student")

            system_prompt = f"""You are a world-class educator creating extraordinary learning experiences.

Your mission: Explain concepts in a way that creates genuine "aha!" moments and builds deep, intuitive understanding.

PEDAGOGICAL PRINCIPLES (inspired by Grant Sanderson/3Blue1Brown, Sal Khan, Richard Feynman):

1. START WITH WHY
   - Begin with motivation: "Why does this matter?" "Where do we see this in real life?"
   - Connect to student's existing knowledge and experiences
   - Make the topic feel relevant and exciting

2. BUILD INTUITION BEFORE FORMALISM
   - Start with concrete, relatable examples (actual numbers, real objects)
   - Use powerful analogies that map to student's experience
   - Only introduce abstract notation AFTER intuition is established

3. GRADUAL COMPLEXITY SCALING
   - Begin with the simplest possible case
   - Add ONE layer of complexity at a time
   - Each step should feel natural and inevitable

4. VISUAL THINKING
   - Every concept should connect to something visual/tangible
   - Use phrases like "imagine...", "picture this...", "watch what happens when..."
   - Guide attention: "notice that...", "see how...", "look at..."

5. CONVERSATIONAL & ENGAGING
   - Use a dialogue format between {teacher_name} (enthusiastic explainer) and {student_name} (curious learner)
   - {student_name} asks authentic questions, provides "aha" moments, relates concepts to real life
   - Natural, energetic tone - like an excited friend sharing something cool

6. ANTICIPATE CONFUSION
   - Address common misconceptions directly
   - {student_name} asks clarifying questions at natural points of confusion
   - {teacher_name} validates questions and provides clear distinctions

DIALOGUE CHARACTERS:
- {teacher_name}: Clear, enthusiastic, uses analogies, builds step-by-step
- {student_name}: Curious, asks clarifying questions, provides "aha" moments, relates to real life

OUTPUT FORMAT (JSON):
Return a JSON object with key "dialogue" containing an array of segments:
[
  {{"speaker": "{teacher_name}" or "{student_name}", "text": "..."}},
  ...
]

TIMING:
- Keep segments short (1-2 sentences) for visual pacing
- Natural pauses for Student questions and reactions
- Build to key insights with dramatic reveals"""

            user_prompt = f"""Topic: {topic}
Target Duration: ~{duration_seconds} seconds
Target Segments: {max(10, duration_seconds // 4)} segments

CREATE AN EXTRAORDINARY LEARNING EXPERIENCE:

Structure your dialogue like this:

1. HOOK (Why this matters)
   - {teacher_name}: Start with a fascinating question or real-world connection
   - {student_name}: Express curiosity or share a relatable experience

2. BUILD FROM SIMPLE
   - {teacher_name}: Introduce the SIMPLEST possible example with concrete numbers/objects
   - Use visual language: "Let's draw...", "Imagine...", "Picture this..."

3. DEVELOP INTUITION
   - {teacher_name}: Use powerful analogies and visual metaphors
   - {student_name}: Ask clarifying questions, make connections
   - Build complexity gradually, one concept at a time

4. AHA MOMENT
   - {teacher_name}: Reveal the key insight with enthusiasm
   - {student_name}: Express understanding with specific realization

5. REINFORCE & EXTEND
   - {teacher_name}: Show how the concept applies more broadly
   - {student_name}: Ask about extensions or applications

VISUAL INTEGRATION:
Every line should naturally reference visuals:
- "Watch what happens when we..."
- "Notice how these two..."
- "See this pattern?"
- "Let's transform this into..."
- "Look at how this changes..."

Make learning feel like an exciting discovery journey!"""

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
            logger.info(f"Script response preview (first 500 chars): {content[:500]}")

            # Parse JSON response
            parsed = json.loads(content)

            # Handle different possible JSON structures - try multiple keys
            script = None
            # Prioritize "dialogue" as the new standard, but support legacy keys
            possible_keys = ["dialogue", "script", "segments", "conversation", "lines", "content", "data"]

            if isinstance(parsed, list):
                script = parsed
            elif isinstance(parsed, dict):
                # Try known keys first
                for key in possible_keys:
                    if key in parsed and isinstance(parsed[key], list):
                        script = parsed[key]
                        logger.info(f"Found script under key: {key}")
                        break

                # If still not found, try ANY list value
                if script is None:
                    for key, value in parsed.items():
                        if isinstance(value, list) and len(value) > 0:
                            # Check if it looks like a script (has speaker/text)
                            if isinstance(value[0], dict) and ("speaker" in value[0] or "text" in value[0]):
                                script = value
                                logger.info(f"Found script-like list under key: {key}")
                                break

            if script is None:
                logger.error(f"Failed to find script in response. Keys found: {list(parsed.keys()) if isinstance(parsed, dict) else 'not a dict'}")
                logger.error(f"Full response: {content}")
                raise ValueError(f"Could not find script array in response. Available keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'none'}")

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
