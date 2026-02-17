from typing import List
import uuid
from app.config import settings
import random

class Chunk:
    def __init__(self, text: str):
        self.id = str(uuid.uuid4())  # уникальный id для chunk
        self.text = text
        self.embedding = None  # будет список float

def split_document_into_chunks(file_path: str) -> List[Chunk]:
    """
    Разбиваем документ на строки/абзацы.
    Для TXT — по строкам. PDF/DOCX позже через парсер.
    """
    chunks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(Chunk(line))
    return chunks

def generate_embedding(text: str) -> list:
    """
    Генерация embedding для текста.
    Сейчас пример с random числами для теста.
    """
    return [random.random() for _ in range(settings.EMBEDDING_DIM)]
