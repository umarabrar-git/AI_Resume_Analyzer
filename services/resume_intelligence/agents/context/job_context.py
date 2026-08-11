from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class JobContext:
    """
    Structured job-description context used by
    matching, planning and generative tools.
    """

    raw_text: str

    title: Optional[str] = None
    company: Optional[str] = None

    required_skills: List[str] = field(
        default_factory=list
    )

    preferred_skills: List[str] = field(
        default_factory=list
    )

    requirements: List[str] = field(
        default_factory=list
    )

    responsibilities: List[str] = field(
        default_factory=list
    )

    keywords: List[str] = field(
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
                "Job description text is required."
            )

        self.required_skills = (
            self._normalize_list(
                self.required_skills
            )
        )

        self.preferred_skills = (
            self._normalize_list(
                self.preferred_skills
            )
        )

        self.requirements = (
            self._normalize_list(
                self.requirements
            )
        )

        self.responsibilities = (
            self._normalize_list(
                self.responsibilities
            )
        )

        self.keywords = (
            self._normalize_list(
                self.keywords
            )
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
    def all_skills(self) -> List[str]:

        return self._normalize_list(
            self.required_skills
            + self.preferred_skills
        )

    def to_agent_context(self) -> Dict[str, Any]:

        return {
            "title":
                self.title,

            "company":
                self.company,

            "required_skills":
                self.required_skills,

            "preferred_skills":
                self.preferred_skills,

            "requirements":
                self.requirements,

            "responsibilities":
                self.responsibilities,

            "keywords":
                self.keywords,

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