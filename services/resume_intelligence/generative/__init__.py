"""Generative AI layer for resume intelligence."""
from .generation_service import (
    GenerationService,
    generate_content,
    TASK_SUMMARY,
    TASK_BULLETS,
    TASK_EXPERIENCE,
    TASK_RESUME_REWRITE,
    TASK_COVER_LETTER,
)

from .schemas import (
    GenerationRequest,
    GenerationResponse,
)


__all__ = [
    "GenerationService",
    "GenerationRequest",
    "GenerationResponse",
    "generate_content",
    "TASK_SUMMARY",
    "TASK_BULLETS",
    "TASK_EXPERIENCE",
    "TASK_RESUME_REWRITE",
    "TASK_COVER_LETTER",
]