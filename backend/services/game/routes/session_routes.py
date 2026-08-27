from fastapi import APIRouter, HTTPException
from ..controllers.session_controller import SessionController
from ..models.game_session import (
    StartSessionRequest, UpdateSessionRequest, CompleteSessionRequest, GameSession
)

router = APIRouter(prefix="/game", tags=["Session"])
session_controller = SessionController()

@router.post("/sessions/start", response_model=GameSession)
async def start_game_session(request: StartSessionRequest):
    """Start a new game session"""
    return await session_controller.start_session(request)

@router.put("/sessions/update", response_model=GameSession)
async def update_game_session(request: UpdateSessionRequest):
    """Update session progress (puzzle solved, hint used, etc.)"""
    return await session_controller.update_session(request)

@router.post("/sessions/complete", response_model=GameSession)
async def complete_game_session(request: CompleteSessionRequest):
    """Complete/end a game session"""
    return await session_controller.complete_session(request)

@router.get("/sessions/{session_id}", response_model=GameSession)
async def get_game_session(session_id: str):
    """Get a specific game session"""
    return await session_controller.get_session(session_id)

@router.get("/players/{user_id}/sessions", response_model=list[GameSession])
async def get_player_sessions(user_id: str, limit: int = 20):
    """Get sessions for a specific player"""
    return await session_controller.get_player_sessions(user_id, limit)

@router.post("/sessions/{session_id}/join", response_model=GameSession)
async def join_game_session(session_id: str, request: dict):
    """Join an existing game session"""
    return await session_controller.join_session(session_id, request)
