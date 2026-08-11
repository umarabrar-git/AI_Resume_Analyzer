"""
Core contracts shared by all AI providers.

The rest of the resume intelligence platform should depend on
these abstractions rather than directly depending on a vendor SDK.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Any, Dict, List, Mapping, Optional


class ProviderError(RuntimeError):
    """Base exception raised by the provider layer."""


class ProviderConfigurationError(ProviderError):
    """Raised when a provider is configured incorrectly."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider cannot currently serve a request."""


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an invalid response."""


class AIModelTask(str, Enum):
    CHAT = "chat"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    REWRITE = "rewrite"
    PLANNING = "planning"
    TOOL_CALLING = "tool_calling"
    EMBEDDING = "embedding"


@dataclass(frozen=True)
class ProviderCapabilities:
    chat: bool = False
    structured_output: bool = False
    tool_calling: bool = False
    embeddings: bool = False


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def __post_init__(self) -> None:
        if not self.total_tokens:
            self.total_tokens = (
                self.input_tokens
                + self.output_tokens
            )

    def to_dict(self) -> Dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class ProviderResponse:
    content: str = ""
    model: Optional[str] = None
    provider: Optional[str] = None

    finish_reason: Optional[str] = None

    usage: Usage = field(
        default_factory=Usage
    )

    tool_calls: List[Dict[str, Any]] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    latency_ms: Optional[float] = None

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "finish_reason": self.finish_reason,
            "usage": self.usage.to_dict(),
            "tool_calls": self.tool_calls,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
        }


@dataclass
class EmbeddingResponse:
    vectors: List[List[float]]

    model: Optional[str] = None
    provider: Optional[str] = None

    usage: Usage = field(
        default_factory=Usage
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    latency_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vectors": self.vectors,
            "model": self.model,
            "provider": self.provider,
            "usage": self.usage.to_dict(),
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
        }


class BaseProvider(ABC):
    """
    Base contract for every external AI provider adapter.
    """

    provider_name = "base"

    capabilities = ProviderCapabilities()

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:

        self.api_key = api_key
        self.timeout = max(
            1.0,
            float(timeout)
        )

        self.max_retries = max(
            0,
            int(max_retries)
        )

    @abstractmethod
    def health_check(self) -> bool:
        """
        Return True when the provider is usable.
        """

    def supports(
        self,
        capability: str
    ) -> bool:

        return bool(
            getattr(
                self.capabilities,
                capability,
                False
            )
        )

    @staticmethod
    def _validate_metadata(
        metadata: Optional[Mapping[str, Any]]
    ) -> Dict[str, Any]:

        if metadata is None:
            return {}

        return dict(metadata)

    @staticmethod
    def _elapsed_ms(
        started_at: float
    ) -> float:

        return round(
            (perf_counter() - started_at) * 1000,
            2
        )