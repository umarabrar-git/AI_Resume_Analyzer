from __future__ import annotations

from services.resume_intelligence.providers import (
    GenerationConfig,
    LLMProvider,
)


SYSTEM_PROMPT = """
You improve resume bullet points while preserving factual accuracy.

Never invent achievements, metrics, responsibilities, technologies
or business outcomes.
"""


def generate_bullets(
    *,
    provider: LLMProvider,
    model: str,
    source_text: str,
    resume_text: str,
    job_description: str | None = None,
    instructions: str | None = None,
):

    prompt = f"""
Convert the supplied experience information into strong resume bullets.

SOURCE CONTENT:
{source_text}

FULL RESUME CONTEXT:
{resume_text}

JOB DESCRIPTION:
{job_description or "Not provided"}

ADDITIONAL INSTRUCTIONS:
{instructions or "None"}

Requirements:
- Preserve factual meaning.
- Use concise action-oriented bullets.
- Do not invent metrics.
- Do not invent responsibilities.
- Avoid repetitive wording.
- Return only the bullet points.
""".strip()

    return provider.complete(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        model=model,
        config=GenerationConfig(
            temperature=0.2,
            max_output_tokens=700,
        ),
        metadata={
            "generator": "bullet",
        },
    )