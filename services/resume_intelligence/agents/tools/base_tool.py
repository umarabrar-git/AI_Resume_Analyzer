from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from services.resume_intelligence.agents.schemas import ToolResult


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str

    parameters: Dict[str, Any] = field(
        default_factory=dict
    )

    requires_resume: bool = False
    requires_job: bool = False

    category: str = "general"
    version: str = "1.0.0"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "requires_resume": self.requires_resume,
            "requires_job": self.requires_job,
            "category": self.category,
            "version": self.version,
            "metadata": self.metadata,
        }


class BaseTool(ABC):
    """
    Base contract for every Resume AI Agent tool.

    AgentExecutor only communicates with tools through
    this interface.
    """

    definition: ToolDefinition

    @property
    def name(self) -> str:
        return self.definition.name

    def validate_arguments(
        self,
        arguments: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:

        if arguments is None:
            return {}

        if not isinstance(arguments, dict):
            raise TypeError(
                "Tool arguments must be a dictionary."
            )

        return arguments

    @abstractmethod
    def execute(
        self,
        *,
        arguments: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ToolResult:
        """
        Execute the tool and return a standardized ToolResult.
        """

    def schema(self) -> Dict[str, Any]:
        """
        LLM/tool-calling compatible schema.
        """

        return {
            "type": "function",
            "function": {
                "name": self.definition.name,
                "description": self.definition.description,
                "parameters": self.definition.parameters,
            },
        }