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

class JoinSessionRequest(BaseModel):
    """Request for a player to join an active session"""
    player_id: str = Field(..., description="User ID of the joining player")

class ScoreBreakdown(BaseModel):
    """Detailed score calculation breakdown"""
    base_score: int = Field(..., description="Base score (usually 1000)")
    time_bonus: int = Field(default=0, description="Bonus for fast completion")
    difficulty_multiplier: float = Field(default=1.0, description="Multiplier based on difficulty")
    hint_penalty: int = Field(default=0, description="Penalty for using hints")
    team_bonus: int = Field(default=0, description="Bonus for multiplayer cooperation")
    final_score: int = Field(..., description="Total calculated score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "base_score": 1000,
                "time_bonus": 555,
                "difficulty_multiplier": 1.5,
                "hint_penalty": -100,
                "team_bonus": 200,
                "final_score": 2155
            }
        }

class RewardsData(BaseModel):
    """Rewards earned from completing the mystery"""
    coins_earned: int = Field(..., description="Coins awarded for completion")
    xp_earned: int = Field(..., description="Experience points earned")
    achievements: List[str] = Field(default_factory=list, description="Achievements unlocked")
    badges: List[str] = Field(default_factory=list, description="Badges earned")
    
    class Config:
        json_schema_extra = {
            "example": {
                "coins_earned": 50,
                "xp_earned": 150,
                "achievements": ["Speed Demon", "No Hints Master"],
                "badges": ["First Victory", "Mummy Tomb Expert"]
            }
        }

class PlayerPerformance(BaseModel):
    """Individual player's performance in the session"""
    user_id: str = Field(..., description="Player's user ID")
    username: str = Field(..., description="Player's display name")
    puzzles_solved: int = Field(..., description="Number of puzzles solved by this player")
    puzzles_attempted: int = Field(..., description="Number of puzzles attempted")
    hints_used: int = Field(..., description="Number of hints used")
    contribution_percentage: float = Field(..., description="Percentage contribution to team success")
    mvp: bool = Field(default=False, description="Is this player the MVP?")

class SessionStatistics(BaseModel):
    """Complete session statistics for the winning screen"""
    completion_time_seconds: int = Field(..., description="Total time taken")
    completion_time_formatted: str = Field(..., description="Formatted time (MM:SS)")
    time_limit_seconds: int = Field(..., description="Time limit for the mystery")
    time_remaining_seconds: int = Field(..., description="Time remaining when completed")
    puzzles_solved: int = Field(..., description="Number of puzzles solved")
    total_puzzles: int = Field(..., description="Total puzzles in mystery")
    hints_used: int = Field(..., description="Total hints used by all players")
    puzzle_attempts: int = Field(..., description="Total puzzle attempts")
    success_rate: float = Field(..., description="Puzzle success rate percentage")

class MysteryInfo(BaseModel):
    """Mystery information for context"""
    mystery_id: str = Field(..., description="Mystery UUID")
    theme: str = Field(..., description="Mystery theme")
    difficulty: int = Field(..., description="Difficulty level 1-5")
    room: str = Field(..., description="Room type")
    objective: str = Field(..., description="Mission objective")

class WinningScreenData(BaseModel):
    """
    Complete data package for the winning screen UI
    
    This model contains everything the Unity client needs to display
    a comprehensive victory screen with statistics, rewards, and rankings.
    """
    victory: bool = Field(default=True, description="Victory flag (always True for this endpoint)")
    victory_message: str = Field(..., description="Main congratulatory message")
    secondary_message: str = Field(..., description="Performance-based message")
    rank_title: str = Field(..., description="Rank achieved (Master Detective, etc.)")
    
    # Session and Mystery Info
    session_id: str = Field(..., description="Game session ID")
    mystery: MysteryInfo = Field(..., description="Mystery information")
    
    # Statistics
    statistics: SessionStatistics = Field(..., description="Complete session statistics")
    
    # Score and Rewards
    score: ScoreBreakdown = Field(..., description="Detailed score breakdown")
    rewards: RewardsData = Field(..., description="Rewards earned")
    
    # Player Performance (for multiplayer)
    players: List[PlayerPerformance] = Field(default_factory=list, description="Individual player performances")
    
    # Additional Context
    completed_at: datetime = Field(..., description="When the mystery was completed")
    is_new_record: bool = Field(default=False, description="Is this a new personal best?")
    previous_best_time: Optional[int] = Field(None, description="Previous best time for comparison")
    
    class Config:
        json_schema_extra = {
            "example": {
                "victory": True,
                "victory_message": "The ancient curse has been lifted! You've escaped the tomb! Excellent work!",
                "secondary_message": "Team victory! 3 minds solved the mystery together!",
                "rank_title": "Expert Investigator",
                "session_id": "abc-123-xyz",
                "mystery": {
                    "mystery_id": "mystery-456",
                    "theme": "ancient_curse",
                    "difficulty": 3,
                    "room": "mummy_tomb",
                    "objective": "Break the Pharaoh's curse and escape"
                },
                "statistics": {
                    "completion_time_seconds": 1245,
                    "completion_time_formatted": "20:45",
                    "time_limit_seconds": 1800,
                    "time_remaining_seconds": 555,
                    "puzzles_solved": 5,
                    "total_puzzles": 5,
                    "hints_used": 2,
                    "puzzle_attempts": 8,
                    "success_rate": 62.5
                },
                "score": {
                    "base_score": 1000,
                    "time_bonus": 555,
                    "difficulty_multiplier": 1.5,
                    "hint_penalty": -100,
                    "team_bonus": 200,
                    "final_score": 2155
                },
                "rewards": {
                    "coins_earned": 50,
                    "xp_earned": 150,
                    "achievements": ["Speed Demon"],
                    "badges": ["First Victory"]
                },
                "players": [
                    {
                        "user_id": "user1",
                        "username": "Player1",
                        "puzzles_solved": 3,
                        "puzzles_attempted": 5,
                        "hints_used": 1,
                        "contribution_percentage": 60.0,
                        "mvp": True
                    }
                ],
                "completed_at": "2026-09-11T06:47:08.881Z",
                "is_new_record": True,
                "previous_best_time": 1500
            }
        }

