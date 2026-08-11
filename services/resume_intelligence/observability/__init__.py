"""Observability helpers for resume intelligence."""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class AILogEvent:
    event: str

    level: str = "INFO"

    run_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None

    component: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    timestamp: str = field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            ).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AILogger:
    """
    Structured logger for Resume Intelligence.

    Important:
    Raw resumes, job descriptions, prompts and generated
    documents should not be logged by default because they
    can contain personal or confidential information.
    """

    def __init__(
        self,
        name: str = "resume_intelligence",
    ) -> None:

        self.logger = logging.getLogger(
            name
        )

    def log(
        self,
        event: str,
        *,
        level: str = "INFO",
        run_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        component: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        record = AILogEvent(
            event=event,
            level=level.upper(),
            run_id=run_id,
            request_id=request_id,
            user_id=user_id,
            organization_id=(
                organization_id
            ),
            component=component,
            metadata=self._sanitize_metadata(
                metadata or {}
            ),
        )

        message = json.dumps(
            record.to_dict(),
            ensure_ascii=False,
            default=str,
        )

        log_method = getattr(
            self.logger,
            level.lower(),
            self.logger.info,
        )

        log_method(message)

    def info(
        self,
        event: str,
        **kwargs,
    ) -> None:

        self.log(
            event,
            level="INFO",
            **kwargs,
        )

    def warning(
        self,
        event: str,
        **kwargs,
    ) -> None:

        self.log(
            event,
            level="WARNING",
            **kwargs,
        )

    def error(
        self,
        event: str,
        **kwargs,
    ) -> None:

        self.log(
            event,
            level="ERROR",
            **kwargs,
        )

    @staticmethod
    def _sanitize_metadata(
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Remove common high-risk fields from structured logs.
        """

        blocked_keys = {
            "resume_text",
            "job_description",
            "prompt",
            "system_prompt",
            "password",
            "token",
            "api_key",
            "authorization",
            "generated_text",
        }

        result = {}

        for key, value in metadata.items():

            normalized = str(
                key
            ).casefold()

            if normalized in blocked_keys:
                result[key] = "[REDACTED]"
            else:
                result[key] = value

        return result


_default_logger = AILogger()


def get_ai_logger() -> AILogger:
    return _default_logger