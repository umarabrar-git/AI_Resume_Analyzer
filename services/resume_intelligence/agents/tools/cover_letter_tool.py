from __future__ import annotations

from typing import Any, Dict

from services.resume_intelligence.generative import (
    GenerationRequest,
    GenerationService,
    TASK_COVER_LETTER,
)

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .base_tool import (
    BaseTool,
    ToolDefinition,
)


class CoverLetterTool(BaseTool):

    definition = ToolDefinition(
        name="cover_letter",
        description=(
            "Generate a professional cover letter "
            "grounded in the candidate resume."
        ),
        category="generation",
        requires_resume=True,
        parameters={
            "type": "object",
            "properties": {
                "target_role": {
                    "type": "string",
                },
                "instructions": {
                    "type": "string",
                },
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
            task=TASK_COVER_LETTER,

            resume_text=resume[
                "raw_text"
            ],

            job_description=(
                job.get("raw_text")
                or None
            ),

            target_role=(
                arguments.get(
                    "target_role"
                )
                or job.get("title")
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
                    "Cover letter generation "
                    "failed validation."
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
                    "type": "grounded_cover_letter",
                }
            ],
        )