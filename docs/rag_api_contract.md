# RAG API Contract (v1)

## Base URL

`/api/v1`

---

# 1. Upload Document

## POST /upload

Uploads a document and registers it for ingestion and indexing.

### Supported Types

* PDF
* DOCX
* TXT

### Request (multipart/form-data)

file: binary file
metadata: optional JSON

### Response

```json
{
  "upload_id": "uuid",
  "filename": "contract.pdf",
  "status": "uploaded"
}
```

---

# 2. Ask Question (Single-turn)

## POST /ask

Ask a question using RAG retrieval without chat memory.

### Request

```json
{
  "question": "What is the termination clause?",
  "top_k": 5
}
```

### Response

```json
{
  "answer": "The termination clause states...",
  "sources": [
    {
      "chunk_id": "c123",
      "text": "...",
      "score": 0.91
    }
  ]
}
```

---

# 3. Chat (Multi-turn)

## POST /chat

Conversational question answering with history.

### Request

```json
{
  "session_id": "uuid",
  "message": "Explain section 4"
}
```

### Response

```json
{
  "answer": "Section 4 explains...",
  "session_id": "uuid",
  "sources": []
}
```

---

# 4. Data Schemas

## DocumentChunk

```json
{
  "chunk_id": "uuid",
  "upload_id": "uuid",
  "text": "string",
  "tokens": 300
}
```

---

## EmbeddingVector

```json
{
  "chunk_id": "uuid",
  "vector": [0.123, 0.533],
  "dimension": 768
}
```

---

## RetrievalResult

```json
{
  "chunk_id": "uuid",
  "score": 0.88,
  "text": "chunk text"
}
```

---

# Definition of Done

* All endpoints defined
* JSON schemas documented
* Agreed by Backend + ML lead
* Covers upload, retrieval, chat, embeddings
