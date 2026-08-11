from services.resume_intelligence.recommendations.builders import (
    RecommendationBuilder
)


def generate_readability_recommendations(
    ats_result
):
    recommendations = []

    readability = (
        ats_result.get(
            "readability",
            {}
        )
        or {}
    )

    score = readability.get(
        "score",
        10
    )

    issues = readability.get(
        "issues",
        []
    ) or []

    if score >= 9 and not issues:
        return recommendations

    priority = (
        "high"
        if score <= 5
        else "medium"
    )

    for issue in issues:

        recommendations.append(
            RecommendationBuilder.build(
                category="readability",
                priority=priority,

                title="Improve ATS Readability",

                message=issue,

                action=(
                    "Use a clean, conventional resume layout "
                    "with readable text and clearly separated "
                    "sections."
                ),

                impact=(
                    "Reduces the chance of important content "
                    "being parsed incorrectly."
                ),

                evidence={
                    "readability_score":
                        score
                },

                tags=[
                    "ats",
                    "readability"
                ]
            )
        )

    return recommendations