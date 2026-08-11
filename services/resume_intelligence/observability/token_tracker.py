from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Dict, List, Optional


@dataclass
class TokenUsage:
    provider: str
    model: str

    input_tokens: int = 0
    output_tokens: int = 0

    cached_input_tokens: int = 0

    run_id: Optional[str] = None
    request_id: Optional[str] = None

    operation: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.input_tokens = max(
            int(self.input_tokens),
            0,
        )

        self.output_tokens = max(
            int(self.output_tokens),
            0,
        )

        self.cached_input_tokens = max(
            int(self.cached_input_tokens),
            0,
        )

    @property
    def total_tokens(self) -> int:

        return (
            self.input_tokens
            + self.output_tokens
        )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "provider": self.provider,
            "model": self.model,
            "input_tokens":
                self.input_tokens,
            "output_tokens":
                self.output_tokens,
            "cached_input_tokens":
                self.cached_input_tokens,
            "total_tokens":
                self.total_tokens,
            "run_id": self.run_id,
            "request_id":
                self.request_id,
            "operation":
                self.operation,
            "metadata":
                self.metadata,
        }


class TokenTracker:
    """
    Tracks model token consumption.

    Token counts should come from the model provider response
    whenever the provider supplies authoritative usage data.
    """

    def __init__(self) -> None:

        self._records: List[
            TokenUsage
        ] = []

        self._lock = RLock()

    def record(
        self,
        usage: TokenUsage,
    ) -> None:

        if not isinstance(
            usage,
            TokenUsage
        ):
            raise TypeError(
                "usage must be TokenUsage."
            )

        with self._lock:
            self._records.append(
                usage
            )

    def record_usage(
        self,
        *,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached_input_tokens: int = 0,
        run_id: Optional[str] = None,
        request_id: Optional[str] = None,
        operation: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> TokenUsage:

        usage = TokenUsage(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=(
                cached_input_tokens
            ),
            run_id=run_id,
            request_id=request_id,
            operation=operation,
            metadata=metadata or {},
        )

        self.record(
            usage
        )

        return usage

    def summary(
        self,
        *,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        records = self._filter(
            run_id
        )

        input_tokens = sum(
            item.input_tokens
            for item in records
        )

        output_tokens = sum(
            item.output_tokens
            for item in records
        )

        cached_tokens = sum(
            item.cached_input_tokens
            for item in records
        )

        by_model: Dict[
            str,
            Dict[str, int]
        ] = {}

        for item in records:

            key = (
                f"{item.provider}:"
                f"{item.model}"
            )

            model = by_model.setdefault(
                key,
                {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                },
            )

            model["input_tokens"] += (
                item.input_tokens
            )

            model["output_tokens"] += (
                item.output_tokens
            )

            model["total_tokens"] += (
                item.total_tokens
            )

        return {
            "request_count":
                len(records),

            "input_tokens":
                input_tokens,

            "output_tokens":
                output_tokens,

            "cached_input_tokens":
                cached_tokens,

            "total_tokens":
                input_tokens
                + output_tokens,

            "by_model":
                by_model,
        }

    def _filter(
        self,
        run_id: Optional[str],
    ) -> List[TokenUsage]:

        with self._lock:

            if run_id is None:
                return list(
                    self._records
                )

            return [
                item
                for item in self._records
                if item.run_id
                == run_id
            ]