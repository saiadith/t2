#!/usr/bin/env python3
"""
Health Check Server for Railway Deployment
This server responds to Railway's health checks while the main app starts.
"""

import os
import http.server
import socketserver
import threading
import time
import subprocess
import sys
from datetime import datetime

PORT = int(os.getenv("PORT", "8501"))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            html_content = f"""
            <html>
            <head>
                <title>E-commerce Analytics System</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .status {{ color: #28a745; font-weight: bold; }}
                    .time {{ color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛍️ E-commerce Analytics System</h1>
                    <p class="status">✅ Service is running and healthy!</p>
                    <p class="time">Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>📊 <a href="/dashboard">Go to Dashboard</a></p>
                    <p>🔌 <a href="/health">Health Status</a></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "ecommerce-analytics",
                "version": "1.0.0"
            }
            self.wfile.write(str(health_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def start_main_application():
    """Start the main Streamlit application"""
    print("📊 Starting main Streamlit application...")
    
    cmd = [
        "streamlit", "run", "dashboard/app_live.py",
        "--server.port", str(PORT + 1),  # Use different port for Streamlit
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
    """Main function to start health check server and main app"""
    print(f"🏥 Starting health check server on port {PORT}")
    print(f"📊 Main app will start on port {PORT + 1}")
    
    # Start main application in background thread
    app_thread = threading.Thread(target=start_main_application, daemon=True)
    app_thread.start()
    
    # Start health check server
    with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
        print(f"✅ Health check server running on port {PORT}")
        print(f"🌐 Health check available at: http://localhost:{PORT}")
        print(f"📊 Dashboard will be available at: http://localhost:{PORT + 1}")
        httpd.serve_forever()

if __name__ == "__main__":
    main() 