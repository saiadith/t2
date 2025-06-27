import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
import psycopg2
import requests
import websockets
import os

# DB connection config - use environment variables for Docker
DB_CONFIG = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "Rp123456"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "customer_events"),
}

WS_URL = os.getenv("WS_URL", "ws://localhost:8765")

def fetch_products():
    url = "https://fakestoreapi.com/products"
    resp = requests.get(url)
    resp.raise_for_status()
    products = resp.json()
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "price": p["price"],
            "description": p["description"],
            "image": p["image"],
        }
        for p in products
    ]

def load_customers():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT customer_id FROM customers;")
    custs = [str(row[0]) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return custs

class CartManager:
    def __init__(self, customers):
        self.carts = {cid: {} for cid in customers}
        self.cart_timestamps = {cid: None for cid in customers}
    def add_to_cart(self, cid, pid):
        cart = self.carts[cid]
        cart[pid] = cart.get(pid, 0) + 1
        self.cart_timestamps[cid] = datetime.now()
    def remove_from_cart(self, cid, pid):
        cart = self.carts[cid]
        if pid in cart:
            if cart[pid] > 1:
                cart[pid] -= 1
            else:
                del cart[pid]
        self.cart_timestamps[cid] = datetime.now()
    def purchase_cart(self, cid):
        cart = self.carts[cid]
        if cart:
            self.carts[cid] = {}
            self.cart_timestamps[cid] = None
            return True
        return False
    def cart_empty(self, cid):
        return len(self.carts[cid]) == 0
    def get_cart_products(self, cid):
        return list(self.carts[cid].keys())

ACTIONS = ["add_to_cart", "remove_from_cart", "purchase_cart"]

def make_description(action, product_title=None):
    if action == "add_to_cart":
        return f"Added {product_title} to cart."
    elif action == "remove_from_cart":
        return f"Removed {product_title} from cart."
    elif action == "purchase_cart":
        return "Purchased the cart."
    else:
        return ""

def generate_event(cid, cart_mgr, products):
    cart_empty = cart_mgr.cart_empty(cid)
    rand = random.random()
    if cart_empty:
        action = "add_to_cart"
        product = random.choice(products)
        cart_mgr.add_to_cart(cid, product["id"])
        desc = make_description(action, product["title"])
    else:
        if rand < 0.45:
            action = "add_to_cart"
            product = random.choice(products)
            cart_mgr.add_to_cart(cid, product["id"])
            desc = make_description(action, product["title"])
        elif rand < 0.70:
            cart_products = cart_mgr.get_cart_products(cid)
            if cart_products:
                action = "remove_from_cart"
                pid = random.choice(cart_products)
                cart_mgr.remove_from_cart(cid, pid)
                product = next(p for p in products if p["id"] == pid)
                desc = make_description(action, product["title"])
            else:
                action = "add_to_cart"
                product = random.choice(products)
                cart_mgr.add_to_cart(cid, product["id"])
                desc = make_description(action, product["title"])
        else:
            purchased = cart_mgr.purchase_cart(cid)
            if purchased:
                action = "purchase_cart"
                product = None
                desc = make_description(action)
            else:
                action = "add_to_cart"
                product = random.choice(products)
                cart_mgr.add_to_cart(cid, product["id"])
                desc = make_description(action, product["title"])
    event_data = {
        "event_id": str(uuid.uuid4()),
        "customer_id": cid,
        "action": action,
        "timestamp": None,
        "description": desc,
    }
    if product:
        event_data.update({
            "title": product["title"],
            "product_price": product["price"],
            "product_image": product["image"],
        })
    return event_data

async def send_events(ws, customers, products, cart_mgr, start_date, end_date):
    current_date = start_date
    while current_date < end_date:
        for _ in range(25):
            cid = random.choice(customers)
            event = generate_event(cid, cart_mgr, products)
            event_time = current_date + timedelta(seconds=random.randint(0, 86399))
            event["timestamp"] = event_time.isoformat()
            await ws.send(json.dumps(event))
        current_date += timedelta(days=1)
    print(f"Sent historical data from {start_date.date()} to {end_date.date()}")
    while True:
        day_events = []
        for _ in range(25):
            cid = random.choice(customers)
            event = generate_event(cid, cart_mgr, products)
            event_time = current_date + timedelta(seconds=random.randint(0, 86399))
            event["timestamp"] = event_time.isoformat()
            await ws.send(json.dumps(event))
            day_events.append(event)
        print(f"Sent {len(day_events)} events for {current_date.date()}")
        current_date += timedelta(days=1)
        await asyncio.sleep(1)

async def main():
    print(f"Starting event simulator...")
    print(f"Database config: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    print(f"WebSocket URL: {WS_URL}")
    products = fetch_products()
    customers = load_customers()
    cart_mgr = CartManager(customers)
    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=10, ping_timeout=5) as ws:
                print("Connected to WebSocket server")
                await send_events(ws, customers, products, cart_mgr, start_date, end_date)
        except Exception as e:
            print(f"Connection lost: {e}. Reconnecting in 3 seconds...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
