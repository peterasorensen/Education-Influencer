"""
Follow-Up Question Generator Module

Generates intelligent follow-up questions to refine user prompts before video generation.
Uses GPT-4o-mini for fast, cost-effective question generation (<2s latency).
"""

import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import json
import asyncio

logger = logging.getLogger(__name__)

# System prompt for question generation
QUESTION_GENERATION_SYSTEM_PROMPT = """You are an expert educational content advisor. Your job is to ask 2-4 BRIEF, HIGHLY RELEVANT follow-up questions that will help create the BEST educational video for the user's topic.

GOALS:
1. Clarify ambiguity (if topic is vague)
2. Understand target audience
3. Determine desired depth/complexity
4. Identify specific focus areas
5. Match user's learning style preferences

RULES:
- Generate ONLY 2-4 questions (never more)
- Each question must be actionable and specific
- Prioritize questions that most impact video quality
- Questions should be quick to answer (<30 seconds per question)
- Use appropriate question types for efficiency

QUESTION TYPES:
- multiple_choice: When there are 3-5 clear options
- multi_select: When user might want multiple aspects
- toggle: For simple yes/no decisions
- slider: For complexity/depth levels (1-5 scale)
- short_text: Only when open-ended input is essential

CATEGORIES:
- "audience": Who is this for?
- "depth": How deep/complex?
- "style": Teaching approach
- "focus": Specific aspects to emphasize

OUTPUT FORMAT (JSON):
{
  "questions": [
    {
      "id": "q1",
      "question_text": "Who is the target audience?",
      "question_type": "multiple_choice",
      "category": "audience",
      "options": ["High school", "College", "Professionals", "General"],
      "default_value": "General",
      "is_required": false
    }
  ],
  "estimated_time_seconds": 30
}

Be intelligent: For clear topics, ask fewer questions. For vague topics, ask clarifying questions."""


class FollowUpQuestion:
    """Represents a follow-up question."""

    def __init__(
        self,
        id: str,
        question_text: str,
        question_type: str,
        category: str,
        options: Optional[List[str]] = None,
        default_value: Optional[Any] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        is_required: bool = False,
    ):
        self.id = id
        self.question_text = question_text
        self.question_type = question_type
        self.category = category
        self.options = options
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.is_required = is_required

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "category": self.category,
            "is_required": self.is_required,
        }

        if self.options is not None:
            result["options"] = self.options
        if self.default_value is not None:
            result["default_value"] = self.default_value
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value

        return result


class FollowUpQuestionGenerator:
    """Generates follow-up questions to refine user prompts."""

    def __init__(self, api_key: str):
        """
        Initialize the follow-up question generator.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Fast, cheap model for question generation

    async def generate_questions(
        self,
        topic: str,
        max_questions: int = 3,
        time_budget_seconds: float = 2.0,
    ) -> List[FollowUpQuestion]:
        """
        Generate 2-4 smart questions with <2s latency.

        Args:
            topic: The educational topic from the user
            max_questions: Maximum number of questions to generate (2-4)
            time_budget_seconds: Time budget for generation (default: 2.0s)

        Returns:
            List of FollowUpQuestion objects

        Raises:
            Exception: If question generation fails
        """
        try:
            logger.info(f"Generating follow-up questions for topic: {topic}")

            # Prepare user prompt
            user_prompt = f"""Topic: {topic}

Generate {max_questions} follow-up questions to help create the best educational video.

Focus on:
1. Clarifying any ambiguity in the topic
2. Understanding the target audience
3. Determining desired depth/complexity
4. Identifying specific focus areas

Return JSON in the specified format."""

            # Create task with timeout
            async def generate_with_timeout():
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": QUESTION_GENERATION_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,  # Lower temperature for faster, more focused responses
                    max_tokens=500,  # Limit output size for speed
                    response_format={"type": "json_object"},
                )
                return response

            # Execute with timeout
            try:
                response = await asyncio.wait_for(
                    generate_with_timeout(), timeout=time_budget_seconds
                )
            except asyncio.TimeoutError:
                logger.warning(
                    f"Question generation timed out after {time_budget_seconds}s, returning fallback questions"
                )
                return self._get_fallback_questions(topic)

            # Parse response
            content = response.choices[0].message.content
            logger.info(
                f"Question generation response preview (first 300 chars): {content[:300]}"
            )

            parsed = json.loads(content)

            # Extract questions array
            questions_data = parsed.get("questions", [])

            if not questions_data:
                logger.warning("No questions in response, returning fallback questions")
                return self._get_fallback_questions(topic)

            # Convert to FollowUpQuestion objects
            questions = []
            for q_data in questions_data:
                try:
                    question = FollowUpQuestion(
                        id=q_data.get("id", f"q{len(questions) + 1}"),
                        question_text=q_data.get("question_text", ""),
                        question_type=q_data.get("question_type", "short_text"),
                        category=q_data.get("category", "general"),
                        options=q_data.get("options"),
                        default_value=q_data.get("default_value"),
                        min_value=q_data.get("min_value"),
                        max_value=q_data.get("max_value"),
                        is_required=q_data.get("is_required", False),
                    )
                    questions.append(question)
                except Exception as e:
                    logger.warning(f"Failed to parse question: {e}")
                    continue

            if not questions:
                logger.warning("Failed to parse any questions, returning fallback")
                return self._get_fallback_questions(topic)

            logger.info(f"Generated {len(questions)} follow-up questions")
            return questions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._get_fallback_questions(topic)
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return self._get_fallback_questions(topic)

    def _get_fallback_questions(self, topic: str) -> List[FollowUpQuestion]:
        """
        Return fallback questions if generation fails or times out.

        Args:
            topic: The educational topic

        Returns:
            List of fallback FollowUpQuestion objects
        """
        logger.info("Using fallback questions")
        return [
            FollowUpQuestion(
                id="q1",
                question_text="Who is your target audience?",
                question_type="multiple_choice",
                category="audience",
                options=["High school students", "College students", "Professionals", "General audience"],
                default_value="General audience",
                is_required=False,
            ),
            FollowUpQuestion(
                id="q2",
                question_text="How deep should the explanation be?",
                question_type="slider",
                category="depth",
                min_value=1,
                max_value=5,
                default_value=3,
                is_required=False,
            ),
            FollowUpQuestion(
                id="q3",
                question_text="What aspects should we focus on?",
                question_type="multi_select",
                category="focus",
                options=["Theory", "Practical examples", "Real-world applications", "Step-by-step process"],
                default_value=["Practical examples"],
                is_required=False,
            ),
        ]

    async def merge_answers_into_prompt(
        self,
        original_topic: str,
        questions: List[FollowUpQuestion],
        answers: Dict[str, Any],
    ) -> str:
        """
        Merge answers into enriched prompt.

        Args:
            original_topic: The original topic from user
            questions: List of follow-up questions that were asked
            answers: Dictionary mapping question IDs to user answers

        Returns:
            Refined prompt string with context from answers

        Raises:
            Exception: If prompt refinement fails
        """
        try:
            logger.info(f"Merging answers into prompt for topic: {original_topic}")

            # Build context from answers
            context_parts = []

            for question in questions:
                answer = answers.get(question.id)
                if not answer:
                    continue

                # Format answer based on question type
                if question.question_type == "multiple_choice":
                    context_parts.append(f"{question.question_text}: {answer}")
                elif question.question_type == "multi_select":
                    if isinstance(answer, list):
                        context_parts.append(
                            f"{question.question_text}: {', '.join(answer)}"
                        )
                    else:
                        context_parts.append(f"{question.question_text}: {answer}")
                elif question.question_type == "slider":
                    # Map slider values to descriptive text
                    depth_map = {
                        1: "very simple, basic overview",
                        2: "basic with key concepts",
                        3: "balanced depth",
                        4: "detailed with technical aspects",
                        5: "very detailed, expert-level",
                    }
                    depth_desc = depth_map.get(answer, "balanced depth")
                    context_parts.append(f"{question.question_text}: {depth_desc}")
                elif question.question_type == "toggle":
                    context_parts.append(
                        f"{question.question_text}: {'Yes' if answer else 'No'}"
                    )
                else:  # short_text
                    context_parts.append(f"{question.question_text}: {answer}")

            # Create enhanced prompt
            if context_parts:
                context_str = "\n".join(context_parts)
                refined_prompt = f"""{original_topic}

Context:
{context_str}"""
            else:
                # No answers provided, use original topic
                refined_prompt = original_topic

            logger.info(f"Refined prompt created (length: {len(refined_prompt)} chars)")
            logger.info(f"Refined prompt preview: {refined_prompt[:200]}...")

            return refined_prompt

        except Exception as e:
            logger.error(f"Prompt refinement failed: {e}")
            # Fallback to original topic
            return original_topic
