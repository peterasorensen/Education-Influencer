"""
Pydantic models for custom photo and audio uploads.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Tuple, List
from pydantic import BaseModel, Field


class PhotoMetadata(BaseModel):
    """Metadata for uploaded photos."""

    photo_id: str = Field(..., description="Unique photo identifier (UUID)")
    photo_url: str = Field(..., description="URL path to access the photo")
    thumbnail_url: str = Field(..., description="URL path to access the thumbnail")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    dimensions: Tuple[int, int] = Field(..., description="Image dimensions (width, height)")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Upload timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "photo_id": "550e8400-e29b-41d4-a716-446655440000",
                "photo_url": "/api/media/photos/default/550e8400-e29b-41d4-a716-446655440000.jpg",
                "thumbnail_url": "/api/media/photos/default/550e8400-e29b-41d4-a716-446655440000_thumb.jpg",
                "filename": "my_photo.jpg",
                "size": 2048576,
                "dimensions": [1024, 1024],
                "created_at": "2025-11-21T10:30:00"
            }
        }


class AudioMetadata(BaseModel):
    """Metadata for uploaded audio clips."""

    audio_id: str = Field(..., description="Unique audio identifier (UUID)")
    audio_url: str = Field(..., description="URL path to access the audio")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    duration: float = Field(..., description="Audio duration in seconds")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Upload timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_id": "660e8400-e29b-41d4-a716-446655440000",
                "audio_url": "/api/media/audio/default/660e8400-e29b-41d4-a716-446655440000.mp3",
                "filename": "my_voice.mp3",
                "size": 102400,
                "duration": 4.5,
                "sample_rate": 24000,
                "created_at": "2025-11-21T10:30:00"
            }
        }


class QuestionType(str, Enum):
    """Types of follow-up questions."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_BLANK = "fill_blank"


class FollowUpQuestion(BaseModel):
    """Follow-up question model for educational content."""

    question: str = Field(..., description="The question text")
    question_type: QuestionType = Field(..., description="Type of question")
    options: Optional[list[str]] = Field(default=None, description="Answer options for multiple choice")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: str = Field(..., description="Explanation of the correct answer")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the capital of France?",
                "question_type": "multiple_choice",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": "Paris",
                "explanation": "Paris is the capital and largest city of France."
            }
        }


class CelebrityConfig(BaseModel):
    """Configuration for a single celebrity (preset or custom)."""

    mode: str = Field(
        default="preset",
        description="Celebrity mode: 'preset' or 'custom'"
    )
    name: Optional[str] = Field(
        default=None,
        description="For presets: 'drake' or 'sydney_sweeney'"
    )
    photo_id: Optional[str] = Field(
        default=None,
        description="For custom uploads: Photo ID"
    )
    audio_id: Optional[str] = Field(
        default=None,
        description="For custom uploads: Audio ID for voice cloning"
    )
    user_id: str = Field(
        default="default",
        description="User ID for accessing custom media"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "preset",
                "name": "drake",
                "user_id": "default"
            }
        }


class CustomCelebrityRequest(BaseModel):
    """Request model for custom celebrity mode (LEGACY - backward compatibility)."""

    celebrity_mode: str = Field(
        default="preset",
        description="Celebrity mode: 'preset' (drake/sydney_sweeney) or 'custom' (user uploads)"
    )
    custom_photo_id: Optional[str] = Field(
        default=None,
        description="Photo ID for custom celebrity (required if celebrity_mode='custom')"
    )
    custom_audio_id: Optional[str] = Field(
        default=None,
        description="Audio ID for custom voice (required if celebrity_mode='custom')"
    )
    user_id: str = Field(
        default="default",
        description="User ID for accessing custom media"
    )
