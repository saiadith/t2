import asyncio
import websockets
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("receiver")

EVENTS_FILE = "events.json"

async def receive_events():
    uri = "ws://localhost:8765"

    # Load existing events if the file exists
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            try:
                events = json.load(f)
            except json.JSONDecodeError:
                events = []
    else:
        events = []

    async with websockets.connect(uri, ping_interval=10, ping_timeout=10) as ws:
        logger.info("Receiver connected to WebSocket server.")
        try:
            async for message in ws:
                try:
                    event = json.loads(message)
                    logger.info(f"Received event {event.get('event_id', 'unknown')}")
                    events.append(event)

                    # Save all events back to the file
                    with open(EVENTS_FILE, "w") as f:
                        json.dump(events, f, indent=2)

                except json.JSONDecodeError:
                    logger.warning("Received invalid JSON data.")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed.")

if __name__ == "__main__":
    asyncio.run(receive_events())
