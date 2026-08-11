"""
Provider registry and factory.

Concrete vendor adapters register themselves here without forcing
the rest of the application to know their implementation classes.
"""

from __future__ import annotations

from threading import RLock
from typing import Dict, List, Type

from .base_provider import (
    BaseProvider,
    ProviderConfigurationError,
)


class ProviderFactory:

    _providers: Dict[
        str,
        Type[BaseProvider]
    ] = {}

    _lock = RLock()

    @classmethod
    def register(
        cls,
        name: str,
        provider_class: Type[BaseProvider],
        *,
        replace: bool = False
    ) -> None:

        normalized_name = (
            name
            or ""
        ).strip().lower()

        if not normalized_name:
            raise ValueError(
                "Provider name is required."
            )

        if not issubclass(
            provider_class,
            BaseProvider
        ):
            raise TypeError(
                "Provider must inherit from BaseProvider."
            )

        with cls._lock:

            if (
                normalized_name in cls._providers
                and not replace
            ):
                raise ValueError(
                    f"Provider '{normalized_name}' "
                    "is already registered."
                )

            cls._providers[
                normalized_name
            ] = provider_class

    @classmethod
    def unregister(
        cls,
        name: str
    ) -> None:

        normalized_name = (
            name
            or ""
        ).strip().lower()

        with cls._lock:
            cls._providers.pop(
                normalized_name,
                None
            )

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs
    ) -> BaseProvider:

        normalized_name = (
            name
            or ""
        ).strip().lower()

        provider_class = cls._providers.get(
            normalized_name
        )

        if provider_class is None:

            available = ", ".join(
                cls.available()
            ) or "none"

            raise ProviderConfigurationError(
                f"Unknown AI provider "
                f"'{normalized_name}'. "
                f"Registered providers: {available}."
            )

        return provider_class(
            **kwargs
        )

    @classmethod
    def available(
        cls
    ) -> List[str]:

        return sorted(
            cls._providers.keys()
        )