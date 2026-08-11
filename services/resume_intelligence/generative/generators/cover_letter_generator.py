from __future__ import annotations

from services.resume_intelligence.providers import (
    GenerationConfig,
    LLMProvider,
)

from services.resume_intelligence.generative.prompts import (
    COVER_LETTER_SYSTEM_PROMPT,
    build_cover_letter_prompt,
)


def generate_cover_letter(
    *,
    provider: LLMProvider,
    model: str,
    resume_text: str,
    job_description: str | None = None,
    target_role: str | None = None,
    instructions: str | None = None,
):

    prompt = build_cover_letter_prompt(
        resume_text=resume_text,
        job_description=job_description,
        target_role=target_role,
        instructions=instructions,
    )

    return provider.complete(
        prompt=prompt,
        system_prompt=COVER_LETTER_SYSTEM_PROMPT,
        model=model,
        config=GenerationConfig(
            temperature=0.3,
            max_output_tokens=1000,
        ),
        metadata={
            "generator": "cover_letter",
        },
    )