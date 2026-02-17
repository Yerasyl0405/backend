"""
Upload Endpoint
Handles document upload and ingestion
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.database import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentUploadResponse
from app.services.storage import storage_service
from app.config import settings
from app.services.embedding import split_document_into_chunks, generate_embedding
from app.services.vector_db import vector_db_service
import time
router = APIRouter()

# Allowed MIME types
ALLOWED_TYPES = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'text/plain': '.txt'
}

MAX_FILE_SIZE = settings.MAX_FILE_SIZE


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing
    
    - **file**: PDF, DOCX, or TXT file (max 50MB)
    
    Returns:
    - upload_id: Unique identifier for tracking
    - status: Initial status (pending)
    - message: Success message
    """
    
    # 1. Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "UNSUPPORTED_FILE_TYPE",
                "message": f"File type '{file.content_type}' not supported. Allowed types: PDF, DOCX, TXT",
                "allowed_types": list(ALLOWED_TYPES.keys())
            }
        )
    
    # 2. Validate file size
    # Read file to check size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)",
                "max_size_mb": MAX_FILE_SIZE / (1024 * 1024)
            }
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "EMPTY_FILE",
                "message": "Uploaded file is empty"
            }
        )
    
    # 3. Validate filename
    if not file.filename or len(file.filename) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_FILENAME",
                "message": "Filename must be between 1 and 255 characters"
            }
        )
    
    # 4. Generate unique upload_id
    upload_id = uuid4()
    
    try:
        # 5. Save file to storage
        file_path = await storage_service.save_file(upload_id, file)

        # Разбиваем документ на chunks
        chunks = split_document_into_chunks(file_path)

        # Генерируем embedding для каждого chunk
        for chunk in chunks:
            chunk.embedding = generate_embedding(chunk.text)

        # Подготавливаем и вставляем векторные данные в Vector DB
        vectors_to_insert = []
        for chunk in chunks:
            vectors_to_insert.append({
                "id": chunk.id,
                "vector": chunk.embedding,
                "payload": {
                    "doc_id": str(upload_id),
                    "text": chunk.text,
                    "timestamp": int(time.time())
                }
            })

        vector_db_service.insert_vectors(vectors_to_insert)

        # 6. Create database record
        document = Document(
            upload_id=upload_id,
            filename=file.filename,
            file_type=file.content_type,
            file_size=file_size,
            file_path=file_path,
            status=DocumentStatus.PENDING,
            created_at=datetime.utcnow(),
            doc_metadata={}
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 7. Trigger async processing via Celery
       # process_document.delay(str(upload_id))

        # 8. Return response
        return DocumentUploadResponse(
            upload_id=upload_id,
            status=document.status.value,
            message="Document uploaded successfully and queued for processing",
            filename=file.filename,
            file_size=file_size,
            estimated_processing_time=30
        )
        
    except Exception as e:
        # Cleanup on error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "UPLOAD_FAILED",
                "message": f"Failed to upload document: {str(e)}"
            }
        )
