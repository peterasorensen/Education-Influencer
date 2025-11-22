"""
Script Generator Module

Generates multi-voice conversational scripts using OpenAI GPT-4o.
Creates engaging educational content with multiple characters (boy and girl voices).
"""

import logging
from typing import Callable, Optional, List, Dict, Any
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """Generate multi-voice educational scripts using OpenAI GPT-4o."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize the script generator.

        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_script(
        self,
        topic: str,
        duration_seconds: int = 60,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        speaker_names: Optional[Dict[str, str]] = None,
        refined_context: Optional[Dict[str, Any]] = None,
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
            refined_context: Optional enhanced context from follow-up questions
                            Contains: audience, complexity_level, focus_areas, teaching_style

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

            # If refined context provided, enhance prompts
            if refined_context:
                enhancements = []
                if audience := refined_context.get("audience"):
                    enhancements.append(f"\nAUDIENCE: {audience}. Adjust language and examples accordingly.")
                if complexity := refined_context.get("complexity_level"):
                    levels = {
                        1: "simple analogies, no jargon",
                        2: "basic terminology",
                        3: "balanced",
                        4: "technical details",
                        5: "expert-level"
                    }
                    complexity_desc = levels.get(complexity, "balanced")
                    enhancements.append(f"\nCOMPLEXITY: {complexity_desc}")
                if focus := refined_context.get("focus_areas"):
                    if focus:  # Check if list is not empty
                        enhancements.append(f"\nFOCUS: Emphasize {', '.join(str(f) for f in focus)}")
                if teaching_style := refined_context.get("teaching_style"):
                    if teaching_style:  # Check if list is not empty
                        enhancements.append(f"\nTEACHING STYLE: {', '.join(str(s) for s in teaching_style)}")

                if enhancements:
                    system_prompt += "\n".join(enhancements)
                    logger.info(f"Enhanced system prompt with context: {', '.join(refined_context.keys())}")

            # Calculate word count constraint based on speaking rate
            # Average speaking rate: 2.5 words per second (150 words/minute)
            # Use conservative estimate to ensure we stay under duration_seconds
            max_words = int(duration_seconds * 2.5)

            user_prompt = f"""Topic: {topic}
Target Duration: EXACTLY {duration_seconds} seconds (STRICT MAXIMUM)
Target Segments: {max(10, duration_seconds // 4)} segments
CRITICAL WORD LIMIT: {max_words} words TOTAL across ALL segments (Average speaking rate: 2.5 words/sec)

BREVITY IS ESSENTIAL - This must fit in {duration_seconds} seconds of audio!

CREATE AN EXTRAORDINARY LEARNING EXPERIENCE:

Structure your dialogue like this:

1. HOOK (Why this matters) - 2-3 SHORT exchanges
   - {teacher_name}: Start with a fascinating question or real-world connection (1 sentence)
   - {student_name}: Express curiosity or share a relatable experience (1 sentence)

2. BUILD FROM SIMPLE - 2-3 SHORT exchanges
   - {teacher_name}: Introduce the SIMPLEST possible example with concrete numbers/objects (1-2 sentences)
   - Use visual language: "Let's draw...", "Imagine...", "Picture this..."

3. DEVELOP INTUITION - 3-4 SHORT exchanges
   - {teacher_name}: Use powerful analogies and visual metaphors (1-2 sentences per exchange)
   - {student_name}: Ask clarifying questions, make connections (1 sentence)
   - Build complexity gradually, one concept at a time

4. AHA MOMENT - 2 SHORT exchanges
   - {teacher_name}: Reveal the key insight with enthusiasm (1 sentence)
   - {student_name}: Express understanding with specific realization (1 sentence)

5. REINFORCE & EXTEND - 1-2 SHORT exchanges
   - {teacher_name}: Show how the concept applies more broadly (1 sentence)
   - {student_name}: Ask about extensions or applications (1 sentence)

STRICT RULES:
- Each segment MUST be 1-2 sentences maximum (10-20 words per segment)
- NO long explanations - keep it punchy and fast-paced
- TOTAL word count across ALL segments cannot exceed {max_words} words
- Prioritize clarity and impact over completeness

VISUAL INTEGRATION:
Every line should naturally reference visuals:
- "Watch what happens when we..."
- "Notice how these two..."
- "See this pattern?"
- "Let's transform this into..."
- "Look at how this changes..."

Make learning feel like an exciting discovery journey - but KEEP IT BRIEF!"""

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

            # Validate and enforce word count limit
            total_words = sum(len(segment["text"].split()) for segment in script)
            logger.info(f"Total word count: {total_words} words (limit: {max_words} words)")

            if total_words > max_words:
                logger.warning(f"Script exceeds word limit ({total_words} > {max_words}), truncating to fit duration")
                script = self._truncate_script_to_word_limit(script, max_words)
                total_words = sum(len(segment["text"].split()) for segment in script)
                logger.info(f"Script truncated to {len(script)} segments, {total_words} words")

            # Estimate duration based on speaking rate
            estimated_duration = total_words / 2.5
            logger.info(f"Estimated audio duration: {estimated_duration:.1f} seconds (target: {duration_seconds} seconds)")

            if estimated_duration > duration_seconds * 1.1:  # Allow 10% tolerance
                logger.warning(f"Estimated duration ({estimated_duration:.1f}s) significantly exceeds target ({duration_seconds}s)")

            if progress_callback:
                progress_callback(
                    f"Script generated with {len(script)} dialogue segments (~{estimated_duration:.0f}s)", 20
                )

            return script

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise Exception(f"Invalid JSON response from OpenAI: {e}")
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise Exception(f"Failed to generate script: {e}")

    def _truncate_script_to_word_limit(
        self, script: List[Dict[str, str]], max_words: int
    ) -> List[Dict[str, str]]:
        """
        Truncate script to fit within word limit while preserving dialogue flow.

        Args:
            script: Original script segments
            max_words: Maximum total word count

        Returns:
            Truncated script that fits within word limit
        """
        truncated = []
        current_words = 0

        for segment in script:
            segment_words = len(segment["text"].split())

            # If adding this segment would exceed limit, check if we can add a shortened version
            if current_words + segment_words > max_words:
                # Calculate how many words we can still add
                remaining_words = max_words - current_words

                if remaining_words >= 5:  # Only add if we can include at least 5 words
                    # Truncate this segment to fit
                    words = segment["text"].split()
                    truncated_text = " ".join(words[:remaining_words]) + "..."
                    truncated.append({
                        "speaker": segment["speaker"],
                        "text": truncated_text
                    })

                break  # Stop adding more segments

            truncated.append(segment)
            current_words += segment_words

        return truncated

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
