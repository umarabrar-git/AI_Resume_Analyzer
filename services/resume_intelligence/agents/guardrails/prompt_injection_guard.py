"""
Prompt-injection detection for untrusted resume and job content.

This module detects suspicious instruction-like text. Detection does
not automatically mean malicious intent; the caller decides whether
to warn, sanitize, restrict tools, or reject the request.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class InjectionRisk(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class InjectionSignal:
    category: str
    pattern: str
    matched_text: str
    weight: int


@dataclass
class InjectionAssessment:
    detected: bool
    risk: InjectionRisk
    score: int

    signals: List[InjectionSignal] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict:

        return {
            "detected": self.detected,
            "risk": self.risk.value,
            "score": self.score,
            "signals": [
                {
                    "category": signal.category,
                    "pattern": signal.pattern,
                    "matched_text": signal.matched_text,
                    "weight": signal.weight,
                }
                for signal in self.signals
            ],
            "warnings": self.warnings,
        }


_PATTERNS = [
    (
        "instruction_override",
        r"\bignore\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions?\b",
        4,
    ),
    (
        "instruction_override",
        r"\bdisregard\s+(?:all\s+)?(?:previous|prior|system)\s+instructions?\b",
        4,
    ),
    (
        "system_prompt_request",
        r"\b(?:reveal|show|print|display|return)\s+(?:the\s+)?system\s+prompt\b",
        4,
    ),
    (
        "hidden_instruction_request",
        r"\b(?:reveal|show|print|display)\s+(?:your\s+)?hidden\s+instructions?\b",
        4,
    ),
    (
        "role_override",
        r"\byou\s+are\s+now\s+(?:a|an|the)\b",
        2,
    ),
    (
        "role_override",
        r"\bact\s+as\s+(?:a|an|the)\b",
        1,
    ),
    (
        "tool_manipulation",
        r"\b(?:call|invoke|execute|run)\s+(?:the\s+)?(?:tool|function|command)\b",
        3,
    ),
    (
        "security_bypass",
        r"\b(?:bypass|disable|ignore|remove)\s+(?:the\s+)?(?:guardrail|security|safety|restriction|policy)",
        4,
    ),
    (
        "secret_request",
        r"\b(?:reveal|print|show|return)\s+(?:the\s+)?(?:api\s*key|secret|token|password|credentials?)\b",
        5,
    ),
]


def _risk_from_score(
    score: int
) -> InjectionRisk:

    if score <= 0:
        return InjectionRisk.NONE

    if score <= 2:
        return InjectionRisk.LOW

    if score <= 6:
        return InjectionRisk.MEDIUM

    return InjectionRisk.HIGH


def assess_prompt_injection(
    text: str
) -> InjectionAssessment:

    normalized = (
        text or ""
    ).strip()

    if not normalized:

        return InjectionAssessment(
            detected=False,
            risk=InjectionRisk.NONE,
            score=0,
        )

    signals: List[
        InjectionSignal
    ] = []

    total_score = 0

    for category, pattern, weight in _PATTERNS:

        for match in re.finditer(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        ):

            matched = match.group(0)

            signals.append(
                InjectionSignal(
                    category=category,
                    pattern=pattern,
                    matched_text=matched[:200],
                    weight=weight,
                )
            )

            total_score += weight

    risk = _risk_from_score(
        total_score
    )

    warnings = []

    if risk == InjectionRisk.LOW:
        warnings.append(
            "Instruction-like content was detected."
        )

    elif risk == InjectionRisk.MEDIUM:
        warnings.append(
            "Potential prompt-injection content was detected."
        )

    elif risk == InjectionRisk.HIGH:
        warnings.append(
            "High-risk prompt-injection content was detected."
        )

    return InjectionAssessment(
        detected=bool(signals),
        risk=risk,
        score=total_score,
        signals=signals,
        warnings=warnings,
    )


def contains_high_risk_injection(
    text: str
) -> bool:

    assessment = assess_prompt_injection(
        text
    )

    return (
        assessment.risk
        == InjectionRisk.HIGH
    )