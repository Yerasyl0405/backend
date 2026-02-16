"""
File Storage Service
Handles file upload, storage, and retrieval
"""
import os
import aiofiles
from pathlib import Path
from uuid import UUID
from fastapi import UploadFile

from app.config import settings


class StorageService:
    """Service for managing file storage"""
    
    def __init__(self):
        self.base_dir = Path(settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, upload_id: UUID, file: UploadFile) -> str:
        """
        Save uploaded file to disk
        
        Args:
            upload_id: Unique identifier for the upload
            file: FastAPI UploadFile object
            
        Returns:
            str: Full file path where file was saved
        """
        # Create directory for this upload
        upload_dir = self.base_dir / str(upload_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        safe_filename = self._sanitize_filename(file.filename)
        file_path = upload_dir / safe_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return str(file_path)
    
    def get_file_path(self, upload_id: UUID, filename: str) -> str:
        """Get full path to a stored file"""
        return str(self.base_dir / str(upload_id) / filename)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                # Try to remove parent directory if empty
                try:
                    path.parent.rmdir()
                except OSError:
                    pass  # Directory not empty
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove any path components
        filename = os.path.basename(filename)
        # Remove potentially dangerous characters
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
        return filename or "unnamed_file"


# Global storage service instance
storage_service = StorageService()
