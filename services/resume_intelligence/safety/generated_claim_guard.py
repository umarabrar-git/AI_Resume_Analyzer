from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .factuality_guard import (
    FactualityGuard,
    FactualityIssue,
)


@dataclass
class GeneratedClaimResult:
    allowed: bool

    generated_text: str

    claims: List[str] = field(
        default_factory=list
    )

    issues: List[
        FactualityIssue
    ] = field(
        default_factory=list
    )

    risk_score: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "allowed": self.allowed,
            "generated_text":
                self.generated_text,
            "claims":
                self.claims,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "risk_score":
                self.risk_score,
            "metadata":
                self.metadata,
        }


class GeneratedClaimGuard:
    """
    Safety layer for AI-generated resume content.

    Checks:
    - unsupported factual statements
    - newly introduced numerical metrics
    - high-risk fabrication indicators
    """

    SENTENCE_PATTERN = re.compile(
        r"(?<=[.!?])\s+"
    )

    def __init__(
        self,
        factuality_guard: Optional[
            FactualityGuard
        ] = None,
    ) -> None:

        self.factuality_guard = (
            factuality_guard
            or FactualityGuard()
        )

    def validate(
        self,
        *,
        generated_text: str,
        source_resume: str,
        known_facts: Optional[
            List[str]
        ] = None,
        strict: bool = False,
    ) -> GeneratedClaimResult:

        generated_text = (
            generated_text
            or ""
        ).strip()

        source_resume = (
            source_resume
            or ""
        ).strip()

        if not generated_text:

            return GeneratedClaimResult(
                allowed=False,
                generated_text="",
                issues=[
                    FactualityIssue(
                        category="empty_generation",
                        claim="",
                        reason=(
                            "Generated content "
                            "is empty."
                        ),
                        severity="high",
                    )
                ],
                risk_score=1.0,
            )

        claims = self._extract_claims(
            generated_text
        )

        factuality = (
            self.factuality_guard.validate(
                generated_claims=claims,
                source_text=source_resume,
                known_facts=known_facts,
            )
        )

        metric_issues = (
            self.factuality_guard
            .validate_metrics(
                generated_text=(
                    generated_text
                ),
                source_text=(
                    source_resume
                ),
            )
        )

        issues = (
            factuality.issues
            + metric_issues
        )

        issues = (
            self._deduplicate_issues(
                issues
            )
        )

        risk_score = (
            self._calculate_risk(
                issues=issues,
                claim_count=len(claims),
            )
        )

        high_risk = any(
            issue.severity == "high"
            for issue in issues
        )

        if strict:
            allowed = not issues
        else:
            allowed = not high_risk

        return GeneratedClaimResult(
            allowed=allowed,
            generated_text=generated_text,
            claims=claims,
            issues=issues,
            risk_score=risk_score,
            metadata={
                "strict_mode":
                    strict,

                "claim_count":
                    len(claims),

                "supported_claims":
                    len(
                        factuality
                        .supported_claims
                    ),

                "unsupported_claims":
                    len(
                        factuality
                        .unsupported_claims
                    ),
            },
        )

    def _extract_claims(
        self,
        text: str,
    ) -> List[str]:

        parts = (
            self.SENTENCE_PATTERN
            .split(text)
        )

        claims = []

        for part in parts:

            claim = (
                part
                .strip()
                .lstrip("•-* ")
                .strip()
            )

            if not claim:
                continue

            claims.append(claim)

        return claims

    @staticmethod
    def _calculate_risk(
        *,
        issues: List[
            FactualityIssue
        ],
        claim_count: int,
    ) -> float:

        if not issues:
            return 0.0

        weights = {
            "info": 0.05,
            "warning": 0.15,
            "high": 0.35,
            "critical": 0.60,
        }

        total = sum(
            weights.get(
                issue.severity,
                0.15
            )
            for issue in issues
        )

        denominator = max(
            claim_count,
            1
        )

        score = total / denominator

        return round(
            min(score, 1.0),
            4,
        )

    @staticmethod
    def _deduplicate_issues(
        issues: List[
            FactualityIssue
        ],
    ) -> List[FactualityIssue]:

        result = []
        seen = set()

        for issue in issues:

            key = (
                issue.category,
                issue.claim.casefold(),
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(issue)

        return result