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
class CoverLetterWorkflowRequest:
    resume_text: str

    job_description: Optional[str] = None
    target_role: Optional[str] = None

    company_name: Optional[str] = None

    instructions: Optional[str] = None

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    organization_id: Optional[str] = None

    plan: Optional[str] = None

    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CoverLetterWorkflow:
    """
    Grounded cover-letter generation workflow.

    Candidate claims must originate from resume evidence.
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
        request: CoverLetterWorkflowRequest,
    ) -> AgentResponse:

        resume_text = (
            request.resume_text or ""
        ).strip()

        if not resume_text:
            raise ValueError(
                "Resume text is required."
            )

        target_role = (
            request.target_role or ""
        ).strip()

        company_name = (
            request.company_name or ""
        ).strip()

        instructions = (
            request.instructions or ""
        ).strip()

        goal_parts = [
            "Create a professional cover letter grounded "
            "strictly in the candidate's resume evidence."
        ]

        if target_role:
            goal_parts.append(
                f"Target role: {target_role}."
            )

        if company_name:
            goal_parts.append(
                f"Target company: {company_name}."
            )

        if request.job_description:
            goal_parts.append(
                "Use the supplied job description to improve "
                "relevance without inventing candidate claims."
            )

        if instructions:
            goal_parts.append(
                f"User requirements: {instructions}"
            )

        return self.agent_service.run(
            message=" ".join(goal_parts),

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

            mode="cover_letter",

            context={
                **(request.context or {}),

                "workflow":
                    "cover_letter",

                "target_role":
                    target_role or None,

                "company_name":
                    company_name or None,

                "user_instructions":
                    instructions or None,
            },

            metadata={
                **(request.metadata or {}),

                "workflow":
                    "cover_letter",
            },
        )