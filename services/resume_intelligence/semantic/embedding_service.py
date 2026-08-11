from typing import List


class EmbeddingService:
    """Lightweight embedding service wrapper for semantic similarity workflows."""

    def encode(self, texts: List[str]):
        """Return placeholder embeddings for the provided texts."""
        if not texts:
            return []

        return [
            {"text": text, "vector": []}
            for text in texts
        ]
