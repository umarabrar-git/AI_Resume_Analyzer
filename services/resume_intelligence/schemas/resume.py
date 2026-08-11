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
class ResumeIdentity:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    location: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    github: Optional[str] = None

    def __post_init__(self) -> None:

        self.name = normalize_text(
            self.name
        )

        self.email = normalize_text(
            self.email
        )

        self.phone = normalize_text(
            self.phone
        )

        self.location = normalize_text(
            self.location
        )

        self.linkedin = normalize_text(
            self.linkedin
        )

        self.portfolio = normalize_text(
            self.portfolio
        )

        self.github = normalize_text(
            self.github
        )


@dataclass
class ResumeExperience:
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

    start_date: Optional[str] = None
    end_date: Optional[str] = None

    description: Optional[str] = None

    achievements: List[str] = field(
        default_factory=list
    )

    skills: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.title = normalize_text(
            self.title
        )

        self.company = normalize_text(
            self.company
        )

        self.description = normalize_text(
            self.description
        )

        self.achievements = (
            normalize_string_list(
                self.achievements
            )
        )

        self.skills = (
            normalize_string_list(
                self.skills
            )
        )


@dataclass
class ResumeEducation:
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None

    start_date: Optional[str] = None
    end_date: Optional[str] = None

    grade: Optional[str] = None

    description: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ResumeProject:
    name: str

    description: Optional[str] = None
    role: Optional[str] = None
    url: Optional[str] = None

    skills: List[str] = field(
        default_factory=list
    )

    achievements: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.name = self.name.strip()

        if not self.name:
            raise ValueError(
                "Project name is required."
            )

        self.skills = (
            normalize_string_list(
                self.skills
            )
        )

        self.achievements = (
            normalize_string_list(
                self.achievements
            )
        )


@dataclass
class ResumeCertification:
    name: str

    issuer: Optional[str] = None

    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None

    credential_id: Optional[str] = None
    credential_url: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.name = self.name.strip()

        if not self.name:
            raise ValueError(
                "Certification name is required."
            )


@dataclass
class Resume:
    raw_text: str

    resume_id: str = field(
        default_factory=lambda:
            generate_id("resume")
    )

    identity: ResumeIdentity = field(
        default_factory=ResumeIdentity
    )

    summary: Optional[str] = None

    experiences: List[
        ResumeExperience
    ] = field(
        default_factory=list
    )

    education: List[
        ResumeEducation
    ] = field(
        default_factory=list
    )

    projects: List[
        ResumeProject
    ] = field(
        default_factory=list
    )

    certifications: List[
        ResumeCertification
    ] = field(
        default_factory=list
    )

    skills: List[Skill] = field(
        default_factory=list
    )

    languages: List[str] = field(
        default_factory=list
    )

    detected_roles: List[str] = field(
        default_factory=list
    )

    seniority: SeniorityLevel = (
        SeniorityLevel.UNKNOWN
    )

    sections: Dict[str, Any] = field(
        default_factory=dict
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
                "Resume raw text is required."
            )

        self.summary = normalize_text(
            self.summary
        )

        self.languages = (
            normalize_string_list(
                self.languages
            )
        )

        self.detected_roles = (
            normalize_string_list(
                self.detected_roles
            )
        )

    @property
    def skill_names(self) -> List[str]:

        return [
            skill.name
            for skill in self.skills
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