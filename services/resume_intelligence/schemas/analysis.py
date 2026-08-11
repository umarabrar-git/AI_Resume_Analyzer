from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .common import (
    Score,
    generate_id,
    normalize_string_list,
    serialize,
)


@dataclass
class AnalysisFinding:
    title: str
    description: str

    category: str = "general"

    severity: str = "info"

    evidence: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.title = self.title.strip()

        self.description = (
            self.description.strip()
        )

        if not self.title:
            raise ValueError(
                "Finding title is required."
            )


@dataclass
class SkillGap:
    matched_required: List[str] = field(
        default_factory=list
    )

    missing_required: List[str] = field(
        default_factory=list
    )

    matched_preferred: List[str] = field(
        default_factory=list
    )

    missing_preferred: List[str] = field(
        default_factory=list
    )

    required_match_rate: Optional[
        float
    ] = None

    def __post_init__(self) -> None:

        self.matched_required = (
            normalize_string_list(
                self.matched_required
            )
        )

        self.missing_required = (
            normalize_string_list(
                self.missing_required
            )
        )

        self.matched_preferred = (
            normalize_string_list(
                self.matched_preferred
            )
        )

        self.missing_preferred = (
            normalize_string_list(
                self.missing_preferred
            )
        )

        if (
            self.required_match_rate
            is not None
        ):

            self.required_match_rate = max(
                0.0,
                min(
                    float(
                        self.required_match_rate
                    ),
                    1.0
                )
            )


@dataclass
class ATSAnalysis:
    overall_score: Score

    section_score: Optional[
        Score
    ] = None

    content_score: Optional[
        Score
    ] = None

    keyword_score: Optional[
        Score
    ] = None

    readability_score: Optional[
        Score
    ] = None

    strengths: List[str] = field(
        default_factory=list
    )

    weaknesses: List[str] = field(
        default_factory=list
    )

    findings: List[
        AnalysisFinding
    ] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class JobMatchAnalysis:
    overall_score: Score

    semantic_score: Optional[
        Score
    ] = None

    skill_score: Optional[
        Score
    ] = None

    keyword_score: Optional[
        Score
    ] = None

    skill_gap: Optional[
        SkillGap
    ] = None

    matched_requirements: List[str] = field(
        default_factory=list
    )

    missing_requirements: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ResumeAnalysis:
    analysis_id: str = field(
        default_factory=lambda:
            generate_id("analysis")
    )

    resume_id: Optional[str] = None
    job_id: Optional[str] = None

    ats: Optional[
        ATSAnalysis
    ] = None

    job_match: Optional[
        JobMatchAnalysis
    ] = None

    findings: List[
        AnalysisFinding
    ] = field(
        default_factory=list
    )

    recommendations: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    confidence: Optional[float] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        if self.confidence is not None:

            self.confidence = max(
                0.0,
                min(
                    float(self.confidence),
                    1.0
                )
            )

    def to_dict(self) -> Dict[str, Any]:
        return serialize(self)