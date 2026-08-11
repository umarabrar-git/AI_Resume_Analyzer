from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from time import perf_counter
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass
class TraceSpan:
    name: str

    span_id: str = field(
        default_factory=lambda:
            str(uuid4())
    )

    parent_span_id: Optional[str] = None

    component: Optional[str] = None

    started_at: str = field(
        default_factory=_utc_now
    )

    ended_at: Optional[str] = None

    duration_ms: Optional[float] = None

    status: str = "running"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    error: Optional[str] = None

    _start_clock: float = field(
        default_factory=perf_counter,
        repr=False,
    )

    def finish(
        self,
        *,
        status: str = "completed",
        error: Optional[str] = None,
    ) -> None:

        self.ended_at = _utc_now()

        self.duration_ms = round(
            (
                perf_counter()
                - self._start_clock
            )
            * 1000,
            2,
        )

        self.status = status
        self.error = error

    def to_dict(self) -> Dict[str, Any]:

        return {
            "span_id": self.span_id,
            "parent_span_id":
                self.parent_span_id,
            "name": self.name,
            "component": self.component,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms":
                self.duration_ms,
            "status": self.status,
            "metadata": self.metadata,
            "error": self.error,
        }


@dataclass
class AgentTrace:
    run_id: str

    trace_id: str = field(
        default_factory=lambda:
            str(uuid4())
    )

    request_id: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None

    started_at: str = field(
        default_factory=_utc_now
    )

    ended_at: Optional[str] = None

    status: str = "running"

    spans: List[TraceSpan] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "organization_id":
                self.organization_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "status": self.status,
            "spans": [
                span.to_dict()
                for span in self.spans
            ],
            "metadata": self.metadata,
        }


class AgentTracer:
    """
    In-process agent execution tracer.

    Storage can later be replaced with OpenTelemetry,
    Firebase, PostgreSQL or another observability backend.
    """

    def __init__(self) -> None:

        self._traces: Dict[
            str,
            AgentTrace
        ] = {}

        self._lock = RLock()

    def start_trace(
        self,
        *,
        run_id: str,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> AgentTrace:

        trace = AgentTrace(
            run_id=run_id,
            request_id=request_id,
            user_id=user_id,
            organization_id=(
                organization_id
            ),
            metadata=metadata or {},
        )

        with self._lock:
            self._traces[
                run_id
            ] = trace

        return trace

    def start_span(
        self,
        run_id: str,
        name: str,
        *,
        component: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> TraceSpan:

        trace = self._require_trace(
            run_id
        )

        span = TraceSpan(
            name=name,
            component=component,
            parent_span_id=(
                parent_span_id
            ),
            metadata=metadata or {},
        )

        with self._lock:
            trace.spans.append(
                span
            )

        return span

    def finish_span(
        self,
        run_id: str,
        span_id: str,
        *,
        status: str = "completed",
        error: Optional[str] = None,
    ) -> None:

        trace = self._require_trace(
            run_id
        )

        with self._lock:

            for span in trace.spans:

                if (
                    span.span_id
                    == span_id
                ):

                    span.finish(
                        status=status,
                        error=error,
                    )

                    return

        raise KeyError(
            f"Unknown span: {span_id}"
        )

    def finish_trace(
        self,
        run_id: str,
        *,
        status: str = "completed",
    ) -> AgentTrace:

        trace = self._require_trace(
            run_id
        )

        with self._lock:

            trace.status = status
            trace.ended_at = _utc_now()

        return trace

    def get_trace(
        self,
        run_id: str,
    ) -> Optional[AgentTrace]:

        with self._lock:
            return self._traces.get(
                run_id
            )

    def remove_trace(
        self,
        run_id: str,
    ) -> bool:

        with self._lock:

            return (
                self._traces.pop(
                    run_id,
                    None,
                )
                is not None
            )

    def _require_trace(
        self,
        run_id: str,
    ) -> AgentTrace:

        trace = self.get_trace(
            run_id
        )

        if trace is None:
            raise KeyError(
                f"Trace not found for run "
                f"'{run_id}'."
            )

        return trace