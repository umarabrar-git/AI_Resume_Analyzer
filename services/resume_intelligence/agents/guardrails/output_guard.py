"""
Output boundary for agent responses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from services.resume_intelligence.agents.schemas import (
    AgentResponse,
)


MAX_OUTPUT_CHARS = 50_000


_SECRET_PATTERNS = [
    re.compile(
        r"(?i)\bapi[_\-\s]?key\s*[:=]\s*[^\s]+"
    ),
    re.compile(
        r"(?i)\bsecret\s*[:=]\s*[^\s]+"
    ),
    re.compile(
        r"(?i)\bpassword\s*[:=]\s*[^\s]+"
    ),
    re.compile(
        r"(?i)\bbearer\s+[a-z0-9._\-]+"
    ),
]


@dataclass
class OutputGuardResult:
    allowed: bool

    content: str

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict:

        return {
            "allowed": self.allowed,
            "content": self.content,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


class OutputGuard:
    """
    Validates final content before it leaves the agent boundary.
    """

    def __init__(
        self,
        *,
        max_output_chars: int = MAX_OUTPUT_CHARS,
        redact_secret_like_values: bool = True,
    ) -> None:

        self.max_output_chars = max(
            100,
            int(max_output_chars)
        )

        self.redact_secret_like_values = (
            redact_secret_like_values
        )

    @staticmethod
    def _redact_secrets(
        content: str
    ) -> tuple[str, int]:

        redacted = content
        count = 0

        for pattern in _SECRET_PATTERNS:

            redacted, replacements = (
                pattern.subn(
                    "[REDACTED]",
                    redacted
                )
            )

            count += replacements

        return redacted, count

    def validate_content(
        self,
        content: str
    ) -> OutputGuardResult:

        normalized = (
            content or ""
        ).strip()

        errors = []
        warnings = []

        if not normalized:

            errors.append(
                "Agent produced an empty response."
            )

        if len(normalized) > self.max_output_chars:

            errors.append(
                "Agent response exceeds the maximum allowed size."
            )

        redaction_count = 0

        if (
            normalized
            and self.redact_secret_like_values
        ):

            normalized, redaction_count = (
                self._redact_secrets(
                    normalized
                )
            )

            if redaction_count:

                warnings.append(
                    "Potential secret-like values were redacted from the response."
                )

        return OutputGuardResult(
            allowed=not errors,
            content=normalized,
            errors=errors,
            warnings=warnings,
            metadata={
                "character_count":
                    len(normalized),

                "redaction_count":
                    redaction_count,
            },
        )

    def validate_response(
        self,
        response: AgentResponse
    ) -> AgentResponse:

        if not isinstance(
            response,
            AgentResponse
        ):
            raise TypeError(
                "response must be an AgentResponse."
            )

        result = self.validate_content(
            response.content
        )

        response.content = (
            result.content
        )

        response.warnings.extend(
            warning
            for warning in result.warnings
            if warning not in response.warnings
        )

        response.errors.extend(
            error
            for error in result.errors
            if error not in response.errors
        )

        if not result.allowed:
            response.success = False

        response.metadata[
            "output_guard"
        ] = result.metadata

        return response