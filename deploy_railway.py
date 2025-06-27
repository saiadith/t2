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
import sys
import http.server
import socketserver

# Railway environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "customer_events")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "Rp123456")
PORT = int(os.getenv("PORT", "8501"))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
            <html>
            <head><title>E-commerce Analytics System</title></head>
            <body>
                <h1>🛍️ E-commerce Analytics System</h1>
                <p>✅ Service is running and healthy!</p>
                <p>Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>📊 <a href="/dashboard">Go to Dashboard</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def start_health_server():
    """Start a simple health check server"""
    print(f"🏥 Starting health check server on port {PORT}")
    
    with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
        print(f"✅ Health check server running on port {PORT}")
        httpd.serve_forever()

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
    """Start Streamlit dashboard on a different port"""
    print("📊 Starting Streamlit dashboard...")
    
    streamlit_port = PORT + 1
    cmd = [
        "streamlit", "run", "dashboard/app_live.py",
        "--server.port", str(streamlit_port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
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
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    time.sleep(1)  # Give health server time to start
    
    # Step 1: Wait for database
    if not wait_for_database():
        print("❌ Failed to connect to database. Exiting.")
        sys.exit(1)
    
    # Step 2: Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database. Exiting.")
        sys.exit(1)
    
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