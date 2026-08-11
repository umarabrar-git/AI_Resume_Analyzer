def validate_recommendation(recommendation):
    """Validate that a single recommendation has the minimum fields required by the UI."""
    if not isinstance(recommendation, dict):
        return None
    if not recommendation.get("title") or not recommendation.get("message"):
        return None
    return recommendation


def validate_recommendations(recommendations):
    """Validate that recommendations have the minimum fields required by the UI."""
    valid = []
    for recommendation in recommendations or []:
        validated = validate_recommendation(recommendation)
        if validated is not None:
            valid.append(validated)
    return valid
