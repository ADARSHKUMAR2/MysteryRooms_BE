from pydantic import BaseModel, Field
from beanie import Document
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class GameStatus(str, Enum):
    """Game session status"""
    WAITING = "waiting"  # Lobby, waiting for players
    IN_PROGRESS = "in_progress"  # Game is active
    COMPLETED = "completed"  # Successfully escaped
    FAILED = "failed"  # Time ran out or gave up
    ABANDONED = "abandoned"  # Players disconnected

class PlayerProgress(BaseModel):
    """Individual player's progress in a session"""
    user_id: str = Field(..., description="Player's user ID (from auth service)")
    username: str = Field(..., description="Player's display name")
    hints_used: int = Field(default=0, description="Number of hints used")
    puzzles_attempted: List[str] = Field(default_factory=list, description="Puzzle IDs attempted")
    puzzles_solved: List[str] = Field(default_factory=list, description="Puzzle IDs solved")
    objects_inspected: List[str] = Field(default_factory=list, description="Objects interacted with")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

class PuzzleAttempt(BaseModel):
    """Record of a puzzle attempt"""
    puzzle_id: str
    attempted_by: str  # user_id
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
    solved: bool = False
    time_spent_seconds: Optional[int] = None

class GameSession(BaseModel):
    """Live game session data"""
    session_id: str = Field(..., description="Unique session identifier")
    mystery_id: str = Field(..., description="Mystery being played")
    room: str = Field(..., description="Room type")
    status: GameStatus = Field(default=GameStatus.WAITING)
    
    # Player info
    players: List[PlayerProgress] = Field(default_factory=list, description="Players in this session")
    max_players: int = Field(default=4, ge=1, le=8)
    
    # Game progress
    puzzles_solved: List[str] = Field(default_factory=list, description="Globally solved puzzle IDs")
    puzzle_attempts: List[PuzzleAttempt] = Field(default_factory=list, description="All puzzle attempts")
    current_objective: Optional[str] = Field(None, description="Current objective text")
    
    # Timing
    started_at: Optional[datetime] = Field(None, description="When game actually started")
    completed_at: Optional[datetime] = Field(None, description="When game ended")
    time_limit_seconds: int = Field(default=1800)
    time_elapsed_seconds: int = Field(default=0, description="Time elapsed in seconds")
    
    # Analytics
    total_hints_used: int = Field(default=0)
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5, description="Player-rated difficulty")
    completion_time_seconds: Optional[int] = Field(None, description="Total time to complete")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GameSessionDocument(Document, GameSession):
    """MongoDB document for game sessions"""
    
    class Settings:
        name = "game_sessions"
        indexes = [
            "session_id",
            "mystery_id",
            "status",
            "created_at",
            [("players.user_id", 1)],  # Compound index for player queries
        ]

class StartSessionRequest(BaseModel):
    """Request to start a new game session"""
    mystery_id: str = Field(..., description="Mystery to play")
    player_ids: List[str] = Field(..., description="List of player user IDs")
    max_players: int = Field(default=4, ge=1, le=8)

class UpdateSessionRequest(BaseModel):
    """Request to update session progress"""
    session_id: str
    puzzle_solved: Optional[str] = Field(None, description="Puzzle ID that was just solved")
    puzzle_attempted: Optional[str] = Field(None, description="Puzzle ID that was attempted")
    hint_used: Optional[bool] = Field(None, description="Was a hint used?")
    player_id: Optional[str] = Field(None, description="Which player made the action")
    time_elapsed_seconds: Optional[int] = Field(None, description="Current elapsed time")

class CompleteSessionRequest(BaseModel):
    """Request to complete/end a session"""
    session_id: str
    status: GameStatus = Field(..., description="Final status (completed/failed/abandoned)")
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5, description="Player's difficulty rating")
