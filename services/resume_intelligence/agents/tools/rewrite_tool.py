from __future__ import annotations

from typing import Any, Dict

from services.resume_intelligence.generative import (
    GenerationService,
    GenerationRequest,
    TASK_RESUME_REWRITE,
)

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .base_tool import (
    BaseTool,
    ToolDefinition,
)


class RewriteTool(BaseTool):

    definition = ToolDefinition(
        name="rewrite",
        description=(
            "Rewrite or optimize resume content "
            "using grounded Generative AI."
        ),
        category="generation",
        requires_resume=True,
        parameters={
            "type": "object",
            "properties": {
                "instructions": {
                    "type": "string",
                }
            },
            "additionalProperties": False,
        },
    )

    def __init__(
        self,
        generation_service: GenerationService
    ) -> None:

        self.generation_service = (
            generation_service
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

        request = GenerationRequest(
            task=TASK_RESUME_REWRITE,

            resume_text=resume[
                "raw_text"
            ],

            job_description=(
                job.get("raw_text")
                or None
            ),

            recommendations=(
                resume.get(
                    "recommendations",
                    []
                )
            ),

            instructions=(
                arguments.get(
                    "instructions"
                )
            ),
        )

        response = (
            self.generation_service.generate(
                request
            )
        )

        if not response.success:

            return ToolResult.failed(
                tool_name=self.name,
                error_code=(
                    "GENERATION_FAILED"
                ),
                error_message=(
                    "Resume rewrite failed validation."
                ),
                warnings=response.warnings,
                data=response.to_dict(),
            )

        return ToolResult.successful(
            tool_name=self.name,
            data=response.to_dict(),
            warnings=response.warnings,
            evidence=[
                {
                    "source": "generative_ai",
                    "type": "grounded_resume_rewrite",
                }
            ],
        )