from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GenerationRequest:
    task: str

    resume_text: str = ""
    job_description: Optional[str] = None

    source_text: Optional[str] = None
    target_role: Optional[str] = None

    instructions: Optional[str] = None

    resume_facts: Dict[str, Any] = field(
        default_factory=dict
    )

    recommendations: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.task = (
            self.task or ""
        ).strip().lower()

        self.resume_text = (
            self.resume_text or ""
        ).strip()

        self.source_text = (
            self.source_text.strip()
            if self.source_text
            else None
        )

        self.job_description = (
            self.job_description.strip()
            if self.job_description
            else None
        )

        self.target_role = (
            self.target_role.strip()
            if self.target_role
            else None
        )

        self.instructions = (
            self.instructions.strip()
            if self.instructions
            else None
        )

        if not self.task:
            raise ValueError(
                "Generation task is required."
            )

        if not self.resume_text:
            raise ValueError(
                "Resume text is required."
            )