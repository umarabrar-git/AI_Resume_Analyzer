import re

from services.resume_intelligence.recommendations.builders import (
    RecommendationBuilder
)


RESULT_PATTERNS = [
    r"\b\d+(?:\.\d+)?%",
    r"[$£€]\s?\d+",
    r"\b(?:increased|decreased|reduced|improved|grew|saved)\b"
]


def _has_result_evidence(text):
    if not text:
        return False

    return any(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )
        for pattern in RESULT_PATTERNS
    )


def generate_experience_recommendations(
    resume_text,
    ats_result
):
    recommendations = []

    sections = (
        ats_result.get(
            "sections",
            {}
        )
        or {}
    )

    detected = (
        sections.get(
            "detected",
            {}
        )
        or {}
    )

    if not detected.get(
        "experience",
        False
    ):
        return recommendations

    content = (
        ats_result.get(
            "content",
            {}
        )
        or {}
    )

    quantified = content.get(
        "quantified_achievements",
        0
    )

    if (
        quantified < 2
        and not _has_result_evidence(
            resume_text
        )
    ):

        recommendations.append(
            RecommendationBuilder.build(
                category="experience",
                priority="high",

                title="Make Experience More Outcome-Focused",

                message=(
                    "Your experience appears to contain "
                    "limited measurable outcome evidence."
                ),

                action=(
                    "For relevant responsibilities, describe "
                    "the action you took and the result it "
                    "produced. Add metrics only when they are "
                    "accurate and supported by your experience."
                ),

                impact=(
                    "Helps recruiters understand the scale "
                    "and impact of your work."
                ),

                evidence={
                    "quantified_achievements":
                        quantified
                },

                tags=[
                    "experience",
                    "achievements",
                    "impact"
                ]
            )
        )

    return recommendations