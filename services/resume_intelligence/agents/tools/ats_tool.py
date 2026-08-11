from __future__ import annotations

from typing import Any, Dict

from services.resume_intelligence.ats import (
    analyze_ats,
)

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .base_tool import (
    BaseTool,
    ToolDefinition,
)


class ATSTool(BaseTool):

    definition = ToolDefinition(
        name="ats",
        description=(
            "Analyze resume ATS compatibility, "
            "content quality, sections and keywords."
        ),
        category="analysis",
        requires_resume=True,
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

        resume = context["resume"]

        job = context.get(
            "job"
        ) or {}

        raw_text = resume.get(
            "raw_text"
        )

        if not raw_text:
            return ToolResult.failed(
                tool_name=self.name,
                error_code="RESUME_TEXT_MISSING",
                error_message=(
                    "Resume text is unavailable."
                ),
            )

        identity = resume.get(
            "identity",
            {}
        )

        result = analyze_ats(
            resume_text=raw_text,
            name=identity.get("name"),
            email=identity.get("email"),
            phone=identity.get("phone"),
            job_description=(
                job.get("raw_text")
                or None
            ),
        )

        return ToolResult.successful(
            tool_name=self.name,
            data=result,
            evidence=[
                {
                    "source": "ats_engine",
                    "type": "resume_analysis",
                }
            ],
        )