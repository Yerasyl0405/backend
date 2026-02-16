"""
Celery Tasks for Document Processing
"""
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.document import Document, DocumentStatus
from datetime import datetime
import logging

# Document processing libraries
import pdfplumber
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_document(self, upload_id: str):
    """
    Background task for processing uploaded documents
    
    Args:
        upload_id: UUID string of the uploaded document
    """
    db = SessionLocal()
    
    try:
        # 1. Fetch document from database
        document = db.query(Document).filter(
            Document.upload_id == upload_id
        ).first()
        
        if not document:
            logger.error(f"Document {upload_id} not found")
            return {"status": "error", "message": "Document not found"}
        
        logger.info(f"Processing document {upload_id}: {document.filename}")
        
        # 2. Update status to processing
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        # 3. Extract text from file
        text_content = extract_text(document.file_path, document.file_type)
        logger.info(f"Extracted {len(text_content)} characters from {document.filename}")
        
        # 4. Chunk the text
        chunks = chunk_text(text_content)
        document.chunk_count = len(chunks)
        logger.info(f"Created {len(chunks)} chunks")
        
        # 5. Generate embeddings (placeholder for now)
        # In a real implementation, you would:
        # - Call an embedding API (OpenAI, Cohere, etc.)
        # - Store embeddings in a vector database
        # embeddings = generate_embeddings(chunks)
        # store_in_vector_db(upload_id, chunks, embeddings)
        
        # 6. Update status to completed
        document.status = DocumentStatus.COMPLETED
        document.processed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Document {upload_id} processed successfully")
        
        return {
            "status": "success",
            "upload_id": upload_id,
            "chunk_count": document.chunk_count
        }
        
    except Exception as e:
        logger.error(f"Error processing document {upload_id}: {str(e)}", exc_info=True)
        
        # Update status to failed
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)
        
    finally:
        db.close()


def extract_text(file_path: str, file_type: str) -> str:
    """
    Extract text from different file formats
    
    Args:
        file_path: Path to the file
        file_type: MIME type of the file
        
    Returns:
        str: Extracted text content
    """
    try:
        if file_type == 'application/pdf':
            # Extract from PDF
            with pdfplumber.open(file_path) as pdf:
                text = '\n\n'.join(
                    page.extract_text() or '' 
                    for page in pdf.pages
                )
            return text
        
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # Extract from DOCX
            doc = DocxDocument(file_path)
            text = '\n\n'.join(
                paragraph.text 
                for paragraph in doc.paragraphs 
                if paragraph.text.strip()
            )
            return text
        
        elif file_type == 'text/plain':
            # Read plain text
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        raise


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Target size of each chunk in tokens (approximate)
        overlap: Number of tokens to overlap between chunks
        
    Returns:
        list: List of text chunks with metadata
    """
    # Simple word-based chunking
    # In production, use a proper tokenizer (tiktoken, sentencepiece, etc.)
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        
        chunks.append({
            'content': chunk_text,
            'chunk_index': len(chunks),
            'word_count': len(chunk_words),
            'start_word': i,
            'end_word': i + len(chunk_words)
        })
    
    return chunks
