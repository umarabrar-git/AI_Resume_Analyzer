from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Dict, Optional

from services.resume_intelligence.agents import (
    AgentService,
    get_agent_service,
)

from services.resume_intelligence.agents.schemas import (
    AgentResponse,
)

from utils.ats.resume_processing import analyze_resume
from utils.parsing.parser import extract_skills, extract_name, extract_email, extract_phone


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalysisWorkflowRequest:
    resume_text: str

    job_description: Optional[str] = None

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    organization_id: Optional[str] = None

    plan: Optional[str] = None

    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisWorkflow:
    """
    Full resume intelligence workflow.

    Typical pipeline:
        Resume
          ↓
        NLP / Context
          ↓
        ATS Analysis
          ↓
        Job Matching (when JD exists)
          ↓
        Skill Gap (when JD exists)
          ↓
        Recommendations
          ↓
        Agent Response
    """

    def __init__(
        self,
        agent_service: Optional[AgentService] = None,
    ) -> None:

        self.agent_service = agent_service

        if self.agent_service is None:
            try:
                self.agent_service = get_agent_service()
            except RuntimeError:
                self.agent_service = None

    def _build_fallback_result(
        self,
        request: AnalysisWorkflowRequest,
    ) -> Dict[str, Any]:
        resume_text = (request.resume_text or "").strip()
        job_description = (request.job_description or "").strip()

        logger.info(
            "[ANALYSIS] fallback_start chars=%s words=%s job_description_present=%s",
            len(resume_text),
            len(resume_text.split()),
            bool(job_description),
        )

        analysis = analyze_resume(resume_text, job_description)

        return {
            "success": True,
            "content": (
                "Resume analysis completed using the built-in parser."
            ),
            "analysis_result": {
                "ats": {
                    "ats_score": analysis.get("ats_score", 0),
                    "word_count": analysis.get("word_count", 0),
                    "resume_status": analysis.get("resume_status", "Unknown"),
                    "sections_found": analysis.get("sections_found", []),
                },
                "job_match": {
                    "matched_skills": analysis.get("matched_skills", []),
                    "missing_skills": analysis.get("missing_skills", []),
                    "match_percentage": analysis.get("match_percentage", 0),
                },
                "resume": {
                    "name": analysis.get("name"),
                    "email": analysis.get("email"),
                    "phone": analysis.get("phone"),
                    "skills": analysis.get("skills", []),
                    "profession_field": analysis.get("profession_field"),
                    "profile_strength": analysis.get("profile_strength"),
                    "profile_checklist": analysis.get("profile_checklist", []),
                    "format_checks": analysis.get("format_checks", []),
                    "format_score": analysis.get("format_score", 0),
                    "page_count": analysis.get("page_count", 0),
                    "reading_time": analysis.get("reading_time", 0),
                },
                "recommendations": analysis.get("recommendations", []),
                "raw": analysis,
            },
            "metadata": {
                "mode": "fallback",
                "workflow": "analysis",
                "job_description_provided": bool(job_description),
            },
        }

    def run(
        self,
        request: AnalysisWorkflowRequest,
    ) -> AgentResponse:

        resume_text = (
            request.resume_text or ""
        ).strip()

        if not resume_text:
            raise ValueError(
                "Resume text is required."
            )

        has_job = bool(
            (
                request.job_description
                or ""
            ).strip()
        )

        message = (
            "Analyze this resume against the target "
            "job description. Evaluate ATS compatibility, "
            "job match, skill gaps, strengths, weaknesses, "
            "and provide prioritized recommendations."
            if has_job
            else
            "Analyze this resume. Evaluate ATS compatibility, "
            "resume structure, content quality, strengths, "
            "weaknesses, and provide prioritized recommendations."
        )

        if self.agent_service is None:
            return self._build_fallback_result(request)

        try:
            logger.info(
                "[ANALYSIS] agent_start chars=%s words=%s job_description_present=%s",
                len(resume_text),
                len(resume_text.split()),
                has_job,
            )
            return self.agent_service.run(
                message=message,

                resume_text=resume_text,

                job_description=(
                    request.job_description
                ),

                user_id=request.user_id,
                session_id=request.session_id,

                conversation_id=(
                    request.conversation_id
                ),

                organization_id=(
                    request.organization_id
                ),

                plan=request.plan,

                mode="analyze",

                context={
                    **(request.context or {}),
                    "workflow": "analysis",
                },

                metadata={
                    **(request.metadata or {}),
                    "workflow": "analysis",
                },
            )
        except Exception:
            logger.exception("[ANALYSIS] agent_failed; falling back to built-in analysis")
            return self._build_fallback_result(request)