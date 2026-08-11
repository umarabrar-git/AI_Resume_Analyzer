from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class MemoryItem:
    """
    One item stored inside agent working memory.
    """

    key: str
    value: Any

    namespace: str = "default"

    item_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=utc_now
    )

    updated_at: datetime = field(
        default_factory=utc_now
    )

    expires_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def storage_key(self) -> str:
        return f"{self.namespace}:{self.key}"

    @property
    def expired(self) -> bool:
        return (
            self.expires_at is not None
            and utc_now() >= self.expires_at
        )

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "key": self.key,
            "namespace": self.namespace,
            "value": deepcopy(self.value),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at
                else None
            ),
            "metadata": deepcopy(self.metadata),
        }


class WorkingMemory:
    """
    Thread-safe short-term memory for a single agent run.

    Intended for:
    - intermediate tool outputs
    - ATS results
    - job matching results
    - recommendations
    - temporary planning information
    - generated artifacts

    This is not permanent user storage.
    """

    def __init__(
        self,
        *,
        max_items: int = 100,
        default_ttl_seconds: Optional[int] = None,
    ) -> None:

        self.max_items = max(
            1,
            int(max_items)
        )

        self.default_ttl_seconds = (
            int(default_ttl_seconds)
            if default_ttl_seconds is not None
            else None
        )

        self._items: OrderedDict[
            str,
            MemoryItem
        ] = OrderedDict()

        self._lock = RLock()

    @staticmethod
    def _normalize_key(
        key: str
    ) -> str:

        normalized = (
            key or ""
        ).strip()

        if not normalized:
            raise ValueError(
                "Memory key is required."
            )

        return normalized

    @staticmethod
    def _normalize_namespace(
        namespace: str
    ) -> str:

        return (
            namespace or "default"
        ).strip().lower()

    def _storage_key(
        self,
        key: str,
        namespace: str
    ) -> str:

        return (
            f"{self._normalize_namespace(namespace)}:"
            f"{self._normalize_key(key)}"
        )

    def _calculate_expiry(
        self,
        ttl_seconds: Optional[int]
    ) -> Optional[datetime]:

        ttl = (
            ttl_seconds
            if ttl_seconds is not None
            else self.default_ttl_seconds
        )

        if ttl is None:
            return None

        ttl = int(ttl)

        if ttl <= 0:
            raise ValueError(
                "ttl_seconds must be greater than zero."
            )

        return utc_now() + timedelta(
            seconds=ttl
        )

    def _purge_expired(self) -> None:

        expired_keys = [
            key
            for key, item in self._items.items()
            if item.expired
        ]

        for key in expired_keys:
            self._items.pop(
                key,
                None
            )

    def _enforce_limit(self) -> None:

        while len(self._items) > self.max_items:
            self._items.popitem(
                last=False
            )

    def set(
        self,
        key: str,
        value: Any,
        *,
        namespace: str = "default",
        ttl_seconds: Optional[int] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> MemoryItem:

        storage_key = self._storage_key(
            key,
            namespace
        )

        with self._lock:

            self._purge_expired()

            existing = self._items.get(
                storage_key
            )

            if existing:

                existing.value = deepcopy(
                    value
                )

                existing.metadata.update(
                    metadata or {}
                )

                existing.expires_at = (
                    self._calculate_expiry(
                        ttl_seconds
                    )
                )

                existing.touch()

                self._items.move_to_end(
                    storage_key
                )

                return existing

            item = MemoryItem(
                key=self._normalize_key(key),
                value=deepcopy(value),
                namespace=(
                    self._normalize_namespace(
                        namespace
                    )
                ),
                expires_at=(
                    self._calculate_expiry(
                        ttl_seconds
                    )
                ),
                metadata=deepcopy(
                    metadata or {}
                ),
            )

            self._items[
                storage_key
            ] = item

            self._enforce_limit()

            return item

    def get(
        self,
        key: str,
        default: Any = None,
        *,
        namespace: str = "default"
    ) -> Any:

        storage_key = self._storage_key(
            key,
            namespace
        )

        with self._lock:

            self._purge_expired()

            item = self._items.get(
                storage_key
            )

            if item is None:
                return default

            self._items.move_to_end(
                storage_key
            )

            return deepcopy(
                item.value
            )

    def get_item(
        self,
        key: str,
        *,
        namespace: str = "default"
    ) -> Optional[MemoryItem]:

        storage_key = self._storage_key(
            key,
            namespace
        )

        with self._lock:

            self._purge_expired()

            return self._items.get(
                storage_key
            )

    def has(
        self,
        key: str,
        *,
        namespace: str = "default"
    ) -> bool:

        return (
            self.get_item(
                key,
                namespace=namespace
            )
            is not None
        )

    def delete(
        self,
        key: str,
        *,
        namespace: str = "default"
    ) -> bool:

        storage_key = self._storage_key(
            key,
            namespace
        )

        with self._lock:

            return (
                self._items.pop(
                    storage_key,
                    None
                )
                is not None
            )

    def clear(
        self,
        *,
        namespace: Optional[str] = None
    ) -> None:

        with self._lock:

            if namespace is None:
                self._items.clear()
                return

            normalized = (
                self._normalize_namespace(
                    namespace
                )
            )

            keys = [
                key
                for key, item
                in self._items.items()
                if item.namespace == normalized
            ]

            for key in keys:
                self._items.pop(
                    key,
                    None
                )

    def values(
        self,
        *,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:

        with self._lock:

            self._purge_expired()

            result = {}

            for item in self._items.values():

                if (
                    namespace is not None
                    and item.namespace
                    != self._normalize_namespace(
                        namespace
                    )
                ):
                    continue

                result[item.key] = deepcopy(
                    item.value
                )

            return result

    def snapshot(self) -> Dict[str, Any]:

        with self._lock:

            self._purge_expired()

            return {
                "max_items": self.max_items,
                "count": len(self._items),
                "items": [
                    item.to_dict()
                    for item
                    in self._items.values()
                ],
            }

    def __len__(self) -> int:

        with self._lock:
            self._purge_expired()
            return len(self._items)