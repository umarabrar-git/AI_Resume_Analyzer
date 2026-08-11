from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set


@dataclass
class MatchingEvaluationCase:
    case_id: str

    expected_matched_skills: List[str] = field(
        default_factory=list
    )

    expected_missing_skills: List[str] = field(
        default_factory=list
    )

    expected_min_score: Optional[float] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class MatchingEvaluationResult:
    case_id: str

    passed: bool

    precision: float
    recall: float
    f1_score: float

    missing_skill_accuracy: float

    actual_score: Optional[float] = None

    errors: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "missing_skill_accuracy":
                self.missing_skill_accuracy,
            "actual_score": self.actual_score,
            "errors": self.errors,
        }


class MatchingEvaluator:
    """
    Evaluates skill/job matching quality.

    Metrics:
    - precision
    - recall
    - F1
    - missing-skill accuracy
    """

    def evaluate(
        self,
        *,
        case: MatchingEvaluationCase,
        actual_result: Dict[str, Any],
    ) -> MatchingEvaluationResult:

        expected_matched = self._set(
            case.expected_matched_skills
        )

        actual_matched = self._set(
            actual_result.get(
                "matched_skills",
                []
            )
        )

        expected_missing = self._set(
            case.expected_missing_skills
        )

        actual_missing = self._set(
            actual_result.get(
                "missing_skills",
                []
            )
        )

        true_positive = len(
            expected_matched
            & actual_matched
        )

        precision = (
            true_positive
            / len(actual_matched)
            if actual_matched
            else (
                1.0
                if not expected_matched
                else 0.0
            )
        )

        recall = (
            true_positive
            / len(expected_matched)
            if expected_matched
            else 1.0
        )

        f1 = (
            2
            * precision
            * recall
            / (
                precision
                + recall
            )
            if (
                precision
                + recall
            )
            else 0.0
        )

        missing_union = (
            expected_missing
            | actual_missing
        )

        missing_accuracy = (
            len(
                expected_missing
                & actual_missing
            )
            / len(missing_union)

            if missing_union
            else 1.0
        )

        score = self._extract_score(
            actual_result
        )

        errors = []

        score_valid = True

        if (
            case.expected_min_score
            is not None
        ):

            score_valid = (
                score is not None
                and score
                >= case.expected_min_score
            )

            if not score_valid:
                errors.append(
                    "Job-match score was below "
                    "the expected threshold."
                )

        passed = (
            f1 >= 0.80
            and missing_accuracy >= 0.80
            and score_valid
        )

        return MatchingEvaluationResult(
            case_id=case.case_id,
            passed=passed,
            precision=round(
                precision,
                4
            ),
            recall=round(
                recall,
                4
            ),
            f1_score=round(
                f1,
                4
            ),
            missing_skill_accuracy=round(
                missing_accuracy,
                4
            ),
            actual_score=score,
            errors=errors,
        )

    def evaluate_batch(
        self,
        cases: Iterable[
            tuple[
                MatchingEvaluationCase,
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

        if not results:

            return {
                "total": 0,
                "pass_rate": 0.0,
                "average_f1": 0.0,
                "results": [],
            }

        passed = sum(
            result.passed
            for result in results
        )

        average_f1 = sum(
            result.f1_score
            for result in results
        ) / len(results)

        return {
            "total": len(results),

            "pass_rate": round(
                passed / len(results),
                4
            ),

            "average_f1": round(
                average_f1,
                4
            ),

            "results": [
                result.to_dict()
                for result in results
            ],
        }

    @staticmethod
    def _set(
        values: Any
    ) -> Set[str]:

        if not isinstance(
            values,
            (list, tuple, set)
        ):
            return set()

        return {
            str(value)
            .casefold()
            .strip()

            for value in values

            if str(value).strip()
        }

    @staticmethod
    def _extract_score(
        result: Dict[str, Any]
    ) -> Optional[float]:

        for key in (
            "score",
            "match_score",
            "overall_score",
        ):

            value = result.get(
                key
            )

            if isinstance(
                value,
                dict
            ):
                value = value.get(
                    "value"
                )

            try:
                if value is not None:
                    return float(value)

            except (
                TypeError,
                ValueError
            ):
                pass

        return None