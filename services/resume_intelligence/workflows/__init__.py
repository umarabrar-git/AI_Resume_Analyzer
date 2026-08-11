from .analysis_workflow import (
    AnalysisWorkflow,
    AnalysisWorkflowRequest,
)

from .optimization_workflow import (
    OptimizationWorkflow,
    OptimizationWorkflowRequest,
)

from .job_tailoring_workflow import (
    JobTailoringWorkflow,
    JobTailoringWorkflowRequest,
)

from .cover_letter_workflow import (
    CoverLetterWorkflow,
    CoverLetterWorkflowRequest,
)


__all__ = [
    "AnalysisWorkflow",
    "AnalysisWorkflowRequest",

    "OptimizationWorkflow",
    "OptimizationWorkflowRequest",

    "JobTailoringWorkflow",
    "JobTailoringWorkflowRequest",

    "CoverLetterWorkflow",
    "CoverLetterWorkflowRequest",
]