# app/services/vector_db.py

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.config import settings

class VectorDBService:
    def __init__(self):
        # Инициализация клиента Qdrant
        self.client = QdrantClient(
            url=f"http://{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}"
        )
        self.collection_name = settings.VECTOR_DB_COLLECTION_NAME
        self.vector_size = settings.EMBEDDING_DIM
        self._init_collection()

    def _init_collection(self):
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            print("✅ Collection ready")
        except Exception as e:
            print(f"Ошибка при создании коллекции: {e}")

    def insert_vectors(self, vectors: list):
        """Вставка списка векторов с payload"""
        self.client.upsert(
            collection_name=self.collection_name,
            points=vectors
        )

    def search_vectors(self, query_vector: list, top_k: int = 5, query_filter=None):
        """Поиск векторов с фильтром или без"""
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter
        )

# Экземпляр для импорта в других модулях
vector_db_service = VectorDBService()
