#!/usr/bin/env python3
"""
Simple Flask app for Railway deployment
Handles health checks and serves the Streamlit dashboard
"""

import os
import subprocess
import threading
import time
import psycopg2
from datetime import datetime
from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

# Railway environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "customer_events")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "Rp123456")
PORT = int(os.getenv("PORT", "8501"))

# HTML template for the landing page
LANDING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>E-commerce Analytics System</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            background: rgba(255,255,255,0.1); 
            padding: 40px; 
            border-radius: 20px; 
            backdrop-filter: blur(10px);
            text-align: center;
            max-width: 600px;
        }
        .status { 
            color: #4ade80; 
            font-weight: bold; 
            font-size: 18px;
        }
        .time { 
            color: #e5e7eb; 
            font-size: 14px; 
            margin: 20px 0;
        }
        .btn {
            display: inline-block;
            background: #4ade80;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #22c55e;
            transform: translateY(-2px);
        }
        .features {
            margin: 30px 0;
            text-align: left;
        }
        .features h3 {
            color: #4ade80;
        }
        .features ul {
            list-style: none;
            padding: 0;
        }
        .features li {
            margin: 10px 0;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛍️ E-commerce Analytics System</h1>
        <p class="status">✅ Service is running and healthy!</p>
        <p class="time">Started at: {{ start_time }}</p>
        
        <div class="features">
            <h3>🚀 Features Available:</h3>
            <ul>
                <li>📊 Real-time Analytics Dashboard</li>
                <li>👥 Customer Behavior Analysis</li>
                <li>📈 Conversion Rate Tracking</li>
                <li>🛒 Abandoned Cart Analysis</li>
                <li>🎯 Product Performance Insights</li>
                <li>📅 Seasonal Trends Analysis</li>
            </ul>
        </div>
        
        <a href="/dashboard" class="btn">📊 Launch Dashboard</a>
        <a href="/health" class="btn">🔌 Health Status</a>
    </div>
</body>
</html>
"""

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
        from db.init_postgres import init_database
        from db.generate_customers import generate_customers
        
        init_database()
        generate_customers()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_background_services():
    """Start WebSocket server and event simulator"""
    print("🔌 Starting background services...")
    
    def start_websocket():
        try:
            from streaming.server import main
            import asyncio
            asyncio.run(main())
        except Exception as e:
            print(f"❌ WebSocket server error: {e}")
    
    def start_simulator():
        try:
            from streaming.event_simulator import main
            import asyncio
            asyncio.run(main())
        except Exception as e:
            print(f"❌ Event simulator error: {e}")
    
    # Start services in background threads
    threading.Thread(target=start_websocket, daemon=True).start()
    threading.Thread(target=start_simulator, daemon=True).start()
    print("✅ Background services started")

def start_streamlit():
    """Start Streamlit dashboard"""
    print("📊 Starting Streamlit dashboard...")
    
    cmd = [
        "streamlit", "run", "dashboard/app_live.py",
        "--server.port", "8502",
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

@app.route('/')
def health_check():
    """Health check endpoint for Railway"""
    return render_template_string(LANDING_PAGE, start_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/health')
def health_status():
    """Health status endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ecommerce-analytics",
        "version": "1.0.0"
    }

@app.route('/dashboard')
def dashboard():
    """Redirect to Streamlit dashboard"""
    return redirect("http://localhost:8502")

def main():
    """Main function"""
    print("🚀 Starting E-commerce Analytics System on Railway...")
    print(f"📅 Started at: {datetime.now()}")
    print(f"🌐 Port: {PORT}")
    print(f"🗄️ Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    # Initialize database
    if not wait_for_database():
        print("❌ Failed to connect to database. Exiting.")
        return
    
    if not initialize_database():
        print("❌ Failed to initialize database. Exiting.")
        return
    
    # Start background services
    start_background_services()
    
    # Start Streamlit in background
    threading.Thread(target=start_streamlit, daemon=True).start()
    
    print("🎉 All services started successfully!")
    print(f"📊 Dashboard will be available at: https://your-app.railway.app/dashboard")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == "__main__":
    main() 