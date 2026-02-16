"""
Test Upload Script
Tests the complete upload workflow
"""
import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"


def test_upload_workflow():
    """Test complete upload and processing workflow"""
    
    print("🧪 Testing RAG Document Upload Workflow\n")
    
    # Step 1: Create a test file
    print("📝 Step 1: Creating test document...")
    test_file = Path("test_document.txt")
    test_content = "This is a test document for the RAG system. " * 100
    test_file.write_text(test_content)
    print(f"   ✅ Created: {test_file} ({len(test_content)} chars)")
    
    # Step 2: Upload the file
    print("\n📤 Step 2: Uploading file...")
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'text/plain')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code != 202:
        print(f"   ❌ Upload failed!")
        print(f"   Response: {response.text}")
        return False
    
    data = response.json()
    upload_id = data['upload_id']
    print(f"   ✅ Upload successful!")
    print(f"   Upload ID: {upload_id}")
    print(f"   Initial Status: {data['status']}")
    
    # Step 3: Monitor processing status
    print("\n⏳ Step 3: Monitoring processing status...")
    max_wait = 30  # Wait up to 30 seconds
    
    for i in range(max_wait):
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/documents/{upload_id}")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get document status")
            return False
        
        doc_data = response.json()
        status = doc_data['status']
        
        print(f"   [{i+1}s] Status: {status}", end='')
        
        if status == 'completed':
            print(f"\n   ✅ Processing completed!")
            print(f"\n📊 Final Document Details:")
            print(f"   - Filename: {doc_data['filename']}")
            print(f"   - File Size: {doc_data['file_size']} bytes")
            print(f"   - Chunks Created: {doc_data['chunk_count']}")
            print(f"   - Processed At: {doc_data['processed_at']}")
            return True
        
        elif status == 'failed':
            print(f"\n   ❌ Processing failed!")
            print(f"   Error: {doc_data.get('error_message', 'Unknown error')}")
            return False
        
        print("\r", end='')  # Clear line
    
    print(f"\n   ⚠️  Processing still pending after {max_wait} seconds")
    print("   This might indicate Celery worker is not running.")
    return False


def test_list_documents():
    """Test listing documents"""
    print("\n📋 Step 4: Listing all documents...")
    response = requests.get(f"{BASE_URL}/documents")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to list documents")
        return False
    
    data = response.json()
    print(f"   ✅ Found {data['total']} document(s)")
    
    for doc in data['documents'][:5]:  # Show first 5
        print(f"   - {doc['filename']} ({doc['status']})")
    
    return True


def test_error_cases():
    """Test error handling"""
    print("\n🧪 Step 5: Testing error cases...")
    
    # Test 1: Unsupported file type
    print("   Testing unsupported file type...")
    files = {'file': ('test.jpg', b'fake image', 'image/jpeg')}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    assert response.status_code == 415, "Should reject unsupported file type"
    print("   ✅ Correctly rejected unsupported file type")
    
    # Test 2: Empty file
    print("   Testing empty file...")
    files = {'file': ('empty.txt', b'', 'text/plain')}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    assert response.status_code == 400, "Should reject empty file"
    print("   ✅ Correctly rejected empty file")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("RAG DOCUMENT INGESTION - INTEGRATION TEST")
    print("=" * 60 + "\n")
    
    success = True
    success = test_upload_workflow() and success
    success = test_list_documents() and success
    success = test_error_cases() and success
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("=" * 60)
