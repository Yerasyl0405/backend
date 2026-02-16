"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload"""
    upload_id: UUID
    status: str
    message: str
    filename: str
    file_size: int
    estimated_processing_time: int = 30
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Response schema for document details"""
    upload_id: UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    chunk_count: int = 0
    doc_metadata: Dict[str, Any] = {}
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response schema for document listing"""
    documents: list[DocumentResponse]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
