from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from services.resume_intelligence.agents.schemas import (
    AgentRequest,
)

from .resume_context import ResumeContext
from .job_context import JobContext


@dataclass
class AgentExecutionContext:
    """
    Complete working context available to the agent.

    This object separates user input from derived
    resume/job intelligence.
    """

    request: AgentRequest

    resume: Optional[
        ResumeContext
    ] = None

    job: Optional[
        JobContext
    ] = None

    additional_context: Optional[
        Dict[str, Any]
    ] = None

    def __post_init__(self) -> None:

        if self.additional_context is None:
            self.additional_context = {}

    @property
    def has_resume(self) -> bool:
        return self.resume is not None

    @property
    def has_job(self) -> bool:
        return self.job is not None

    def to_dict(
        self,
        *,
        include_raw_text: bool = True
    ) -> Dict[str, Any]:

        return {
            "request": {
                "request_id":
                    self.request.request_id,

                "message":
                    self.request.message,

                "mode":
                    self.request.mode,

                "user_id":
                    self.request.user_id,

                "session_id":
                    self.request.session_id,

                "conversation_id":
                    self.request.conversation_id,
            },

            "resume": (
                self.resume.to_dict(
                    include_raw_text=include_raw_text
                )
                if self.resume
                else None
            ),

            "job": (
                self.job.to_dict(
                    include_raw_text=include_raw_text
                )
                if self.job
                else None
            ),

            "additional_context":
                self.additional_context,
        }


class ContextBuilder:
    """
    Builds standardized agent execution context.

    It accepts intelligence produced by the existing
    NLP, ATS, matching and recommendation layers.
    """

    def build(
        self,
        request: AgentRequest,
        *,
        resume_analysis: Optional[
            Dict[str, Any]
        ] = None,
        ats_result: Optional[
            Dict[str, Any]
        ] = None,
        recommendation_result: Optional[
            Dict[str, Any]
        ] = None,
        job_analysis: Optional[
            Dict[str, Any]
        ] = None,
        additional_context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> AgentExecutionContext:

        if not isinstance(
            request,
            AgentRequest
        ):
            raise TypeError(
                "request must be an AgentRequest."
            )

        resume_context = (
            self._build_resume_context(
                request=request,
                resume_analysis=resume_analysis,
                ats_result=ats_result,
                recommendation_result=(
                    recommendation_result
                ),
            )
        )

        job_context = (
            self._build_job_context(
                request=request,
                job_analysis=job_analysis,
            )
        )

        merged_context = {}

        if request.context:
            merged_context.update(
                request.context
            )

        if additional_context:
            merged_context.update(
                additional_context
            )

        return AgentExecutionContext(
            request=request,
            resume=resume_context,
            job=job_context,
            additional_context=merged_context,
        )

    def _build_resume_context(
        self,
        *,
        request: AgentRequest,
        resume_analysis: Optional[
            Dict[str, Any]
        ],
        ats_result: Optional[
            Dict[str, Any]
        ],
        recommendation_result: Optional[
            Dict[str, Any]
        ],
    ) -> Optional[ResumeContext]:

        if not request.resume_text:
            return None

        resume_analysis = (
            resume_analysis or {}
        )

        ats_result = (
            ats_result or {}
        )

        recommendation_result = (
            recommendation_result or {}
        )

        recommendations = (
            recommendation_result.get(
                "recommendations",
                request.recommendations,
            )
            or []
        )

        name = (
            resume_analysis.get("name")
            or resume_analysis.get(
                "full_name"
            )
        )

        skills = (
            resume_analysis.get(
                "skills",
                []
            )
            or []
        )

        detected_role = (
            resume_analysis.get(
                "detected_role"
            )
            or resume_analysis.get(
                "role"
            )
        )

        return ResumeContext(
            raw_text=request.resume_text,

            name=name,

            email=resume_analysis.get(
                "email"
            ),

            phone=resume_analysis.get(
                "phone"
            ),

            detected_role=detected_role,

            skills=skills,

            entities=(
                resume_analysis.get(
                    "entities",
                    {}
                )
                or {}
            ),

            sections=(
                resume_analysis.get(
                    "sections",
                    {}
                )
                or {}
            ),

            ats_result=ats_result,

            recommendations=(
                recommendations
            ),

            metadata={
                "analysis_available":
                    bool(resume_analysis),

                "ats_available":
                    bool(ats_result),

                "recommendations_available":
                    bool(recommendations),
            },
        )

    def _build_job_context(
        self,
        *,
        request: AgentRequest,
        job_analysis: Optional[
            Dict[str, Any]
        ],
    ) -> Optional[JobContext]:

        if not request.job_description:
            return None

        job_analysis = (
            job_analysis or {}
        )

        return JobContext(
            raw_text=(
                request.job_description
            ),

            title=(
                job_analysis.get(
                    "title"
                )
                or job_analysis.get(
                    "role"
                )
            ),

            company=job_analysis.get(
                "company"
            ),

            required_skills=(
                job_analysis.get(
                    "required_skills",
                    []
                )
                or []
            ),

            preferred_skills=(
                job_analysis.get(
                    "preferred_skills",
                    []
                )
                or []
            ),

            requirements=(
                job_analysis.get(
                    "requirements",
                    []
                )
                or []
            ),

            responsibilities=(
                job_analysis.get(
                    "responsibilities",
                    []
                )
                or []
            ),

            keywords=(
                job_analysis.get(
                    "keywords",
                    []
                )
                or []
            ),

            metadata={
                "job_analysis_available":
                    bool(job_analysis)
            },
        )