from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class PlanStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentPlanStep:

    tool_name: str

    objective: str

    step_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    status: PlanStepStatus = (
        PlanStepStatus.PENDING
    )

    arguments: Dict[str, Any] = field(
        default_factory=dict
    )

    dependencies: List[str] = field(
        default_factory=list
    )

    result_key: Optional[str] = None

    required: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def mark_running(self) -> None:
        self.status = PlanStepStatus.RUNNING

    def mark_completed(self) -> None:
        self.status = PlanStepStatus.COMPLETED

    def mark_failed(self) -> None:
        self.status = PlanStepStatus.FAILED

    def mark_skipped(self) -> None:
        self.status = PlanStepStatus.SKIPPED

    def to_dict(self) -> Dict[str, Any]:

        return {
            "step_id": self.step_id,
            "tool_name": self.tool_name,
            "objective": self.objective,
            "status": self.status.value,
            "arguments": self.arguments,
            "dependencies": self.dependencies,
            "result_key": self.result_key,
            "required": self.required,
            "metadata": self.metadata,
        }


@dataclass
class AgentPlan:
    """
    Executable plan produced by the planning layer.
    """

    intent: str

    plan_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    goal: Optional[str] = None

    steps: List[AgentPlanStep] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def add_step(
        self,
        tool_name: str,
        objective: str,
        *,
        arguments: Optional[
            Dict[str, Any]
        ] = None,
        dependencies: Optional[
            List[str]
        ] = None,
        result_key: Optional[str] = None,
        required: bool = True,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> AgentPlanStep:

        step = AgentPlanStep(
            tool_name=tool_name,
            objective=objective,
            arguments=arguments or {},
            dependencies=dependencies or [],
            result_key=result_key,
            required=required,
            metadata=metadata or {},
        )

        self.steps.append(step)

        return step

    @property
    def completed(self) -> bool:

        return all(
            step.status in {
                PlanStepStatus.COMPLETED,
                PlanStepStatus.SKIPPED,
            }
            for step in self.steps
        )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "plan_id": self.plan_id,
            "intent": self.intent,
            "goal": self.goal,
            "completed": self.completed,
            "steps": [
                step.to_dict()
                for step in self.steps
            ],
            "metadata": self.metadata,
        }