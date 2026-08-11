from __future__ import annotations

from typing import Any, Dict

from services.resume_intelligence.matching.job_matcher import (
    match_resume_to_job,
)

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .base_tool import (
    BaseTool,
    ToolDefinition,
)


class JobMatchTool(BaseTool):

    definition = ToolDefinition(
        name="job_match",
        description=(
            "Compare the candidate resume with "
            "a target job description."
        ),
        category="matching",
        requires_resume=True,
        requires_job=True,
        parameters={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    )

    def execute(
        self,
        *,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ToolResult:

        resume_text = (
            context["resume"].get(
                "raw_text"
            )
        )

        job_text = (
            context["job"].get(
                "raw_text"
            )
        )

        if not resume_text or not job_text:

            return ToolResult.failed(
                tool_name=self.name,
                error_code="MATCH_CONTEXT_MISSING",
                error_message=(
                    "Resume and job description "
                    "are required."
                ),
            )

        result = match_resume_to_job(
            resume_text=resume_text,
            job_description=job_text,
        )

        return ToolResult.successful(
            tool_name=self.name,
            data=result,
            evidence=[
                {
                    "source": "job_match_engine",
                    "type": "resume_job_comparison",
                }
            ],
        )