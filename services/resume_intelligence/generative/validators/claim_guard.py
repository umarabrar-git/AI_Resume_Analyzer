from __future__ import annotations

import re
from typing import Any, Dict, List, Set


NUMBER_PATTERN = re.compile(
    r"""
    (?:
        [$£€]\s*
    )?
    \b\d+(?:[.,]\d+)?%?
    """,
    re.VERBOSE,
)


def _extract_numeric_claims(
    text: str
) -> Set[str]:

    if not text:
        return set()

    return {
        match.group(0).strip()
        for match in NUMBER_PATTERN.finditer(text)
    }


def detect_unsupported_numeric_claims(
    source_text: str,
    generated_text: str,
) -> List[str]:

    source_numbers = _extract_numeric_claims(
        source_text
    )

    generated_numbers = _extract_numeric_claims(
        generated_text
    )

    return sorted(
        generated_numbers - source_numbers
    )


def validate_generated_claims(
    source_text: str,
    generated_text: str,
) -> Dict[str, Any]:

    unsupported_numbers = (
        detect_unsupported_numeric_claims(
            source_text,
            generated_text,
        )
    )

    warnings = []

    if unsupported_numbers:
        warnings.append(
            "Generated content introduced numeric claims "
            "that were not detected in the source resume."
        )

    return {
        "valid": not unsupported_numbers,
        "unsupported_numeric_claims":
            unsupported_numbers,
        "warnings": warnings,
    }