from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ResumeContext:
    """
    Structured resume context used by the AI agent.

    Keeps raw resume data, extracted intelligence and
    derived analysis separate from agent execution logic.
    """

    raw_text: str

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    detected_role: Optional[str] = None

    skills: List[str] = field(
        default_factory=list
    )

    entities: Dict[str, Any] = field(
        default_factory=dict
    )

    sections: Dict[str, Any] = field(
        default_factory=dict
    )

    ats_result: Dict[str, Any] = field(
        default_factory=dict
    )

    recommendations: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.raw_text = (
            self.raw_text or ""
        ).strip()

        if not self.raw_text:
            raise ValueError(
                "Resume text is required."
            )

        self.skills = self._normalize_list(
            self.skills
        )

    @staticmethod
    def _normalize_list(
        values: List[str]
    ) -> List[str]:

        seen = set()
        result = []

        for value in values or []:

            normalized = (
                str(value)
                .strip()
            )

            if not normalized:
                continue

            key = normalized.casefold()

            if key in seen:
                continue

            seen.add(key)
            result.append(normalized)

        return result

    @property
    def has_contact_information(self) -> bool:
        return bool(
            self.email or self.phone
        )

    @property
    def has_ats_analysis(self) -> bool:
        return bool(
            self.ats_result
        )

    def to_agent_context(self) -> Dict[str, Any]:
        """
        Return compact structured information suitable
        for agent reasoning and tool execution.
        """

        return {
            "identity": {
                "name": self.name,
                "email": self.email,
                "phone": self.phone,
            },

            "detected_role":
                self.detected_role,

            "skills":
                self.skills,

            "entities":
                self.entities,

            "sections":
                self.sections,

            "ats":
                self.ats_result,

            "recommendations":
                self.recommendations,

            "metadata":
                self.metadata,
        }

    def to_dict(
        self,
        *,
        include_raw_text: bool = True
    ) -> Dict[str, Any]:

        result = self.to_agent_context()

        if include_raw_text:
            result["raw_text"] = (
                self.raw_text
            )

        return result