from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class ATSEvaluationCase:
    case_id: str
    resume_text: str

    job_description: Optional[str] = None

    expected_min_score: Optional[float] = None
    expected_max_score: Optional[float] = None

    expected_strengths: List[str] = field(
        default_factory=list
    )

    expected_weaknesses: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ATSEvaluationResult:
    case_id: str

    passed: bool

    actual_score: Optional[float]

    score_valid: bool
    strengths_valid: bool
    weaknesses_valid: bool

    errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "actual_score": self.actual_score,
            "score_valid": self.score_valid,
            "strengths_valid": self.strengths_valid,
            "weaknesses_valid": self.weaknesses_valid,
            "errors": self.errors,
            "metadata": self.metadata,
        }


class ATSEvaluator:
    """
    Evaluates ATS engine behavior against deterministic
    acceptance criteria.

    The evaluator does not define whether an ATS score
    predicts hiring outcomes.
    """

    def evaluate(
        self,
        *,
        case: ATSEvaluationCase,
        actual_result: Dict[str, Any],
    ) -> ATSEvaluationResult:

        errors: List[str] = []

        score = self._extract_score(
            actual_result
        )

        score_valid = True

        if score is None:

            score_valid = False

            errors.append(
                "ATS result did not contain a valid score."
            )

        else:

            if (
                case.expected_min_score is not None
                and score < case.expected_min_score
            ):
                score_valid = False

                errors.append(
                    "ATS score was below the expected minimum."
                )

            if (
                case.expected_max_score is not None
                and score > case.expected_max_score
            ):
                score_valid = False

                errors.append(
                    "ATS score exceeded the expected maximum."
                )

        actual_strengths = self._normalize_items(
            actual_result.get(
                "strengths",
                []
            )
        )

        actual_weaknesses = self._normalize_items(
            actual_result.get(
                "weaknesses",
                []
            )
        )

        strengths_valid = self._contains_expected(
            expected=case.expected_strengths,
            actual=actual_strengths,
        )

        weaknesses_valid = self._contains_expected(
            expected=case.expected_weaknesses,
            actual=actual_weaknesses,
        )

        if not strengths_valid:
            errors.append(
                "Expected ATS strengths were not detected."
            )

        if not weaknesses_valid:
            errors.append(
                "Expected ATS weaknesses were not detected."
            )

        passed = all(
            (
                score_valid,
                strengths_valid,
                weaknesses_valid,
            )
        )

        return ATSEvaluationResult(
            case_id=case.case_id,
            passed=passed,
            actual_score=score,
            score_valid=score_valid,
            strengths_valid=strengths_valid,
            weaknesses_valid=weaknesses_valid,
            errors=errors,
        )

    def evaluate_batch(
        self,
        cases: Iterable[
            tuple[
                ATSEvaluationCase,
                Dict[str, Any],
            ]
        ],
    ) -> Dict[str, Any]:

        results = [
            self.evaluate(
                case=case,
                actual_result=result,
            )
            for case, result in cases
        ]

        total = len(results)

        passed = sum(
            1
            for result in results
            if result.passed
        )

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,

            "pass_rate": (
                round(
                    passed / total,
                    4
                )
                if total
                else 0.0
            ),

            "results": [
                result.to_dict()
                for result in results
            ],
        }

    @staticmethod
    def _extract_score(
        result: Dict[str, Any]
    ) -> Optional[float]:

        candidates = (
            result.get("overall_score"),
            result.get("score"),
            result.get("ats_score"),
        )

        for candidate in candidates:

            if isinstance(
                candidate,
                dict
            ):
                candidate = candidate.get(
                    "value"
                )

            try:
                if candidate is not None:
                    return float(candidate)

            except (
                TypeError,
                ValueError
            ):
                continue

        return None

    @staticmethod
    def _normalize_items(
        items: Any
    ) -> List[str]:

        if not isinstance(
            items,
            (list, tuple, set)
        ):
            return []

        return [
            str(item).casefold().strip()
            for item in items
            if str(item).strip()
        ]

    @staticmethod
    def _contains_expected(
        *,
        expected: List[str],
        actual: List[str],
    ) -> bool:

        if not expected:
            return True

        actual_text = " ".join(
            actual
        )

        return all(
            expected_item.casefold().strip()
            in actual_text

            for expected_item
            in expected
        )