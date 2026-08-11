from services.resume_intelligence.recommendations.engines import (
    generate_structure_recommendations,
    generate_content_recommendations,
    generate_experience_recommendations,
    generate_skills_recommendations,
    generate_keyword_recommendations,
    generate_readability_recommendations,
    prioritize_recommendations
)

from services.resume_intelligence.recommendations.builders import (
    build_insights
)

from services.resume_intelligence.recommendations.validators import (
    validate_recommendations
)


def generate_recommendations(
    resume_text,
    ats_result,
    job_description=None,
    max_recommendations=20
):
    """
    Main recommendation engine.

    Inputs:
        resume_text:
            Extracted resume text.

        ats_result:
            Output from analyze_ats().

        job_description:
            Optional JD. Reserved for richer contextual
            recommendation logic.

        max_recommendations:
            Maximum recommendations returned.

    Returns:
        Structured recommendation response suitable for
        Web, API, Android, iOS and AI-agent tools.
    """

    if not resume_text or not resume_text.strip():

        raise ValueError(
            "Resume text is required."
        )

    if not isinstance(
        ats_result,
        dict
    ):

        raise ValueError(
            "A valid ATS analysis result is required."
        )

    recommendations = []

    # -------------------------------------------------
    # Structure
    # -------------------------------------------------

    recommendations.extend(
        generate_structure_recommendations(
            ats_result
        )
    )

    # -------------------------------------------------
    # Content
    # -------------------------------------------------

    recommendations.extend(
        generate_content_recommendations(
            ats_result
        )
    )

    # -------------------------------------------------
    # Experience
    # -------------------------------------------------

    recommendations.extend(
        generate_experience_recommendations(
            resume_text,
            ats_result
        )
    )

    # -------------------------------------------------
    # Skills
    # -------------------------------------------------

    recommendations.extend(
        generate_skills_recommendations(
            ats_result
        )
    )

    # -------------------------------------------------
    # Job Alignment
    # -------------------------------------------------

    recommendations.extend(
        generate_keyword_recommendations(
            ats_result
        )
    )

    # -------------------------------------------------
    # Readability
    # -------------------------------------------------

    recommendations.extend(
        generate_readability_recommendations(
            ats_result
        )
    )

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

    recommendations = validate_recommendations(
        recommendations
    )

    # -------------------------------------------------
    # Priority ranking
    # -------------------------------------------------

    recommendations = prioritize_recommendations(
        recommendations
    )

    # -------------------------------------------------
    # Limit result
    # -------------------------------------------------

    if max_recommendations is not None:

        max_recommendations = max(
            1,
            int(max_recommendations)
        )

        recommendations = recommendations[
            :max_recommendations
        ]

    # -------------------------------------------------
    # Insights
    # -------------------------------------------------

    insights = build_insights(
        recommendations
    )

    return {
        "summary": insights,

        "recommendations": [
            recommendation.to_dict()
            for recommendation in recommendations
        ],

        "context": {
            "ats_score":
                ats_result.get(
                    "ats_score"
                ),

            "ats_rating":
                ats_result.get(
                    "rating"
                ),

            "job_description_used":
                bool(job_description)
                or bool(
                    (
                        ats_result.get(
                            "keywords",
                            {}
                        )
                        or {}
                    ).get(
                        "job_description_used",
                        False
                    )
                )
        }
    }