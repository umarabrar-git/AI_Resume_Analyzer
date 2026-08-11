from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, Iterable, Optional

from services.resume_intelligence.agents.guardrails import (
    ToolGuard,
)

from services.resume_intelligence.agents.schemas import (
    ToolResult,
)

from .tool_registry import ToolRegistry


class ToolExecutor:
    """
    Secure tool execution coordinator.

    Responsibilities:
    - registry lookup
    - authorization
    - argument validation
    - context requirement checks
    - exception isolation
    - execution timing
    """

    def __init__(
        self,
        registry: ToolRegistry,
        *,
        tool_guard: Optional[
            ToolGuard
        ] = None,
    ) -> None:

        self.registry = registry

        self.tool_guard = (
            tool_guard
            or ToolGuard()
        )

    def execute(
        self,
        tool_name: str,
        *,
        arguments: Optional[
            Dict[str, Any]
        ] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
        mode: str = "analyze",
        plan_allowed_tools: Optional[
            Iterable[str]
        ] = None,
        organization_allowed_tools: Optional[
            Iterable[str]
        ] = None,
    ) -> ToolResult:

        started_at = perf_counter()

        try:

            authorization = (
                self.tool_guard.authorize(
                    tool_name,
                    mode=mode,
                    plan_allowed_tools=(
                        plan_allowed_tools
                    ),
                    organization_allowed_tools=(
                        organization_allowed_tools
                    ),
                )
            )

            if not authorization.allowed:

                return ToolResult.failed(
                    tool_name=tool_name,
                    error_code="TOOL_NOT_AUTHORIZED",
                    error_message=(
                        authorization.reason
                        or "Tool execution denied."
                    ),
                    duration_ms=self._elapsed(
                        started_at
                    ),
                )

            tool = self.registry.get(
                tool_name
            )

            safe_arguments = (
                tool.validate_arguments(
                    arguments
                )
            )

            execution_context = (
                context or {}
            )

            requirement_error = (
                self._validate_context(
                    tool=tool,
                    context=execution_context,
                )
            )

            if requirement_error:

                return ToolResult.failed(
                    tool_name=tool.name,
                    error_code=(
                        "MISSING_TOOL_CONTEXT"
                    ),
                    error_message=(
                        requirement_error
                    ),
                    duration_ms=self._elapsed(
                        started_at
                    ),
                )

            result = tool.execute(
                arguments=safe_arguments,
                context=execution_context,
            )

            if not isinstance(
                result,
                ToolResult
            ):
                raise TypeError(
                    f"Tool '{tool.name}' returned "
                    "an invalid result type."
                )

            result.duration_ms = (
                result.duration_ms
                or self._elapsed(
                    started_at
                )
            )

            return result

        except KeyError as exc:

            return ToolResult.failed(
                tool_name=tool_name,
                error_code="TOOL_NOT_FOUND",
                error_message=str(exc),
                duration_ms=self._elapsed(
                    started_at
                ),
            )

        except (ValueError, TypeError) as exc:

            return ToolResult.failed(
                tool_name=tool_name,
                error_code="INVALID_TOOL_INPUT",
                error_message=str(exc),
                duration_ms=self._elapsed(
                    started_at
                ),
            )

        except Exception as exc:

            return ToolResult.failed(
                tool_name=tool_name,
                error_code="TOOL_EXECUTION_ERROR",
                error_message=(
                    f"{type(exc).__name__}: {exc}"
                ),
                retryable=False,
                duration_ms=self._elapsed(
                    started_at
                ),
            )

    @staticmethod
    def _validate_context(
        *,
        tool,
        context: Dict[str, Any]
    ) -> Optional[str]:

        resume = context.get(
            "resume"
        )

        job = context.get(
            "job"
        )

        if (
            tool.definition.requires_resume
            and not resume
        ):
            return (
                f"Tool '{tool.name}' requires "
                "resume context."
            )

        if (
            tool.definition.requires_job
            and not job
        ):
            return (
                f"Tool '{tool.name}' requires "
                "job context."
            )

        return None

    @staticmethod
    def _elapsed(
        started_at: float
    ) -> float:

        return round(
            (
                perf_counter()
                - started_at
            )
            * 1000,
            2
        )