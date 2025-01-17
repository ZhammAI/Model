# backend/src/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import asyncio
import json
import logging
from datetime import datetime
from typing import Set

# Initialize FastAPI app
app = FastAPI(title="Zham AI Backend", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Connection closed. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                await self.disconnect(connection)

manager = ConnectionManager()

# Mock data generator (replace with actual data fetching)
async def generate_market_data():
    return {
        "trending": [
            {"name": "ai", "percentage": 91.9},
            {"name": "new", "percentage": 24.0},
            {"name": "squid", "percentage": 11.2},
            {"name": "agent", "percentage": 9.6},
            {"name": "game", "percentage": 8.7}
        ],
        "rising": [
            {"name": "mascot", "percentage": 8.1},
            {"name": "live", "percentage": 7.5},
            {"name": "sol", "percentage": 6.8},
            {"name": "year", "percentage": 5.9}
        ],
        "declining": [],
        "timestamp": datetime.now().isoformat()
    }

async def generate_sentiment_data():
    return {
        "value": 65,
        "classification": "Greed",
        "metrics": {
            "priceAction": 70,
            "volume": 65,
            "socialSentiment": 60,
            "metaMomentum": 68,
            "liquidityFlow": 62
        },
        "timestamp": datetime.now().isoformat()
    }

async def generate_runners_data():
    return {
        "current": [
            {
                "name": "SOLAI",
                "price": 0.00001234,
                "priceChange": 25.5,
                "volume": 150000,
                "matchedMeta": ["ai", "new"]
            }
        ],
        "potential": [
            {
                "name": "SQUID2",
                "price": 0.00000789,
                "priceChange": 15.2,
                "volume": 75000,
                "matchedMeta": ["squid", "game"]
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

# Background task for sending updates
async def periodic_update():
    while True:
        try:
            # Get market data
            meta_data = await generate_market_data()
            sentiment_data = await generate_sentiment_data()
            runners_data = await generate_runners_data()

            # Broadcast updates
            await manager.broadcast({
                "type": "meta_update",
                "payload": meta_data
            })
            await manager.broadcast({
                "type": "sentiment_update",
                "payload": sentiment_data
            })
            await manager.broadcast({
                "type": "runners_update",
                "payload": runners_data
            })

            # Wait before next update
            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error in periodic update: {e}")
            await asyncio.sleep(5)

# WebSocket endpoint
@app.websocket("/ws/meta")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial data
        meta_data = await generate_market_data()
        sentiment_data = await generate_sentiment_data()
        runners_data = await generate_runners_data()

        await websocket.send_json({
            "type": "meta_update",
            "payload": meta_data
        })
        await websocket.send_json({
            "type": "sentiment_update",
            "payload": sentiment_data
        })
        await websocket.send_json({
            "type": "runners_update",
            "payload": runners_data
        })

        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                if message.get("type") == "refresh_request":
                    # Handle refresh request
                    meta_data = await generate_market_data()
                    await websocket.send_json({
                        "type": "meta_update",
                        "payload": meta_data
                    })
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                break
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                break
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

# REST endpoints
@app.get("/api/meta/current")
async def get_current_meta():
    return await generate_market_data()

@app.get("/api/sentiment/current")
async def get_current_sentiment():
    return await generate_sentiment_data()

@app.get("/api/runners/current")
async def get_current_runners():
    return await generate_runners_data()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting background tasks...")
    asyncio.create_task(periodic_update())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)