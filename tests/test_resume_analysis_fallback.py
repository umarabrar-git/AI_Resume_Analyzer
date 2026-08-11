from utils.dashboard.dashboard_context import extract_analysis_session_data


def test_extract_analysis_session_data_uses_fallback_payload_shape():
    payload = {
        "analysis_result": {
            "ats": {"ats_score": 72, "word_count": 250, "resume_status": "Complete resume"},
            "job_match": {"matched_skills": ["Python"], "missing_skills": ["Flask"], "match_percentage": 60},
            "resume": {"name": "Ada Lovelace", "email": "ada@example.com", "phone": "+1 555 1234", "skills": ["Python", "SQL"], "profession_field": "Software Engineering"},
            "raw": {"ats_score": 72, "match_percentage": 60},
        }
    }

    data = extract_analysis_session_data(payload, resume_text="Sample resume text", job_description="Python developer")

    assert data["ats_score"] == 72
    assert data["match_percentage"] == 60
    assert data["matched_skills"] == ["Python"]
    assert data["missing_skills"] == ["Flask"]
    assert data["resume_status"] == "Complete resume"
    assert data["name"] == "Ada Lovelace"
