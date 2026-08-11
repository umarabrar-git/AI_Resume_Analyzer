from __future__ import annotations

from typing import Any, Dict


MINIMUM_LENGTH = 20
MAXIMUM_LENGTH = 30000


def validate_generated_content(
    content: str,
) -> Dict[str, Any]:

    errors = []
    warnings = []

    normalized = (
        content or ""
    ).strip()

    if not normalized:
        errors.append(
            "The AI provider returned empty content."
        )

    if (
        normalized
        and len(normalized) < MINIMUM_LENGTH
    ):
        warnings.append(
            "Generated content is unusually short."
        )

    if len(normalized) > MAXIMUM_LENGTH:
        errors.append(
            "Generated content exceeds the allowed size."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "character_count": len(normalized),
    }