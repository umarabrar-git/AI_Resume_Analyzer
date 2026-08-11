"""Catalog package public exports."""

from .profession_catalog import (
    PROFESSION_ICON_FALLBACK,
    PROFESSION_KEYWORDS,
    SKILL_ICON_MAP,
)
from .skill_catalog import SKILLS

__all__ = [
    "PROFESSION_ICON_FALLBACK",
    "PROFESSION_KEYWORDS",
    "SKILL_ICON_MAP",
    "SKILLS",
]
