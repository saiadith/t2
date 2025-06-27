import asyncio
import json
import psycopg2
from datetime import datetime
import websockets
import os

# Database configuration - use environment variables for Docker
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "Rp123456"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "customer_events"),
}

# WebSocket server configuration
WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", "8765"))

# Store connected clients
clients = set()

async def handle_client(websocket, path):
    path = path[0] if isinstance(path, (list, tuple)) else path
    clients.add(websocket)
    print(f"Client connected. Total clients: {len(clients)}")
    try:
        async for message in websocket:
            event_data = json.loads(message)
            await store_event(event_data)
            await broadcast_event(event_data)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(clients)}")

# Wrapper function to handle the argument mismatch
async def handle_client_wrapper(websocket):
    await handle_client(websocket, None)

async def store_event(event_data):
    """Store event data in PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Insert event into database
        cur.execute("""
            INSERT INTO events (
                event_id, customer_id, product_id, product_title, 
                product_price, product_image, action, description, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            event_data.get('event_id'),
            event_data.get('customer_id'),
            event_data.get('product_id'),
            event_data.get('title'),
            event_data.get('product_price'),
            event_data.get('product_image'),
            event_data.get('action'),
            event_data.get('description'),
            event_data.get('timestamp')
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error storing event: {e}")

async def broadcast_event(event_data):
    """Broadcast event to all connected WebSocket clients"""
    if clients:
        message = json.dumps(event_data)
        await asyncio.gather(
            *[client.send(message) for client in clients],
            return_exceptions=True
        )

async def main():
    """Main WebSocket server function"""
    print(f"Starting WebSocket server on {WS_HOST}:{WS_PORT}")
    print(f"Database config: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    
    # Test database connection
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return
    
    # Start WebSocket server with wrapper function
    async with websockets.serve(handle_client_wrapper, WS_HOST, WS_PORT) as server:
        print(f"WebSocket server is running on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()  # Keep server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())
