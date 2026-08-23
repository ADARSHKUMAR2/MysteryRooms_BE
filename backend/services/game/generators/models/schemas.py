from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class StoryOutput(BaseModel):
    theme: str = Field(description="Thematic element of the mystery (e.g., 'ancient_curse')")
    objective: str = Field(description="The main goal for the players")
    twist: Optional[str] = Field(default=None, description="An optional plot twist")

class PuzzleStructureOutput(BaseModel):
    id: str = Field(description="Unique ID for the puzzle")
    type: str = Field(description="Type of puzzle")
    position: str = Field(description="Location in the room")
    dependencies: List[str] = Field(description="IDs of puzzles that must be solved first")
    unlocks: List[str] = Field(description="IDs of puzzles unlocked, or ['victory']")
    hint: Optional[str] = Field(default=None, description="Optional hint text")

class PuzzleListOutput(BaseModel):
    puzzles: List[PuzzleStructureOutput]

class PuzzleConfigOutput(BaseModel):
    config: Dict[str, Any] = Field(description="The specific configuration parameters for the puzzle")

class PuzzleConfigListOutput(BaseModel):
    configs: List[PuzzleConfigOutput]

class ClueOutput(BaseModel):
    id: str = Field(description="Unique clue identifier")
    type: str = Field(description="Type: inscription, visual, environmental, or audio")
    location: str = Field(description="Where the clue is located")
    content: str = Field(description="The clue content/text")
    related_puzzle: str = Field(description="Which puzzle this clue helps with")
    requires_puzzle_solved: Optional[str] = Field(default=None, description="Only visible after this puzzle is solved")

class ClueListOutput(BaseModel):
    clues: List[ClueOutput]
