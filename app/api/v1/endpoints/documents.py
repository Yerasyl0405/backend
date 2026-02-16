"""
Documents Management Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.storage import storage_service

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    status_filter: Optional[DocumentStatus] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents with optional filtering
    
    - **status**: Filter by processing status (pending, processing, completed, failed)
    - **limit**: Maximum number of results (1-100, default 20)
    - **offset**: Number of results to skip (for pagination)
    """
    query = db.query(Document)
    
    # Apply status filter
    if status_filter:
        query = query.filter(Document.status == status_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    documents = query.order_by(
        Document.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return DocumentListResponse(
        documents=[DocumentResponse.from_orm(doc) for doc in documents],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/documents/{upload_id}", response_model=DocumentResponse)
async def get_document(
    upload_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific document
    
    - **upload_id**: UUID of the uploaded document
    """
    document = db.query(Document).filter(
        Document.upload_id == upload_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "DOCUMENT_NOT_FOUND",
                "message": f"Document with ID {upload_id} not found"
            }
        )
    
    return DocumentResponse.from_orm(document)


@router.delete("/documents/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    upload_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a document and its associated files
    
    - **upload_id**: UUID of the document to delete
    """
    document = db.query(Document).filter(
        Document.upload_id == upload_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "DOCUMENT_NOT_FOUND",
                "message": f"Document with ID {upload_id} not found"
            }
        )
    
    # Delete file from storage
    storage_service.delete_file(document.file_path)
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return None
