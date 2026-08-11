from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


@dataclass
class EvidenceItem:
    """
    Normalized evidence collected from an agent tool result.
    """

    source: str
    evidence_type: str

    evidence_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    content: Any = None
    tool_name: Optional[str] = None

    confidence: Optional[float] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.source = (
            self.source or "unknown"
        ).strip()

        self.evidence_type = (
            self.evidence_type or "general"
        ).strip()

        if self.confidence is not None:
            self.confidence = max(
                0.0,
                min(
                    1.0,
                    float(self.confidence)
                )
            )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "evidence_id": self.evidence_id,
            "source": self.source,
            "type": self.evidence_type,
            "tool_name": self.tool_name,
            "content": deepcopy(self.content),
            "confidence": self.confidence,
            "metadata": deepcopy(
                self.metadata
            ),
        }


from services.resume_intelligence.agents.schemas import (
    ToolResult,
)


class EvidenceCollector:
    """
    Collects and normalizes evidence produced by agent tools.

    This prevents the final synthesizer from reasoning directly
    over arbitrary ToolResult structures.
    """

    def collect(
        self,
        tool_results: Iterable[ToolResult]
    ) -> List[EvidenceItem]:

        evidence_items: List[
            EvidenceItem
        ] = []

        seen = set()

        for result in tool_results:

            if not isinstance(
                result,
                ToolResult
            ):
                continue

            if not result.success:
                continue

            explicit_evidence = (
                result.evidence or []
            )

            if explicit_evidence:

                for evidence in explicit_evidence:

                    item = (
                        self._from_explicit_evidence(
                            result,
                            evidence,
                        )
                    )

                    fingerprint = (
                        self._fingerprint(
                            item
                        )
                    )

                    if fingerprint in seen:
                        continue

                    seen.add(
                        fingerprint
                    )

                    evidence_items.append(
                        item
                    )

            # Also preserve the actual successful tool output.
            if result.data is not None:

                item = EvidenceItem(
                    source=result.tool_name,
                    evidence_type=(
                        "tool_result"
                    ),
                    tool_name=result.tool_name,
                    content=deepcopy(
                        result.data
                    ),
                    metadata={
                        "execution_id":
                            result.execution_id,

                        "duration_ms":
                            result.duration_ms,
                    },
                )

                fingerprint = (
                    self._fingerprint(
                        item
                    )
                )

                if fingerprint not in seen:

                    seen.add(
                        fingerprint
                    )

                    evidence_items.append(
                        item
                    )

        return evidence_items

    @staticmethod
    def _from_explicit_evidence(
        result: ToolResult,
        evidence: Dict[str, Any],
    ) -> EvidenceItem:

        if not isinstance(
            evidence,
            dict
        ):

            evidence = {
                "content": evidence
            }

        return EvidenceItem(
            source=str(
                evidence.get(
                    "source",
                    result.tool_name
                )
            ),

            evidence_type=str(
                evidence.get(
                    "type",
                    "general"
                )
            ),

            tool_name=result.tool_name,

            content=deepcopy(
                evidence.get(
                    "content"
                )
            ),

            confidence=(
                evidence.get(
                    "confidence"
                )
            ),

            metadata={
                key: deepcopy(value)
                for key, value
                in evidence.items()
                if key not in {
                    "source",
                    "type",
                    "content",
                    "confidence",
                }
            },
        )

    @staticmethod
    def _fingerprint(
        item: EvidenceItem
    ) -> str:

        return (
            f"{item.tool_name}|"
            f"{item.source}|"
            f"{item.evidence_type}|"
            f"{repr(item.content)}"
        )

    def summarize(
        self,
        evidence: Iterable[
            EvidenceItem
        ]
    ) -> Dict[str, Any]:

        items = list(
            evidence
        )

        by_tool: Dict[
            str,
            int
        ] = {}

        by_type: Dict[
            str,
            int
        ] = {}

        for item in items:

            tool = (
                item.tool_name
                or "unknown"
            )

            by_tool[tool] = (
                by_tool.get(
                    tool,
                    0
                )
                + 1
            )

            by_type[
                item.evidence_type
            ] = (
                by_type.get(
                    item.evidence_type,
                    0
                )
                + 1
            )

        return {
            "total_evidence":
                len(items),

            "by_tool":
                by_tool,

            "by_type":
                by_type,
        }