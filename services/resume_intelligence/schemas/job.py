from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .common import (
    SeniorityLevel,
    Skill,
    generate_id,
    normalize_string_list,
    normalize_text,
    serialize,
)


@dataclass
class JobRequirement:
    text: str

    required: bool = True

    category: Optional[str] = None

    confidence: Optional[float] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.text = self.text.strip()

        if not self.text:
            raise ValueError(
                "Job requirement text is required."
            )


@dataclass
class Job:
    raw_text: str

    job_id: str = field(
        default_factory=lambda:
            generate_id("job")
    )

    title: Optional[str] = None

    company: Optional[str] = None
    location: Optional[str] = None

    employment_type: Optional[str] = None

    seniority: SeniorityLevel = (
        SeniorityLevel.UNKNOWN
    )

    summary: Optional[str] = None

    required_skills: List[Skill] = field(
        default_factory=list
    )

    preferred_skills: List[Skill] = field(
        default_factory=list
    )

    requirements: List[
        JobRequirement
    ] = field(
        default_factory=list
    )

    responsibilities: List[str] = field(
        default_factory=list
    )

    qualifications: List[str] = field(
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
                "Job description raw text "
                "is required."
            )

        self.title = normalize_text(
            self.title
        )

        self.company = normalize_text(
            self.company
        )

        self.location = normalize_text(
            self.location
        )

        self.summary = normalize_text(
            self.summary
        )

        self.responsibilities = (
            normalize_string_list(
                self.responsibilities
            )
        )

        self.qualifications = (
            normalize_string_list(
                self.qualifications
            )
        )

        self.keywords = (
            normalize_string_list(
                self.keywords
            )
        )

    @property
    def required_skill_names(
        self
    ) -> List[str]:

        return [
            skill.name
            for skill
            in self.required_skills
        ]

    @property
    def preferred_skill_names(
        self
    ) -> List[str]:

        return [
            skill.name
            for skill
            in self.preferred_skills
        ]

    def to_dict(
        self,
        *,
        include_raw_text: bool = True,
    ) -> Dict[str, Any]:

        data = serialize(self)

        if not include_raw_text:
            data.pop(
                "raw_text",
                None
            )

        return data