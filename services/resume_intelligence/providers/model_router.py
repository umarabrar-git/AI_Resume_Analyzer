"""
Task-aware AI model routing.

Routing decisions remain separate from generators, agents and
vendor-specific provider adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .base_provider import (
    AIModelTask,
    ProviderConfigurationError,
)


@dataclass(frozen=True)
class ModelRoute:
    task: AIModelTask

    provider: str
    model: str

    fallback_provider: Optional[str] = None
    fallback_model: Optional[str] = None

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


class ModelRouter:

    def __init__(self) -> None:

        self._routes: Dict[
            AIModelTask,
            ModelRoute
        ] = {}

    def register(
        self,
        task: AIModelTask,
        *,
        provider: str,
        model: str,
        fallback_provider: Optional[str] = None,
        fallback_model: Optional[str] = None,
        metadata: Optional[
            Dict[str, str]
        ] = None,
    ) -> None:

        if not provider:
            raise ValueError(
                "Provider is required."
            )

        if not model:
            raise ValueError(
                "Model is required."
            )

        self._routes[task] = ModelRoute(
            task=task,

            provider=provider.strip().lower(),

            model=model.strip(),

            fallback_provider=(
                fallback_provider.strip().lower()
                if fallback_provider
                else None
            ),

            fallback_model=(
                fallback_model.strip()
                if fallback_model
                else None
            ),

            metadata=metadata or {}
        )

    def resolve(
        self,
        task: AIModelTask
    ) -> ModelRoute:

        route = self._routes.get(
            task
        )

        if route is None:
            raise ProviderConfigurationError(
                f"No model route configured "
                f"for task '{task.value}'."
            )

        return route

    def has_route(
        self,
        task: AIModelTask
    ) -> bool:

        return task in self._routes

    def remove(
        self,
        task: AIModelTask
    ) -> None:

        self._routes.pop(
            task,
            None
        )

    def all_routes(
        self
    ) -> Dict[str, ModelRoute]:

        return {
            task.value: route
            for task, route
            in self._routes.items()
        }