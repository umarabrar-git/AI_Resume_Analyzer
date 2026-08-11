from __future__ import annotations

from services.resume_intelligence.providers import (
    GenerationConfig,
    LLMProvider,
)

from services.resume_intelligence.generative.prompts import (
    EXPERIENCE_SYSTEM_PROMPT,
    build_experience_prompt,
)


def rewrite_experience(
    *,
    provider: LLMProvider,
    model: str,
    source_text: str,
    resume_text: str,
    job_description: str | None = None,
    instructions: str | None = None,
):

    prompt = build_experience_prompt(
        source_text=source_text,
        resume_text=resume_text,
        job_description=job_description,
        instructions=instructions,
    )

    return provider.complete(
        prompt=prompt,
        system_prompt=EXPERIENCE_SYSTEM_PROMPT,
        model=model,
        config=GenerationConfig(
            temperature=0.15,
            max_output_tokens=900,
        ),
        metadata={
            "generator": "experience_rewriter",
        },
    )