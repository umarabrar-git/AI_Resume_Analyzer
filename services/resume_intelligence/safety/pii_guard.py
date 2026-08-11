from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PIIType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    LINKEDIN = "linkedin"
    GITHUB = "github"


@dataclass(frozen=True)
class PIIMatch:
    pii_type: PIIType
    value: str
    start: int
    end: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.pii_type.value,
            "value": self.value,
            "start": self.start,
            "end": self.end,
        }


@dataclass
class PIIResult:
    contains_pii: bool
    matches: List[PIIMatch] = field(
        default_factory=list
    )
    redacted_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contains_pii": self.contains_pii,
            "matches": [
                item.to_dict()
                for item in self.matches
            ],
            "redacted_text": self.redacted_text,
        }


class PIIGuard:
    """
    Detects and optionally redacts common contact PII.

    This layer intentionally focuses on deterministic,
    high-confidence patterns rather than guessing sensitive
    attributes from free text.
    """

    PATTERNS = {
        PIIType.EMAIL: re.compile(
            r"\b[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),

        PIIType.PHONE: re.compile(
            r"(?<!\w)"
            r"(?:\+?\d{1,3}[\s.-]?)?"
            r"(?:\(?\d{2,4}\)?[\s.-]?)"
            r"\d{3,4}[\s.-]?\d{3,4}"
            r"(?!\w)"
        ),

        PIIType.LINKEDIN: re.compile(
            r"(?:https?://)?"
            r"(?:www\.)?"
            r"linkedin\.com/in/[^\s]+",
            re.IGNORECASE,
        ),

        PIIType.GITHUB: re.compile(
            r"(?:https?://)?"
            r"(?:www\.)?"
            r"github\.com/[A-Za-z0-9_.-]+",
            re.IGNORECASE,
        ),

        PIIType.URL: re.compile(
            r"https?://[^\s]+",
            re.IGNORECASE,
        ),
    }

    REDACTION_LABELS = {
        PIIType.EMAIL: "[EMAIL]",
        PIIType.PHONE: "[PHONE]",
        PIIType.LINKEDIN: "[LINKEDIN]",
        PIIType.GITHUB: "[GITHUB]",
        PIIType.URL: "[URL]",
    }

    def detect(
        self,
        text: str,
    ) -> PIIResult:

        if not text:
            return PIIResult(
                contains_pii=False
            )

        matches: List[PIIMatch] = []

        # Specific URL patterns first.
        order = (
            PIIType.EMAIL,
            PIIType.PHONE,
            PIIType.LINKEDIN,
            PIIType.GITHUB,
            PIIType.URL,
        )

        occupied: List[
            tuple[int, int]
        ] = []

        for pii_type in order:

            pattern = self.PATTERNS[
                pii_type
            ]

            for match in pattern.finditer(
                text
            ):

                start, end = match.span()

                if self._overlaps(
                    start,
                    end,
                    occupied,
                ):
                    continue

                matches.append(
                    PIIMatch(
                        pii_type=pii_type,
                        value=match.group(),
                        start=start,
                        end=end,
                    )
                )

                occupied.append(
                    (start, end)
                )

        matches.sort(
            key=lambda item: item.start
        )

        return PIIResult(
            contains_pii=bool(matches),
            matches=matches,
        )

    def redact(
        self,
        text: str,
    ) -> PIIResult:

        result = self.detect(text)

        if not result.matches:
            result.redacted_text = text
            return result

        redacted = text

        # Reverse replacement preserves offsets.
        for item in reversed(
            result.matches
        ):

            replacement = (
                self.REDACTION_LABELS[
                    item.pii_type
                ]
            )

            redacted = (
                redacted[:item.start]
                + replacement
                + redacted[item.end:]
            )

        result.redacted_text = redacted

        return result

    @staticmethod
    def _overlaps(
        start: int,
        end: int,
        occupied: List[
            tuple[int, int]
        ],
    ) -> bool:

        return any(
            start < existing_end
            and end > existing_start
            for existing_start,
            existing_end
            in occupied
        )