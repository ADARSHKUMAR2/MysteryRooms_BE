from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.services.game.routes import game_routes, session_routes
from backend.services.game.config.db import init_game_db
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
from backend.shared.exceptions import register_exception_handlers
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown logic.
    
    On startup:
    1. Connect to MongoDB
    2. Initialize Beanie with Mystery models
    """
    # Initialize MongoDB
    await init_game_db()
    
    print("✅ Game Service Ready")
    yield
    
    # Shutdown logic (cleanup connections, etc.)
    print("🛑 Game Service Shutting Down")

app = FastAPI(
    lifespan=lifespan,
    title="Mystery Rooms Game Service",
    description="Handles mystery generation and game logic"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app, "Game Service")
# Register routes
app.include_router(game_routes.router)
app.include_router(session_routes.router)

@app.get("/")
async def game_root():
    return {
        "status": "Game Service Running",
        "endpoints": [
            "POST /game/generate - Generate new mystery",
            "GET /game/mysteries - List mysteries",
            "GET /game/mysteries/{id} - Get specific mystery"
        ]
    }

@app.get("/health")
async def health_check():
    """Public endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Run the server on port 8002 with auto-reload enabled
    port = int(os.getenv("GAME_SERVICE_PORT", 8002))
    uvicorn.run("backend.services.game.main:app", host="0.0.0.0", port=port, reload=True)
