from pydantic import BaseModel, Field
from beanie import Document
from typing import List, Optional, Dict, Any
from datetime import datetime

class MysteryStats(BaseModel):
    """Statistics for a specific mystery"""
    mystery_id: str
    times_played: int = 0
    times_completed: int = 0
    times_failed: int = 0
    average_completion_time_seconds: Optional[float] = None
    fastest_completion_time_seconds: Optional[int] = None
    average_hints_used: float = 0.0
    average_player_rating: Optional[float] = None

class PlayerStats(BaseModel):
    """Individual player statistics"""
    user_id: str = Field(..., description="Player's user ID")
    username: str = Field(..., description="Player's display name")
    
    # Overall stats
    total_games_played: int = 0
    total_games_won: int = 0
    total_games_lost: int = 0
    win_rate: float = 0.0
    
    # Puzzle stats
    total_puzzles_solved: int = 0
    total_puzzles_attempted: int = 0
    puzzle_success_rate: float = 0.0
    
    # Time stats
    total_playtime_seconds: int = 0
    average_game_duration_seconds: Optional[float] = None
    fastest_escape_time_seconds: Optional[int] = None
    
    # Hints and difficulty
    total_hints_used: int = 0
    average_hints_per_game: float = 0.0
    preferred_difficulty: Optional[int] = Field(None, description="Most played difficulty level")
    
    # Mystery history
    mysteries_played: List[str] = Field(default_factory=list, description="Mystery IDs played")
    favorite_room: Optional[str] = Field(None, description="Most played room type")
    
    # Metadata
    first_played: datetime = Field(default_factory=datetime.utcnow)
    last_played: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PlayerStatsDocument(Document, PlayerStats):
    """MongoDB document for player analytics"""
    
    class Settings:
        name = "player_stats"
        indexes = [
            "user_id",
            "win_rate",
            "total_games_played",
            "fastest_escape_time_seconds",
        ]

class LeaderboardEntry(BaseModel):
    """Entry for leaderboards"""
    user_id: str
    username: str
    value: float  # The metric value (time, win rate, etc.)
    rank: int

class GlobalStats(BaseModel):
    """Global game statistics"""
    total_mysteries_generated: int = 0
    total_games_played: int = 0
    total_games_completed: int = 0
    total_players: int = 0
    average_completion_rate: float = 0.0
    most_popular_room: Optional[str] = None
    most_popular_difficulty: Optional[int] = None
    mystery_stats: Dict[str, MysteryStats] = Field(default_factory=dict)
