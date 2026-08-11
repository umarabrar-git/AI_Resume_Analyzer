PRIORITY_WEIGHTS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1
}


CATEGORY_WEIGHTS = {
    "job_alignment": 5,
    "structure": 5,
    "experience": 4,
    "skills": 4,
    "achievements": 4,
    "content": 3,
    "readability": 3,
    "general": 1
}


def calculate_priority_score(
    recommendation
):
    priority_score = PRIORITY_WEIGHTS.get(
        recommendation.priority,
        1
    )

    category_score = CATEGORY_WEIGHTS.get(
        recommendation.category,
        1
    )

    return (
        priority_score * 10
        + category_score
    )


def prioritize_recommendations(
    recommendations
):
    """
    Sort recommendations by impact while preserving
    deterministic behavior.
    """

    return sorted(
        recommendations,
        key=lambda item: (
            -calculate_priority_score(item),
            item.title.casefold()
        )
    )