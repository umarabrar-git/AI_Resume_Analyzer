from services.resume_intelligence.recommendations.builders import (
    RecommendationBuilder
)


def generate_content_recommendations(
    ats_result
):
    recommendations = []

    content = (
        ats_result.get(
            "content",
            {}
        )
        or {}
    )

    word_count = content.get(
        "word_count",
        0
    )

    action_verbs = content.get(
        "action_verbs",
        0
    )

    quantified = content.get(
        "quantified_achievements",
        0
    )

    if word_count < 200:

        recommendations.append(
            RecommendationBuilder.build(
                category="content",
                priority="high",

                title="Strengthen Resume Content",

                message=(
                    "The resume contains relatively "
                    "limited readable content."
                ),

                action=(
                    "Add relevant responsibilities, "
                    "achievements, projects or professional "
                    "evidence without adding unnecessary filler."
                ),

                impact=(
                    "Provides stronger evidence of your "
                    "professional capabilities."
                ),

                evidence={
                    "word_count":
                        word_count
                },

                tags=[
                    "content",
                    "completeness"
                ]
            )
        )

    elif word_count > 1300:

        recommendations.append(
            RecommendationBuilder.build(
                category="content",
                priority="medium",

                title="Make Resume More Concise",

                message=(
                    "The resume contains a large amount "
                    "of text and may benefit from tighter wording."
                ),

                action=(
                    "Remove repetition and prioritize "
                    "recent, relevant and high-impact information."
                ),

                impact=(
                    "Improves readability and helps important "
                    "information stand out."
                ),

                evidence={
                    "word_count":
                        word_count
                },

                tags=[
                    "content",
                    "clarity"
                ]
            )
        )

    if action_verbs < 3:

        recommendations.append(
            RecommendationBuilder.build(
                category="content",
                priority="medium",

                title="Use Stronger Action Language",

                message=(
                    "Your resume shows limited use of "
                    "achievement-oriented action language."
                ),

                action=(
                    "Start relevant experience bullets with "
                    "clear action verbs that describe what "
                    "you actually did."
                ),

                impact=(
                    "Makes responsibilities and contributions "
                    "clearer to recruiters."
                ),

                evidence={
                    "action_verbs":
                        action_verbs
                },

                tags=[
                    "content",
                    "writing"
                ]
            )
        )

    if quantified == 0:

        recommendations.append(
            RecommendationBuilder.build(
                category="achievements",
                priority="high",

                title="Add Measurable Achievements",

                message=(
                    "No clear quantified achievements "
                    "were detected."
                ),

                action=(
                    "Where truthful and relevant, add measurable "
                    "outcomes such as percentages, volumes, "
                    "time saved, team size, revenue, customers, "
                    "projects or other role-specific metrics."
                ),

                impact=(
                    "Adds evidence of impact instead of "
                    "listing responsibilities alone."
                ),

                evidence={
                    "quantified_achievements":
                        quantified
                },

                tags=[
                    "achievement",
                    "impact",
                    "content"
                ]
            )
        )

    return recommendations