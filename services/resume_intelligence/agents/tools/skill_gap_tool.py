from __future__ import annotations

from typing import Any, Dict, List, Set

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .base_tool import (
    BaseTool,
    ToolDefinition,
)


class SkillGapTool(BaseTool):

    definition = ToolDefinition(
        name="skill_gap",
        description=(
            "Identify required job skills that "
            "are not evidenced in the resume."
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

    @staticmethod
    def _normalize(
        skills: List[str]
    ) -> Dict[str, str]:

        result = {}

        for skill in skills or []:

            value = str(skill).strip()

            if value:
                result[
                    value.casefold()
                ] = value

        return result

    def execute(
        self,
        *,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ToolResult:

        resume = context["resume"]
        job = context["job"]

        resume_skills = self._normalize(
            resume.get(
                "skills",
                []
            )
        )

        required_skills = self._normalize(
            job.get(
                "required_skills",
                []
            )
        )

        preferred_skills = self._normalize(
            job.get(
                "preferred_skills",
                []
            )
        )

        matched_required = sorted(
            required_skills[key]
            for key in (
                set(resume_skills)
                & set(required_skills)
            )
        )

        missing_required = sorted(
            required_skills[key]
            for key in (
                set(required_skills)
                - set(resume_skills)
            )
        )

        matched_preferred = sorted(
            preferred_skills[key]
            for key in (
                set(resume_skills)
                & set(preferred_skills)
            )
        )

        missing_preferred = sorted(
            preferred_skills[key]
            for key in (
                set(preferred_skills)
                - set(resume_skills)
            )
        )

        total_required = len(
            required_skills
        )

        required_match_rate = (
            round(
                len(matched_required)
                / total_required,
                4
            )
            if total_required
            else None
        )

        result = {
            "resume_skills": sorted(
                resume_skills.values()
            ),
            "matched_required_skills":
                matched_required,
            "missing_required_skills":
                missing_required,
            "matched_preferred_skills":
                matched_preferred,
            "missing_preferred_skills":
                missing_preferred,
            "required_match_rate":
                required_match_rate,
        }

        return ToolResult.successful(
            tool_name=self.name,
            data=result,
            evidence=[
                {
                    "source": "resume_and_job_context",
                    "type": "skill_gap_analysis",
                }
            ],
        )