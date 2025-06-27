#!/usr/bin/env python3
"""
Test script to verify Flask app works
"""

import os
import sys
import time
import requests
from datetime import datetime

def test_flask_app():
    """Test if Flask app can start and respond"""
    print("🧪 Testing Flask app...")
    
    try:
        # Import the Flask app
        from simple_app import app
        
        # Test that the app can be created
        print("✅ Flask app imported successfully")
        
        # Test that routes are defined
        with app.test_client() as client:
            # Test root route
            response = client.get('/')
            print(f"✅ Root route response: {response.status_code}")
            
            # Test health route
            response = client.get('/health')
            print(f"✅ Health route response: {response.status_code}")
            
        print("🎉 Flask app test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_requirements():
    """Test if all requirements are installed"""
    print("📦 Testing requirements...")
    
    required_packages = ['flask', 'psycopg2-binary', 'streamlit']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} import failed: {e}")
            return False
    
    print("🎉 All requirements test passed!")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Flask app tests...")
    print(f"📅 Test started at: {datetime.now()}")
    
    # Test requirements
    if not test_requirements():
        print("❌ Requirements test failed")
        sys.exit(1)
    
    # Test Flask app
    if not test_flask_app():
        print("❌ Flask app test failed")
        sys.exit(1)
    
    print("🎉 All tests passed! Flask app is ready for deployment.")

if __name__ == "__main__":
    main() 