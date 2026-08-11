from services.resume_intelligence.nlp.skill_extractor import (
    extract_skill_candidates
)

from services.resume_intelligence.semantic.semantic_matcher import (
    match_candidates
)


def analyze_keywords(
    resume_text,
    job_description=None
):
    """
    Analyze resume skill/keyword evidence.

    Maximum: 25 points.

    If a job description exists, semantic candidate matching
    becomes the main relevance signal.
    """

    resume_candidates = (
        extract_skill_candidates(
            resume_text
        )
    )

    # -----------------------------------------
    # NO JOB DESCRIPTION
    # -----------------------------------------

    if not job_description:

        candidate_count = len(
            resume_candidates
        )

        if candidate_count >= 15:
            score = 20

        elif candidate_count >= 10:
            score = 17

        elif candidate_count >= 5:
            score = 13

        elif candidate_count >= 1:
            score = 8

        else:
            score = 0

        return {
            "score": score,
            "max_score": 25,
            "resume_candidates": resume_candidates,
            "job_candidates": [],
            "matched": [],
            "missing": [],
            "match_percentage": None,
            "job_description_used": False
        }

    # -----------------------------------------
    # WITH JOB DESCRIPTION
    # -----------------------------------------

    job_candidates = (
        extract_skill_candidates(
            job_description
        )
    )

    match_result = (
        match_candidates(
            resume_candidates,
            job_candidates
        )
    )

    percentage = (
        match_result[
            "match_percentage"
        ]
    )

    score = round(
        percentage / 100 * 25,
        2
    )

    return {
        "score": min(score, 25),
        "max_score": 25,

        "resume_candidates":
            resume_candidates,

        "job_candidates":
            job_candidates,

        "matched":
            match_result["matched"],

        "missing":
            match_result["missing"],

        "match_percentage":
            percentage,

        "job_description_used":
            True
    }