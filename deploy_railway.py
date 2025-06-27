#!/usr/bin/env python3
"""
Railway Deployment Script for E-commerce Analytics System
This script adapts the system for Railway hosting by combining services.
"""

import os
import subprocess
import time
import psycopg2
from datetime import datetime
import threading

# Railway environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "customer_events")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "Rp123456")
PORT = os.getenv("PORT", "8501")

def wait_for_database():
    """Wait for database to be ready"""
    print("🔄 Waiting for database to be ready...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            conn.close()
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Database not ready (attempt {attempt}/{max_attempts}): {e}")
            time.sleep(2)
    
    print("❌ Database connection failed after maximum attempts")
    return False

def initialize_database():
    """Initialize database schema and data"""
    print("🗄️ Initializing database...")
    
    try:
        # Import and run database initialization
        from db.init_postgres import init_database
        from db.generate_customers import generate_customers
        
        init_database()
        generate_customers()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_websocket_server():
    """Start WebSocket server in a separate thread"""
    print("🔌 Starting WebSocket server...")
    
    def run_server():
        try:
            from streaming.server import main
            import asyncio
            asyncio.run(main())
        except Exception as e:
            print(f"❌ WebSocket server error: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("✅ WebSocket server started in background")

def start_event_simulator():
    """Start event simulator in a separate thread"""
    print("🎲 Starting event simulator...")
    
    def run_simulator():
        try:
            from streaming.event_simulator import main
            import asyncio
            asyncio.run(main())
        except Exception as e:
            print(f"❌ Event simulator error: {e}")
    
    simulator_thread = threading.Thread(target=run_simulator, daemon=True)
    simulator_thread.start()
    print("✅ Event simulator started in background")

def start_streamlit():
    """Start Streamlit dashboard"""
    print("📊 Starting Streamlit dashboard...")
    
    cmd = [
        "streamlit", "run", "dashboard/app_live.py",
        "--server.port", PORT,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit error: {e}")
    except KeyboardInterrupt:
        print("🛑 Streamlit stopped by user")

def main():
    """Main deployment function"""
    print("🚀 Starting E-commerce Analytics System on Railway...")
    print(f"📅 Started at: {datetime.now()}")
    print(f"🌐 Port: {PORT}")
    print(f"🗄️ Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    # Step 1: Wait for database
    if not wait_for_database():
        print("❌ Failed to connect to database. Exiting.")
        return
    
    # Step 2: Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database. Exiting.")
        return
    
    # Step 3: Start background services
    start_websocket_server()
    time.sleep(2)  # Give WebSocket server time to start
    
    start_event_simulator()
    time.sleep(2)  # Give simulator time to start
    
    # Step 4: Start Streamlit dashboard
    print("🎉 All services started successfully!")
    print(f"📊 Dashboard will be available at: https://your-app.railway.app")
    start_streamlit()

if __name__ == "__main__":
    main() 