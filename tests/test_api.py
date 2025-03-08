import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_documents_empty():
    """Test listing documents when none exist"""
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_document_not_found():
    """Test getting a document that doesn't exist"""
    response = client.get("/documents/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_search_nonexistent_document():
    """Test searching a document that doesn't exist"""
    response = client.post(
        "/documents/nonexistent-id/search", 
        json={"query": "test query", "top_k": 5}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.skipif(
    not os.path.exists("test_files/sample.txt"), 
    reason="Test file not available"
)
def test_upload_document():
    """Test uploading a document"""
    with open("test_files/sample.txt", "rb") as f:
        response = client.post(
            "/documents",
            files={"file": ("sample.txt", f, "text/plain")}
        )
    
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["filename"] == "sample.txt"
    assert response.json()["status"] == "processing"