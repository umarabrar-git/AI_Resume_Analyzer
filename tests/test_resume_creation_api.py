import io
import secrets
import uuid

import pytest

from app import app
from database import db
from models.resume import Resume
from models.user import User
from routes.resume_creation import view as resume_creation_view
from services.resume_intelligence.generative.local_generation import (
    TASK_BULLETS,
    TASK_EXPERIENCE,
    local_generate,
)


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def _make_user(prefix: str) -> User:
    user = User(
        full_name=f"{prefix} User",
        email=f"{prefix}-{uuid.uuid4().hex[:8]}@example.com",
        subscription_plan="free",
        scans_left=5,
    )
    user.set_password("StrongPass123!")
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user


def _auth_session(client, user_id: int):
    csrf_token = secrets.token_urlsafe(24)
    with client.session_transaction() as session:
        session["user_id"] = user_id
        session["resume_csrf_token"] = csrf_token
    client.environ_base["HTTP_X_CSRF_TOKEN"] = csrf_token


def test_authenticated_user_can_create_resume(client):
    user = _make_user("create")
    _auth_session(client, user.id)

    response = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Backend Resume"},
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["resume"]["title"] == "Backend Resume"


def test_unauthenticated_user_cannot_create_resume(client):
    with client.session_transaction() as session:
        session.clear()

    response = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Blocked"},
    )

    assert response.status_code == 401


def test_user_cannot_edit_another_users_resume(client):
    owner = _make_user("owner")
    attacker = _make_user("attacker")

    with app.app_context():
        resume = Resume(user_id=owner.id, title="Owner Resume", template="classic")
        resume.set_content({
            "personal_information": {
                "full_name": "Owner",
                "professional_title": "Engineer",
                "email": "owner@example.com",
                "phone": "111",
                "location": "",
                "linkedin": "",
                "github": "",
                "portfolio": "",
            },
            "summary": "Owner summary",
            "experience": [],
            "education": [],
            "skills": ["Python"],
            "projects": [],
            "certifications": [],
            "languages": [],
            "custom_sections": [],
            "section_order": [
                "personal_information",
                "summary",
                "experience",
                "education",
                "skills",
                "projects",
                "certifications",
                "languages",
            ],
        })
        db.session.add(resume)
        db.session.commit()
        resume_id = resume.id

    _auth_session(client, attacker.id)

    response = client.patch(
        f"/resume-creation/api/resumes/{resume_id}",
        json={"title": "Hacked"},
    )

    assert response.status_code == 403
    payload = response.get_json()
    assert payload["success"] is False


def test_section_order_persists_on_save(client):
    user = _make_user("order")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Order Resume"},
    ).get_json()
    resume_id = created["resume"]["id"]

    reordered = [
        "summary",
        "personal_information",
        "skills",
        "experience",
        "education",
        "projects",
        "certifications",
        "languages",
    ]

    response = client.patch(
        f"/resume-creation/api/resumes/{resume_id}",
        json={
            "content": {
                "personal_information": {
                    "full_name": "User",
                    "professional_title": "Dev",
                    "email": "order@example.com",
                    "phone": "999",
                    "location": "",
                    "linkedin": "",
                    "github": "",
                    "portfolio": "",
                },
                "summary": "summary",
                "experience": [],
                "education": [],
                "skills": ["Python"],
                "projects": [],
                "certifications": [],
                "languages": [],
                "custom_sections": [],
                "section_order": reordered,
            }
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["resume"]["content"]["section_order"][:3] == reordered[:3]


def test_template_switch_preserves_content(client):
    user = _make_user("template")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={
            "creation_method": "scratch",
            "title": "Template Resume",
            "content": {
                "personal_information": {
                    "full_name": "Template User",
                    "professional_title": "Engineer",
                    "email": "template@example.com",
                    "phone": "123",
                    "location": "",
                    "linkedin": "",
                    "github": "",
                    "portfolio": "",
                },
                "summary": "Keep this summary",
                "experience": [],
                "education": [],
                "skills": ["Flask", "SQL"],
                "projects": [],
                "certifications": [],
                "languages": [],
                "custom_sections": [],
                "section_order": [
                    "personal_information",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                    "projects",
                    "certifications",
                    "languages",
                ],
            },
        },
    ).get_json()

    resume_id = created["resume"]["id"]

    response = client.patch(
        f"/resume-creation/api/resumes/{resume_id}",
        json={"template": "modern"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["resume"]["template"] == "modern"
    assert payload["resume"]["content"]["summary"] == "Keep this summary"
    assert payload["resume"]["content"]["skills"] == ["Flask", "SQL"]


def test_duplicate_resume_creates_new_owned_copy(client):
    user = _make_user("duplicate")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Original"},
    ).get_json()
    resume_id = created["resume"]["id"]

    response = client.post(f"/resume-creation/api/resumes/{resume_id}/duplicate")

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["resume"]["id"] != resume_id
    assert "Copy" in payload["resume"]["title"]


def test_invalid_template_rejected(client):
    user = _make_user("invalid-template")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Template Guard"},
    ).get_json()
    resume_id = created["resume"]["id"]

    response = client.patch(
        f"/resume-creation/api/resumes/{resume_id}",
        json={"template": "fancy-unknown-template"},
    )

    assert response.status_code == 422
    payload = response.get_json()
    assert payload["success"] is False


def test_premium_template_requires_persisted_subscription_plan(client):
    user = _make_user("premium-template")
    _auth_session(client, user.id)
    with client.session_transaction() as session:
        session["is_premium"] = True
        session["premium"] = True
        session["subscription_tier"] = "enterprise"

    denied = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "template": "executive"},
    )
    assert denied.status_code == 403
    assert denied.get_json()["code"] == "premium_required"
    catalog = client.get("/resume-creation/api/resumes").get_json()["templates"]
    executive_template = next(item for item in catalog if item["id"] == "executive")
    assert executive_template["available"] is False

    with app.app_context():
        persisted_user = db.session.get(User, user.id)
        persisted_user.subscription_plan = "pro"
        db.session.commit()

    allowed = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "template": "executive"},
    )
    assert allowed.status_code == 201
    assert allowed.get_json()["resume"]["template"] == "executive"

    with app.app_context():
        persisted_user = db.session.get(User, user.id)
        persisted_user.subscription_plan = "free"
        db.session.commit()

    blocked_export = client.get(
        f"/resume-creation/api/resumes/{allowed.get_json()['resume']['id']}/export/pdf"
    )
    assert blocked_export.status_code == 403


def test_resume_creation_page_renders_builder_workspace(client):
    user = _make_user("page")
    _auth_session(client, user.id)

    response = client.get("/resume-creation")

    assert response.status_code == 200
    assert b"data-resume-builder" in response.data
    assert b"builder-workspace" in response.data
    assert response.data.count(b'id="resumePicker"') == 1
    assert response.data.count(b'id="templateSection"') == 1
    assert b"createFromProfileBtn" in response.data
    assert b"importResumeBtn" in response.data


def test_profile_creation_prefills_saved_contact_details(client):
    user = _make_user("profile")
    _auth_session(client, user.id)

    response = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "profile"},
    )

    assert response.status_code == 201
    personal = response.get_json()["resume"]["content"]["personal_information"]
    assert personal["full_name"] == user.full_name
    assert personal["email"] == user.email


def test_resume_import_extracts_contact_skills_and_keeps_source_text(client, monkeypatch):
    user = _make_user("import")
    _auth_session(client, user.id)
    monkeypatch.setattr(
        resume_creation_view,
        "extract_resume_text",
        lambda _path, _extension: "Taylor Quinn\ntaylor@example.com\n+1 555 123 4567\nSummary\nData analyst with Python experience.\nExperience\nAnalyst at Civic Lab\n- Reviewed public datasets\nEducation\nBS Statistics, State University\nSkills\nPython, SQL, Flask",
    )

    response = client.post(
        "/resume-creation/api/resumes/import",
        data={"resume": (io.BytesIO(b"fake docx"), "Taylor-Quinn.docx")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    content = response.get_json()["resume"]["content"]
    assert content["personal_information"]["full_name"] == "Taylor Quinn"
    assert content["personal_information"]["email"] == "taylor@example.com"
    assert content["summary"] == "Data analyst with Python experience."
    assert "Python" in content["skills"]
    imported_titles = {section["title"] for section in content["custom_sections"]}
    assert {"Experience", "Education", "Original Imported Resume"}.issubset(imported_titles)
    source_section = next(section for section in content["custom_sections"] if section["title"] == "Original Imported Resume")
    assert "Taylor Quinn" in source_section["items"][0]["description"]


def test_ai_apply_rejects_unsupported_numeric_claims(client):
    user = _make_user("claim-guard")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={
            "creation_method": "scratch",
            "title": "Claim Guard Resume",
            "content": {"summary": "Software engineer with API development experience."},
        },
    ).get_json()
    resume_id = created["resume"]["id"]

    response = client.post(
        f"/resume-creation/api/resumes/{resume_id}/generate",
        json={
            "operation": "rewrite_summary",
            "apply": True,
            "apply_to": "summary",
            "source_type": "summary",
            "generated_content": "Improved service performance by 25%.",
        },
    )

    assert response.status_code == 422
    assert response.get_json()["code"] == "unsupported_claims"
    with app.app_context():
        saved_resume = db.session.get(Resume, resume_id)
        assert saved_resume.get_content()["summary"] == "Software engineer with API development experience."


def test_resume_agent_receives_owned_current_resume_and_job_description(client, monkeypatch):
    user = _make_user("resume-agent")
    _auth_session(client, user.id)
    created = client.post(
        "/resume-creation/api/resumes",
        json={
            "creation_method": "scratch",
            "title": "Current Data Resume",
            "content": {
                "personal_information": {"full_name": "Candidate"},
                "summary": "Current canonical summary for a data role.",
                "skills": ["Python", "SQL"],
            },
        },
    ).get_json()["resume"]

    class StubRegistry:
        @staticmethod
        def names():
            return ["resume", "ats", "job_match", "skill_gap", "recommendation"]

    class StubResponse:
        @staticmethod
        def to_dict():
            return {"success": True, "content": "Consider highlighting the existing SQL experience."}

    class StubAgentService:
        tool_registry = StubRegistry()

        def __init__(self):
            self.call = None

        def run(self, **kwargs):
            self.call = kwargs
            return StubResponse()

    agent = StubAgentService()
    monkeypatch.setattr(resume_creation_view, "get_agent_service", lambda: agent)

    response = client.post(
        f"/resume-creation/api/resumes/{created['id']}/assistant",
        json={
            "message": "How should I tailor this resume?",
            "job_description": "Data Scientist role requiring Python and SQL.",
        },
    )

    assert response.status_code == 200
    assert "Current canonical summary" in agent.call["resume_text"]
    assert agent.call["job_description"] == "Data Scientist role requiring Python and SQL."
    assert agent.call["context"]["active_resume"]["content"]["skills"] == ["Python", "SQL"]


def test_local_generation_does_not_invent_experience_actions_or_metrics():
    resume_data = {
        "skills": ["Python"],
        "profession_field": "Analyst",
        "sections_found": ["experience"],
        "text": "",
    }
    source = "Reviewed customer records and prepared weekly reports for operations."

    rewritten = local_generate(
        task=TASK_EXPERIENCE,
        resume_data=resume_data,
        source_text=source,
    )
    bullets = local_generate(
        task=TASK_BULLETS,
        resume_data=resume_data,
        source_text="Python",
    )

    assert "Reviewed" in rewritten
    assert "measurable improvements" not in rewritten
    assert not any(verb in rewritten for verb in ("Led", "Architected", "Engineered"))
    assert bullets == ""


def test_resume_content_schema_round_trips_order_objective_categories_and_achievements(client):
    user = _make_user("structured-content")
    _auth_session(client, user.id)
    content = {
        "personal_information": {"full_name": "Structured Candidate"},
        "summary": "Hidden summary text",
        "career_objective": "Build data products that improve access to public services.",
        "experience": [{"title": "Analyst", "company": "Civic Lab", "bullets": ["Reviewed datasets."], "achievements": ["Published a verified quarterly report."]}],
        "education": [{"degree": "BS", "institution": "State University", "coursework": "Statistics, Databases", "academic_achievements": "Dean's List"}],
        "skills": ["Python", "AWS"],
        "skills_by_category": {"Programming Languages": ["Python"], "Cloud": ["AWS"]},
        "projects": [{"name": "Open Data Portal", "description": "Built a public dashboard.", "achievements": ["Used by three city departments."]}],
        "section_order": ["personal_information", "career_objective", "experience", "education", "skills", "projects"],
        "hidden_sections": ["summary"],
    }

    response = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Structured Resume", "content": content},
    )

    assert response.status_code == 201
    saved = response.get_json()["resume"]["content"]
    assert saved["career_objective"] == content["career_objective"]
    assert saved["skills_by_category"] == content["skills_by_category"]
    assert saved["experience"][0]["achievements"] == content["experience"][0]["achievements"]
    assert saved["education"][0]["coursework"] == "Statistics, Databases"

    sections = resume_creation_view._content_to_sections(saved)
    keys = [section["key"] for section in sections]
    assert keys.index("career_objective") < keys.index("experience") < keys.index("education")
    assert "summary" not in keys
    assert "Hidden summary text" not in resume_creation_view._content_to_text(saved)


def test_resume_update_rejects_stale_updated_at_without_overwriting(client):
    user = _make_user("stale-update")
    _auth_session(client, user.id)
    created = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Version A"},
    ).get_json()["resume"]
    resume_id = created["id"]

    first_update = client.patch(
        f"/resume-creation/api/resumes/{resume_id}",
        json={"title": "Version B", "base_updated_at": created["updated_at"]},
    )
    assert first_update.status_code == 200

    stale_update = client.patch(
        f"/resume-creation/api/resumes/{resume_id}",
        json={"title": "Stale overwrite", "base_updated_at": created["updated_at"]},
    )
    assert stale_update.status_code == 409
    assert stale_update.get_json()["code"] == "stale_update"

    with app.app_context():
        saved_resume = db.session.get(Resume, resume_id)
        assert saved_resume.title == "Version B"


def test_resume_mutations_require_session_csrf_token(client):
    user = _make_user("csrf")
    with client.session_transaction() as session:
        session["user_id"] = user.id

    response = client.post(
        "/resume-creation/api/resumes",
        json={"creation_method": "scratch", "title": "Blocked without CSRF"},
    )

    assert response.status_code == 403
    assert response.get_json()["code"] == "csrf_failed"


def test_resume_analysis_returns_structured_intelligence(client):
    user = _make_user("intelligence")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={
            "creation_method": "scratch",
            "title": "Intelligence Resume",
            "content": {
                "personal_information": {
                    "full_name": "Intelligent User",
                    "professional_title": "Backend Engineer",
                    "email": "intel@example.com",
                    "phone": "5551234",
                    "location": "Remote",
                    "linkedin": "",
                    "github": "",
                    "portfolio": "",
                },
                "summary": "Backend engineer with Python and Flask experience.",
                "experience": [
                    {
                        "title": "Software Engineer",
                        "company": "Acme",
                        "location": "Remote",
                        "start_date": "2022",
                        "end_date": "2025",
                        "current": False,
                        "bullets": [
                            "Built APIs for internal tools.",
                            "Improved response times by 30 percent.",
                        ],
                    }
                ],
                "education": [],
                "skills": ["Python", "Flask", "SQL"],
                "projects": [],
                "certifications": [],
                "languages": [],
                "custom_sections": [],
                "section_order": [
                    "personal_information",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                    "projects",
                    "certifications",
                    "languages",
                ],
            },
        },
    ).get_json()

    resume_id = created["resume"]["id"]

    response = client.post(
        f"/resume-creation/api/resumes/{resume_id}/analyze",
        json={
            "job_description": "We need a backend engineer with Python, Flask, SQL, Docker, Kubernetes and CI/CD experience.",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "intelligence" in payload
    assert isinstance(payload.get("recommendations"), list)
    assert "readiness_score" in payload["intelligence"]
    assert "diagnostics" in payload["intelligence"]


def test_version_history_create_list_restore(client):
    user = _make_user("versions")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={
            "creation_method": "scratch",
            "title": "Versioned Resume",
            "content": {
                "personal_information": {
                    "full_name": "Version User",
                    "professional_title": "Engineer",
                    "email": "version@example.com",
                    "phone": "123",
                    "location": "",
                    "linkedin": "",
                    "github": "",
                    "portfolio": "",
                },
                "summary": "v1",
                "experience": [],
                "education": [],
                "skills": ["Python"],
                "projects": [],
                "certifications": [],
                "languages": [],
                "custom_sections": [],
                "section_order": [
                    "personal_information",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                    "projects",
                    "certifications",
                    "languages",
                ],
            },
        },
    ).get_json()

    resume_id = created["resume"]["id"]

    save_response = client.patch(
        f"/resume-creation/api/resumes/{resume_id}",
        json={
            "content": {
                "personal_information": {
                    "full_name": "Version User",
                    "professional_title": "Engineer",
                    "email": "version@example.com",
                    "phone": "123",
                    "location": "",
                    "linkedin": "",
                    "github": "",
                    "portfolio": "",
                },
                "summary": "v2",
                "experience": [],
                "education": [],
                "skills": ["Python"],
                "projects": [],
                "certifications": [],
                "languages": [],
                "custom_sections": [],
                "section_order": [
                    "personal_information",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                    "projects",
                    "certifications",
                    "languages",
                ],
            },
            "autosave": False,
        },
    )
    assert save_response.status_code == 200

    manual_version = client.post(
        f"/resume-creation/api/resumes/{resume_id}/versions",
        json={"note": "milestone"},
    )
    assert manual_version.status_code == 201

    listed = client.get(f"/resume-creation/api/resumes/{resume_id}/versions")
    assert listed.status_code == 200
    versions = listed.get_json()["versions"]
    assert len(versions) >= 1

    version_id = versions[0]["id"]
    restored = client.post(
        f"/resume-creation/api/resumes/{resume_id}/versions/{version_id}/restore"
    )
    assert restored.status_code == 200
    assert restored.get_json()["success"] is True


def test_resume_export_pdf_and_docx(client):
    user = _make_user("export")
    _auth_session(client, user.id)

    created = client.post(
        "/resume-creation/api/resumes",
        json={
            "creation_method": "scratch",
            "title": "Export Resume",
            "content": {
                "personal_information": {
                    "full_name": "Export User",
                    "professional_title": "Developer",
                    "email": "export@example.com",
                    "phone": "321",
                    "location": "",
                    "linkedin": "",
                    "github": "",
                    "portfolio": "",
                },
                "summary": "Export summary",
                "experience": [],
                "education": [],
                "skills": ["Flask"],
                "projects": [],
                "certifications": [],
                "languages": [],
                "custom_sections": [],
                "section_order": [
                    "personal_information",
                    "summary",
                    "experience",
                    "education",
                    "skills",
                    "projects",
                    "certifications",
                    "languages",
                ],
            },
        },
    ).get_json()

    resume_id = created["resume"]["id"]

    pdf_response = client.get(f"/resume-creation/api/resumes/{resume_id}/export/pdf")
    assert pdf_response.status_code == 200
    assert "application/pdf" in (pdf_response.content_type or "")
    assert len(pdf_response.data) > 100

    docx_response = client.get(f"/resume-creation/api/resumes/{resume_id}/export/docx")
    assert docx_response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in (docx_response.content_type or "")
    assert len(docx_response.data) > 100


def test_reports_export_pdf_and_docx(client):
    with client.session_transaction() as session:
        session["analysis_result"] = {}
        session["resume_text"] = "A resume for a software engineer."
        session["job_description"] = ""

    pdf_response = client.post(
        "/reports/export/pdf",
        json={"template": "modern"},
    )
    assert pdf_response.status_code == 200
    assert "application/pdf" in (pdf_response.content_type or "")
    assert pdf_response.data.startswith(b"%PDF")
    assert "modern.pdf" in pdf_response.headers["Content-Disposition"]

    docx_response = client.post(
        "/reports/export/docx",
        json={"template": "minimal"},
    )
    assert docx_response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in (docx_response.content_type or "")
    assert docx_response.data.startswith(b"PK")
    assert "minimal.docx" in docx_response.headers["Content-Disposition"]
