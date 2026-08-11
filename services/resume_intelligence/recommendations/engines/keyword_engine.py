from services.resume_intelligence.recommendations.builders import (
    RecommendationBuilder
)


def generate_keyword_recommendations(
    ats_result
):
    recommendations = []

    keywords = (
        ats_result.get(
            "keywords",
            {}
        )
        or {}
    )

    if not keywords.get(
        "job_description_used",
        False
    ):
        return recommendations

    match_percentage = keywords.get(
        "match_percentage"
    )

    missing = keywords.get(
        "missing",
        []
    ) or []

    if match_percentage is None:
        return recommendations

    if match_percentage < 50:

        priority = "critical"

    elif match_percentage < 70:

        priority = "high"

    elif match_percentage < 85:

        priority = "medium"

    else:
        priority = "low"

    if match_percentage < 85:

        recommendations.append(
            RecommendationBuilder.build(
                category="job_alignment",
                priority=priority,

                title="Improve Job Description Alignment",

                message=(
                    f"Current semantic candidate alignment "
                    f"is approximately {match_percentage:.1f}%."
                ),

                action=(
                    "Review the missing job requirements and "
                    "incorporate only those skills, experiences "
                    "or concepts that genuinely reflect your "
                    "background."
                ),

                impact=(
                    "Can improve relevance for the specific "
                    "role while keeping the resume accurate."
                ),

                evidence={
                    "match_percentage":
                        match_percentage,

                    "missing_count":
                        len(missing),

                    "missing_candidates":
                        missing[:15]
                },

                tags=[
                    "job-match",
                    "keywords",
                    "semantic"
                ]
            )
        )

    return recommendations