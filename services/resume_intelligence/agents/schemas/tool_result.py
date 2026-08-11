from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class ToolResult:
    """
    Standard result returned by every agent tool.
    """

    tool_name: str
    success: bool

    data: Any = None

    execution_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    error_code: Optional[str] = None
    error_message: Optional[str] = None

    warnings: List[str] = field(
        default_factory=list
    )

    evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    duration_ms: Optional[float] = None

    retryable: bool = False

    def __post_init__(self) -> None:

        self.tool_name = (
            self.tool_name or ""
        ).strip()

        if not self.tool_name:
            raise ValueError(
                "tool_name is required."
            )

        if self.success:
            self.error_code = None
            self.error_message = None

    @classmethod
    def successful(
        cls,
        tool_name: str,
        data: Any = None,
        **kwargs
    ) -> "ToolResult":

        return cls(
            tool_name=tool_name,
            success=True,
            data=data,
            **kwargs
        )

    @classmethod
    def failed(
        cls,
        tool_name: str,
        error_message: str,
        *,
        error_code: Optional[str] = None,
        retryable: bool = False,
        **kwargs
    ) -> "ToolResult":

        return cls(
            tool_name=tool_name,
            success=False,
            error_code=error_code,
            error_message=error_message,
            retryable=retryable,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "execution_id": self.execution_id,
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "evidence": self.evidence,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
            "retryable": self.retryable,
        }