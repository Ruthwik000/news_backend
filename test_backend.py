#!/usr/bin/env python3
"""
Comprehensive test script for Agricultural News Backend
"""

import asyncio
import requests
import json
import time
import sys
from datetime import datetime

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*50}")
    print(f"🧪 {test_name}")
    print(f"{'='*50}")

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_imports():
    """Test all module imports"""
    print_test_header("Module Import Tests")
    
    try:
        # Test core dependencies
        import fastapi
        import uvicorn
        import firebase_admin
        import google.generativeai
        import aiohttp
        import schedule
        import requests
        import bs4  # beautifulsoup4 is imported as bs4
        print_result(True, "All core dependencies imported successfully")
        
        # Test custom modules
        from main import app
        from services.scraper_service import ScraperService
        from services.gemini_service import GeminiService
        from services.firestore_service import FirestoreService
        from services.scheduler_service import SchedulerService
        from models.news_models import NewsItem, NewsResponse, ScrapingStatus
        print_result(True, "All custom modules imported successfully")
        
        return True
        
    except ImportError as e:
        print_result(False, f"Import error: {e}")
        return False

def test_service_initialization():
    """Test service initialization"""
    print_test_header("Service Initialization Tests")
    
    try:
        from services.scraper_service import ScraperService
        from services.gemini_service import GeminiService
        from services.firestore_service import FirestoreService
        from services.scheduler_service import SchedulerService
        
        # Initialize services
        scraper = ScraperService()
        gemini = GeminiService()
        firestore = FirestoreService()
        scheduler = SchedulerService(scraper, gemini, firestore)
        
        print_result(True, "All services initialized successfully")
        return True
        
    except Exception as e:
        print_result(False, f"Service initialization error: {e}")
        return False

def test_api_endpoints(base_url="http://127.0.0.1:8001"):
    """Test API endpoints"""
    print_test_header("API Endpoint Tests")
    
    endpoints = [
        ("GET", "/", "Health check"),
        ("GET", "/health", "Detailed health check"),
        ("GET", "/news", "News retrieval"),
        ("GET", "/scraping-status", "Scraping status"),
        ("POST", "/scrape", "Manual scraping trigger")
    ]
    
    all_passed = True
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print_result(True, f"{description} - Status: {response.status_code}")
            else:
                print_result(False, f"{description} - Status: {response.status_code}")
                all_passed = False
                
        except requests.exceptions.RequestException as e:
            print_result(False, f"{description} - Connection error: {e}")
            all_passed = False
    
    return all_passed

def test_data_models():
    """Test data model validation"""
    print_test_header("Data Model Tests")
    
    try:
        from models.news_models import NewsItem, MultilingualText, NewsCategory
        
        # Test MultilingualText
        title = MultilingualText(
            en="Test Title",
            hi="परीक्षण शीर्षक",
            te="పరీక్ష శీర్షిక"
        )
        print_result(True, "MultilingualText model works")
        
        # Test NewsItem
        news_item = NewsItem(
            id="test_001",
            title=title,
            summary=title,  # Reusing for test
            category=NewsCategory.NEWS,
            source="Test Source",
            url="https://test.com",
            date="2024-03-10T10:00:00Z"
        )
        print_result(True, "NewsItem model works")
        
        return True
        
    except Exception as e:
        print_result(False, f"Data model error: {e}")
        return False

def test_environment_config():
    """Test environment configuration"""
    print_test_header("Environment Configuration Tests")
    
    import os
    from pathlib import Path
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print_result(True, ".env file exists")
        
        # Check for placeholder values
        env_content = env_file.read_text()
        if "YOUR_PRIVATE_KEY_HERE" in env_content:
            print_result(False, "Firebase credentials not configured")
            return False
        else:
            print_result(True, "Firebase credentials configured")
            
        if "your-gemini-api-key" in env_content:
            print_result(False, "Gemini API key not configured")
            return False
        else:
            print_result(True, "Gemini API key configured")
            
    else:
        print_result(False, ".env file not found")
        return False
    
    return True

def run_server_test():
    """Run server and test endpoints"""
    print_test_header("Server Integration Test")
    
    import subprocess
    import threading
    import time
    
    # Start server in background
    print("🚀 Starting test server...")
    
    try:
        # Import and test server startup
        from main import app
        import uvicorn
        
        # Start server in a thread
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test endpoints
        success = test_api_endpoints()
        
        print_result(success, "Server integration test completed")
        return success
        
    except Exception as e:
        print_result(False, f"Server test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🌾 Agricultural News Backend - Comprehensive Test Suite")
    print(f"📅 Test run: {datetime.now().isoformat()}")
    
    tests = [
        ("Import Tests", test_imports),
        ("Service Tests", test_service_initialization),
        ("Data Model Tests", test_data_models),
        ("Environment Tests", test_environment_config),
        ("Server Tests", run_server_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_result(False, f"{test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_test_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())