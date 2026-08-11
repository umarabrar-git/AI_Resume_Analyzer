from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from services.resume_intelligence.agents.schemas import (
    AgentPlan,
    AgentRequest,
)

from .intent_classifier import (
    AgentIntent,
    IntentClassifier,
    IntentPrediction,
)

from .tool_selector import (
    ToolSelection,
    ToolSelector,
)


TOOL_OBJECTIVES = {
    "resume":
        "Inspect structured candidate resume information.",

    "ats":
        "Evaluate resume quality and ATS compatibility.",

    "job_match":
        "Compare resume evidence against the target job.",

    "skill_gap":
        "Identify required and preferred skill gaps.",

    "recommendation":
        "Produce prioritized evidence-based resume improvements.",

    "rewrite":
        "Generate an improved resume grounded in existing candidate evidence.",

    "cover_letter":
        "Generate a cover letter grounded in the candidate resume and target role.",
}


class TaskPlanner:
    """
    Converts an AgentRequest into an executable AgentPlan.

    The planner creates dependency-aware steps rather than
    directly executing tools.
    """

    def __init__(
        self,
        *,
        intent_classifier: Optional[
            IntentClassifier
        ] = None,
        tool_selector: Optional[
            ToolSelector
        ] = None,
    ) -> None:

        self.intent_classifier = (
            intent_classifier
            or IntentClassifier()
        )

        self.tool_selector = (
            tool_selector
            or ToolSelector()
        )

    def create_plan(
        self,
        request: AgentRequest,
        *,
        available_tools: Iterable[str],
        plan_allowed_tools: Optional[
            Iterable[str]
        ] = None,
    ) -> AgentPlan:

        prediction = (
            self.intent_classifier.classify(
                request
            )
        )

        intent = self._resolve_intent(
            request,
            prediction
        )

        selection = (
            self.tool_selector.select(
                intent,
                available_tools=available_tools,
                plan_allowed_tools=(
                    plan_allowed_tools
                ),
                has_resume=bool(
                    request.resume_text
                ),
                has_job=bool(
                    request.job_description
                ),
            )
        )

        plan = AgentPlan(
            intent=intent.value,
            goal=request.message,
            metadata={
                "intent_prediction":
                    prediction.to_dict(),

                "tool_selection":
                    selection.to_dict(),

                "planner_version":
                    "1.0.0",
            },
        )

        step_ids: Dict[
            str,
            str
        ] = {}

        for tool_name in selection.tools:

            dependencies = (
                self._dependencies_for(
                    tool_name,
                    step_ids
                )
            )

            arguments = (
                self._arguments_for(
                    tool_name,
                    request
                )
            )

            step = plan.add_step(
                tool_name=tool_name,
                objective=(
                    TOOL_OBJECTIVES.get(
                        tool_name,
                        f"Execute {tool_name} capability."
                    )
                ),
                arguments=arguments,
                dependencies=dependencies,
                result_key=(
                    f"{tool_name}_result"
                ),
                required=self._is_required(
                    tool_name,
                    intent
                ),
                metadata={
                    "planner":
                        "task_planner_v1"
                },
            )

            step_ids[
                tool_name
            ] = step.step_id

        return plan

    @staticmethod
    def _resolve_intent(
        request: AgentRequest,
        prediction: IntentPrediction,
    ) -> AgentIntent:

        if (
            prediction.intent
            != AgentIntent.UNKNOWN
        ):
            return prediction.intent

        fallback = {
            "analyze":
                AgentIntent.RESUME_ANALYSIS,

            "optimize":
                AgentIntent.RESUME_OPTIMIZATION,

            "tailor":
                AgentIntent.JOB_TAILORING,

            "rewrite":
                AgentIntent.RESUME_REWRITE,

            "cover_letter":
                AgentIntent.COVER_LETTER,

            "career_assist":
                AgentIntent.CAREER_ASSISTANCE,
        }

        return fallback.get(
            request.mode,
            AgentIntent.RESUME_ANALYSIS,
        )

    @staticmethod
    def _dependencies_for(
        tool_name: str,
        step_ids: Dict[str, str],
    ) -> List[str]:

        dependency_tools = {
            "ats": [
                "resume",
            ],

            "job_match": [
                "resume",
            ],

            "skill_gap": [
                "resume",
                "job_match",
            ],

            "recommendation": [
                "ats",
            ],

            "rewrite": [
                "ats",
                "recommendation",
            ],

            "cover_letter": [
                "resume",
            ],
        }

        return [
            step_ids[name]
            for name
            in dependency_tools.get(
                tool_name,
                []
            )
            if name in step_ids
        ]

    @staticmethod
    def _arguments_for(
        tool_name: str,
        request: AgentRequest,
    ) -> Dict:

        if tool_name == "resume":

            return {
                "include_raw_text": False
            }

        if tool_name == "rewrite":

            return {
                "instructions":
                    request.message
            }

        if tool_name == "cover_letter":

            return {
                "instructions":
                    request.message,

                "target_role":
                    request.context.get(
                        "target_role"
                    ),
            }

        return {}

    @staticmethod
    def _is_required(
        tool_name: str,
        intent: AgentIntent,
    ) -> bool:

        critical = {
            AgentIntent.ATS_ANALYSIS: {
                "ats"
            },

            AgentIntent.JOB_MATCH: {
                "job_match"
            },

            AgentIntent.SKILL_GAP: {
                "skill_gap"
            },

            AgentIntent.RESUME_REWRITE: {
                "rewrite"
            },

            AgentIntent.RESUME_OPTIMIZATION: {
                "rewrite"
            },

            AgentIntent.JOB_TAILORING: {
                "rewrite"
            },

            AgentIntent.COVER_LETTER: {
                "cover_letter"
            },
        }

        return (
            tool_name
            in critical.get(
                intent,
                set()
            )
        )