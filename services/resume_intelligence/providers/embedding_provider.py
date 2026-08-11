"""
Embedding provider abstraction.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import List, Optional, Sequence

from .base_provider import (
    BaseProvider,
    EmbeddingResponse,
)


class EmbeddingProvider(BaseProvider):
    """
    Interface for embedding model providers.
    """

    @abstractmethod
    def embed(
        self,
        texts: Sequence[str],
        *,
        model: Optional[str] = None
    ) -> EmbeddingResponse:
        """
        Convert multiple texts into vectors.
        """

    def embed_one(
        self,
        text: str,
        *,
        model: Optional[str] = None
    ) -> List[float]:

        if not text or not text.strip():
            raise ValueError(
                "Embedding text cannot be empty."
            )

        result = self.embed(
            [text],
            model=model
        )

        if not result.vectors:
            raise RuntimeError(
                "Embedding provider returned no vectors."
            )

        return result.vectors[0]