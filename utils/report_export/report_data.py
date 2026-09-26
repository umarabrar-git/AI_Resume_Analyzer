from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from services.resume_intelligence.adapters.analysis_ui_adapter import (
    AnalysisUIAdapter,
)


@dataclass(frozen=True)
class ReportData:
    name: str
    profession_field: str

    ats_score: int
    ats_rating: str
    ats_breakdown: Dict[str, int]

    match_percentage: int
    matched_skills: List[str]
    missing_skills: List[str]

    skills: List[str]

    resume_status: str
    sections_found: List[str]

    word_count: int
    page_count: int
    reading_time: int

    profile_strength: int
    profile_checklist: List[Any]

    format_score: int
    format_checks: List[Any]

    recommendations: List[Any]

    resume_text: str
    job_description: str

    analysis_result: Dict[str, Any]


class ReportDataBuilder:
    """
    Builds the canonical report data object from the existing
    Resume Intelligence UI adapter.

    No analysis values are invented here.
    """

    def __init__(
        self,
        adapter: Optional[AnalysisUIAdapter] = None,
    ) -> None:
        self.adapter = adapter or AnalysisUIAdapter()

    def build(
        self,
        analysis_result: Mapping[str, Any],
        *,
        resume_text: str = "",
        job_description: str = "",
        name: str = "",
    ) -> ReportData:

        ui = self.adapter.build(
            analysis_result,
            resume_text=resume_text,
            job_description=job_description,
        )

        return ReportData(
            name=name or "Resume Owner",

            profession_field=str(
                ui.get("profession_field")
                or "General Professional"
            ),

            ats_score=int(
                ui.get("ats_score") or 0
            ),

            ats_rating=str(
                ui.get("ats_rating") or ""
            ),

            ats_breakdown=dict(
                ui.get("ats_breakdown") or {}
            ),

            match_percentage=int(
                ui.get("match_percentage") or 0
            ),

            matched_skills=list(
                ui.get("matched_skills") or []
            ),

            missing_skills=list(
                ui.get("missing_skills") or []
            ),

            skills=list(
                ui.get("skills") or []
            ),

            resume_status=str(
                ui.get("resume_status") or ""
            ),

            sections_found=list(
                ui.get("sections_found") or []
            ),

            word_count=int(
                ui.get("word_count") or 0
            ),

            page_count=int(
                ui.get("page_count") or 0
            ),

            reading_time=int(
                ui.get("reading_time") or 0
            ),

            profile_strength=int(
                ui.get("profile_strength") or 0
            ),

            profile_checklist=list(
                ui.get("profile_checklist") or []
            ),

            format_score=int(
                ui.get("format_score") or 0
            ),

            format_checks=list(
                ui.get("format_checks") or []
            ),

            recommendations=list(
                ui.get("recommendations") or []
            ),

            resume_text=str(
                ui.get("text") or ""
            ),

            job_description=str(
                ui.get("job_description") or ""
            ),

            analysis_result=dict(
                ui.get("analysis_result") or {}
            ),
        )


report_data_builder = ReportDataBuilder()