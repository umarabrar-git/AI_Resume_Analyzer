from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional
from uuid import uuid4


VALID_ROLES = {
    "system",
    "user",
    "assistant",
    "tool",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ConversationTurn:
    """
    One conversation event.
    """

    role: str
    content: str

    turn_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    name: Optional[str] = None

    tool_call_id: Optional[str] = None

    created_at: datetime = field(
        default_factory=utc_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.role = (
            self.role or ""
        ).strip().lower()

        self.content = (
            self.content or ""
        ).strip()

        if self.role not in VALID_ROLES:
            raise ValueError(
                f"Unsupported conversation role: "
                f"{self.role}"
            )

        if not self.content:
            raise ValueError(
                "Conversation content is required."
            )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "turn_id": self.turn_id,
            "role": self.role,
            "content": self.content,
            "name": self.name,
            "tool_call_id": self.tool_call_id,
            "created_at": (
                self.created_at.isoformat()
            ),
            "metadata": self.metadata,
        }


class ConversationMemory:
    """
    Bounded multi-turn conversation memory.

    A conversation belongs to one logical
    conversation/session context.
    """

    def __init__(
        self,
        conversation_id: str,
        *,
        max_turns: int = 50,
    ) -> None:

        self.conversation_id = (
            conversation_id or ""
        ).strip()

        if not self.conversation_id:
            raise ValueError(
                "conversation_id is required."
            )

        self.max_turns = max(
            2,
            int(max_turns)
        )

        self._turns: List[
            ConversationTurn
        ] = []

        self._lock = RLock()

    def add(
        self,
        role: str,
        content: str,
        *,
        name: Optional[str] = None,
        tool_call_id: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ConversationTurn:

        turn = ConversationTurn(
            role=role,
            content=content,
            name=name,
            tool_call_id=tool_call_id,
            metadata=metadata or {},
        )

        with self._lock:

            self._turns.append(
                turn
            )

            self._trim()

        return turn

    def add_user(
        self,
        content: str,
        **kwargs
    ) -> ConversationTurn:

        return self.add(
            "user",
            content,
            **kwargs
        )

    def add_assistant(
        self,
        content: str,
        **kwargs
    ) -> ConversationTurn:

        return self.add(
            "assistant",
            content,
            **kwargs
        )

    def add_system(
        self,
        content: str,
        **kwargs
    ) -> ConversationTurn:

        return self.add(
            "system",
            content,
            **kwargs
        )

    def add_tool(
        self,
        content: str,
        *,
        name: str,
        tool_call_id: Optional[str] = None,
        **kwargs
    ) -> ConversationTurn:

        return self.add(
            "tool",
            content,
            name=name,
            tool_call_id=tool_call_id,
            **kwargs
        )

    def _trim(self) -> None:

        if len(self._turns) <= self.max_turns:
            return

        system_turns = [
            turn
            for turn in self._turns
            if turn.role == "system"
        ]

        non_system = [
            turn
            for turn in self._turns
            if turn.role != "system"
        ]

        remaining_slots = max(
            0,
            self.max_turns
            - len(system_turns[:1])
        )

        self._turns = (
            system_turns[:1]
            + non_system[-remaining_slots:]
        )

    def recent(
        self,
        limit: int = 10
    ) -> List[ConversationTurn]:

        limit = max(
            1,
            int(limit)
        )

        with self._lock:
            return list(
                self._turns[-limit:]
            )

    def all(
        self
    ) -> List[ConversationTurn]:

        with self._lock:
            return list(
                self._turns
            )

    def to_messages(
        self,
        *,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:

        with self._lock:

            turns = (
                self._turns[-limit:]
                if limit
                else self._turns
            )

            messages = []

            for turn in turns:

                message = {
                    "role": turn.role,
                    "content": turn.content,
                }

                if turn.name:
                    message["name"] = (
                        turn.name
                    )

                messages.append(
                    message
                )

            return messages

    def clear(self) -> None:

        with self._lock:
            self._turns.clear()

    def snapshot(self) -> Dict[str, Any]:

        with self._lock:

            return {
                "conversation_id":
                    self.conversation_id,

                "max_turns":
                    self.max_turns,

                "turn_count":
                    len(self._turns),

                "turns": [
                    turn.to_dict()
                    for turn in self._turns
                ],
            }

    def __len__(self) -> int:

        with self._lock:
            return len(self._turns)