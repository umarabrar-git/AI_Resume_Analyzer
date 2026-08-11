from typing import Any, Dict, List, Optional

from services.resume_intelligence.recommendations.models import (
    Recommendation
)


class RecommendationBuilder:
    """
    Factory responsible for creating standardized
    Recommendation objects.
    """

    @staticmethod
    def build(
        category: str,
        title: str,
        message: str,
        priority: str = "medium",
        action: Optional[str] = None,
        impact: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Recommendation:

        return Recommendation(
            category=category,
            title=title,
            message=message,
            priority=priority,
            action=action,
            impact=impact,
            evidence=evidence or {},
            metadata=metadata or {},
            tags=tags or []
        )