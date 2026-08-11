from .base_tool import (
    BaseTool,
    ToolDefinition,
)

from .tool_registry import (
    ToolRegistry,
)

from .tool_executor import (
    ToolExecutor,
)

from .resume_tool import (
    ResumeTool,
)

from .ats_tool import (
    ATSTool,
)

from .job_match_tool import (
    JobMatchTool,
)

from .skill_gap_tool import (
    SkillGapTool,
)

from .recommendation_tool import (
    RecommendationTool,
)

from .rewrite_tool import (
    RewriteTool,
)

from .cover_letter_tool import (
    CoverLetterTool,
)


def build_default_tool_registry(
    *,
    generation_service=None
) -> ToolRegistry:
    """
    Build the default Resume Agent tool registry.

    Generative tools are registered only when a
    GenerationService instance is supplied.
    """

    registry = ToolRegistry()

    registry.register(
        ResumeTool()
    )

    registry.register(
        ATSTool()
    )

    registry.register(
        JobMatchTool()
    )

    registry.register(
        SkillGapTool()
    )

    registry.register(
        RecommendationTool()
    )

    if generation_service is not None:

        registry.register(
            RewriteTool(
                generation_service
            )
        )

        registry.register(
            CoverLetterTool(
                generation_service
            )
        )

    return registry


__all__ = [
    "BaseTool",
    "ToolDefinition",
    "ToolRegistry",
    "ToolExecutor",
    "ResumeTool",
    "ATSTool",
    "JobMatchTool",
    "SkillGapTool",
    "RecommendationTool",
    "RewriteTool",
    "CoverLetterTool",
    "build_default_tool_registry",
]