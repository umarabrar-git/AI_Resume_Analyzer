from __future__ import annotations

from services.resume_intelligence.providers import (
    GenerationConfig,
    LLMProvider,
)

from services.resume_intelligence.generative.prompts import (
    REWRITE_SYSTEM_PROMPT,
    build_rewrite_prompt,
)


def rewrite_resume(
    *,
    provider: LLMProvider,
    model: str,
    resume_text: str,
    job_description: str | None = None,
    recommendations=None,
    instructions: str | None = None,
):

    prompt = build_rewrite_prompt(
        resume_text=resume_text,
        job_description=job_description,
        recommendations=recommendations,
        instructions=instructions,
    )

    return provider.complete(
        prompt=prompt,
        system_prompt=REWRITE_SYSTEM_PROMPT,
        model=model,
        config=GenerationConfig(
            temperature=0.15,
            max_output_tokens=3500,
        ),
        metadata={
            "generator": "resume_rewriter",
        },
    )