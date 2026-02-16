"""
Health Check Script
Verifies all services are running
"""
import requests
import redis
from sqlalchemy import create_engine
from celery import Celery
import sys


def check_all_services():
    """Check if all required services are running"""
    results = {
        'fastapi': False,
        'redis': False,
        'postgres': False,
        'celery': False
    }
    
    print("🔍 Checking RAG Document Ingestion Service Health...\n")
    
    # Check FastAPI
    print("1. FastAPI Server:")
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        results['fastapi'] = response.status_code == 200
        print(f"   {'✅' if results['fastapi'] else '❌'} FastAPI: {'Running' if results['fastapi'] else 'Down'}")
    except Exception as e:
        print(f"   ❌ FastAPI: Down ({e})")
    
    # Check Redis
    print("\n2. Redis:")
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        results['redis'] = r.ping()
        print(f"   {'✅' if results['redis'] else '❌'} Redis: {'Running' if results['redis'] else 'Down'}")
    except Exception as e:
        print(f"   ❌ Redis: Down ({e})")
    
    # Check PostgreSQL
    print("\n3. PostgreSQL:")
    try:
        engine = create_engine('postgresql://user:password@localhost:5432/rag_db')
        conn = engine.connect()
        conn.close()
        results['postgres'] = True
        print("   ✅ PostgreSQL: Running")
    except Exception as e:
        print(f"   ❌ PostgreSQL: Down ({e})")
    
    # Check Celery
    print("\n4. Celery Worker:")
    try:
        celery_app = Celery('rag_tasks', broker='redis://localhost:6379/0')
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        results['celery'] = stats is not None and len(stats) > 0
        worker_count = len(stats) if stats else 0
        print(f"   {'✅' if results['celery'] else '❌'} Celery: {'Running' if results['celery'] else 'No workers'} ({worker_count} worker(s))")
    except Exception as e:
        print(f"   ❌ Celery: Down ({e})")
    
    # Overall status
    print("\n" + "=" * 60)
    all_running = all(results.values())
    if all_running:
        print("🎉 All services are running!")
        return 0
    else:
        print("⚠️  Some services are down. Check above for details.")
        print("\nTo start missing services:")
        if not results['postgres']:
            print("  - PostgreSQL: docker-compose up -d postgres")
        if not results['redis']:
            print("  - Redis: docker-compose up -d redis")
        if not results['celery']:
            print("  - Celery: celery -A app.tasks.celery_app worker --loglevel=info")
        if not results['fastapi']:
            print("  - FastAPI: uvicorn app.main:app --reload")
        return 1


if __name__ == "__main__":
    sys.exit(check_all_services())
