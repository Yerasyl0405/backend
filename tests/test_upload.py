"""
Tests for Upload Endpoint
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import UUID
import io

from app.main import app
from app.database import Base, get_db
from app.models.document import DocumentStatus

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_text_file():
    """Test uploading a text file"""
    # Create test file
    file_content = b"This is a test document for RAG system."
    files = {
        "file": ("test.txt", io.BytesIO(file_content), "text/plain")
    }
    
    response = client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 202
    data = response.json()
    assert "upload_id" in data
    assert UUID(data["upload_id"])  # Valid UUID
    assert data["status"] == "pending"
    assert data["filename"] == "test.txt"
    assert data["file_size"] == len(file_content)


def test_upload_unsupported_file_type():
    """Test uploading unsupported file type"""
    files = {
        "file": ("test.jpg", io.BytesIO(b"fake image"), "image/jpeg")
    }
    
    response = client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 415
    data = response.json()
    assert "UNSUPPORTED_FILE_TYPE" in str(data)


def test_upload_empty_file():
    """Test uploading empty file"""
    files = {
        "file": ("empty.txt", io.BytesIO(b""), "text/plain")
    }
    
    response = client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "EMPTY_FILE" in str(data)


def test_upload_large_file():
    """Test uploading file that exceeds size limit"""
    # Create 51MB file
    large_content = b"x" * (51 * 1024 * 1024)
    files = {
        "file": ("large.txt", io.BytesIO(large_content), "text/plain")
    }
    
    response = client.post("/api/v1/upload", files=files)
    
    assert response.status_code == 413
    data = response.json()
    assert "FILE_TOO_LARGE" in str(data)


def test_list_documents():
    """Test listing documents"""
    response = client.get("/api/v1/documents")
    
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data
    assert isinstance(data["documents"], list)


def test_get_document():
    """Test getting document details"""
    # First upload a document
    files = {
        "file": ("test.txt", io.BytesIO(b"test content"), "text/plain")
    }
    upload_response = client.post("/api/v1/upload", files=files)
    upload_id = upload_response.json()["upload_id"]
    
    # Get document details
    response = client.get(f"/api/v1/documents/{upload_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["upload_id"] == upload_id
    assert data["filename"] == "test.txt"


def test_get_nonexistent_document():
    """Test getting non-existent document"""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/documents/{fake_uuid}")
    
    assert response.status_code == 404
    data = response.json()
    assert "DOCUMENT_NOT_FOUND" in str(data)


def test_delete_document():
    """Test deleting a document"""
    # First upload a document
    files = {
        "file": ("test.txt", io.BytesIO(b"test content"), "text/plain")
    }
    upload_response = client.post("/api/v1/upload", files=files)
    upload_id = upload_response.json()["upload_id"]
    
    # Delete document
    response = client.delete(f"/api/v1/documents/{upload_id}")
    
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/v1/documents/{upload_id}")
    assert get_response.status_code == 404
