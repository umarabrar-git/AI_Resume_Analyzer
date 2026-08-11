import uuid

import pytest

from app import app
from database import db
from models.resume import Resume
from models.user import User


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
    with client.session_transaction() as session:
        session["user_id"] = user_id


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
    payload = response.get_json()
    assert payload["success"] is False


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


def test_resume_creation_page_renders_builder_workspace(client):
    user = _make_user("page")
    _auth_session(client, user.id)

    response = client.get("/resume-creation")

    assert response.status_code == 200
    assert b"data-resume-builder" in response.data


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
