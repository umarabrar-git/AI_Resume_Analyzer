from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from uuid import uuid4


VALID_PRIORITIES = {
    "critical",
    "high",
    "medium",
    "low"
}


@dataclass
class Recommendation:
    """
    Standard recommendation object used across the
    resume intelligence platform.
    """

    category: str
    title: str
    message: str

    priority: str = "medium"
    action: Optional[str] = None
    impact: Optional[str] = None

    evidence: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    tags: List[str] = field(
        default_factory=list
    )

    recommendation_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    def __post_init__(self):
        self.category = (
            self.category or "general"
        ).strip().lower()

        self.priority = (
            self.priority or "medium"
        ).strip().lower()

        if self.priority not in VALID_PRIORITIES:
            self.priority = "medium"

        self.title = (
            self.title or ""
        ).strip()

        self.message = (
            self.message or ""
        ).strip()

        if self.action:
            self.action = self.action.strip()

        if self.impact:
            self.impact = self.impact.strip()

    def to_dict(self):
        return asdict(self)