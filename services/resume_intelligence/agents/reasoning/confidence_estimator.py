from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from services.resume_intelligence.agents.schemas import (
    AgentPlan,
    PlanStepStatus,
    ToolResult,
)

from .evidence_collector import (
    EvidenceItem,
)


@dataclass
class ConfidenceResult:
    score: float
    level: str

    factors: Dict[str, float] = field(
        default_factory=dict
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict:

        return {
            "score": self.score,
            "level": self.level,
            "factors": self.factors,
            "warnings": self.warnings,
        }


class ConfidenceEstimator:
    """
    Estimates operational confidence from execution evidence.

    This is not a probability that the generated text is true.
    It is an execution-quality indicator.
    """

    def estimate(
        self,
        *,
        plan: AgentPlan,
        tool_results: Iterable[
            ToolResult
        ],
        evidence: Iterable[
            EvidenceItem
        ],
    ) -> ConfidenceResult:

        results = list(
            tool_results
        )

        evidence_items = list(
            evidence
        )

        total_steps = len(
            plan.steps
        )

        completed_steps = sum(
            1
            for step in plan.steps
            if step.status
            == PlanStepStatus.COMPLETED
        )

        required_steps = [
            step
            for step in plan.steps
            if step.required
        ]

        required_completed = sum(
            1
            for step in required_steps
            if step.status
            == PlanStepStatus.COMPLETED
        )

        successful_results = sum(
            1
            for result in results
            if result.success
        )

        failed_results = sum(
            1
            for result in results
            if not result.success
        )

        execution_ratio = (
            completed_steps
            / total_steps
            if total_steps
            else 0.0
        )

        required_ratio = (
            required_completed
            / len(required_steps)
            if required_steps
            else 1.0
        )

        tool_success_ratio = (
            successful_results
            / len(results)
            if results
            else 0.0
        )

        evidence_factor = min(
            len(evidence_items) / 5.0,
            1.0,
        )

        failure_penalty = min(
            failed_results * 0.10,
            0.30,
        )

        score = (
            execution_ratio * 0.30
            + required_ratio * 0.35
            + tool_success_ratio * 0.20
            + evidence_factor * 0.15
            - failure_penalty
        )

        score = round(
            max(
                0.0,
                min(
                    score,
                    1.0
                )
            ),
            4,
        )

        warnings = []

        if required_ratio < 1.0:

            warnings.append(
                "One or more required agent steps were not completed."
            )

        if failed_results:

            warnings.append(
                f"{failed_results} tool execution(s) failed."
            )

        if not evidence_items:

            warnings.append(
                "No supporting evidence was collected."
            )

        return ConfidenceResult(
            score=score,
            level=self._level(
                score
            ),
            factors={
                "execution_completion":
                    round(
                        execution_ratio,
                        4
                    ),

                "required_step_completion":
                    round(
                        required_ratio,
                        4
                    ),

                "tool_success":
                    round(
                        tool_success_ratio,
                        4
                    ),

                "evidence_coverage":
                    round(
                        evidence_factor,
                        4
                    ),

                "failure_penalty":
                    round(
                        failure_penalty,
                        4
                    ),
            },
            warnings=warnings,
        )

    @staticmethod
    def _level(
        score: float
    ) -> str:

        if score >= 0.85:
            return "high"

        if score >= 0.65:
            return "moderate"

        if score >= 0.40:
            return "limited"

        return "low"