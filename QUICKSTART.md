# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Extract and Navigate
```bash
unzip rag-document-ingestion.zip
cd rag-document-ingestion
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Start Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Wait a few seconds for services to start
sleep 5

# Verify services are running
docker-compose ps
```

### Step 5: Start Application

**Open 2 Terminal Windows:**

**Terminal 1 - FastAPI:**
```bash
cd rag-document-ingestion
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
cd rag-document-ingestion
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A app.tasks.celery_app worker --loglevel=info
```

### Step 6: Test It!

**Open a 3rd terminal:**
```bash
cd rag-document-ingestion
source venv/bin/activate

# Run health check
python scripts/health_check.py

# Run integration test
python scripts/test_workflow.py
```

## 🌐 Access Points

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Alternative Docs**: http://localhost:8000/redoc

## 📤 Test Upload

Create a test file:
```bash
echo "This is a test document for RAG system" > test.txt
```

Upload it:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@test.txt"
```

## ✅ Success Indicators

You should see:
- ✅ FastAPI server running on port 8000
- ✅ Celery worker ready and waiting
- ✅ PostgreSQL and Redis containers running
- ✅ Health check returns all green
- ✅ Test upload completes successfully

## ❌ Troubleshooting

**Problem**: Port already in use
```bash
# Change port
uvicorn app.main:app --reload --port 8001
```

**Problem**: Docker services won't start
```bash
# Check what's using the ports
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Or use different ports in docker-compose.yml
```

**Problem**: Module not found errors
```bash
# Make sure you're in the virtual environment
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: Database errors
```bash
# Recreate database
docker-compose down -v
docker-compose up -d
```

## 📚 Next Steps

1. Read the full README.md
2. Explore API docs at /docs
3. Try uploading different file types (PDF, DOCX)
4. Check the code in app/ directory
5. Run the test suite: `pytest tests/ -v`

## 🎯 What's Implemented

✅ Complete Task 1.2 Requirements:
- Document upload endpoint
- PDF, DOCX, TXT support
- File storage implementation
- Database metadata storage
- Async processing pipeline
- Error handling
- Comprehensive tests

Ready for integration with embedding generation and vector storage!
