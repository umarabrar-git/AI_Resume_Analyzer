from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set

from .intent_classifier import AgentIntent


INTENT_TOOL_MAP = {
    AgentIntent.RESUME_ANALYSIS: [
        "resume",
        "ats",
        "recommendation",
    ],

    AgentIntent.ATS_ANALYSIS: [
        "resume",
        "ats",
    ],

    AgentIntent.JOB_MATCH: [
        "resume",
        "ats",
        "job_match",
        "skill_gap",
    ],

    AgentIntent.SKILL_GAP: [
        "resume",
        "job_match",
        "skill_gap",
    ],

    AgentIntent.RECOMMENDATIONS: [
        "resume",
        "ats",
        "recommendation",
    ],

    AgentIntent.RESUME_REWRITE: [
        "resume",
        "ats",
        "recommendation",
        "rewrite",
    ],

    AgentIntent.RESUME_OPTIMIZATION: [
        "resume",
        "ats",
        "recommendation",
        "rewrite",
    ],

    AgentIntent.JOB_TAILORING: [
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
        "rewrite",
    ],

    AgentIntent.COVER_LETTER: [
        "resume",
        "job_match",
        "cover_letter",
    ],

    AgentIntent.CAREER_ASSISTANCE: [
        "resume",
        "ats",
        "recommendation",
    ],

    AgentIntent.UNKNOWN: [],
}


@dataclass
class ToolSelection:
    tools: List[str]

    excluded_tools: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict:

        return {
            "tools": self.tools,
            "excluded_tools":
                self.excluded_tools,
            "warnings":
                self.warnings,
        }


class ToolSelector:
    """
    Selects capabilities required for an agent intent.

    Registry availability and SaaS-plan restrictions
    can both be applied here.
    """

    def select(
        self,
        intent: AgentIntent,
        *,
        available_tools: Iterable[str],
        plan_allowed_tools: Optional[
            Iterable[str]
        ] = None,
        has_resume: bool = True,
        has_job: bool = False,
    ) -> ToolSelection:

        requested = list(
            INTENT_TOOL_MAP.get(
                intent,
                []
            )
        )

        available: Set[str] = {
            str(name).strip().lower()
            for name in available_tools
        }

        plan_allowed = None

        if plan_allowed_tools is not None:

            plan_allowed = {
                str(name).strip().lower()
                for name
                in plan_allowed_tools
            }

        selected = []
        excluded = []
        warnings = []

        for tool in requested:

            if tool not in available:

                excluded.append(tool)

                warnings.append(
                    f"Required capability '{tool}' "
                    "is not currently available."
                )

                continue

            if (
                plan_allowed is not None
                and tool not in plan_allowed
            ):

                excluded.append(tool)

                warnings.append(
                    f"Capability '{tool}' is not "
                    "available for the current plan."
                )

                continue

            if (
                tool != "cover_letter"
                and tool != "resume"
                and not has_resume
            ):

                excluded.append(tool)

                warnings.append(
                    f"Capability '{tool}' requires "
                    "resume context."
                )

                continue

            if (
                tool in {
                    "job_match",
                    "skill_gap",
                }
                and not has_job
            ):

                excluded.append(tool)

                warnings.append(
                    f"Capability '{tool}' requires "
                    "a job description."
                )

                continue

            selected.append(tool)

        # Cover letters can still be produced without
        # a JD if a target role is supplied later.
        if (
            "cover_letter" in selected
            and not has_resume
        ):

            selected.remove(
                "cover_letter"
            )

            excluded.append(
                "cover_letter"
            )

            warnings.append(
                "Cover-letter generation requires "
                "resume context."
            )

        return ToolSelection(
            tools=selected,
            excluded_tools=excluded,
            warnings=warnings,
        )