"""
Character Profile System

Dynamically generates character personalities, relationships, and dialogue patterns
based on celebrity selections. Injects authentic character context into script generation.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class CharacterPersonality:
    """Represents a character's personality, speech patterns, and relationships."""

    name: str
    role: str  # "teacher" or "student"
    personality_traits: List[str]
    speech_patterns: List[str]
    catchphrases: List[str]
    background: str
    teaching_style: Optional[str] = None  # For teacher role
    learning_style: Optional[str] = None  # For student role

    def to_prompt_context(self) -> str:
        """Convert character profile to LLM prompt context."""
        context = f"""
CHARACTER: {self.name} ({self.role.upper()})

PERSONALITY:
{chr(10).join(f"- {trait}" for trait in self.personality_traits)}

SPEECH PATTERNS:
{chr(10).join(f"- {pattern}" for pattern in self.speech_patterns)}

CATCHPHRASES: {", ".join(self.catchphrases)}

BACKGROUND: {self.background}
"""
        if self.teaching_style:
            context += f"\nTEACHING STYLE: {self.teaching_style}"
        if self.learning_style:
            context += f"\nLEARNING STYLE: {self.learning_style}"

        return context


@dataclass
class CharacterRelationship:
    """Defines relationship dynamics between characters."""

    character1: str
    character2: str
    relationship_type: str  # "rivals", "friends", "mentor-student", etc.
    dynamic_description: str
    interaction_notes: List[str]

    def to_prompt_context(self) -> str:
        """Convert relationship to LLM prompt context."""
        return f"""
RELATIONSHIP: {self.character1} & {self.character2}
Type: {self.relationship_type}
Dynamic: {self.dynamic_description}
Interaction Notes:
{chr(10).join(f"- {note}" for note in self.interaction_notes)}
"""


class CharacterProfileGenerator:
    """Generates dynamic character profiles using LLM based on celebrity names."""

    # Predefined character knowledge base
    CHARACTER_KNOWLEDGE = {
        "goku": {
            "full_name": "Son Goku (Kakarot)",
            "universe": "Dragon Ball",
            "key_traits": ["pure-hearted", "battle-loving", "naive", "loyal", "always hungry"],
            "signature_moves": ["Kamehameha", "Instant Transmission", "Spirit Bomb"],
            "background": "Saiyan warrior raised on Earth, protector of the universe"
        },
        "vegeta": {
            "full_name": "Vegeta",
            "universe": "Dragon Ball",
            "key_traits": ["prideful", "competitive", "tsundere", "strategic", "royal"],
            "signature_moves": ["Final Flash", "Galick Gun", "Big Bang Attack"],
            "background": "Prince of all Saiyans, eternal rival to Goku"
        },
        "trump": {
            "full_name": "Donald Trump",
            "universe": "Real World Politics",
            "key_traits": ["confident", "boastful", "direct", "deal-maker", "controversial"],
            "catchphrases": ["huge", "tremendous", "the best", "believe me"],
            "background": "45th and 47th President of the United States, businessman"
        },
        "biden": {
            "full_name": "Joe Biden",
            "universe": "Real World Politics",
            "key_traits": ["empathetic", "gaffe-prone", "folksy", "experienced", "aviator-wearing"],
            "catchphrases": ["come on, man", "here's the deal", "folks"],
            "background": "46th President of the United States, career politician"
        },
        "drake": {
            "full_name": "Drake (Aubrey Graham)",
            "universe": "Music/Hip-Hop",
            "key_traits": ["emotional", "confident", "melodic", "introspective", "Toronto-proud"],
            "catchphrases": ["YOLO", "started from the bottom"],
            "background": "Canadian rapper, singer, and cultural icon"
        },
        "sydney_sweeney": {
            "full_name": "Sydney Sweeney",
            "universe": "Entertainment/Acting",
            "key_traits": ["talented", "hardworking", "versatile", "relatable", "ambitious"],
            "background": "Actress known for Euphoria and White Lotus"
        }
    }

    # Predefined relationship templates
    RELATIONSHIP_TEMPLATES = {
        ("goku", "vegeta"): {
            "type": "friendly rivals",
            "notes": [
                "Vegeta calls Goku 'Kakarot' (his Saiyan name)",
                "Constant competitive banter about who's stronger",
                "Vegeta is tsundere - acts tough but respects Goku",
                "They reference their past battles and training",
                "Vegeta gets annoyed when Goku surpasses him"
            ]
        },
        ("trump", "biden"): {
            "type": "political rivals",
            "notes": [
                "Frequent disagreements on approach/methodology",
                "Trump brags about his business acumen",
                "Biden appeals to common people and experience",
                "Competitive but trying to work together on education",
                "References to their debates and campaigns"
            ]
        }
    }

    def __init__(self, api_key: str):
        """Initialize character profile generator."""
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_character_profile(
        self,
        character_name: str,
        role: str,
        topic: str
    ) -> CharacterPersonality:
        """
        Generate a dynamic character profile using LLM.

        Args:
            character_name: Name of the character (e.g., "goku", "drake")
            role: "teacher" or "student"
            topic: Educational topic for context

        Returns:
            CharacterPersonality with generated traits and patterns
        """
        # Normalize name
        char_key = character_name.lower().replace(" ", "_")

        # Get base knowledge if available
        base_knowledge = self.CHARACTER_KNOWLEDGE.get(char_key, {})

        # Generate profile using LLM
        prompt = f"""You are creating a character profile for an educational video where {character_name} plays the role of {role}.

{"KNOWN CHARACTER INFO:" if base_knowledge else ""}
{chr(10).join(f"{k}: {v}" for k, v in base_knowledge.items()) if base_knowledge else ""}

TOPIC: {topic}
ROLE: {role.upper()}

Generate a detailed character profile in JSON format with:
1. personality_traits: List of 5-7 core personality traits
2. speech_patterns: List of 4-6 unique ways this character speaks
3. catchphrases: List of 3-5 signature phrases they would use
4. background: Brief character background (2-3 sentences)
5. {"teaching_style" if role == "teacher" else "learning_style"}: How they approach {"teaching" if role == "teacher" else "learning"} (2-3 sentences)

Make it authentic to the character's known personality. If it's a real person or fictional character, stay true to their established traits.
Be creative and specific. This will be used to generate natural dialogue.

Respond ONLY with valid JSON matching this structure:
{{
    "personality_traits": [...],
    "speech_patterns": [...],
    "catchphrases": [...],
    "background": "...",
    "{"teaching_style" if role == "teacher" else "learning_style"}": "..."
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            import json
            profile_data = json.loads(response.choices[0].message.content)

            return CharacterPersonality(
                name=character_name,
                role=role,
                personality_traits=profile_data["personality_traits"],
                speech_patterns=profile_data["speech_patterns"],
                catchphrases=profile_data["catchphrases"],
                background=profile_data["background"],
                teaching_style=profile_data.get("teaching_style") if role == "teacher" else None,
                learning_style=profile_data.get("learning_style") if role == "student" else None
            )

        except Exception as e:
            logger.error(f"Failed to generate character profile for {character_name}: {e}")
            # Return basic fallback profile
            return self._create_fallback_profile(character_name, role, base_knowledge)

    def _create_fallback_profile(
        self,
        character_name: str,
        role: str,
        base_knowledge: Dict[str, Any]
    ) -> CharacterPersonality:
        """Create a basic fallback profile if LLM generation fails."""
        return CharacterPersonality(
            name=character_name,
            role=role,
            personality_traits=base_knowledge.get("key_traits", ["intelligent", "curious"]),
            speech_patterns=["Clear and articulate", "Uses examples"],
            catchphrases=base_knowledge.get("catchphrases", []),
            background=base_knowledge.get("background", f"A knowledgeable {role}"),
            teaching_style="Engaging and interactive" if role == "teacher" else None,
            learning_style="Curious and questioning" if role == "student" else None
        )

    async def generate_relationship(
        self,
        char1_name: str,
        char2_name: str,
        char1_profile: CharacterPersonality,
        char2_profile: CharacterPersonality
    ) -> CharacterRelationship:
        """
        Generate relationship dynamics between two characters.

        Args:
            char1_name: First character name
            char2_name: Second character name
            char1_profile: First character's personality
            char2_profile: Second character's personality

        Returns:
            CharacterRelationship defining their dynamic
        """
        # Normalize names for lookup
        key1 = char1_name.lower().replace(" ", "_")
        key2 = char2_name.lower().replace(" ", "_")

        # Check for predefined relationship
        template = (
            self.RELATIONSHIP_TEMPLATES.get((key1, key2)) or
            self.RELATIONSHIP_TEMPLATES.get((key2, key1))
        )

        if template:
            return CharacterRelationship(
                character1=char1_name,
                character2=char2_name,
                relationship_type=template["type"],
                dynamic_description=f"Dynamic relationship between {char1_name} and {char2_name}",
                interaction_notes=template["notes"]
            )

        # Generate relationship using LLM
        prompt = f"""Create a relationship dynamic between these two characters for an educational video:

CHARACTER 1: {char1_name} ({char1_profile.role})
Traits: {", ".join(char1_profile.personality_traits[:3])}

CHARACTER 2: {char2_name} ({char2_profile.role})
Traits: {", ".join(char2_profile.personality_traits[:3])}

Generate relationship dynamics in JSON format:
1. relationship_type: One word/phrase (e.g., "rivals", "mentor-student", "friends")
2. dynamic_description: How they interact (2-3 sentences)
3. interaction_notes: List of 4-6 specific interaction patterns/behaviors

Respond ONLY with valid JSON:
{{
    "relationship_type": "...",
    "dynamic_description": "...",
    "interaction_notes": [...]
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            import json
            rel_data = json.loads(response.choices[0].message.content)

            return CharacterRelationship(
                character1=char1_name,
                character2=char2_name,
                relationship_type=rel_data["relationship_type"],
                dynamic_description=rel_data["dynamic_description"],
                interaction_notes=rel_data["interaction_notes"]
            )

        except Exception as e:
            logger.error(f"Failed to generate relationship: {e}")
            # Return basic fallback
            return CharacterRelationship(
                character1=char1_name,
                character2=char2_name,
                relationship_type="collaborative educators",
                dynamic_description=f"{char1_name} and {char2_name} work together to explain concepts.",
                interaction_notes=[
                    "They complement each other's explanations",
                    "They build on each other's points"
                ]
            )


class CharacterContext:
    """Complete character context for script generation."""

    def __init__(
        self,
        characters: List[CharacterPersonality],
        relationship: Optional[CharacterRelationship] = None
    ):
        """Initialize character context."""
        self.characters = characters
        self.relationship = relationship

    def to_prompt_context(self) -> str:
        """Convert full character context to LLM prompt."""
        context = "=== CHARACTER CONTEXT ===\n\n"

        for char in self.characters:
            context += char.to_prompt_context() + "\n"

        if self.relationship:
            context += "\n" + self.relationship.to_prompt_context() + "\n"

        context += """
=== DIALOGUE REQUIREMENTS ===
- Characters MUST speak according to their personality traits and speech patterns
- Use their catchphrases naturally in conversation
- Reflect their relationship dynamic in interactions
- Stay authentic to the character's established personality
- Make dialogue feel natural, not forced
"""

        return context
