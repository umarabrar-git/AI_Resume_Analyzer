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
    "academic_research": {
        "label": "Academic Research",
        "tier": "free",
        "layout": "academic",
        "accent": "#315f58",
        "font": "Times-Roman",
    },
    "research_dossier": {
        "label": "Research Dossier",
        "tier": "premium",
        "layout": "research-dossier",
        "accent": "#28766f",
        "font": "Helvetica",
    },
    "scholars_folio": {
        "label": "Scholar's Folio",
        "tier": "premium",
        "layout": "scholars-folio",
        "accent": "#702f43",
        "font": "Times-Roman",
    },
    "campus_launch": {
        "label": "Campus Launch",
        "tier": "premium",
        "layout": "student-launch",
        "accent": "#f0b35a",
        "font": "Helvetica",
    },
    "first_mile": {
        "label": "First Mile",
        "tier": "premium",
        "layout": "student-first-mile",
        "accent": "#b6533c",
        "font": "Helvetica",
    },
    "launchpad": {
        "label": "Launchpad",
        "tier": "premium",
        "layout": "student-launchpad",
        "accent": "#315b96",
        "font": "Helvetica",
    },
    "technical": {
        "label": "Technical",
        "tier": "free",
        "layout": "technical",
        "accent": "#087e83",
        "font": "Courier",
    },
    "data_scientist": {
        "label": "Data Scientist",
        "tier": "premium",
        "layout": "data-science",
        "accent": "#147d78",
        "font": "Helvetica",
    },
    "cybersecurity_analyst": {
        "label": "Cybersecurity Analyst",
        "tier": "premium",
        "layout": "cybersecurity",
        "accent": "#a3d65c",
        "font": "Helvetica",
    },
    "technical_blueprint": {
        "label": "Technical Blueprint",
        "tier": "premium",
        "layout": "technical-blueprint",
        "accent": "#2d6cdf",
        "font": "Helvetica",
    },
    "executive": {
        "label": "Executive",
        "tier": "premium",
        "layout": "executive",
        "accent": "#9b742d",
        "font": "Times-Roman",
    },
    "operations_atlas": {
        "label": "Operations Atlas",
        "tier": "premium",
        "layout": "operations-atlas",
        "accent": "#246b55",
        "font": "Helvetica",
    },
    "boardroom_brief": {
        "label": "Boardroom Brief",
        "tier": "premium",
        "layout": "boardroom-brief",
        "accent": "#354d73",
        "font": "Helvetica",
    },
    "finance_ledger": {
        "label": "Finance Ledger",
        "tier": "premium",
        "layout": "finance-ledger",
        "accent": "#1f765d",
        "font": "Helvetica",
    },
    "capital_brief": {
        "label": "Capital Brief",
        "tier": "premium",
        "layout": "capital-brief",
        "accent": "#0b8b87",
        "font": "Helvetica",
    },
    "market_signal": {
        "label": "Market Signal",
        "tier": "premium",
        "layout": "market-signal",
        "accent": "#24a879",
        "font": "Helvetica",
    },
    "clinical_compass": {
        "label": "Clinical Compass",
        "tier": "premium",
        "layout": "clinical-compass",
        "accent": "#0c766e",
        "font": "Helvetica",
    },
    "carepath": {
        "label": "CarePath",
        "tier": "premium",
        "layout": "healthcare-carepath",
        "accent": "#287c91",
        "font": "Helvetica",
    },
    "ai_insights": {
        "label": "AI Insights",
        "tier": "premium",
        "layout": "insights",
        "accent": "#b84d62",
        "font": "Helvetica",
    },
    "prompt_engineer": {
        "label": "Prompt Engineer",
        "tier": "premium",
        "layout": "prompt-engineering",
        "accent": "#287b9b",
        "font": "Helvetica",
    },
    "model_card": {
        "label": "Model Card",
        "tier": "premium",
        "layout": "model-card",
        "accent": "#146b68",
        "font": "Helvetica",
    },
    "insight_grid": {
        "label": "Insight Grid",
        "tier": "premium",
        "layout": "insight-grid",
        "accent": "#3977a8",
        "font": "Helvetica",
    },
    "career_analytics": {
        "label": "Career Analytics",
        "tier": "premium",
        "layout": "analytics",
        "accent": "#4b7180",
        "font": "Helvetica",
    },
    "brand_identity": {
        "label": "Brand Identity",
        "tier": "premium",
        "layout": "brand-identity",
        "accent": "#e65d3b",
        "font": "Times-Roman",
    },
    "creative_portfolio": {
        "label": "Creative Portfolio",
        "tier": "premium",
        "layout": "creative",
        "accent": "#d65f8d",
        "font": "Helvetica",
    },
    "creative_studio": {
        "label": "Creative Studio",
        "tier": "premium",
        "layout": "creative-studio",
        "accent": "#5667f2",
        "font": "Helvetica",
    },
    "ats_professional": {
        "label": "ATS Professional",
        "tier": "premium",
        "layout": "ats",
        "accent": "#21496e",
        "font": "Helvetica",
    },
    "career_compass": {
        "label": "Career Compass",
        "tier": "premium",
        "layout": "career-compass",
        "accent": "#2f7561",
        "font": "Helvetica",
    },
    "product_manager": {
        "label": "Product Manager",
        "tier": "premium",
        "layout": "product",
        "accent": "#276678",
        "font": "Helvetica",
    },
    "product_impact": {
        "label": "Product Impact",
        "tier": "premium",
        "layout": "product-editorial",
        "accent": "#cf6749",
        "font": "Helvetica",
    },
    "discovery_research": {
        "label": "Discovery Research",
        "tier": "premium",
        "layout": "discovery-research",
        "accent": "#6357a5",
        "font": "Helvetica",
    },
    "cloud_architect": {
        "label": "Cloud Architect",
        "tier": "premium",
        "layout": "cloud-architect",
        "accent": "#3976a8",
        "font": "Helvetica",
    },
    "data_engineer": {
        "label": "Data Engineer",
        "tier": "premium",
        "layout": "data-engineering",
        "accent": "#167d78",
        "font": "Helvetica",
    },
    "legal_associate": {
        "label": "Legal Associate",
        "tier": "free",
        "layout": "legal-ats",
        "accent": "#315a78",
        "font": "Helvetica",
    },
    "counsel_portfolio": {
        "label": "Counsel Portfolio",
        "tier": "premium",
        "layout": "legal-editorial",
        "accent": "#8a6741",
        "font": "Times-Roman",
    },
    "revenue_operator": {
        "label": "Revenue Operator",
        "tier": "free",
        "layout": "sales-ats",
        "accent": "#245c86",
        "font": "Helvetica",
    },
    "account_growth": {
        "label": "Account Growth",
        "tier": "premium",
        "layout": "customer-success",
        "accent": "#b66a43",
        "font": "Helvetica",
    },
    "service_standard": {
        "label": "Service Standard",
        "tier": "free",
        "layout": "hospitality-ats",
        "accent": "#23645c",
        "font": "Helvetica",
    },
    "guest_experience": {
        "label": "Guest Experience",
        "tier": "premium",
        "layout": "hospitality-editorial",
        "accent": "#b87945",
        "font": "Times-Roman",
    },
    "engineering_core": {"label": "Engineering Core", "tier": "free", "layout": "engineering-ats", "accent": "#315c78", "font": "Helvetica"},
    "engineering_portfolio": {"label": "Engineering Portfolio", "tier": "premium", "layout": "engineering-editorial", "accent": "#c16b42", "font": "Times-Roman"},
    "educator_standard": {"label": "Educator Standard", "tier": "free", "layout": "education-ats", "accent": "#315f70", "font": "Helvetica"},
    "learning_architect": {"label": "Learning Architect", "tier": "premium", "layout": "education-editorial", "accent": "#b47a43", "font": "Times-Roman"},
    "public_service_standard": {"label": "Public Service Standard", "tier": "free", "layout": "public-service-ats", "accent": "#245b50", "font": "Helvetica"},
    "mission_impact": {"label": "Mission Impact", "tier": "premium", "layout": "nonprofit-editorial", "accent": "#b36c43", "font": "Times-Roman"},
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