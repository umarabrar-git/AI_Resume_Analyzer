from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from services.resume_intelligence.agents.context import (
    ContextBuilder,
)

from services.resume_intelligence.agents.guardrails import (
    InputGuard,
    OutputGuard,
)

from services.resume_intelligence.agents.planning import (
    TaskPlanner,
)

from services.resume_intelligence.agents.schemas import (
    AgentRequest,
    AgentResponse,
)

from services.resume_intelligence.agents.tools import (
    ToolExecutor,
    ToolRegistry,
)

from services.resume_intelligence.agents.memory import (
    MemoryService,
)

from services.resume_intelligence.agents.reasoning import (
    ResultSynthesizer,
)

from services.resume_intelligence.agents.agent_executor import (
    AgentExecutor,
    ExecutionConfig,
)


@dataclass
class ResumeAgentConfig:
    """
    Runtime configuration for ResumeAgent.
    """

    max_iterations: int = 20

    stop_on_required_failure: bool = True

    continue_on_optional_failure: bool = True

    persist_memory: bool = False

    enable_input_guard: bool = True

    enable_output_guard: bool = True

    default_mode: str = "analyze"


class ResumeAgent:
    """
    Main Resume Intelligence autonomous agent.

    Responsibilities:
    - validate incoming requests
    - apply input safety controls
    - construct execution context
    - classify user intent
    - generate execution plans
    - execute tools
    - synthesize results
    - apply output safety controls

    This class does not contain ATS, matching, NLP,
    recommendation, or generation logic directly.
    Those capabilities are accessed through agent tools.
    """

    def __init__(
        self,
        *,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
        context_builder: Optional[
            ContextBuilder
        ] = None,
        task_planner: Optional[
            TaskPlanner
        ] = None,
        memory_service: Optional[
            MemoryService
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
        config: Optional[
            ResumeAgentConfig
        ] = None,
    ) -> None:

        if not isinstance(
            tool_registry,
            ToolRegistry
        ):
            raise TypeError(
                "tool_registry must be a ToolRegistry."
            )

        if not isinstance(
            tool_executor,
            ToolExecutor
        ):
            raise TypeError(
                "tool_executor must be a ToolExecutor."
            )

        self.tool_registry = tool_registry

        self.tool_executor = tool_executor

        self.context_builder = (
            context_builder
            or ContextBuilder()
        )

        self.task_planner = (
            task_planner
            or TaskPlanner()
        )

        self.memory_service = (
            memory_service
            or MemoryService()
        )

        self.result_synthesizer = (
            result_synthesizer
            or ResultSynthesizer()
        )

        self.input_guard = (
            input_guard
            or InputGuard()
        )

        self.output_guard = (
            output_guard
            or OutputGuard()
        )

        self.config = (
            config
            or ResumeAgentConfig()
        )

        self.executor = AgentExecutor(
            tool_executor=(
                self.tool_executor
            ),
            memory_service=(
                self.memory_service
            ),
            result_synthesizer=(
                self.result_synthesizer
            ),
            config=ExecutionConfig(
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
                persist_memory_after_run=(
                    self.config.persist_memory
                ),
            ),
        )

    def run(
        self,
        request: AgentRequest,
        *,
        plan_allowed_tools: Optional[
            Iterable[str]
        ] = None,
        organization_allowed_tools: Optional[
            Iterable[str]
        ] = None,
    ) -> AgentResponse:
        """
        Execute one complete Resume Agent request.
        """

        try:

            self._validate_request(
                request
            )

            # ---------------------------------
            # 1. INPUT GUARD
            # ---------------------------------

            if self.config.enable_input_guard:

                guard_result = (
                    self.input_guard.validate(
                        request
                    )
                )

                if not guard_result.allowed:

                    return self._blocked_response(
                        request=request,
                        reason=(
                            guard_result.reason
                            or "Request was rejected."
                        ),
                    )

            # ---------------------------------
            # 2. BUILD CONTEXT
            # ---------------------------------

            execution_context = (
                self.context_builder.build(
                    request
                )
            )

            # ---------------------------------
            # 3. DISCOVER AVAILABLE TOOLS
            # ---------------------------------

            available_tools = (
                self.tool_registry.names()
            )

            # ---------------------------------
            # 4. CREATE AGENT PLAN
            # ---------------------------------

            plan = (
                self.task_planner.create_plan(
                    request,
                    available_tools=(
                        available_tools
                    ),
                    plan_allowed_tools=(
                        plan_allowed_tools
                    ),
                )
            )

            if not plan.steps:

                return self._no_plan_response(
                    request=request,
                    intent=plan.intent,
                )

            # ---------------------------------
            # 5. EXECUTE PLAN
            # ---------------------------------

            response = (
                self.executor.execute(
                    request=request,
                    plan=plan,
                    execution_context=(
                        execution_context
                    ),
                    plan_allowed_tools=(
                        plan_allowed_tools
                    ),
                    organization_allowed_tools=(
                        organization_allowed_tools
                    ),
                )
            )

            # ---------------------------------
            # 6. OUTPUT GUARD
            # ---------------------------------

            if self.config.enable_output_guard:

                response = (
                    self._apply_output_guard(
                        response
                    )
                )

            return response

        except Exception as exc:

            return self._error_response(
                request=request,
                error=exc,
            )

    def capabilities(
        self
    ) -> Dict[str, Any]:
        """
        Public description of currently available
        agent capabilities.
        """

        tools = (
            self.tool_registry.all()
        )

        return {
            "agent":
                "resume_intelligence_agent",

            "version":
                "1.0.0",

            "default_mode":
                self.config.default_mode,

            "tools": [
                tool.definition.to_dict()
                for tool in tools
            ],

            "tool_names": [
                tool.name
                for tool in tools
            ],

            "features": {
                "planning": True,
                "tool_execution": True,
                "memory": True,
                "guardrails": True,
                "evidence_grounding": True,
                "confidence_estimation": True,
                "generative_ai": (
                    "rewrite"
                    in self.tool_registry.names()
                ),
                "cover_letter_generation": (
                    "cover_letter"
                    in self.tool_registry.names()
                ),
            },
        }

    def _apply_output_guard(
        self,
        response: AgentResponse,
    ) -> AgentResponse:

        guard_result = (
            self.output_guard.validate(
                response
            )
        )

        if guard_result.allowed:

            if (
                getattr(
                    guard_result,
                    "sanitized_content",
                    None
                )
            ):

                response.content = (
                    guard_result
                    .sanitized_content
                )

            return response

        response.success = False

        response.content = (
            "The generated response could not "
            "be returned because it failed "
            "output validation."
        )

        response.warnings.append(
            guard_result.reason
            or "Output validation failed."
        )

        return response

    @staticmethod
    def _validate_request(
        request: AgentRequest
    ) -> None:

        if not isinstance(
            request,
            AgentRequest
        ):
            raise TypeError(
                "request must be an AgentRequest."
            )

        if not request.message.strip():

            raise ValueError(
                "Agent request message "
                "cannot be empty."
            )

    @staticmethod
    def _blocked_response(
        *,
        request: AgentRequest,
        reason: str,
    ) -> AgentResponse:

        return AgentResponse(
            request_id=(
                request.request_id
            ),
            success=False,
            content=(
                "The request could not be processed."
            ),
            intent=None,
            confidence=0.0,
            warnings=[
                reason
            ],
            metadata={
                "blocked":
                    True,

                "stage":
                    "input_guard",
            },
        )

    @staticmethod
    def _no_plan_response(
        *,
        request: AgentRequest,
        intent: str,
    ) -> AgentResponse:

        return AgentResponse(
            request_id=(
                request.request_id
            ),
            success=False,
            content=(
                "No executable agent workflow "
                "could be created for this request."
            ),
            intent=intent,
            confidence=0.0,
            warnings=[
                "No compatible tools were available."
            ],
            metadata={
                "stage":
                    "planning"
            },
        )

    @staticmethod
    def _error_response(
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
                "The AI agent encountered an "
                "unexpected processing error."
            ),
            confidence=0.0,
            errors=[
                f"{type(error).__name__}: {error}"
            ],
            metadata={
                "stage":
                    "agent_orchestration"
            },
        )