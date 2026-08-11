from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentResponse:
    """
    Public response returned by the Resume AI Agent.
    """

    run_id: str
    request_id: str

    success: bool
    content: str

    intent: Optional[str] = None

    confidence: Optional[float] = None

    actions_performed: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )

    artifacts: List[Dict[str, Any]] = field(
        default_factory=list
    )

    usage: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        if self.confidence is not None:
            self.confidence = max(
                0.0,
                min(
                    1.0,
                    float(self.confidence)
                )
            )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "run_id": self.run_id,
            "request_id": self.request_id,
            "success": self.success,
            "content": self.content,
            "intent": self.intent,
            "confidence": self.confidence,
            "actions_performed":
                self.actions_performed,
            "warnings": self.warnings,
            "errors": self.errors,
            "evidence": self.evidence,
            "artifacts": self.artifacts,
            "usage": self.usage,
            "metadata": self.metadata,
        }