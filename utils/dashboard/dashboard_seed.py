from utils.parsing.parser import (
    calculate_profile_strength,
    estimate_page_count,
    estimate_reading_time,
    extract_resume_sections,
    infer_profession_field,
    resume_completion_status,
    run_format_style_checks,
)


def seed_dashboard_session(session_obj):
    """Populate session with sample values when no resume has been analyzed yet."""
    sample_text = "Sample resume text preview..."
    sample_sections = extract_resume_sections(sample_text)
    sample_name = "John Doe"
    sample_email = "john.doe@example.com"
    sample_phone = "+1 555 123 4567"
    sample_skills = ["Python", "Flask", "SQL", "Git", "Docker"]

    profile_strength, profile_checklist = calculate_profile_strength(
        sample_name,
        sample_email,
        sample_phone,
        sample_sections,
        sample_skills,
    )

    format_checks, format_score = run_format_style_checks(
        sample_text,
        sample_name,
        sample_email,
        sample_phone,
        820,
        sample_sections,
    )

    session_obj.update(
        dict(
            name=sample_name,
            email=sample_email,
            phone=sample_phone,
            skills=sample_skills,
            ats_score=88,
            word_count=820,
            matched_skills=["Python", "Flask", "SQL", "Git", "Docker"],
            missing_skills=["PHP"],
            match_percentage=83,
            text=sample_text,
            job_description="Sample job description preview...",
            sections_found=sample_sections,
            page_count=estimate_page_count(sample_text, 820),
            reading_time=estimate_reading_time(820),
            resume_status=resume_completion_status(sample_text, 820, sample_sections),
            profession_field=infer_profession_field(sample_text, ""),
            profile_strength=profile_strength,
            profile_checklist=profile_checklist,
            format_checks=format_checks,
            format_score=format_score,
        )
    )
