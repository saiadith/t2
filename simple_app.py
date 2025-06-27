#!/usr/bin/env python3
"""
Simple Flask app for Railway deployment
Responds immediately to health checks
"""

import os
from datetime import datetime
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Railway environment variables
PORT = int(os.getenv("PORT", "8501"))

# Simple HTML template
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🛍️ E-commerce Analytics System</h1>
        <p class="status">✅ Service is running and healthy!</p>
        <p class="time">Started at: {{ start_time }}</p>
        <p>🚀 Railway deployment successful!</p>
        <p>📊 Dashboard will be available soon...</p>
        <a href="/health" class="btn">🔌 Health Status</a>
    </div>
</body>
</html>
"""

@app.route('/')
def health_check():
    """Health check endpoint for Railway"""
    return render_template_string(LANDING_PAGE, start_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/health')
def health_status():
    """Health status endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ecommerce-analytics",
        "version": "1.0.0",
        "message": "Railway deployment successful!"
    })

if __name__ == "__main__":
    print(f"🚀 Starting simple Flask app on port {PORT}")
    print(f"📅 Started at: {datetime.now()}")
    app.run(host='0.0.0.0', port=PORT, debug=False) 