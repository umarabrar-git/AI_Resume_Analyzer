from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .agent_plan import AgentPlan
from .agent_request import AgentRequest
from .tool_result import ToolResult


class AgentStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentState:
    """
    Runtime state for one agent execution.

    Do not use this object as permanent database storage.
    Persistence will later be handled by memory/storage services.
    """

    request: AgentRequest

    run_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: AgentStatus = (
        AgentStatus.CREATED
    )

    intent: Optional[str] = None

    plan: Optional[AgentPlan] = None

    tool_results: List[ToolResult] = field(
        default_factory=list
    )

    working_context: Dict[str, Any] = field(
        default_factory=dict
    )

    evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    iteration: int = 0

    max_iterations: int = 10

    confidence: Optional[float] = None

    final_content: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def set_status(
        self,
        status: AgentStatus
    ) -> None:

        self.status = status

    def add_tool_result(
        self,
        result: ToolResult
    ) -> None:

        self.tool_results.append(result)

        if result.evidence:
            self.evidence.extend(
                result.evidence
            )

        if result.warnings:
            self.warnings.extend(
                result.warnings
            )

        if (
            not result.success
            and result.error_message
        ):
            self.errors.append(
                result.error_message
            )

    def increment_iteration(self) -> None:

        self.iteration += 1

        if self.iteration > self.max_iterations:
            raise RuntimeError(
                "Maximum agent iterations exceeded."
            )

    def fail(
        self,
        message: str
    ) -> None:

        self.errors.append(message)

        self.status = AgentStatus.FAILED

    def complete(
        self,
        content: str,
        confidence: Optional[float] = None
    ) -> None:

        self.final_content = content
        self.confidence = confidence
        self.status = AgentStatus.COMPLETED

    def to_dict(self) -> Dict[str, Any]:

        return {
            "run_id": self.run_id,
            "status": self.status.value,
            "intent": self.intent,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "confidence": self.confidence,
            "warnings": self.warnings,
            "errors": self.errors,
            "working_context": self.working_context,
            "evidence": self.evidence,
            "plan": (
                self.plan.to_dict()
                if self.plan
                else None
            ),
            "tool_results": [
                result.to_dict()
                for result in self.tool_results
            ],
            "metadata": self.metadata,
        }