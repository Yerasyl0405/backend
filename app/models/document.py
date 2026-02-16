
from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, JSON
from datetime import datetime
import uuid
import enum

from app.database import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Document model for storing uploaded files"""
    __tablename__ = "documents"
    
    upload_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Processing metadata
    chunk_count = Column(Integer, default=0)
    doc_metadata = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Document {self.filename} ({self.status})>"

