from __future__ import annotations

from typing import Any, Dict

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .base_tool import (
    BaseTool,
    ToolDefinition,
)


class ResumeTool(BaseTool):

    definition = ToolDefinition(
        name="resume",
        description=(
            "Retrieve structured information about "
            "the candidate resume."
        ),
        category="resume",
        requires_resume=True,
        parameters={
            "type": "object",
            "properties": {
                "include_raw_text": {
                    "type": "boolean",
                    "description": (
                        "Whether raw resume text "
                        "should be included."
                    ),
                }
            },
            "additionalProperties": False,
        },
    )

    def execute(
        self,
        *,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ToolResult:

        resume = context.get(
            "resume",
            {}
        )

        include_raw = bool(
            arguments.get(
                "include_raw_text",
                False
            )
        )

        data = dict(resume)

        if not include_raw:
            data.pop(
                "raw_text",
                None
            )

        return ToolResult.successful(
            tool_name=self.name,
            data=data,
            evidence=[
                {
                    "source": "resume",
                    "type": "candidate_document",
                }
            ],
        )