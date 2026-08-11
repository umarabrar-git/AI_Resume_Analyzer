from services.resume_intelligence.recommendations.builders import (
    RecommendationBuilder
)


def generate_skills_recommendations(
    ats_result
):
    recommendations = []

    keyword_data = (
        ats_result.get(
            "keywords",
            {}
        )
        or {}
    )

    candidates = keyword_data.get(
        "resume_candidates",
        []
    ) or []

    if len(candidates) < 5:

        recommendations.append(
            RecommendationBuilder.build(
                category="skills",
                priority="high",

                title="Strengthen Skill Representation",

                message=(
                    "The analysis detected relatively few "
                    "professional skill candidates."
                ),

                action=(
                    "Review whether your relevant professional, "
                    "technical, operational, interpersonal or "
                    "domain-specific capabilities are clearly "
                    "represented in the resume."
                ),

                impact=(
                    "Helps ATS systems and recruiters identify "
                    "your relevant capabilities."
                ),

                evidence={
                    "detected_candidates":
                        len(candidates)
                },

                tags=[
                    "skills",
                    "ats"
                ]
            )
        )

    return recommendations