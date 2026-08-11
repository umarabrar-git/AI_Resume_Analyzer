from __future__ import annotations

from typing import Any, Dict

from services.resume_intelligence.recommendations import (
    generate_recommendations,
)

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .base_tool import (
    BaseTool,
    ToolDefinition,
)


class RecommendationTool(BaseTool):

    definition = ToolDefinition(
        name="recommendation",
        description=(
            "Generate prioritized resume improvement "
            "recommendations from analysis evidence."
        ),
        category="recommendation",
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

        resume_text = resume.get(
            "raw_text"
        )

        ats_result = resume.get(
            "ats"
        ) or {}

        if not ats_result:

            return ToolResult.failed(
                tool_name=self.name,
                error_code="ATS_RESULT_REQUIRED",
                error_message=(
                    "ATS analysis must be available "
                    "before recommendations are generated."
                ),
            )

        result = generate_recommendations(
            resume_text=resume_text,
            ats_result=ats_result,
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
                    "source": "recommendation_engine",
                    "type": "resume_recommendations",
                }
            ],
        )