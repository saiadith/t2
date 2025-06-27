#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
"""

import os
import sys
from datetime import datetime

def main():
    """Start the Flask app"""
    print("🚀 Starting E-commerce Analytics System...")
    print(f"📅 Started at: {datetime.now()}")
    
    # Get port from environment
    port = int(os.getenv("PORT", "8501"))
    print(f"🌐 Port: {port}")
    
    try:
        # Import and run the Flask app
        from simple_app import app
        
        print("✅ Flask app imported successfully")
        print("🔌 Starting Flask server...")
        
        # Start the Flask app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        print("📦 Checking if Flask is installed...")
        
        try:
            import flask
            print("✅ Flask is installed")
        except ImportError:
            print("❌ Flask is not installed")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 