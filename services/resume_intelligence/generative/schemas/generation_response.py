from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class GenerationResponse:
    content: str

    task: str
    success: bool = True

    generation_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    model: Optional[str] = None
    provider: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )

    validation: Dict[str, Any] = field(
        default_factory=dict
    )

    usage: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation_id": self.generation_id,
            "task": self.task,
            "success": self.success,
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "warnings": self.warnings,
            "validation": self.validation,
            "usage": self.usage,
            "metadata": self.metadata,
        }