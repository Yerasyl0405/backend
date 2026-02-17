# test_vector_db_full.py

from app.services.vector_db import vector_db_service
from qdrant_client.models import Filter, FieldCondition, MatchValue
import random
from datetime import datetime

# тестовый вектор (размер должен совпадать с settings.EMBEDDING_DIM)
test_vector = [random.random() for _ in range(1536)]  # пример для dim=1536

# вставка нескольких точек
vectors_to_insert = [
    {"id": 1, "vector": test_vector, "payload": {"doc_id": 1, "timestamp": datetime.now().isoformat()}},
    {"id": 2, "vector": test_vector, "payload": {"doc_id": 2, "timestamp": datetime.now().isoformat()}}
]

print("🔹 Starting Vector DB smoke test...")

vector_db_service.insert_vectors(vectors_to_insert)
print("✅ Vectors inserted successfully")

# поиск без фильтра
results_no_filter = vector_db_service.search_vectors(test_vector, top_k=3)
print("🔹 Search results without filter:", results_no_filter)

# поиск с фильтром
filter_query = Filter(
    must=[FieldCondition(key="doc_id", match=MatchValue(value=1))]
)

results_with_filter = vector_db_service.search_vectors(
    query_vector=test_vector,
    top_k=3,
    query_filter=filter_query
)
print("🔹 Search results with filter:", results_with_filter)
