from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class FactualityIssue:
    category: str
    claim: str
    reason: str

    severity: str = "warning"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "claim": self.claim,
            "reason": self.reason,
            "severity": self.severity,
            "metadata": self.metadata,
        }


@dataclass
class FactualityResult:
    valid: bool

    issues: List[
        FactualityIssue
    ] = field(
        default_factory=list
    )

    supported_claims: List[str] = field(
        default_factory=list
    )

    unsupported_claims: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "supported_claims":
                self.supported_claims,
            "unsupported_claims":
                self.unsupported_claims,
        }


class FactualityGuard:
    """
    Lightweight deterministic factuality validation.

    It does NOT decide semantic truth.

    Its purpose is to identify generated statements that
    cannot be traced back to candidate evidence and should
    therefore receive additional validation.
    """

    METRIC_PATTERN = re.compile(
        r"\b\d+(?:\.\d+)?\s*%"
        r"|\$\s?\d[\d,.]*"
        r"|\b\d+(?:\.\d+)?x\b",
        re.IGNORECASE,
    )

    def validate(
        self,
        *,
        generated_claims: Iterable[str],
        source_text: str,
        known_facts: Optional[
            Iterable[str]
        ] = None,
    ) -> FactualityResult:

        source = self._normalize(
            source_text
        )

        facts = {
            self._normalize(fact)
            for fact in (
                known_facts or []
            )
            if self._normalize(fact)
        }

        supported = []
        unsupported = []
        issues = []

        for claim in generated_claims:

            claim = (
                claim or ""
            ).strip()

            if not claim:
                continue

            normalized = self._normalize(
                claim
            )

            if self._is_supported(
                normalized,
                source,
                facts,
            ):

                supported.append(claim)
                continue

            unsupported.append(claim)

            severity = (
                "high"
                if self.METRIC_PATTERN.search(
                    claim
                )
                else "warning"
            )

            issues.append(
                FactualityIssue(
                    category=(
                        "unsupported_claim"
                    ),
                    claim=claim,
                    reason=(
                        "The generated claim could "
                        "not be directly traced to "
                        "candidate evidence."
                    ),
                    severity=severity,
                )
            )

        return FactualityResult(
            valid=not unsupported,
            issues=issues,
            supported_claims=supported,
            unsupported_claims=unsupported,
        )

    def validate_metrics(
        self,
        *,
        generated_text: str,
        source_text: str,
    ) -> List[FactualityIssue]:
        """
        Detect newly introduced numerical claims.
        """

        generated_metrics = set(
            self.METRIC_PATTERN.findall(
                generated_text or ""
            )
        )

        source_metrics = set(
            self.METRIC_PATTERN.findall(
                source_text or ""
            )
        )

        new_metrics = (
            generated_metrics
            - source_metrics
        )

        return [
            FactualityIssue(
                category="invented_metric",
                claim=metric,
                reason=(
                    "Generated numerical claim "
                    "does not appear in the "
                    "source resume."
                ),
                severity="high",
            )
            for metric in sorted(
                new_metrics
            )
        ]

    @staticmethod
    def _is_supported(
        claim: str,
        source: str,
        facts: set[str],
    ) -> bool:

        if not claim:
            return True

        if claim in source:
            return True

        if claim in facts:
            return True

        return False

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:

        return " ".join(
            (
                value
                or ""
            )
            .casefold()
            .split()
        )