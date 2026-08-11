"""
Input validation boundary for the Resume AI Agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from services.resume_intelligence.agents.schemas import (
    AgentRequest,
)

from .prompt_injection_guard import (
    InjectionRisk,
    assess_prompt_injection,
)


MAX_MESSAGE_CHARS = 10_000
MAX_RESUME_CHARS = 100_000
MAX_JOB_DESCRIPTION_CHARS = 60_000


@dataclass
class InputGuardResult:
    allowed: bool

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    security: Dict = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict:

        return {
            "allowed": self.allowed,
            "errors": self.errors,
            "warnings": self.warnings,
            "security": self.security,
        }


class InputGuard:
    """
    Validates public agent input before planning/execution.
    """

    def __init__(
        self,
        *,
        max_message_chars: int = MAX_MESSAGE_CHARS,
        max_resume_chars: int = MAX_RESUME_CHARS,
        max_job_description_chars: int = MAX_JOB_DESCRIPTION_CHARS,
        block_high_risk_user_prompt: bool = True,
    ) -> None:

        self.max_message_chars = max_message_chars
        self.max_resume_chars = max_resume_chars

        self.max_job_description_chars = (
            max_job_description_chars
        )

        self.block_high_risk_user_prompt = (
            block_high_risk_user_prompt
        )

    def validate(
        self,
        request: AgentRequest
    ) -> InputGuardResult:

        if not isinstance(
            request,
            AgentRequest
        ):
            raise TypeError(
                "request must be an AgentRequest."
            )

        errors = []
        warnings = []

        if len(request.message) > self.max_message_chars:

            errors.append(
                "Agent message exceeds the maximum allowed size."
            )

        if (
            request.resume_text
            and len(request.resume_text)
            > self.max_resume_chars
        ):
            errors.append(
                "Resume content exceeds the maximum allowed size."
            )

        if (
            request.job_description
            and len(request.job_description)
            > self.max_job_description_chars
        ):
            errors.append(
                "Job description exceeds the maximum allowed size."
            )

        user_assessment = (
            assess_prompt_injection(
                request.message
            )
        )

        resume_assessment = (
            assess_prompt_injection(
                request.resume_text or ""
            )
        )

        job_assessment = (
            assess_prompt_injection(
                request.job_description or ""
            )
        )

        if (
            self.block_high_risk_user_prompt
            and user_assessment.risk
            == InjectionRisk.HIGH
        ):
            errors.append(
                "The request contains prohibited instruction-manipulation patterns."
            )

        # Resume/JD are documents, not trusted instructions.
        # Detection therefore produces warnings rather than blindly
        # rejecting legitimate uploaded documents.

        if resume_assessment.detected:

            warnings.append(
                "The resume contains instruction-like text and will be treated as untrusted document content."
            )

        if job_assessment.detected:

            warnings.append(
                "The job description contains instruction-like text and will be treated as untrusted document content."
            )

        security = {
            "user_message":
                user_assessment.to_dict(),

            "resume":
                resume_assessment.to_dict(),

            "job_description":
                job_assessment.to_dict(),
        }

        return InputGuardResult(
            allowed=not errors,
            errors=errors,
            warnings=warnings,
            security=security,
        )