from __future__ import annotations

from typing import Dict, Optional

from services.resume_intelligence.providers import (
    AIModelTask,
    LLMProvider,
    ModelRouter,
    ProviderFactory,
)

from .generators import (
    generate_bullets,
    generate_cover_letter,
    generate_summary,
    rewrite_experience,
    rewrite_resume,
)

from .schemas import (
    GenerationRequest,
    GenerationResponse,
)

from .validators import (
    validate_generated_claims,
    validate_generated_content,
)


TASK_SUMMARY = "summary"
TASK_BULLETS = "bullets"
TASK_EXPERIENCE = "experience_rewrite"
TASK_RESUME_REWRITE = "resume_rewrite"
TASK_COVER_LETTER = "cover_letter"


SUPPORTED_TASKS = {
    TASK_SUMMARY,
    TASK_BULLETS,
    TASK_EXPERIENCE,
    TASK_RESUME_REWRITE,
    TASK_COVER_LETTER,
}


class GenerationService:
    """
    Central service for all resume-related generative AI tasks.

    Responsibilities:
    - validate generation requests
    - select the appropriate model
    - obtain provider instance
    - dispatch to a specialized generator
    - validate generated content
    - detect unsupported numeric claims
    - normalize output for API/UI/agents
    """

    def __init__(
        self,
        model_router: ModelRouter,
        provider_options: Optional[
            Dict[str, Dict]
        ] = None,
    ) -> None:

        self.model_router = model_router

        self.provider_options = (
            provider_options or {}
        )

    def _resolve_provider(
        self,
        task: AIModelTask
    ):

        route = self.model_router.resolve(
            task
        )

        options = self.provider_options.get(
            route.provider,
            {}
        )

        provider = ProviderFactory.create(
            route.provider,
            **options
        )

        if not isinstance(
            provider,
            LLMProvider
        ):
            raise TypeError(
                f"Provider '{route.provider}' "
                "does not implement LLMProvider."
            )

        return provider, route

    @staticmethod
    def _source_for_validation(
        request: GenerationRequest
    ) -> str:

        if request.source_text:
            return (
                request.resume_text
                + "\n"
                + request.source_text
            )

        return request.resume_text

    def generate(
        self,
        request: GenerationRequest
    ) -> GenerationResponse:

        if request.task not in SUPPORTED_TASKS:
            raise ValueError(
                f"Unsupported generation task: "
                f"{request.task}"
            )

        provider, route = (
            self._resolve_provider(
                AIModelTask.GENERATION
            )
        )

        provider_response = (
            self._dispatch(
                request=request,
                provider=provider,
                model=route.model,
            )
        )

        content = (
            provider_response.content
            or ""
        ).strip()

        content_validation = (
            validate_generated_content(
                content
            )
        )

        claim_validation = (
            validate_generated_claims(
                source_text=(
                    self._source_for_validation(
                        request
                    )
                ),
                generated_text=content,
            )
        )

        warnings = []

        warnings.extend(
            content_validation.get(
                "warnings",
                []
            )
        )

        warnings.extend(
            claim_validation.get(
                "warnings",
                []
            )
        )

        errors = content_validation.get(
            "errors",
            []
        )

        success = (
            content_validation.get(
                "valid",
                False
            )
            and not errors
        )

        validation = {
            "content":
                content_validation,

            "claims":
                claim_validation,
        }

        return GenerationResponse(
            task=request.task,

            content=content,

            success=success,

            model=(
                provider_response.model
                or route.model
            ),

            provider=(
                provider_response.provider
                or route.provider
            ),

            warnings=warnings,

            validation=validation,

            usage=(
                provider_response.usage.to_dict()
            ),

            metadata={
                "finish_reason":
                    provider_response.finish_reason,

                "latency_ms":
                    provider_response.latency_ms,

                "provider_metadata":
                    provider_response.metadata,
            },
        )

    def _dispatch(
        self,
        *,
        request: GenerationRequest,
        provider: LLMProvider,
        model: str,
    ):

        if request.task == TASK_SUMMARY:

            return generate_summary(
                provider=provider,
                model=model,
                resume_text=request.resume_text,
                target_role=request.target_role,
                job_description=(
                    request.job_description
                ),
                instructions=request.instructions,
            )

        if request.task == TASK_BULLETS:

            if not request.source_text:
                raise ValueError(
                    "source_text is required "
                    "for bullet generation."
                )

            return generate_bullets(
                provider=provider,
                model=model,
                source_text=request.source_text,
                resume_text=request.resume_text,
                job_description=(
                    request.job_description
                ),
                instructions=request.instructions,
            )

        if request.task == TASK_EXPERIENCE:

            if not request.source_text:
                raise ValueError(
                    "source_text is required "
                    "for experience rewriting."
                )

            return rewrite_experience(
                provider=provider,
                model=model,
                source_text=request.source_text,
                resume_text=request.resume_text,
                job_description=(
                    request.job_description
                ),
                instructions=request.instructions,
            )

        if request.task == TASK_RESUME_REWRITE:

            return rewrite_resume(
                provider=provider,
                model=model,
                resume_text=request.resume_text,
                job_description=(
                    request.job_description
                ),
                recommendations=(
                    request.recommendations
                ),
                instructions=request.instructions,
            )

        if request.task == TASK_COVER_LETTER:

            return generate_cover_letter(
                provider=provider,
                model=model,
                resume_text=request.resume_text,
                job_description=(
                    request.job_description
                ),
                target_role=request.target_role,
                instructions=request.instructions,
            )

        raise ValueError(
            f"No generator registered "
            f"for task '{request.task}'."
        )


def generate_content(
    *,
    service: GenerationService,
    task: str,
    resume_text: str,
    job_description: str | None = None,
    source_text: str | None = None,
    target_role: str | None = None,
    instructions: str | None = None,
    recommendations=None,
    metadata=None,
):
    """
    Convenience API used by routes, workflows and agent tools.
    """

    request = GenerationRequest(
        task=task,
        resume_text=resume_text,
        job_description=job_description,
        source_text=source_text,
        target_role=target_role,
        instructions=instructions,
        recommendations=(
            recommendations or []
        ),
        metadata=metadata or {},
    )

    return service.generate(
        request
    )