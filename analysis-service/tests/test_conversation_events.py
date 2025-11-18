import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from src.main import app
from src.api import projects


class ConversationServiceStub:
    def __init__(self, *, project_exists=True, conversation_exists=True):
        self.project_exists_flag = project_exists
        self.conversation_exists_flag = conversation_exists
        self.logged_project_ids = []
        self.last_get_events_args = {}
        self.events_response = [
            {
                "id": "evt-1",
                "type": "user_message_received",
                "severity": "info",
                "source": "user",
                "description": "使用者發送訊息",
                "payload": {"length": 12},
                "timestamp": datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc),
            },
            {
                "id": "evt-2",
                "type": "agent_stream_error",
                "severity": "error",
                "source": "agent",
                "description": "Gemini timeout",
                "payload": {},
                "timestamp": datetime(2025, 1, 1, 8, 1, tzinfo=timezone.utc),
            },
        ]

    async def project_exists(self, project_id: str) -> bool:
        self.logged_project_ids.append(project_id)
        return self.project_exists_flag

    async def get_conversation(self, conversation_id: str):
        if not self.conversation_exists_flag:
            return None
        return {
            "conversation_id": conversation_id,
            "project_id": self.logged_project_ids[-1] if self.logged_project_ids else "proj-test",
        }

    async def get_events(self, conversation_id: str, *, limit: int, severity=None, since=None):
        self.last_get_events_args = {
            "conversation_id": conversation_id,
            "limit": limit,
            "severity": severity,
            "since": since,
        }
        return self.events_response


@pytest.fixture
def client():
    return TestClient(app)


def test_get_conversation_events_success(monkeypatch, client):
    service = ConversationServiceStub()
    monkeypatch.setattr(projects, "conversation_service", service)

    resp = client.get(
        "/api/projects/proj-123/conversation/conv-456/events",
        params={"limit": 10, "severity": "info", "since": "2025-01-01T08:00:00Z"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["conversationId"] == "conv-456"
    assert body["projectId"] == "proj-123"
    assert len(body["events"]) == 2
    assert body["events"][0]["timestamp"].endswith("+00:00")

    # 確認後端收到正確的查詢參數（limit 已被限制在 200 以內）
    assert service.last_get_events_args["conversation_id"] == "conv-456"
    assert service.last_get_events_args["limit"] == 10
    assert service.last_get_events_args["severity"] == "info"
    assert isinstance(service.last_get_events_args["since"], datetime)


def test_get_conversation_events_invalid_timestamp(monkeypatch, client):
    service = ConversationServiceStub()
    monkeypatch.setattr(projects, "conversation_service", service)

    resp = client.get(
        "/api/projects/proj-1/conversation/conv-1/events",
        params={"since": "not-a-timestamp"},
    )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid 'since' timestamp. Use ISO 8601 format."


def test_get_conversation_events_not_found(monkeypatch, client):
    service = ConversationServiceStub(conversation_exists=False)
    monkeypatch.setattr(projects, "conversation_service", service)

    resp = client.get("/api/projects/proj-1/conversation/conv-missing/events")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Conversation not found"
