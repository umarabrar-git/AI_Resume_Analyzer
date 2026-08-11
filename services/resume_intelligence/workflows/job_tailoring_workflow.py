from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from services.resume_intelligence.agents import (
    AgentService,
    get_agent_service,
)

from services.resume_intelligence.agents.schemas import (
    AgentResponse,
)


@dataclass(frozen=True)
class JobTailoringWorkflowRequest:
    resume_text: str
    job_description: str

    target_role: Optional[str] = None
    instructions: Optional[str] = None

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    organization_id: Optional[str] = None

    plan: Optional[str] = None

    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class JobTailoringWorkflow:
    """
    Target-job resume tailoring workflow.

    Pipeline:
        Resume + Job Description
                 ↓
             Job Match
                 ↓
             Skill Gap
                 ↓
               ATS
                 ↓
         Recommendations
                 ↓
          Grounded Rewrite
                 ↓
          Tailored Resume
    """

    def __init__(
        self,
        agent_service: Optional[AgentService] = None,
    ) -> None:

        self.agent_service = (
            agent_service
            or get_agent_service()
        )

    def run(
        self,
        request: JobTailoringWorkflowRequest,
    ) -> AgentResponse:

        resume_text = (
            request.resume_text or ""
        ).strip()

        job_description = (
            request.job_description or ""
        ).strip()

        if not resume_text:
            raise ValueError(
                "Resume text is required."
            )

        if not job_description:
            raise ValueError(
                "Job description is required "
                "for job tailoring."
            )

        target_role = (
            request.target_role or ""
        ).strip()

        instructions = (
            request.instructions or ""
        ).strip()

        goal = (
            "Tailor this resume for the supplied job. "
            "Analyze job fit, ATS compatibility and skill gaps, "
            "then rewrite the resume to emphasize relevant "
            "candidate evidence. Never add a missing skill or "
            "qualification unless supported by the resume."
        )

        if target_role:
            goal += (
                f" Target role: {target_role}."
            )

        if instructions:
            goal += (
                f" User requirements: {instructions}"
            )

        return self.agent_service.run(
            message=goal,

            resume_text=resume_text,

            job_description=job_description,

            user_id=request.user_id,
            session_id=request.session_id,

            conversation_id=(
                request.conversation_id
            ),

            organization_id=(
                request.organization_id
            ),

            plan=request.plan,

            mode="tailor",

            context={
                **(request.context or {}),

                "workflow":
                    "job_tailoring",

                "target_role":
                    target_role or None,

                "user_instructions":
                    instructions or None,
            },

            metadata={
                **(request.metadata or {}),

                "workflow":
                    "job_tailoring",
            },
        )