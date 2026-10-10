"""Server-owned resume template metadata and entitlement rules."""

from __future__ import annotations

from typing import Any, Dict


TEMPLATE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "classic": {
        "label": "Classic",
        "tier": "free",
        "layout": "single-column",
        "accent": "#2865df",
        "font": "Helvetica",
    },
    "professional": {
        "label": "Professional",
        "tier": "free",
        "layout": "single-column",
        "accent": "#137f79",
        "font": "Helvetica",
    },
    "modern": {
        "label": "Modern",
        "tier": "free",
        "layout": "sidebar",
        "accent": "#0f8b80",
        "font": "Helvetica",
    },
    "minimal": {
        "label": "Minimal",
        "tier": "free",
        "layout": "editorial",
        "accent": "#a35c48",
        "font": "Times-Roman",
    },
    "modern_editorial": {
        "label": "Modern Editorial",
        "tier": "free",
        "layout": "editorial",
        "accent": "#b65c43",
        "font": "Times-Roman",
    },
    "technical": {
        "label": "Technical",
        "tier": "free",
        "layout": "technical",
        "accent": "#087e83",
        "font": "Courier",
    },
    "executive": {
        "label": "Executive",
        "tier": "premium",
        "layout": "executive",
        "accent": "#9b742d",
        "font": "Times-Roman",
    },
    "ai_insights": {
        "label": "AI Insights",
        "tier": "premium",
        "layout": "insights",
        "accent": "#b84d62",
        "font": "Helvetica",
    },
    "career_analytics": {
        "label": "Career Analytics",
        "tier": "premium",
        "layout": "analytics",
        "accent": "#4b7180",
        "font": "Helvetica",
    },
}

PREMIUM_PLANS = {"pro", "enterprise"}


def can_use_template(template_id: str, subscription_plan: str) -> bool:
    template = TEMPLATE_REGISTRY.get(str(template_id or "").strip().lower())
    if template is None:
        return False
    return template["tier"] == "free" or str(subscription_plan or "free").lower() in PREMIUM_PLANS


def get_template_catalog(subscription_plan: str) -> list[Dict[str, Any]]:
    return [
        {
            "id": template_id,
            **metadata,
            "available": can_use_template(template_id, subscription_plan),
        }
        for template_id, metadata in TEMPLATE_REGISTRY.items()
    ]