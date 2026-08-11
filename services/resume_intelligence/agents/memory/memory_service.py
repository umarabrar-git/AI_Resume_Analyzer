from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import RLock
from typing import Any, Dict, Optional

from .conversation_memory import (
    ConversationMemory,
)

from .working_memory import (
    WorkingMemory,
)


@dataclass(frozen=True)
class MemoryScope:
    """
    Identifies memory ownership.

    Important for multi-user SaaS isolation.
    """

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    run_id: Optional[str] = None

    def key(self) -> str:

        parts = [
            self.user_id or "anonymous",
            self.session_id or "no-session",
            self.conversation_id or "no-conversation",
            self.run_id or "no-run",
        ]

        return ":".join(parts)


class PersistentMemoryStore(ABC):
    """
    Contract for future persistent memory backends.

    Examples:
    - Firestore
    - PostgreSQL
    - Redis
    - managed database storage
    """

    @abstractmethod
    def load(
        self,
        scope: MemoryScope
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save(
        self,
        scope: MemoryScope,
        data: Dict[str, Any]
    ) -> None:
        pass

    @abstractmethod
    def delete(
        self,
        scope: MemoryScope
    ) -> None:
        pass


class MemoryService:
    """
    Central memory coordinator for agent executions.

    Keeps:
    - working memory
    - conversation memory
    - optional persistence adapter

    isolated behind one service.
    """

    def __init__(
        self,
        *,
        persistent_store: Optional[
            PersistentMemoryStore
        ] = None,
        max_working_items: int = 100,
        max_conversation_turns: int = 50,
    ) -> None:

        self.persistent_store = (
            persistent_store
        )

        self.max_working_items = max(
            1,
            int(max_working_items)
        )

        self.max_conversation_turns = max(
            2,
            int(max_conversation_turns)
        )

        self._working_memories: Dict[
            str,
            WorkingMemory
        ] = {}

        self._conversation_memories: Dict[
            str,
            ConversationMemory
        ] = {}

        self._lock = RLock()

    def get_working_memory(
        self,
        scope: MemoryScope
    ) -> WorkingMemory:

        scope_key = scope.key()

        with self._lock:

            memory = (
                self._working_memories.get(
                    scope_key
                )
            )

            if memory is None:

                memory = WorkingMemory(
                    max_items=(
                        self.max_working_items
                    )
                )

                self._working_memories[
                    scope_key
                ] = memory

            return memory

    def get_conversation_memory(
        self,
        scope: MemoryScope
    ) -> ConversationMemory:

        conversation_key = (
            scope.conversation_id
            or scope.session_id
            or scope.key()
        )

        with self._lock:

            memory = (
                self._conversation_memories.get(
                    conversation_key
                )
            )

            if memory is None:

                memory = ConversationMemory(
                    conversation_id=(
                        conversation_key
                    ),
                    max_turns=(
                        self.max_conversation_turns
                    ),
                )

                self._conversation_memories[
                    conversation_key
                ] = memory

            return memory

    def remember(
        self,
        scope: MemoryScope,
        key: str,
        value: Any,
        *,
        namespace: str = "agent",
        ttl_seconds: Optional[int] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        memory = self.get_working_memory(
            scope
        )

        memory.set(
            key,
            value,
            namespace=namespace,
            ttl_seconds=ttl_seconds,
            metadata=metadata,
        )

    def recall(
        self,
        scope: MemoryScope,
        key: str,
        default: Any = None,
        *,
        namespace: str = "agent",
    ) -> Any:

        memory = self.get_working_memory(
            scope
        )

        return memory.get(
            key,
            default,
            namespace=namespace,
        )

    def add_user_message(
        self,
        scope: MemoryScope,
        content: str,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        conversation = (
            self.get_conversation_memory(
                scope
            )
        )

        conversation.add_user(
            content,
            metadata=metadata or {},
        )

    def add_assistant_message(
        self,
        scope: MemoryScope,
        content: str,
        *,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        conversation = (
            self.get_conversation_memory(
                scope
            )
        )

        conversation.add_assistant(
            content,
            metadata=metadata or {},
        )

    def build_agent_memory_context(
        self,
        scope: MemoryScope,
        *,
        conversation_limit: int = 12
    ) -> Dict[str, Any]:
        """
        Build memory context consumed by the agent.
        """

        working = self.get_working_memory(
            scope
        )

        conversation = (
            self.get_conversation_memory(
                scope
            )
        )

        return {
            "working_memory":
                working.values(),

            "conversation":
                conversation.to_messages(
                    limit=conversation_limit
                ),
        }

    def persist(
        self,
        scope: MemoryScope
    ) -> bool:
        """
        Persist memory when a persistent backend
        has been configured.
        """

        if self.persistent_store is None:
            return False

        working = self.get_working_memory(
            scope
        )

        conversation = (
            self.get_conversation_memory(
                scope
            )
        )

        payload = {
            "working_memory":
                working.snapshot(),

            "conversation_memory":
                conversation.snapshot(),
        }

        self.persistent_store.save(
            scope,
            payload
        )

        return True

    def delete_scope(
        self,
        scope: MemoryScope,
        *,
        delete_persistent: bool = False
    ) -> None:

        scope_key = scope.key()

        conversation_key = (
            scope.conversation_id
            or scope.session_id
            or scope_key
        )

        with self._lock:

            self._working_memories.pop(
                scope_key,
                None
            )

            self._conversation_memories.pop(
                conversation_key,
                None
            )

        if (
            delete_persistent
            and self.persistent_store
        ):
            self.persistent_store.delete(
                scope
            )

    def snapshot(
        self,
        scope: MemoryScope
    ) -> Dict[str, Any]:

        return {
            "scope": {
                "user_id":
                    scope.user_id,

                "session_id":
                    scope.session_id,

                "conversation_id":
                    scope.conversation_id,

                "run_id":
                    scope.run_id,
            },

            "working_memory":
                self.get_working_memory(
                    scope
                ).snapshot(),

            "conversation_memory":
                self.get_conversation_memory(
                    scope
                ).snapshot(),
        }