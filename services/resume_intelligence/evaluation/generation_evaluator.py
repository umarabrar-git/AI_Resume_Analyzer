from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from services.resume_intelligence.safety import (
    GeneratedClaimGuard,
)


@dataclass
class GenerationEvaluationResult:
    passed: bool

    factuality_score: float
    completeness_score: float
    readability_score: float

    overall_score: float

    hallucination_risk: float

    issues: List[
        Dict[str, Any]
    ] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "passed": self.passed,
            "factuality_score":
                self.factuality_score,
            "completeness_score":
                self.completeness_score,
            "readability_score":
                self.readability_score,
            "overall_score":
                self.overall_score,
            "hallucination_risk":
                self.hallucination_risk,
            "issues":
                self.issues,
            "metadata":
                self.metadata,
        }


class GenerationEvaluator:
    """
    Evaluates generated resume content.

    This deterministic evaluator can later be supplemented
    by semantic/LLM evaluators without changing callers.
    """

    def __init__(
        self,
        claim_guard: Optional[
            GeneratedClaimGuard
        ] = None,
    ) -> None:

        self.claim_guard = (
            claim_guard
            or GeneratedClaimGuard()
        )

    def evaluate(
        self,
        *,
        generated_text: str,
        source_resume: str,
        required_terms: Optional[
            List[str]
        ] = None,
        known_facts: Optional[
            List[str]
        ] = None,
    ) -> GenerationEvaluationResult:

        generated_text = (
            generated_text or ""
        ).strip()

        if not generated_text:

            return GenerationEvaluationResult(
                passed=False,
                factuality_score=0.0,
                completeness_score=0.0,
                readability_score=0.0,
                overall_score=0.0,
                hallucination_risk=1.0,
                issues=[
                    {
                        "type":
                            "empty_generation",

                        "message":
                            "Generated content is empty.",
                    }
                ],
            )

        safety_result = (
            self.claim_guard.validate(
                generated_text=generated_text,
                source_resume=source_resume,
                known_facts=known_facts,
            )
        )

        factuality_score = max(
            0.0,
            1.0
            - safety_result.risk_score
        )

        completeness_score = (
            self._completeness(
                generated_text,
                required_terms or [],
            )
        )

        readability_score = (
            self._readability(
                generated_text
            )
        )

        overall = (
            factuality_score * 0.50
            + completeness_score * 0.25
            + readability_score * 0.25
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
            safety_result.allowed
            and factuality_score >= 0.70
            and overall >= 0.70
        )

        return GenerationEvaluationResult(
            passed=passed,

            factuality_score=round(
                factuality_score,
                4
            ),

            completeness_score=round(
                completeness_score,
                4
            ),

            readability_score=round(
                readability_score,
                4
            ),

            overall_score=overall,

            hallucination_risk=(
                safety_result.risk_score
            ),

            issues=[
                issue.to_dict()
                for issue
                in safety_result.issues
            ],

            metadata={
                "claim_count":
                    len(
                        safety_result.claims
                    )
            },
        )

    @staticmethod
    def _completeness(
        text: str,
        required_terms: List[str],
    ) -> float:

        if not required_terms:
            return 1.0

        normalized = text.casefold()

        matched = sum(
            1
            for term in required_terms
            if (
                term
                and term.casefold()
                in normalized
            )
        )

        return (
            matched
            / len(required_terms)
        )

    @staticmethod
    def _readability(
        text: str
    ) -> float:
        """
        Lightweight structural readability score.

        This is not intended as a linguistic truth metric.
        """

        words = text.split()

        if not words:
            return 0.0

        sentences = [
            sentence.strip()
            for sentence
            in text.replace(
                "!",
                "."
            ).replace(
                "?",
                "."
            ).split(".")
            if sentence.strip()
        ]

        if not sentences:
            return 0.50

        average_sentence_length = (
            len(words)
            / len(sentences)
        )

        if (
            8
            <= average_sentence_length
            <= 25
        ):
            return 1.0

        if (
            5
            <= average_sentence_length
            <= 35
        ):
            return 0.80

        if (
            3
            <= average_sentence_length
            <= 45
        ):
            return 0.60

        return 0.40