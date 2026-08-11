"""
LLM provider abstraction.

Generative AI and Agentic AI consume this interface instead
of importing a specific vendor SDK.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .base_provider import (
    BaseProvider,
    ProviderResponse,
)


@dataclass
class ChatMessage:
    role: str
    content: str

    name: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.role = (
            self.role
            or ""
        ).strip().lower()

        self.content = (
            self.content
            or ""
        ).strip()

        if self.role not in {
            "system",
            "user",
            "assistant",
            "tool",
        }:
            raise ValueError(
                f"Unsupported message role: {self.role}"
            )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "role": self.role,
            "content": self.content,
        }

        if self.name:
            result["name"] = self.name

        if self.metadata:
            result["metadata"] = self.metadata

        return result


@dataclass
class GenerationConfig:
    temperature: float = 0.2

    max_output_tokens: Optional[int] = None

    top_p: Optional[float] = None

    stop: Optional[List[str]] = None

    response_format: Optional[
        Dict[str, Any]
    ] = None

    seed: Optional[int] = None

    def __post_init__(self) -> None:

        self.temperature = min(
            max(
                float(self.temperature),
                0.0
            ),
            2.0
        )

        if (
            self.max_output_tokens
            is not None
            and self.max_output_tokens <= 0
        ):
            raise ValueError(
                "max_output_tokens must be positive."
            )


class LLMProvider(BaseProvider):
    """
    Interface implemented by every chat/generative model adapter.
    """

    @abstractmethod
    def generate(
        self,
        messages: Sequence[ChatMessage],
        *,
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
        tools: Optional[
            Sequence[Mapping[str, Any]]
        ] = None,
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> ProviderResponse:
        """
        Generate a model response.
        """

    def complete(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> ProviderResponse:
        """
        Convenience interface for simple text generation.
        """

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        messages: List[ChatMessage] = []

        if system_prompt:
            messages.append(
                ChatMessage(
                    role="system",
                    content=system_prompt
                )
            )

        messages.append(
            ChatMessage(
                role="user",
                content=prompt
            )
        )

        return self.generate(
            messages,
            model=model,
            config=config,
            metadata=metadata
        )