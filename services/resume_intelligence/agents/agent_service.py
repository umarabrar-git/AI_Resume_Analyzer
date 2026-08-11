from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Dict, Iterable, Optional

from services.resume_intelligence.agents.context import (
    ContextBuilder,
)

from services.resume_intelligence.agents.guardrails import (
    InputGuard,
    OutputGuard,
    ToolGuard,
)

from services.resume_intelligence.agents.memory import (
    MemoryService,
)

from services.resume_intelligence.agents.planning import (
    TaskPlanner,
)

from services.resume_intelligence.agents.reasoning import (
    ResultSynthesizer,
)

from services.resume_intelligence.agents.schemas import (
    AgentRequest,
    AgentResponse,
)

from services.resume_intelligence.agents.tools import (
    ToolExecutor,
    ToolRegistry,
    build_default_tool_registry,
)

from services.resume_intelligence.agents.resume_agent import (
    ResumeAgent,
    ResumeAgentConfig,
)


# ============================================================
# SaaS Plan Definitions
# ============================================================

PLAN_FREE = "free"
PLAN_PRO = "pro"
PLAN_BUSINESS = "business"
PLAN_ENTERPRISE = "enterprise"


PLAN_TOOL_ACCESS = {

    PLAN_FREE: {
        "resume",
        "ats",
    },

    PLAN_PRO: {
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
        "rewrite",
        "cover_letter",
    },

    PLAN_BUSINESS: {
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
        "rewrite",
        "cover_letter",
    },

    PLAN_ENTERPRISE: {
        "resume",
        "ats",
        "job_match",
        "skill_gap",
        "recommendation",
        "rewrite",
        "cover_letter",
    },
}


# ============================================================
# Service Configuration
# ============================================================

@dataclass
class AgentServiceConfig:
    """
    Application-level configuration for the AI Agent service.
    """

    product_name: str = "Resume Intelligence"

    default_plan: str = PLAN_FREE

    max_iterations: int = 20

    persist_memory: bool = False

    enable_input_guard: bool = True

    enable_output_guard: bool = True

    stop_on_required_failure: bool = True

    continue_on_optional_failure: bool = True

    allow_plan_overrides: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.default_plan = (
            self.default_plan
            or PLAN_FREE
        ).strip().lower()

        if self.default_plan not in PLAN_TOOL_ACCESS:

            raise ValueError(
                f"Unsupported SaaS plan: "
                f"{self.default_plan}"
            )

        self.max_iterations = max(
            1,
            int(self.max_iterations)
        )


# ============================================================
# Agent Service
# ============================================================

class AgentService:
    """
    Application facade for ResumeAgent.

    Routes/controllers should communicate with this service
    instead of directly constructing or managing agents.

    Responsibilities:
    - request creation
    - SaaS-plan capability resolution
    - organization restrictions
    - agent lifecycle
    - execution boundary
    - public capability discovery
    - future billing/quota hooks
    - future persistence hooks
    """

    def __init__(
        self,
        *,
        generation_service=None,
        tool_registry: Optional[
            ToolRegistry
        ] = None,
        memory_service: Optional[
            MemoryService
        ] = None,
        context_builder: Optional[
            ContextBuilder
        ] = None,
        task_planner: Optional[
            TaskPlanner
        ] = None,
        result_synthesizer: Optional[
            ResultSynthesizer
        ] = None,
        input_guard: Optional[
            InputGuard
        ] = None,
        output_guard: Optional[
            OutputGuard
        ] = None,
        tool_guard: Optional[
            ToolGuard
        ] = None,
        config: Optional[
            AgentServiceConfig
        ] = None,
    ) -> None:

        self.config = (
            config
            or AgentServiceConfig()
        )

        self._lock = RLock()

        self.memory_service = (
            memory_service
            or MemoryService()
        )

        # ----------------------------------------------------
        # Tool Registry
        # ----------------------------------------------------

        self.tool_registry = (
            tool_registry
            or build_default_tool_registry(
                generation_service=(
                    generation_service
                )
            )
        )

        # ----------------------------------------------------
        # Tool Security Boundary
        # ----------------------------------------------------

        self.tool_guard = (
            tool_guard
            or ToolGuard()
        )

        self.tool_executor = (
            ToolExecutor(
                registry=self.tool_registry,
                tool_guard=self.tool_guard,
            )
        )

        # ----------------------------------------------------
        # Main Agent
        # ----------------------------------------------------

        self.agent = ResumeAgent(
            tool_registry=self.tool_registry,
            tool_executor=self.tool_executor,

            context_builder=(
                context_builder
                or ContextBuilder()
            ),

            task_planner=(
                task_planner
                or TaskPlanner()
            ),

            memory_service=(
                self.memory_service
            ),

            result_synthesizer=(
                result_synthesizer
                or ResultSynthesizer()
            ),

            input_guard=(
                input_guard
                or InputGuard()
            ),

            output_guard=(
                output_guard
                or OutputGuard()
            ),

            config=ResumeAgentConfig(
                max_iterations=(
                    self.config.max_iterations
                ),

                stop_on_required_failure=(
                    self.config
                    .stop_on_required_failure
                ),

                continue_on_optional_failure=(
                    self.config
                    .continue_on_optional_failure
                ),

                persist_memory=(
                    self.config.persist_memory
                ),

                enable_input_guard=(
                    self.config
                    .enable_input_guard
                ),

                enable_output_guard=(
                    self.config
                    .enable_output_guard
                ),
            ),
        )

    # ========================================================
    # Public Execution API
    # ========================================================

    def run(
        self,
        *,
        message: str,
        resume_text: Optional[str] = None,
        job_description: Optional[str] = None,

        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None,

        organization_id: Optional[str] = None,

        plan: Optional[str] = None,

        mode: str = "analyze",

        context: Optional[
            Dict[str, Any]
        ] = None,

        metadata: Optional[
            Dict[str, Any]
        ] = None,

        organization_allowed_tools: Optional[
            Iterable[str]
        ] = None,

    ) -> AgentResponse:
        """
        Main application entry point.

        Flask routes should normally call this method.
        """

        normalized_message = (
            message or ""
        ).strip()

        if not normalized_message:

            return self._validation_error(
                "Agent message is required."
            )

        selected_plan = (
            plan
            or self.config.default_plan
        ).strip().lower()

        try:

            plan_tools = (
                self.resolve_plan_tools(
                    selected_plan
                )
            )

        except ValueError as exc:

            return self._validation_error(
                str(exc)
            )

        # ----------------------------------------------------
        # Organization Restrictions
        # ----------------------------------------------------

        organization_tools = (
            self._normalize_tool_set(
                organization_allowed_tools
            )
        )

        effective_tools = set(
            plan_tools
        )

        if organization_tools is not None:

            effective_tools &= (
                organization_tools
            )

        # ----------------------------------------------------
        # Build Agent Request
        # ----------------------------------------------------

        try:

            request = AgentRequest(
                message=normalized_message,

                resume_text=(
                    resume_text
                    or None
                ),

                job_description=(
                    job_description
                    or None
                ),

                user_id=user_id,

                session_id=session_id,

                conversation_id=(
                    conversation_id
                ),

                mode=(
                    mode
                    or "analyze"
                ),

                context={
                    **(
                        context
                        or {}
                    ),

                    "organization_id":
                        organization_id,

                    "saas_plan":
                        selected_plan,
                },

                metadata={
                    **(
                        metadata
                        or {}
                    ),

                    "organization_id":
                        organization_id,

                    "saas_plan":
                        selected_plan,

                    "service":
                        "resume_agent",
                },
            )

        except (
            ValueError,
            TypeError
        ) as exc:

            return self._validation_error(
                str(exc)
            )

        # ----------------------------------------------------
        # Execute Agent
        # ----------------------------------------------------

        try:

            response = self.agent.run(
                request,

                plan_allowed_tools=(
                    effective_tools
                ),

                organization_allowed_tools=(
                    organization_tools
                ),
            )

        except Exception as exc:

            return self._service_error(
                request=request,
                error=exc,
            )

        # ----------------------------------------------------
        # Attach SaaS Metadata
        # ----------------------------------------------------

        response.metadata.setdefault(
            "service",
            {}
        )

        response.metadata[
            "service"
        ].update(
            {
                "product":
                    self.config.product_name,

                "plan":
                    selected_plan,

                "organization_id":
                    organization_id,

                "available_tools":
                    sorted(
                        effective_tools
                    ),
            }
        )

        return response

    # ========================================================
    # Existing AgentRequest Support
    # ========================================================

    def run_request(
        self,
        request: AgentRequest,
        *,
        plan: Optional[str] = None,
        organization_allowed_tools: Optional[
            Iterable[str]
        ] = None,
    ) -> AgentResponse:
        """
        Execute a pre-built AgentRequest.
        """

        if not isinstance(
            request,
            AgentRequest
        ):

            raise TypeError(
                "request must be an AgentRequest."
            )

        selected_plan = (
            plan
            or request.metadata.get(
                "saas_plan"
            )
            or self.config.default_plan
        )

        plan_tools = (
            self.resolve_plan_tools(
                selected_plan
            )
        )

        organization_tools = (
            self._normalize_tool_set(
                organization_allowed_tools
            )
        )

        effective_tools = set(
            plan_tools
        )

        if organization_tools is not None:

            effective_tools &= (
                organization_tools
            )

        return self.agent.run(
            request,

            plan_allowed_tools=(
                effective_tools
            ),

            organization_allowed_tools=(
                organization_tools
            ),
        )

    # ========================================================
    # SaaS Capability Resolution
    # ========================================================

    def resolve_plan_tools(
        self,
        plan: str
    ) -> set[str]:

        normalized_plan = (
            plan
            or ""
        ).strip().lower()

        if normalized_plan not in (
            PLAN_TOOL_ACCESS
        ):

            raise ValueError(
                f"Unsupported SaaS plan: "
                f"{normalized_plan}"
            )

        allowed = set(
            PLAN_TOOL_ACCESS[
                normalized_plan
            ]
        )

        registered = set(
            self.tool_registry.names()
        )

        return (
            allowed
            & registered
        )

    def capabilities(
        self,
        *,
        plan: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return public product capability information.
        """

        selected_plan = (
            plan
            or self.config.default_plan
        )

        allowed_tools = (
            self.resolve_plan_tools(
                selected_plan
            )
        )

        agent_capabilities = (
            self.agent.capabilities()
        )

        tools = []

        for tool in (
            self.tool_registry.all()
        ):

            definition = (
                tool.definition.to_dict()
            )

            definition[
                "enabled"
            ] = (
                tool.name
                in allowed_tools
            )

            tools.append(
                definition
            )

        return {
            "product":
                self.config.product_name,

            "plan":
                selected_plan,

            "agent":
                agent_capabilities,

            "tools":
                tools,

            "enabled_tools":
                sorted(
                    allowed_tools
                ),

            "features": {
                "agentic_ai":
                    True,

                "generative_ai":
                    (
                        "rewrite"
                        in allowed_tools
                    ),

                "ats_intelligence":
                    (
                        "ats"
                        in allowed_tools
                    ),

                "job_matching":
                    (
                        "job_match"
                        in allowed_tools
                    ),

                "skill_gap_analysis":
                    (
                        "skill_gap"
                        in allowed_tools
                    ),

                "recommendations":
                    (
                        "recommendation"
                        in allowed_tools
                    ),

                "cover_letters":
                    (
                        "cover_letter"
                        in allowed_tools
                    ),
            },
        }

    # ========================================================
    # Health Check
    # ========================================================

    def health(
        self
    ) -> Dict[str, Any]:

        registered_tools = (
            self.tool_registry.names()
        )

        return {
            "status":
                "healthy",

            "service":
                "resume_agent",

            "product":
                self.config.product_name,

            "registered_tools":
                registered_tools,

            "tool_count":
                len(
                    registered_tools
                ),

            "memory":
                "enabled",

            "guardrails":
                {
                    "input":
                        self.config
                        .enable_input_guard,

                    "output":
                        self.config
                        .enable_output_guard,

                    "tool":
                        True,
                },
        }

    # ========================================================
    # Runtime Tool Registration
    # ========================================================

    def register_tool(
        self,
        tool,
        *,
        replace: bool = False,
    ) -> None:
        """
        Allows future plugins/enterprise tools to be added
        without modifying ResumeAgent.
        """

        with self._lock:

            self.tool_registry.register(
                tool,
                replace=replace,
            )

    def unregister_tool(
        self,
        tool_name: str,
    ) -> bool:

        with self._lock:

            return (
                self.tool_registry
                .unregister(
                    tool_name
                )
            )

    # ========================================================
    # Helpers
    # ========================================================

    @staticmethod
    def _normalize_tool_set(
        tools: Optional[
            Iterable[str]
        ],
    ) -> Optional[set[str]]:

        if tools is None:
            return None

        return {
            str(tool)
            .strip()
            .lower()

            for tool in tools

            if str(tool).strip()
        }

    @staticmethod
    def _validation_error(
        message: str,
    ) -> AgentResponse:

        return AgentResponse(
            success=False,

            content=(
                "The request could not "
                "be processed."
            ),

            confidence=0.0,

            errors=[
                message
            ],

            metadata={
                "stage":
                    "service_validation",

                "error_type":
                    "validation_error",
            },
        )

    @staticmethod
    def _service_error(
        *,
        request: AgentRequest,
        error: Exception,
    ) -> AgentResponse:

        return AgentResponse(
            request_id=(
                request.request_id
            ),

            success=False,

            content=(
                "The AI service encountered "
                "an unexpected error."
            ),

            confidence=0.0,

            errors=[
                (
                    f"{type(error).__name__}: "
                    f"{error}"
                )
            ],

            metadata={
                "stage":
                    "agent_service",

                "error_type":
                    "internal_error",
            },
        )


# ============================================================
# Application-Level Singleton
# ============================================================

_service_instance: Optional[
    AgentService
] = None

_service_lock = RLock()


def initialize_agent_service(
    *,
    generation_service=None,
    config: Optional[
        AgentServiceConfig
    ] = None,
    force: bool = False,
) -> AgentService:
    """
    Initialize the application-level agent service.

    Call this during Flask application startup.
    """

    global _service_instance

    with _service_lock:

        if (
            _service_instance is not None
            and not force
        ):
            return _service_instance

        _service_instance = (
            AgentService(
                generation_service=(
                    generation_service
                ),
                config=config,
            )
        )

        return _service_instance


def get_agent_service(
) -> AgentService:
    """
    Return the initialized AgentService.
    """

    if _service_instance is None:

        raise RuntimeError(
            "AgentService has not been initialized. "
            "Call initialize_agent_service() during "
            "application startup."
        )

    return _service_instance


def reset_agent_service(
) -> None:
    """
    Primarily useful for testing.
    """

    global _service_instance

    with _service_lock:
        _service_instance = None