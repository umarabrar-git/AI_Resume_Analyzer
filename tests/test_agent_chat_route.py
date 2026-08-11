import pytest
from app import app
import routes.assistant.route as assistant_route


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_empty_prompt_rejected(client):
    with client.session_transaction() as session:
        session["user_id"] = "user-1"

    response = client.post(
        "/api/agent/chat",
        json={"message": "   "},
    )
    assert response.status_code == 400


def test_unauthenticated_access_rejected(client):
    with client.session_transaction() as session:
        session.clear()

    response = client.post(
        "/api/agent/chat",
        json={"message": "How can I improve this resume?"},
    )
    assert response.status_code in {302, 303}


def test_missing_resume_context_returns_helpful_response(client):
    with client.session_transaction() as session:
        session.clear()
        session["user_id"] = "user-1"

    response = client.post(
        "/api/agent/chat",
        json={"message": "How can I improve this resume?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is False
    assert "upload" in payload["content"].lower()


def test_context_payload_is_extracted_from_analysis_result(client, monkeypatch):
    with client.session_transaction() as session:
        session.clear()
        session["user_id"] = "user-1"
        session["resume_text"] = "resume content"
        session["job_description"] = "target role"
        session["analysis_result"] = {
            "analysis_result": {
                "ats": {"ats_score": 82},
                "job_match": {"matched_skills": ["python"], "missing_skills": ["aws"]},
                "recommendations": [{"title": "Add metrics"}],
            }
        }

    class StubService:
        def __init__(self):
            self.calls = []

        def run(self, **kwargs):
            self.calls.append(kwargs)
            return type(
                "Response",
                (),
                {"to_dict": lambda self: {"success": True, "content": "ok"}},
            )()

    stub_service = StubService()
    monkeypatch.setattr(assistant_route, "get_agent_service", lambda: stub_service)

    response = client.post(
        "/api/agent/chat",
        json={"message": "Improve my resume"},
    )

    assert response.status_code == 200
    assert stub_service.calls
    payload = stub_service.calls[0]
    assert payload["context"]["session_analysis"]["ats"]["ats_score"] == 82
    assert payload["context"]["resume_context"]["matched_skills"] == ["python"]
    assert payload["context"]["resume_context"]["missing_skills"] == ["aws"]
