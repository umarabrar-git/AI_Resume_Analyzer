from utils.parsing.parser import (
    calculate_ats_score,
    calculate_profile_strength,
    estimate_page_count,
    estimate_reading_time,
    extract_docx_text,
    extract_email,
    extract_name,
    extract_pdf_text,
    extract_phone,
    extract_resume_sections,
    extract_skills,
    infer_profession_field,
    match_job_description,
    resume_completion_status,
    run_format_style_checks,
)


def extract_resume_text(filepath, extension):
    """Extract resume text by file extension."""
    if extension == "pdf":
        return extract_pdf_text(filepath)
    if extension == "docx":
        return extract_docx_text(filepath)
    return ""


def analyze_resume(text, job_description):
    """Run full resume analysis and return a session-ready dictionary."""
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    word_count = len(text.split())
    ats_score = calculate_ats_score(name, email, phone, skills, word_count)
    matched_skills, missing_skills, match_percentage = match_job_description(skills, job_description)
    sections_found = extract_resume_sections(text)
    page_count = estimate_page_count(text, word_count)
    reading_time = estimate_reading_time(word_count)
    resume_status = resume_completion_status(text, word_count, sections_found)
    profession_field = infer_profession_field(text, job_description)
    profile_strength, profile_checklist = calculate_profile_strength(
        name, email, phone, sections_found, skills
    )
    format_checks, format_score = run_format_style_checks(
        text, name, email, phone, word_count, sections_found
    )

    return dict(
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        ats_score=ats_score,
        word_count=word_count,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        match_percentage=match_percentage,
        text=text,
        job_description=job_description,
        sections_found=sections_found,
        page_count=page_count,
        reading_time=reading_time,
        resume_status=resume_status,
        profession_field=profession_field,
        profile_strength=profile_strength,
        profile_checklist=profile_checklist,
        format_checks=format_checks,
        format_score=format_score,
    )
