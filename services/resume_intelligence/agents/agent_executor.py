from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Dict, Iterable, List, Optional, Set

from services.resume_intelligence.agents.context import (
    AgentExecutionContext,
)

from services.resume_intelligence.agents.memory import (
    MemoryScope,
    MemoryService,
)

from services.resume_intelligence.agents.reasoning import (
    ResultSynthesizer,
)

from services.resume_intelligence.agents.schemas import (
    AgentPlan,
    AgentPlanStep,
    AgentRequest,
    AgentResponse,
    AgentState,
    AgentStatus,
    PlanStepStatus,
    ToolResult,
)

from services.resume_intelligence.agents.tools import (
    ToolExecutor,
)


@dataclass
class ExecutionConfig:
    """
    Runtime controls for one agent execution.
    """

    max_iterations: int = 20

    stop_on_required_failure: bool = True

    continue_on_optional_failure: bool = True

    store_tool_results_in_memory: bool = True

    store_plan_in_memory: bool = True

    persist_memory_after_run: bool = False

    conversation_limit: int = 12

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:

        self.max_iterations = max(
            1,
            int(self.max_iterations)
        )

        self.conversation_limit = max(
            1,
            int(self.conversation_limit)
        )


class AgentExecutionError(RuntimeError):
    """
    Raised when the execution engine cannot safely
    continue the current agent run.
    """


class AgentExecutor:
    """
    Dependency-aware execution engine for Resume Agent plans.

    Responsibilities:
    - manage AgentState
    - validate step dependencies
    - execute authorized tools
    - isolate tool failures
    - update working memory
    - enforce iteration limits
    - track step lifecycle
    - synthesize final AgentResponse
    """

    def __init__(
        self,
        *,
        tool_executor: ToolExecutor,
        memory_service: Optional[
            MemoryService
        ] = None,
        result_synthesizer: Optional[
            ResultSynthesizer
        ] = None,
        config: Optional[
            ExecutionConfig
        ] = None,
    ) -> None:

        if not isinstance(
            tool_executor,
            ToolExecutor
        ):
            raise TypeError(
                "tool_executor must be a ToolExecutor."
            )

        self.tool_executor = tool_executor

        self.memory_service = (
            memory_service
            or MemoryService()
        )

        self.result_synthesizer = (
            result_synthesizer
            or ResultSynthesizer()
        )

        self.config = (
            config
            or ExecutionConfig()
        )

    def execute(
        self,
        *,
        request: AgentRequest,
        plan: AgentPlan,
        execution_context: AgentExecutionContext,
        plan_allowed_tools: Optional[
            Iterable[str]
        ] = None,
        organization_allowed_tools: Optional[
            Iterable[str]
        ] = None,
        final_content: Optional[str] = None,
    ) -> AgentResponse:
        """
        Execute an AgentPlan and return a public AgentResponse.
        """

        self._validate_execution_input(
            request=request,
            plan=plan,
            execution_context=execution_context,
        )

        started_at = perf_counter()

        state = AgentState(
            request=request,
            status=AgentStatus.CREATED,
            intent=plan.intent,
            plan=plan,
            max_iterations=(
                self.config.max_iterations
            ),
            metadata={
                "executor":
                    "agent_executor_v1",

                "execution_config":
                    {
                        "max_iterations":
                            self.config.max_iterations,

                        "stop_on_required_failure":
                            self.config.stop_on_required_failure,

                        "continue_on_optional_failure":
                            self.config.continue_on_optional_failure,
                    },
            },
        )

        scope = self._build_memory_scope(
            state
        )

        context_dict = (
            execution_context.to_dict(
                include_raw_text=True
            )
        )

        self._initialize_memory(
            scope=scope,
            state=state,
            plan=plan,
            execution_context=execution_context,
        )

        try:

            state.set_status(
                AgentStatus.EXECUTING
            )

            self._execute_plan(
                state=state,
                scope=scope,
                context=context_dict,
                plan_allowed_tools=(
                    plan_allowed_tools
                ),
                organization_allowed_tools=(
                    organization_allowed_tools
                ),
            )

            state.set_status(
                AgentStatus.SYNTHESIZING
            )

            response = (
                self.result_synthesizer.synthesize(
                    run_id=state.run_id,
                    request=request,
                    plan=plan,
                    tool_results=(
                        state.tool_results
                    ),
                    final_content=final_content,
                )
            )

            state.complete(
                content=response.content,
                confidence=(
                    response.confidence
                ),
            )

            response.metadata[
                "execution"
            ] = {
                "run_id":
                    state.run_id,

                "status":
                    state.status.value,

                "iterations":
                    state.iteration,

                "duration_ms":
                    self._elapsed(
                        started_at
                    ),
            }

            self._finalize_memory(
                scope=scope,
                state=state,
                response=response,
            )

            return response

        except Exception as exc:

            state.fail(
                str(exc)
            )

            response = (
                self._build_failure_response(
                    state=state,
                    plan=plan,
                    started_at=started_at,
                )
            )

            self._finalize_memory(
                scope=scope,
                state=state,
                response=response,
            )

            return response

    def _execute_plan(
        self,
        *,
        state: AgentState,
        scope: MemoryScope,
        context: Dict[str, Any],
        plan_allowed_tools: Optional[
            Iterable[str]
        ],
        organization_allowed_tools: Optional[
            Iterable[str]
        ],
    ) -> None:

        if not state.plan:
            raise AgentExecutionError(
                "Agent plan is unavailable."
            )

        pending: Dict[
            str,
            AgentPlanStep
        ] = {
            step.step_id: step
            for step in state.plan.steps
        }

        while pending:

            state.increment_iteration()

            executable_steps = [
                step
                for step in pending.values()
                if self._dependencies_satisfied(
                    step=step,
                    plan=state.plan,
                )
            ]

            if not executable_steps:

                self._resolve_blocked_steps(
                    pending=pending,
                    plan=state.plan,
                    state=state,
                )

                break

            progress_made = False

            for step in executable_steps:

                if (
                    step.step_id
                    not in pending
                ):
                    continue

                if self._dependency_failed(
                    step=step,
                    plan=state.plan,
                ):

                    step.mark_skipped()

                    state.warnings.append(
                        f"Step '{step.tool_name}' "
                        "was skipped because a dependency failed."
                    )

                    pending.pop(
                        step.step_id,
                        None
                    )

                    progress_made = True

                    if (
                        step.required
                        and self.config.stop_on_required_failure
                    ):
                        raise AgentExecutionError(
                            f"Required step '{step.tool_name}' "
                            "could not run because a dependency failed."
                        )

                    continue

                result = self._execute_step(
                    step=step,
                    state=state,
                    context=context,
                    plan_allowed_tools=(
                        plan_allowed_tools
                    ),
                    organization_allowed_tools=(
                        organization_allowed_tools
                    ),
                )

                state.add_tool_result(
                    result
                )

                self._store_tool_result(
                    scope=scope,
                    step=step,
                    result=result,
                )

                self._inject_result_into_context(
                    context=context,
                    step=step,
                    result=result,
                )

                pending.pop(
                    step.step_id,
                    None
                )

                progress_made = True

                if not result.success:

                    if (
                        step.required
                        and self.config.stop_on_required_failure
                    ):
                        raise AgentExecutionError(
                            f"Required tool '{step.tool_name}' failed: "
                            f"{result.error_message or 'unknown error'}"
                        )

                    if (
                        not step.required
                        and not self.config.continue_on_optional_failure
                    ):
                        raise AgentExecutionError(
                            f"Optional tool '{step.tool_name}' failed "
                            "and execution policy prevents continuation."
                        )

            if not progress_made:

                raise AgentExecutionError(
                    "Agent execution made no progress. "
                    "The plan may contain invalid dependencies."
                )

    def _execute_step(
        self,
        *,
        step: AgentPlanStep,
        state: AgentState,
        context: Dict[str, Any],
        plan_allowed_tools: Optional[
            Iterable[str]
        ],
        organization_allowed_tools: Optional[
            Iterable[str]
        ],
    ) -> ToolResult:

        step.mark_running()

        result = self.tool_executor.execute(
            step.tool_name,
            arguments=step.arguments,
            context=context,
            mode=state.request.mode,
            plan_allowed_tools=(
                plan_allowed_tools
            ),
            organization_allowed_tools=(
                organization_allowed_tools
            ),
        )

        if result.success:
            step.mark_completed()
        else:
            step.mark_failed()

        return result

    @staticmethod
    def _dependencies_satisfied(
        *,
        step: AgentPlanStep,
        plan: AgentPlan,
    ) -> bool:

        if not step.dependencies:
            return True

        step_map = {
            item.step_id: item
            for item in plan.steps
        }

        for dependency_id in (
            step.dependencies
        ):

            dependency = step_map.get(
                dependency_id
            )

            if dependency is None:
                return False

            if dependency.status in {
                PlanStepStatus.PENDING,
                PlanStepStatus.RUNNING,
            }:
                return False

        return True

    @staticmethod
    def _dependency_failed(
        *,
        step: AgentPlanStep,
        plan: AgentPlan,
    ) -> bool:

        if not step.dependencies:
            return False

        step_map = {
            item.step_id: item
            for item in plan.steps
        }

        return any(
            (
                step_map.get(
                    dependency_id
                ) is None
                or step_map[
                    dependency_id
                ].status
                in {
                    PlanStepStatus.FAILED,
                    PlanStepStatus.SKIPPED,
                }
            )
            for dependency_id
            in step.dependencies
        )

    @staticmethod
    def _resolve_blocked_steps(
        *,
        pending: Dict[
            str,
            AgentPlanStep
        ],
        plan: AgentPlan,
        state: AgentState,
    ) -> None:

        step_map = {
            step.step_id: step
            for step in plan.steps
        }

        for step in list(
            pending.values()
        ):

            missing_dependencies = [
                dependency_id
                for dependency_id
                in step.dependencies
                if dependency_id
                not in step_map
            ]

            if missing_dependencies:

                step.mark_failed()

                state.errors.append(
                    f"Step '{step.tool_name}' references "
                    "missing dependencies."
                )

            else:

                step.mark_skipped()

                state.warnings.append(
                    f"Step '{step.tool_name}' could not "
                    "be scheduled."
                )

            pending.pop(
                step.step_id,
                None
            )

    def _initialize_memory(
        self,
        *,
        scope: MemoryScope,
        state: AgentState,
        plan: AgentPlan,
        execution_context: AgentExecutionContext,
    ) -> None:

        self.memory_service.add_user_message(
            scope,
            state.request.message,
            metadata={
                "request_id":
                    state.request.request_id,

                "run_id":
                    state.run_id,

                "mode":
                    state.request.mode,
            },
        )

        self.memory_service.remember(
            scope,
            "agent_intent",
            state.intent,
            namespace="execution",
        )

        self.memory_service.remember(
            scope,
            "execution_context",
            execution_context.to_dict(
                include_raw_text=False
            ),
            namespace="execution",
        )

        if self.config.store_plan_in_memory:

            self.memory_service.remember(
                scope,
                "agent_plan",
                plan.to_dict(),
                namespace="execution",
            )

    def _store_tool_result(
        self,
        *,
        scope: MemoryScope,
        step: AgentPlanStep,
        result: ToolResult,
    ) -> None:

        if (
            not self.config
            .store_tool_results_in_memory
        ):
            return

        key = (
            step.result_key
            or f"{step.tool_name}_result"
        )

        self.memory_service.remember(
            scope,
            key,
            result.to_dict(),
            namespace="tools",
            metadata={
                "tool_name":
                    step.tool_name,

                "step_id":
                    step.step_id,

                "success":
                    result.success,
            },
        )

    @staticmethod
    def _inject_result_into_context(
        *,
        context: Dict[str, Any],
        step: AgentPlanStep,
        result: ToolResult,
    ) -> None:
        """
        Make successful upstream results available to
        later dependent tools during the same run.
        """

        if not result.success:
            return

        tool_results = context.setdefault(
            "tool_results",
            {}
        )

        tool_results[
            step.tool_name
        ] = result.data

        resume = context.get(
            "resume"
        )

        if not isinstance(
            resume,
            dict
        ):
            return

        if step.tool_name == "ats":

            resume["ats"] = (
                result.data
                or {}
            )

        elif (
            step.tool_name
            == "recommendation"
        ):

            data = result.data

            if isinstance(
                data,
                dict
            ):

                resume[
                    "recommendations"
                ] = (
                    data.get(
                        "recommendations",
                        []
                    )
                    or []
                )

            elif isinstance(
                data,
                list
            ):

                resume[
                    "recommendations"
                ] = data

        elif step.tool_name == "job_match":

            context[
                "job_match_result"
            ] = result.data

        elif step.tool_name == "skill_gap":

            context[
                "skill_gap_result"
            ] = result.data

    def _finalize_memory(
        self,
        *,
        scope: MemoryScope,
        state: AgentState,
        response: AgentResponse,
    ) -> None:

        self.memory_service.remember(
            scope,
            "final_state",
            state.to_dict(),
            namespace="execution",
        )

        self.memory_service.remember(
            scope,
            "final_response",
            response.to_dict(),
            namespace="execution",
        )

        if response.content:

            self.memory_service.add_assistant_message(
                scope,
                response.content,
                metadata={
                    "run_id":
                        state.run_id,

                    "request_id":
                        state.request.request_id,

                    "success":
                        response.success,

                    "confidence":
                        response.confidence,
                },
            )

        if (
            self.config
            .persist_memory_after_run
        ):

            self.memory_service.persist(
                scope
            )

    def _build_failure_response(
        self,
        *,
        state: AgentState,
        plan: AgentPlan,
        started_at: float,
    ) -> AgentResponse:

        error_message = (
            state.errors[-1]
            if state.errors
            else "Agent execution failed."
        )

        return AgentResponse(
            run_id=state.run_id,
            request_id=(
                state.request.request_id
            ),
            success=False,
            content=(
                "The requested operation could not "
                "be completed safely."
            ),
            intent=plan.intent,
            confidence=0.0,
            actions_performed=[
                result.tool_name
                for result
                in state.tool_results
                if result.success
            ],
            warnings=list(
                dict.fromkeys(
                    state.warnings
                )
            ),
            errors=list(
                dict.fromkeys(
                    state.errors
                    or [error_message]
                )
            ),
            evidence=list(
                state.evidence
            ),
            metadata={
                "plan_id":
                    plan.plan_id,

                "execution": {
                    "run_id":
                        state.run_id,

                    "status":
                        state.status.value,

                    "iterations":
                        state.iteration,

                    "duration_ms":
                        self._elapsed(
                            started_at
                        ),
                },
            },
        )

    @staticmethod
    def _build_memory_scope(
        state: AgentState
    ) -> MemoryScope:

        request = state.request

        return MemoryScope(
            user_id=request.user_id,
            session_id=request.session_id,
            conversation_id=(
                request.conversation_id
            ),
            run_id=state.run_id,
        )

    @staticmethod
    def _validate_execution_input(
        *,
        request: AgentRequest,
        plan: AgentPlan,
        execution_context: AgentExecutionContext,
    ) -> None:

        if not isinstance(
            request,
            AgentRequest
        ):
            raise TypeError(
                "request must be an AgentRequest."
            )

        if not isinstance(
            plan,
            AgentPlan
        ):
            raise TypeError(
                "plan must be an AgentPlan."
            )

        if not isinstance(
            execution_context,
            AgentExecutionContext
        ):
            raise TypeError(
                "execution_context must be "
                "an AgentExecutionContext."
            )

        if (
            execution_context.request.request_id
            != request.request_id
        ):
            raise ValueError(
                "Execution context belongs to "
                "a different AgentRequest."
            )

    @staticmethod
    def _elapsed(
        started_at: float
    ) -> float:

        return round(
            (
                perf_counter()
                - started_at
            )
            * 1000,
            2,
        )