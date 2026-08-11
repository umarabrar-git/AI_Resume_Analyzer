from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from services.resume_intelligence.agents.schemas import AgentRequest


class AgentIntent(str, Enum):
    RESUME_ANALYSIS = "resume_analysis"
    ATS_ANALYSIS = "ats_analysis"
    JOB_MATCH = "job_match"
    SKILL_GAP = "skill_gap"
    RECOMMENDATIONS = "recommendations"
    RESUME_REWRITE = "resume_rewrite"
    COVER_LETTER = "cover_letter"
    RESUME_OPTIMIZATION = "resume_optimization"
    JOB_TAILORING = "job_tailoring"
    CAREER_ASSISTANCE = "career_assistance"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class IntentPrediction:
    intent: AgentIntent
    confidence: float

    matched_signals: List[str] = field(
        default_factory=list
    )

    alternatives: List[
        Tuple[str, float]
    ] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict:

        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "matched_signals":
                self.matched_signals,
            "alternatives": [
                {
                    "intent": intent,
                    "confidence": confidence,
                }
                for intent, confidence
                in self.alternatives
            ],
            "metadata": self.metadata,
        }


INTENT_PATTERNS = {
    AgentIntent.COVER_LETTER: [
        r"\bcover\s+letter\b",
        r"\bapplication\s+letter\b",
        r"\bmotivation\s+letter\b",
    ],

    AgentIntent.RESUME_REWRITE: [
        r"\brewrite\b",
        r"\brephrase\b",
        r"\bimprove\s+(?:my\s+)?resume\b",
        r"\bimprove\s+(?:my\s+)?cv\b",
    ],

    AgentIntent.JOB_TAILORING: [
        r"\btailor\b",
        r"\bcustomi[sz]e\b",
        r"\badapt\s+(?:my\s+)?(?:resume|cv)\b",
        r"\btarget\s+(?:this\s+)?job\b",
    ],

    AgentIntent.ATS_ANALYSIS: [
        r"\bats\b",
        r"\bapplicant\s+tracking\s+system\b",
        r"\bats\s+score\b",
    ],

    AgentIntent.SKILL_GAP: [
        r"\bskill\s+gap\b",
        r"\bmissing\s+skills?\b",
        r"\bskills?\s+(?:am\s+i|are)\s+missing\b",
    ],

    AgentIntent.JOB_MATCH: [
        r"\bjob\s+match\b",
        r"\bmatch\s+(?:my\s+)?resume\b",
        r"\bfit\s+for\s+(?:this|the)\s+(?:job|role)\b",
        r"\bhow\s+well\s+.*\bmatch\b",
    ],

    AgentIntent.RECOMMENDATIONS: [
        r"\brecommend(?:ation|ations)?\b",
        r"\bsuggestions?\b",
        r"\bwhat\s+should\s+i\s+improve\b",
    ],

    AgentIntent.RESUME_OPTIMIZATION: [
        r"\boptimi[sz]e\b",
        r"\bmake\s+(?:my\s+)?resume\s+better\b",
        r"\bstrengthen\s+(?:my\s+)?resume\b",
    ],

    AgentIntent.RESUME_ANALYSIS: [
        r"\banaly[sz]e\b",
        r"\breview\s+(?:my\s+)?(?:resume|cv)\b",
        r"\bcheck\s+(?:my\s+)?(?:resume|cv)\b",
        r"\bevaluate\s+(?:my\s+)?(?:resume|cv)\b",
    ],

    AgentIntent.CAREER_ASSISTANCE: [
        r"\bcareer\b",
        r"\bcareer\s+advice\b",
        r"\bcareer\s+help\b",
    ],
}


MODE_DEFAULT_INTENTS = {
    "analyze":
        AgentIntent.RESUME_ANALYSIS,

    "optimize":
        AgentIntent.RESUME_OPTIMIZATION,

    "tailor":
        AgentIntent.JOB_TAILORING,

    "rewrite":
        AgentIntent.RESUME_REWRITE,

    "cover_letter":
        AgentIntent.COVER_LETTER,

    "career_assist":
        AgentIntent.CAREER_ASSISTANCE,
}


class IntentClassifier:
    """
    Deterministic first-stage intent classifier.

    This deliberately does not require an LLM.

    A semantic/LLM fallback can later be injected
    without changing the planner contract.
    """

    def classify(
        self,
        request: AgentRequest
    ) -> IntentPrediction:

        if not isinstance(
            request,
            AgentRequest
        ):
            raise TypeError(
                "request must be an AgentRequest."
            )

        message = request.message.casefold()

        scores: Dict[
            AgentIntent,
            float
        ] = {}

        signals: Dict[
            AgentIntent,
            List[str]
        ] = {}

        for intent, patterns in (
            INTENT_PATTERNS.items()
        ):

            score = 0.0
            matches = []

            for pattern in patterns:

                match = re.search(
                    pattern,
                    message,
                    flags=re.IGNORECASE,
                )

                if match:

                    score += 1.0

                    matches.append(
                        match.group(0)
                    )

            if score:

                scores[intent] = score
                signals[intent] = matches

        # Context-aware boosts

        if request.job_description:

            for intent in (
                AgentIntent.JOB_MATCH,
                AgentIntent.JOB_TAILORING,
                AgentIntent.SKILL_GAP,
            ):
                scores[intent] = (
                    scores.get(intent, 0.0)
                    + 0.25
                )

        if request.resume_text:

            for intent in (
                AgentIntent.RESUME_ANALYSIS,
                AgentIntent.ATS_ANALYSIS,
                AgentIntent.RESUME_OPTIMIZATION,
            ):
                scores[intent] = (
                    scores.get(intent, 0.0)
                    + 0.10
                )

        mode_intent = (
            MODE_DEFAULT_INTENTS.get(
                request.mode
            )
        )

        if mode_intent:

            scores[mode_intent] = (
                scores.get(
                    mode_intent,
                    0.0
                )
                + 0.50
            )

        if not scores:

            return IntentPrediction(
                intent=AgentIntent.UNKNOWN,
                confidence=0.0,
                metadata={
                    "classifier":
                        "deterministic_v1"
                },
            )

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        best_intent, best_score = (
            ranked[0]
        )

        total_score = sum(
            scores.values()
        )

        confidence = (
            best_score / total_score
            if total_score
            else 0.0
        )

        confidence = round(
            min(
                max(confidence, 0.0),
                1.0
            ),
            4,
        )

        alternatives = [
            (
                intent.value,
                round(
                    score / total_score,
                    4
                ),
            )
            for intent, score
            in ranked[1:4]
        ]

        return IntentPrediction(
            intent=best_intent,
            confidence=confidence,
            matched_signals=signals.get(
                best_intent,
                []
            ),
            alternatives=alternatives,
            metadata={
                "classifier":
                    "deterministic_v1",

                "mode":
                    request.mode,

                "resume_available":
                    bool(request.resume_text),

                "job_available":
                    bool(
                        request.job_description
                    ),
            },
        )