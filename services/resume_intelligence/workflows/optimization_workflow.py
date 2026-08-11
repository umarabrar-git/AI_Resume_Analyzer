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
class OptimizationWorkflowRequest:
    resume_text: str

    job_description: Optional[str] = None

    instructions: Optional[str] = None
    target_role: Optional[str] = None

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    organization_id: Optional[str] = None

    plan: Optional[str] = None

    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class OptimizationWorkflow:
    """
    Analyze and improve a resume while preserving
    candidate factual integrity.

    Pipeline:
        Resume
          ↓
        ATS
          ↓
        Recommendations
          ↓
        Generative Rewrite
          ↓
        Improved Resume
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
        request: OptimizationWorkflowRequest,
    ) -> AgentResponse:

        resume_text = (
            request.resume_text or ""
        ).strip()

        if not resume_text:
            raise ValueError(
                "Resume text is required."
            )

        instructions = (
            request.instructions or ""
        ).strip()

        target_role = (
            request.target_role or ""
        ).strip()

        goal_parts = [
            "Optimize and rewrite this resume using "
            "ATS analysis and evidence-based recommendations."
        ]

        if target_role:
            goal_parts.append(
                f"Target role: {target_role}."
            )

        if instructions:
            goal_parts.append(
                f"User requirements: {instructions}"
            )

        goal_parts.append(
            "Preserve all candidate facts and do not "
            "invent skills, achievements, metrics, "
            "employment history, or qualifications."
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

            mode="optimize",

            context={
                **(request.context or {}),

                "workflow":
                    "optimization",

                "target_role":
                    target_role or None,

                "user_instructions":
                    instructions or None,
            },

            metadata={
                **(request.metadata or {}),

                "workflow":
                    "optimization",
            },
        )