from collections import Counter


def build_insights(recommendations):
    """
    Build summary-level insights from recommendation objects.
    """

    if not recommendations:
        return {
            "total": 0,
            "priority_counts": {},
            "category_counts": {},
            "top_priorities": [],
            "focus_areas": []
        }

    priority_counts = Counter(
        item.priority
        for item in recommendations
    )

    category_counts = Counter(
        item.category
        for item in recommendations
    )

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3
    }

    sorted_items = sorted(
        recommendations,
        key=lambda item: priority_order.get(
            item.priority,
            99
        )
    )

    top_priorities = [
        {
            "id": item.recommendation_id,
            "title": item.title,
            "category": item.category,
            "priority": item.priority
        }
        for item in sorted_items[:5]
    ]

    focus_areas = [
        category
        for category, _ in category_counts.most_common(
            5
        )
    ]

    return {
        "total":
            len(recommendations),

        "priority_counts":
            dict(priority_counts),

        "category_counts":
            dict(category_counts),

        "top_priorities":
            top_priorities,

        "focus_areas":
            focus_areas
    }