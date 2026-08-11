from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from services.resume_intelligence.agents.schemas import (
    AgentResponse,
)


@dataclass
class AgentEvaluationCriteria:
    minimum_confidence: float = 0.60

    require_success: bool = True
    require_evidence: bool = True

    expected_tools: List[str] = field(
        default_factory=list
    )

    forbidden_tools: List[str] = field(
        default_factory=list
    )

    maximum_errors: int = 0


@dataclass
class AgentEvaluationResult:
    passed: bool

    success_score: float
    execution_score: float
    evidence_score: float
    confidence_score: float
    error_score: float

    overall_score: float

    issues: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "passed": self.passed,

            "success_score":
                self.success_score,

            "execution_score":
                self.execution_score,

            "evidence_score":
                self.evidence_score,

            "confidence_score":
                self.confidence_score,

            "error_score":
                self.error_score,

            "overall_score":
                self.overall_score,

            "issues":
                self.issues,

            "metadata":
                self.metadata,
        }


class AgentEvaluator:
    """
    Evaluates an end-to-end agent run.

    Evaluates:
    - workflow success
    - expected tool execution
    - unauthorized/unexpected tool usage
    - evidence availability
    - execution confidence
    - runtime errors
    """

    def evaluate(
        self,
        *,
        response: AgentResponse,
        criteria: Optional[
            AgentEvaluationCriteria
        ] = None,
    ) -> AgentEvaluationResult:

        criteria = (
            criteria
            or AgentEvaluationCriteria()
        )

        issues: List[str] = []

        # ----------------------------------------
        # Success
        # ----------------------------------------

        if criteria.require_success:

            success_score = (
                1.0
                if response.success
                else 0.0
            )

            if not response.success:

                issues.append(
                    "Agent run was not successful."
                )

        else:

            success_score = 1.0

        # ----------------------------------------
        # Tool execution
        # ----------------------------------------

        actual_tools = {
            str(tool).strip()
            for tool
            in response.actions_performed
            if str(tool).strip()
        }

        expected_tools = {
            str(tool).strip()
            for tool
            in criteria.expected_tools
            if str(tool).strip()
        }

        forbidden_tools = {
            str(tool).strip()
            for tool
            in criteria.forbidden_tools
            if str(tool).strip()
        }

        if expected_tools:

            matched = len(
                actual_tools
                & expected_tools
            )

            execution_score = (
                matched
                / len(expected_tools)
            )

            missing = (
                expected_tools
                - actual_tools
            )

            if missing:

                issues.append(
                    "Expected tools were not executed: "
                    + ", ".join(
                        sorted(missing)
                    )
                )

        else:

            execution_score = 1.0

        forbidden_used = (
            actual_tools
            & forbidden_tools
        )

        if forbidden_used:

            execution_score = 0.0

            issues.append(
                "Forbidden tools were executed: "
                + ", ".join(
                    sorted(
                        forbidden_used
                    )
                )
            )

        # ----------------------------------------
        # Evidence
        # ----------------------------------------

        if criteria.require_evidence:

            evidence_score = (
                1.0
                if response.evidence
                else 0.0
            )

            if not response.evidence:

                issues.append(
                    "Agent response contained "
                    "no supporting evidence."
                )

        else:

            evidence_score = 1.0

        # ----------------------------------------
        # Confidence
        # ----------------------------------------

        confidence = (
            float(
                response.confidence
                or 0.0
            )
        )

        confidence_score = max(
            0.0,
            min(
                confidence,
                1.0
            )
        )

        if (
            confidence_score
            < criteria.minimum_confidence
        ):

            issues.append(
                "Execution confidence was below "
                "the configured threshold."
            )

        # ----------------------------------------
        # Errors
        # ----------------------------------------

        error_count = len(
            response.errors
        )

        if (
            error_count
            <= criteria.maximum_errors
        ):

            error_score = 1.0

        else:

            excess = (
                error_count
                - criteria.maximum_errors
            )

            error_score = max(
                0.0,
                1.0
                - (
                    excess * 0.25
                )
            )

            issues.append(
                "Agent produced more errors than allowed."
            )

        # ----------------------------------------
        # Overall
        # ----------------------------------------

        overall = (
            success_score * 0.25
            + execution_score * 0.25
            + evidence_score * 0.20
            + confidence_score * 0.20
            + error_score * 0.10
        )

        overall = round(
            max(
                0.0,
                min(
                    overall,
                    1.0
                )
            ),
            4,
        )

        passed = (
            overall >= 0.70
            and (
                not criteria.require_success
                or response.success
            )
            and not forbidden_used
            and (
                confidence_score
                >= criteria.minimum_confidence
            )
        )

        return AgentEvaluationResult(
            passed=passed,

            success_score=round(
                success_score,
                4
            ),

            execution_score=round(
                execution_score,
                4
            ),

            evidence_score=round(
                evidence_score,
                4
            ),

            confidence_score=round(
                confidence_score,
                4
            ),

            error_score=round(
                error_score,
                4
            ),

            overall_score=overall,

            issues=issues,

            metadata={
                "actual_tools":
                    sorted(actual_tools),

                "expected_tools":
                    sorted(
                        expected_tools
                    ),

                "forbidden_tools":
                    sorted(
                        forbidden_tools
                    ),

                "error_count":
                    error_count,

                "evidence_count":
                    len(
                        response.evidence
                    ),
            },
        )

    def evaluate_batch(
        self,
        evaluations: Iterable[
            tuple[
                AgentResponse,
                AgentEvaluationCriteria,
            ]
        ],
    ) -> Dict[str, Any]:

        results = [
            self.evaluate(
                response=response,
                criteria=criteria,
            )
            for response, criteria
            in evaluations
        ]

        total = len(results)

        if not total:

            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "average_score": 0.0,
                "results": [],
            }

        passed = sum(
            result.passed
            for result in results
        )

        average_score = sum(
            result.overall_score
            for result in results
        ) / total

        return {
            "total":
                total,

            "passed":
                passed,

            "failed":
                total - passed,

            "pass_rate":
                round(
                    passed / total,
                    4
                ),

            "average_score":
                round(
                    average_score,
                    4
                ),

            "results": [
                result.to_dict()
                for result in results
            ],
        }