from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from beanie import Document
from datetime import datetime
import string
import random

def generate_share_code() -> str:
    """Generate a 6-character alphanumeric code (e.g., 'X7B9QA')"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=6))

class PuzzleConfig(BaseModel):
    """Configuration for a single puzzle in the mystery"""
    id: str = Field(..., description="Unique puzzle identifier")
    type: str = Field(..., description="Type of puzzle (rotating_statue, symbol_sequence, etc.)")
    position: str = Field(..., description="Location in the room")
    config: Dict[str, Any] = Field(default_factory=dict, description="Puzzle-specific parameters")
    dependencies: List[str] = Field(default_factory=list, description="Puzzle IDs that must be solved first")
    unlocks: List[str] = Field(default_factory=list, description="What this puzzle unlocks (puzzle IDs or 'final_door')")
    hint: Optional[str] = Field(None, description="Optional hint text")

class ClueConfig(BaseModel):
    """Configuration for a clue in the mystery"""
    id: str = Field(..., description="Unique clue identifier")
    type: str = Field(..., description="Type of clue (inscription, visual, audio, environmental)")
    location: str = Field(..., description="Where the clue is located")
    content: str = Field(..., description="The clue content/text")
    related_puzzle: Optional[str] = Field(None, description="Which puzzle this clue helps with")
    requires_puzzle_solved: Optional[str] = Field(None, description="Only visible after this puzzle is solved")

class MysteryConfig(BaseModel):
    """Complete mystery configuration that Unity will consume"""
    mystery_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique mystery identifier")
    share_code: str = Field(default_factory=generate_share_code, description="6-character code to share this mystery")
    room: str = Field(..., description="Room type (mummy_tomb, etc.)")
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty level 1-5")
    theme: str = Field(..., description="Mystery theme (stolen_artifact, curse, etc.)")
    objective: str = Field(..., description="Player's main objective")
    time_limit_seconds: int = Field(default=1800, description="Time limit in seconds")
    puzzles: List[PuzzleConfig] = Field(..., description="List of puzzles in this mystery")
    clues: List[ClueConfig] = Field(default_factory=list, description="List of clues")
    twist: Optional[str] = Field(None, description="Plot twist or unexpected element")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "mystery_id": "abc-123",
                "room": "mummy_tomb",
                "difficulty": 3,
                "theme": "stolen_artifact",
                "objective": "Recover the Eye of Horus",
                "time_limit_seconds": 1800,
                "puzzles": [
                    {
                        "id": "entrance_statue",
                        "type": "rotating_statue",
                        "position": "entrance_hall",
                        "config": {"correctRotationSteps": 2},
                        "dependencies": [],
                        "unlocks": ["hieroglyph_wall"]
                    }
                ],
                "clues": [],
                "twist": None
            }
        }

class GenerateMysteryRequest(BaseModel):
    """Request model for mystery generation"""
    room: str = Field(default="mummy_tomb", description="Room type")
    difficulty: int = Field(default=3, ge=1, le=5, description="Difficulty level 1-5")
    player_count: Optional[int] = Field(default=1, ge=1, le=4, description="Number of players")

class ValidationResult(BaseModel):
    """Result of mystery validation"""
    is_valid: bool = Field(..., description="Whether the mystery passed validation")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of warnings")
    validated_at: datetime = Field(default_factory=datetime.utcnow)

class MysteryDocument(Document, MysteryConfig):
    """MongoDB document for storing generated mysteries"""
    
    class Settings:
        name = "mysteries"
        indexes = [
            "mystery_id",
            "room",
            "difficulty",
            "created_at",
        ]