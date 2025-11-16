import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import io

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

async def test_upload_quote(client: AsyncClient):
    """Test the file upload endpoint."""
    project_id = "test_project_456"
    # Create a dummy file in memory
    dummy_file_content = b"This is a test pdf content."
    dummy_file = io.BytesIO(dummy_file_content)
    
    response = await client.post(
        f"/api/projects/{project_id}/upload",
        files={"file": ("test_quote.pdf", dummy_file, "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert data["filename"] == "test_quote.pdf"
    assert "File uploaded successfully" in data["message"]

async def test_book_measurement(client: AsyncClient):
    """Test the booking endpoint."""
    booking_data = {
        "project_id": "proj_book_test_789",
        "name": "Test User",
        "contact": "test@example.com"
    }
    
    response = await client.post(
        "/api/projects/book",
        json=booking_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert f"Booking confirmed for project {booking_data['project_id']}" in data["message"]
