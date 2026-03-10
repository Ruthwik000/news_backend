#!/usr/bin/env python3
"""
Start script for the Agricultural News Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import firebase_admin
        import google.generativeai
        import aiohttp
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("📦 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please create .env file with your configuration")
        return False
    
    env_content = env_file.read_text()
    
    # Check for placeholder values
    if "YOUR_PRIVATE_KEY_HERE" in env_content:
        print("⚠️  Firebase credentials not configured!")
        print("🔧 Run: python setup_firebase.py")
        return False
    
    if "your-gemini-api-key" in env_content:
        print("⚠️  Gemini API key not configured!")
        print("🔑 Please add your Gemini API key to .env file")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Agricultural News Backend...")
    print("📡 Server will be available at: http://localhost:8001")
    print("📖 API docs will be available at: http://localhost:8001/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the main app
        from main import app
        import uvicorn
        
        port = int(os.getenv("PORT", 8001))
        host = os.getenv("HOST", "0.0.0.0")
        debug = os.getenv("DEBUG", "True").lower() == "true"
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function"""
    print("🌾 Agricultural News Backend")
    print("=" * 30)
    print()
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check environment
    if not check_env_file():
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()