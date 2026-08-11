from services.resume_intelligence.nlp.role_detector import detect_role_candidates
from services.resume_intelligence.nlp.skill_extractor import extract_skill_candidates
from services.resume_intelligence.semantic.semantic_matcher import calculate_similarity, match_candidates


def _fallback_candidate_analysis(resume_candidates, job_candidates):
    resume_norm = {str(item).strip().casefold(): str(item).strip() for item in (resume_candidates or []) if str(item).strip()}
    job_norm = {str(item).strip().casefold(): str(item).strip() for item in (job_candidates or []) if str(item).strip()}

    if not job_norm:
        return {"matched": [], "missing": [], "match_percentage": 0.0}

    matched = []
    missing = []
    for key, original in job_norm.items():
        if key in resume_norm:
            matched.append({
                "job_candidate": original,
                "resume_candidate": resume_norm[key],
                "similarity": 100.0,
            })
        else:
            missing.append(original)

    match_percentage = round((len(matched) / len(job_norm)) * 100, 2)
    return {
        "matched": matched,
        "missing": missing,
        "match_percentage": match_percentage,
    }


def match_resume_to_job(resume_text, job_description):
    """Run semantic resume-to-job analysis."""

    resume_text = (resume_text or "").strip()
    job_description = (job_description or "").strip()

    if not resume_text:
        raise ValueError("Resume text is required.")

    if not job_description:
        raise ValueError("Job description is required.")

    resume_candidates = extract_skill_candidates(resume_text)
    job_candidates = extract_skill_candidates(job_description)
    analysis_mode = "semantic"
    analysis_warning = None

    try:
        candidate_analysis = match_candidates(resume_candidates, job_candidates)
        semantic_score = calculate_similarity(resume_text, job_description)
    except Exception:
        analysis_mode = "lexical_fallback"
        analysis_warning = "Semantic model unavailable; fallback matching used."
        candidate_analysis = _fallback_candidate_analysis(resume_candidates, job_candidates)

        resume_tokens = {str(item).strip().casefold() for item in resume_candidates if str(item).strip()}
        job_tokens = {str(item).strip().casefold() for item in job_candidates if str(item).strip()}
        if job_tokens:
            semantic_score = round((len(resume_tokens & job_tokens) / len(job_tokens)) * 100, 2)
        else:
            semantic_score = 0.0

    resume_roles = detect_role_candidates(resume_text)
    job_roles = detect_role_candidates(job_description)

    return {
        "analysis_mode": analysis_mode,
        "analysis_warning": analysis_warning,
        "semantic_score": semantic_score,
        "candidate_match_score": candidate_analysis["match_percentage"],
        "resume_candidates": resume_candidates,
        "job_candidates": job_candidates,
        "matched_candidates": candidate_analysis["matched"],
        "missing_candidates": candidate_analysis["missing"],
        "resume_roles": resume_roles,
        "job_roles": job_roles,
    }


class JobMatcher:
    """Resume-to-job matching helper."""

    def analyze_job_match(self, resume_text, job_description):
        """Run semantic resume-to-job analysis via the public helper."""
        return match_resume_to_job(
            resume_text=resume_text,
            job_description=job_description,
        )
