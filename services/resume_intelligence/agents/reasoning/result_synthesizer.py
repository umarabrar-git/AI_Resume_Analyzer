from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from services.resume_intelligence.agents.schemas import (
    AgentPlan,
    AgentRequest,
    AgentResponse,
    ToolResult,
)

from .confidence_estimator import (
    ConfidenceEstimator,
)

from .evidence_collector import (
    EvidenceCollector,
    EvidenceItem,
)


class ResultSynthesizer:
    """
    Produces a grounded public AgentResponse from execution results.

    Tool results remain the source of truth.
    """

    def __init__(
        self,
        *,
        evidence_collector: Optional[
            EvidenceCollector
        ] = None,
        confidence_estimator: Optional[
            ConfidenceEstimator
        ] = None,
    ) -> None:

        self.evidence_collector = (
            evidence_collector
            or EvidenceCollector()
        )

        self.confidence_estimator = (
            confidence_estimator
            or ConfidenceEstimator()
        )

    def synthesize(
        self,
        *,
        run_id: str,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: Iterable[
            ToolResult
        ],
        final_content: Optional[str] = None,
    ) -> AgentResponse:

        results = list(
            tool_results
        )

        evidence = (
            self.evidence_collector.collect(
                results
            )
        )

        confidence = (
            self.confidence_estimator.estimate(
                plan=plan,
                tool_results=results,
                evidence=evidence,
            )
        )

        successful = [
            result
            for result in results
            if result.success
        ]

        failed = [
            result
            for result in results
            if not result.success
        ]

        required_failures = (
            self._required_failures(
                plan,
                results
            )
        )

        success = (
            not required_failures
            and bool(successful)
        )

        content = (
            final_content.strip()
            if final_content
            else self._build_fallback_content(
                request=request,
                plan=plan,
                results=successful,
            )
        )

        warnings = (
            self._collect_warnings(
                results,
                confidence.warnings,
            )
        )

        errors = [
            result.error_message
            for result in failed
            if result.error_message
        ]

        actions = [
            result.tool_name
            for result in successful
        ]

        artifacts = (
            self._extract_artifacts(
                successful
            )
        )

        return AgentResponse(
            run_id=run_id,
            request_id=request.request_id,
            success=success,
            content=content,
            intent=plan.intent,
            confidence=confidence.score,
            actions_performed=actions,
            warnings=warnings,
            errors=errors,
            evidence=[
                item.to_dict()
                for item in evidence
            ],
            artifacts=artifacts,
            metadata={
                "confidence":
                    confidence.to_dict(),

                "plan_id":
                    plan.plan_id,

                "tool_count":
                    len(results),

                "successful_tools":
                    len(successful),

                "failed_tools":
                    len(failed),

                "required_failures":
                    required_failures,
            },
        )

    @staticmethod
    def _required_failures(
        plan: AgentPlan,
        results: List[ToolResult],
    ) -> List[str]:

        result_map = {
            result.tool_name:
                result
            for result in results
        }

        failures = []

        for step in plan.steps:

            if not step.required:
                continue

            result = result_map.get(
                step.tool_name
            )

            if (
                result is None
                or not result.success
            ):
                failures.append(
                    step.tool_name
                )

        return failures

    @staticmethod
    def _collect_warnings(
        results: List[ToolResult],
        confidence_warnings: List[str],
    ) -> List[str]:

        warnings = list(
            confidence_warnings
        )

        for result in results:
            warnings.extend(
                result.warnings
            )

        # Preserve order while removing duplicates.
        return list(
            dict.fromkeys(
                warning
                for warning in warnings
                if warning
            )
        )

    @staticmethod
    def _extract_artifacts(
        results: List[ToolResult]
    ) -> List[Dict[str, Any]]:

        artifacts = []

        for result in results:

            if result.tool_name not in {
                "rewrite",
                "cover_letter",
            }:
                continue

            artifacts.append(
                {
                    "type":
                        result.tool_name,

                    "source_tool":
                        result.tool_name,

                    "execution_id":
                        result.execution_id,

                    "data":
                        result.data,
                }
            )

        return artifacts

    @staticmethod
    def _build_fallback_content(
        *,
        request: AgentRequest,
        plan: AgentPlan,
        results: List[ToolResult],
    ) -> str:
        """
        Safe deterministic fallback.

        Natural-language LLM synthesis will be added
        through the prompt/provider layer.
        """

        if not results:

            return (
                "The agent could not complete the "
                "requested analysis."
            )

        # Prefer generated artifacts when available.

        for preferred_tool in (
            "rewrite",
            "cover_letter",
        ):

            for result in reversed(
                results
            ):

                if (
                    result.tool_name
                    == preferred_tool
                ):

                    generated = (
                        ResultSynthesizer
                        ._extract_generated_content(
                            result.data
                        )
                    )

                    if generated:
                        return generated

        return (
            f"Agent completed the "
            f"'{plan.intent}' workflow using "
            f"{len(results)} successful tool "
            f"execution(s)."
        )

    @staticmethod
    def _extract_generated_content(
        data: Any
    ) -> Optional[str]:

        if isinstance(
            data,
            str
        ):
            return data.strip() or None

        if not isinstance(
            data,
            dict
        ):
            return None

        for key in (
            "content",
            "text",
            "generated_text",
            "output",
        ):

            value = data.get(
                key
            )

            if (
                isinstance(value, str)
                and value.strip()
            ):
                return value.strip()

        return None