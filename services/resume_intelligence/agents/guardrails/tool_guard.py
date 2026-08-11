"""
Authorization and execution-policy guard for agent tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set


DEFAULT_ALLOWED_TOOLS = {
    "resume",
    "ats",
    "job_match",
    "skill_gap",
    "recommendation",
    "rewrite",
    "cover_letter",
}


MODE_TOOL_POLICIES = {
    "analyze": {
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
    },

    "optimize": {
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
        "rewrite",
    },

    "tailor": {
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
        "rewrite",
    },

    "rewrite": {
        "resume",
        "recommendation",
        "rewrite",
    },

    "cover_letter": {
        "resume",
        "job_match",
        "cover_letter",
    },

    "career_assist": {
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
        "rewrite",
        "cover_letter",
    },
}


@dataclass
class ToolGuardResult:
    allowed: bool

    tool_name: str

    reason: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict:

        return {
            "allowed": self.allowed,
            "tool_name": self.tool_name,
            "reason": self.reason,
            "warnings": self.warnings,
        }


class ToolGuard:
    """
    Enforces an allowlist and mode-based tool permissions.

    Later subscription-plan and organization policies can
    be injected without changing ToolExecutor.
    """

    def __init__(
        self,
        *,
        allowed_tools: Optional[
            Iterable[str]
        ] = None,
    ) -> None:

        source = (
            allowed_tools
            if allowed_tools is not None
            else DEFAULT_ALLOWED_TOOLS
        )

        self.allowed_tools: Set[str] = {
            self._normalize_tool_name(name)
            for name in source
        }

    @staticmethod
    def _normalize_tool_name(
        tool_name: str
    ) -> str:

        normalized = (
            tool_name or ""
        ).strip().lower()

        if not normalized:
            raise ValueError(
                "tool_name is required."
            )

        return normalized

    def authorize(
        self,
        tool_name: str,
        *,
        mode: str,
        plan_allowed_tools: Optional[
            Iterable[str]
        ] = None,
        organization_allowed_tools: Optional[
            Iterable[str]
        ] = None,
    ) -> ToolGuardResult:

        tool_name = (
            self._normalize_tool_name(
                tool_name
            )
        )

        mode = (
            mode or "analyze"
        ).strip().lower()

        if tool_name not in self.allowed_tools:

            return ToolGuardResult(
                allowed=False,
                tool_name=tool_name,
                reason=(
                    "Tool is not present in the "
                    "global agent allowlist."
                ),
            )

        mode_tools = MODE_TOOL_POLICIES.get(
            mode
        )

        if mode_tools is None:

            return ToolGuardResult(
                allowed=False,
                tool_name=tool_name,
                reason=(
                    f"Unsupported agent mode: {mode}"
                ),
            )

        if tool_name not in mode_tools:

            return ToolGuardResult(
                allowed=False,
                tool_name=tool_name,
                reason=(
                    f"Tool '{tool_name}' is not allowed "
                    f"in '{mode}' mode."
                ),
            )

        if plan_allowed_tools is not None:

            plan_tools = {
                self._normalize_tool_name(name)
                for name in plan_allowed_tools
            }

            if tool_name not in plan_tools:

                return ToolGuardResult(
                    allowed=False,
                    tool_name=tool_name,
                    reason=(
                        "Tool is unavailable for the "
                        "current subscription plan."
                    ),
                )

        if organization_allowed_tools is not None:

            organization_tools = {
                self._normalize_tool_name(name)
                for name
                in organization_allowed_tools
            }

            if tool_name not in organization_tools:

                return ToolGuardResult(
                    allowed=False,
                    tool_name=tool_name,
                    reason=(
                        "Tool is disabled by organization policy."
                    ),
                )

        return ToolGuardResult(
            allowed=True,
            tool_name=tool_name,
        )