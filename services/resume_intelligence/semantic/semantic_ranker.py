from typing import List, Dict, Any


def rank_semantic_matches(matches: List[Dict[str, Any]]):
    """Rank semantic matches by similarity score in descending order."""
    return sorted(
        matches,
        key=lambda item: item.get("similarity", 0),
        reverse=True,
    )
