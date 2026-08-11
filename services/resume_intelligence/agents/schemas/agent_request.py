from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


SUPPORTED_AGENT_MODES = {
    "analyze",
    "optimize",
    "tailor",
    "rewrite",
    "cover_letter",
    "career_assist",
}


@dataclass
class AgentRequest:
    """
    Standard request contract for the Resume AI Agent.

    Suitable for:
    - Web application
    - REST API
    - Android
    - iOS
    - background workers
    - future external integrations
    """

    message: str

    resume_text: Optional[str] = None
    job_description: Optional[str] = None

    mode: str = "analyze"

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    recommendations: List[Dict[str, Any]] = field(
        default_factory=list
    )

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    preferences: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.message = (
            self.message or ""
        ).strip()

        if not self.message:
            raise ValueError(
                "Agent message is required."
            )

        self.mode = (
            self.mode
            or "analyze"
        ).strip().lower()

        if self.mode not in SUPPORTED_AGENT_MODES:
            raise ValueError(
                f"Unsupported agent mode: {self.mode}"
            )

        self.resume_text = (
            self.resume_text.strip()
            if self.resume_text
            else None
        )

        self.job_description = (
            self.job_description.strip()
            if self.job_description
            else None
        )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "message": self.message,
            "mode": self.mode,
            "resume_text": self.resume_text,
            "job_description": self.job_description,
            "recommendations": self.recommendations,
            "context": self.context,
            "preferences": self.preferences,
            "metadata": self.metadata,
            "preferences": self.preferences,
        }