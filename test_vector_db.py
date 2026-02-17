from app.services.vector_db import vector_db_service

# Пример векторов, размер EMBEDDING_DIM = 768
vectors = [
    {"id": 1, "vector": [0.1]*768, "payload": {"doc_id": 1, "category": "news"}},
    {"id": 2, "vector": [0.2]*768, "payload": {"doc_id": 2, "category": "blog"}},
    {"id": 3, "vector": [0.15]*768, "payload": {"doc_id": 3, "category": "news"}}
]

# Вставляем документы
vector_db_service.insert_vectors(vectors)
print("Документы вставлены ✅")

# Поиск без фильтра
query_vector = [0.1]*768
results = vector_db_service.search_vectors(query_vector, top_k=2)
print("Результаты поиска без фильтра:")
for r in results:
    print(r)

# Поиск с фильтром
filter_condition = {
    "must": [{"key": "category", "match": {"value": "news"}}]
}
filtered_results = vector_db_service.search_vectors(query_vector, top_k=2, filters=filter_condition)
print("Результаты поиска с фильтром category=news:")
for r in filtered_results:
    print(r)
