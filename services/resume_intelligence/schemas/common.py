from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


def generate_id(prefix: Optional[str] = None) -> str:
    value = str(uuid4())

    if prefix:
        return f"{prefix}_{value}"

    return value


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(
        minimum,
        min(float(value), maximum)
    )


def normalize_text(
    value: Optional[str]
) -> Optional[str]:

    if value is None:
        return None

    value = str(value).strip()

    return value or None


def normalize_string_list(
    values: Optional[List[str]]
) -> List[str]:

    if not values:
        return []

    seen = set()
    result = []

    for value in values:

        normalized = str(value).strip()

        if not normalized:
            continue

        key = normalized.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(normalized)

    return result


def serialize(value: Any) -> Any:
    """
    Convert schema objects into JSON-safe structures.
    """

    if value is None:
        return None

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if is_dataclass(value):
        return {
            key: serialize(item)
            for key, item
            in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            str(key): serialize(item)
            for key, item
            in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            serialize(item)
            for item in value
        ]

    return value


class SeniorityLevel(str, Enum):
    INTERN = "intern"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"
    UNKNOWN = "unknown"


class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    BUSINESS = "business"
    MANAGEMENT = "management"
    COMMUNICATION = "communication"
    LANGUAGE = "language"
    DOMAIN = "domain"
    TOOL = "tool"
    CERTIFICATION = "certification"
    OTHER = "other"


@dataclass
class Skill:
    name: str

    category: SkillCategory = (
        SkillCategory.OTHER
    )

    normalized_name: Optional[str] = None

    confidence: Optional[float] = None

    source: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.name = self.name.strip()

        if not self.name:
            raise ValueError(
                "Skill name is required."
            )

        if self.normalized_name is None:
            self.normalized_name = (
                self.name.casefold()
            )

        if self.confidence is not None:
            self.confidence = clamp(
                self.confidence
            )

    def to_dict(self) -> Dict[str, Any]:
        return serialize(self)


@dataclass
class Score:
    value: float

    maximum: float = 100.0

    label: Optional[str] = None

    explanation: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.maximum = max(
            float(self.maximum),
            0.0001
        )

        self.value = max(
            0.0,
            min(
                float(self.value),
                self.maximum
            )
        )

    @property
    def percentage(self) -> float:

        return round(
            (
                self.value
                / self.maximum
            )
            * 100,
            2
        )

    def to_dict(self) -> Dict[str, Any]:

        data = serialize(self)

        data["percentage"] = (
            self.percentage
        )

        return data