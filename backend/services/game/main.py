from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.game_routes import router as game_router
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

app = FastAPI(
    title="Game Service",
    description="Handles mystery generation and game logic",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_router, prefix="/game", tags=["game"])

@app.get("/")
async def root():
    return {"message": "Game Service API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GAME_SERVICE_PORT", 8002))
    uvicorn.run(
        "backend.services.game.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )