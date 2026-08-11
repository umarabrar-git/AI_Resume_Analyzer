from __future__ import annotations

from threading import RLock
from typing import Dict, Iterable, List, Optional

from .base_tool import BaseTool


class ToolRegistry:
    """
    Thread-safe registry of tools available to the agent.
    """

    def __init__(self) -> None:

        self._tools: Dict[
            str,
            BaseTool
        ] = {}

        self._lock = RLock()

    @staticmethod
    def _normalize(
        name: str
    ) -> str:

        normalized = (
            name or ""
        ).strip().lower()

        if not normalized:
            raise ValueError(
                "Tool name is required."
            )

        return normalized

    def register(
        self,
        tool: BaseTool,
        *,
        replace: bool = False
    ) -> None:

        if not isinstance(
            tool,
            BaseTool
        ):
            raise TypeError(
                "tool must inherit from BaseTool."
            )

        name = self._normalize(
            tool.name
        )

        with self._lock:

            if (
                name in self._tools
                and not replace
            ):
                raise ValueError(
                    f"Tool '{name}' is already registered."
                )

            self._tools[name] = tool

    def unregister(
        self,
        name: str
    ) -> bool:

        name = self._normalize(name)

        with self._lock:
            return (
                self._tools.pop(
                    name,
                    None
                )
                is not None
            )

    def get(
        self,
        name: str
    ) -> BaseTool:

        name = self._normalize(name)

        with self._lock:

            tool = self._tools.get(
                name
            )

        if tool is None:
            raise KeyError(
                f"Unknown agent tool: {name}"
            )

        return tool

    def has(
        self,
        name: str
    ) -> bool:

        name = self._normalize(name)

        with self._lock:
            return name in self._tools

    def names(self) -> List[str]:

        with self._lock:
            return sorted(
                self._tools.keys()
            )

    def all(
        self
    ) -> List[BaseTool]:

        with self._lock:
            return list(
                self._tools.values()
            )

    def schemas(
        self,
        *,
        allowed_tools: Optional[
            Iterable[str]
        ] = None
    ) -> List[Dict]:

        allowed = None

        if allowed_tools is not None:
            allowed = {
                self._normalize(name)
                for name in allowed_tools
            }

        with self._lock:

            return [
                tool.schema()
                for name, tool
                in self._tools.items()
                if (
                    allowed is None
                    or name in allowed
                )
            ]