from __future__ import annotations

from services.resume_intelligence.providers import (
    AIModelTask,
    GenerationConfig,
    LLMProvider,
)

from services.resume_intelligence.generative.prompts import (
    SUMMARY_SYSTEM_PROMPT,
    build_summary_prompt,
)


def generate_summary(
    *,
    provider: LLMProvider,
    model: str,
    resume_text: str,
    target_role: str | None = None,
    job_description: str | None = None,
    instructions: str | None = None,
):

    prompt = build_summary_prompt(
        resume_text=resume_text,
        target_role=target_role,
        job_description=job_description,
        instructions=instructions,
    )

    return provider.complete(
        prompt=prompt,
        system_prompt=SUMMARY_SYSTEM_PROMPT,
        model=model,
        config=GenerationConfig(
            temperature=0.2,
            max_output_tokens=350,
        ),
        metadata={
            "task": AIModelTask.GENERATION.value,
            "generator": "summary",
        },
    )