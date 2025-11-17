import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import io

from src.services.spec_tracking import SPEC_FIELDS


def _fill_all_fields(service, conversation_id):
    state = {}
    for field in SPEC_FIELDS:
        state[field.field_id] = {"value": f"{field.field_id}-value", "confidence": 0.95}
    service.spec_state[conversation_id] = state

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def client():
    """Create an async test client for the app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

async def test_create_project(client: AsyncClient):
    """Test the dummy project creation endpoint."""
    response = await client.post("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert data["status"] == "created"

async def test_get_project(client: AsyncClient):
    """Test the dummy project fetching endpoint."""
    project_id = "test_project_123"
    response = await client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert "status" in data

async def test_upload_quote(client: AsyncClient, patch_conversation_service):
    """檔案上傳 API：確認接受 PDF 並回傳 metadata。"""
    project_id = "test_project_456"
    patch_conversation_service.created_projects.add(project_id)
    dummy_file_content = b"This is a test pdf content."

    response = await client.post(
        f"/api/projects/{project_id}/upload",
        files={"file": ("test_quote.pdf", dummy_file_content, "application/pdf")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["filename"] == "test_quote.pdf"
    assert data["metadata"]["content_type"] == "application/pdf"

async def test_book_measurement(client: AsyncClient, patch_conversation_service):
    """Test the booking endpoint (name + phone)."""
    project_id = "proj_book_test_789"
    patch_conversation_service.created_projects.add(project_id)

    response = await client.post(
        f"/api/projects/{project_id}/book",
        json={"name": "Test User", "phone": "0912345678"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["booking"]["name"] == "Test User"


async def test_complete_conversation_success(client: AsyncClient, patch_conversation_service):
    service = patch_conversation_service
    project_id = "proj-complete-1"
    conversation_id = "conv-success"
    service.created_projects.add(project_id)
    service.conversations[conversation_id] = {"conversation_id": conversation_id, "project_id": project_id}

    state = {}
    for field in SPEC_FIELDS:
        state[field.field_id] = {"value": f"{field.field_id}-value", "confidence": 0.95}
    service.spec_state[conversation_id] = state

    resp = await client.post(f"/api/projects/{project_id}/conversation/complete")
    assert resp.status_code == 200
    body = resp.json()
    assert body["briefing"]["project_id"] == project_id
    assert "summary" in body and body["summary"]


async def test_complete_conversation_missing_fields(client: AsyncClient, patch_conversation_service):
    service = patch_conversation_service
    project_id = "proj-complete-2"
    conversation_id = "conv-incomplete"
    service.created_projects.add(project_id)
    service.conversations[conversation_id] = {"conversation_id": conversation_id, "project_id": project_id}

    # Only fill part of the fields
    service.spec_state[conversation_id] = {
        "user_name": {"value": "Alice", "confidence": 0.9},
        "project_type": {"value": "全室裝修", "confidence": 0.9},
    }

    resp = await client.post(f"/api/projects/{project_id}/conversation/complete")
    assert resp.status_code == 400
    body = resp.json()
    assert "missing_fields" in body["detail"]


async def test_get_analysis_result_after_completion(client: AsyncClient, patch_conversation_service):
    service = patch_conversation_service
    project_id = "proj-analysis-1"
    conversation_id = "conv-analysis"
    service.created_projects.add(project_id)
    service.conversations[conversation_id] = {"conversation_id": conversation_id, "project_id": project_id}
    _fill_all_fields(service, conversation_id)

    # 完成對話以觸發後續 Agent 與 DB 寫入
    resp_complete = await client.post(f"/api/projects/{project_id}/conversation/complete")
    assert resp_complete.status_code == 200

    resp = await client.get(f"/api/projects/{project_id}/analysis-result")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == project_id
    assert data["quote"] is not None
    assert "summary" in data
