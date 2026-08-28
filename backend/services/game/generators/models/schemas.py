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

# UPDATED: More specific schema for puzzle configurations
class RotatingStatueConfig(BaseModel):
    correctRotationSteps: int = Field(description="Number of 90-degree rotations (0-3)")

class CombinationLockConfig(BaseModel):
    correctCombination: str = Field(description="3-4 digit combination code")

class PatternStartPosition(BaseModel):
    row: int = Field(description="Row position (0-4)")
    col: int = Field(description="Column position (0-7)")

class SymbolSequenceConfig(BaseModel):
    correctSequence: List[str] = Field(description="List of exactly 4 symbol names")
    patternType: str = Field(description="Either 'horizontal_row' or 'vertical_column'")
    patternStartPosition: PatternStartPosition = Field(description="Starting position in the 8x5 grid")

class PressurePlateConfig(BaseModel):
    correctPattern: List[int] = Field(description="Sequence of plate IDs")

class HiddenCompartmentConfig(BaseModel):
    requiresKey: bool = Field(description="Whether a key is required")

class MapCoordinatesConfig(BaseModel):
    correctCoordinates: str = Field(description="Coordinate string (e.g., 'N23-E45')")

class LightPuzzleConfig(BaseModel):
    correctTorchOrder: Optional[List[int]] = Field(default=None, description="Order of torches")
    requiresAlignment: Optional[bool] = Field(default=None, description="Whether alignment is needed")

# Main config output that wraps the actual configuration
class PuzzleConfigOutput(BaseModel):
    id: str = Field(description="The puzzle ID this configuration is for")
    config: Dict[str, Any] = Field(description="The specific configuration parameters for the puzzle")

class PuzzleConfigListOutput(BaseModel):
    configs: List[PuzzleConfigOutput] = Field(description="List of puzzle configurations, one per puzzle")

class ClueOutput(BaseModel):
    id: str = Field(description="Unique clue identifier")
    type: str = Field(description="Type: inscription, visual, environmental, or audio")
    location: str = Field(description="Where the clue is located")
    content: str = Field(description="The clue content/text")
    related_puzzle: str = Field(description="Which puzzle this clue helps with")
    requires_puzzle_solved: Optional[str] = Field(default=None, description="Only visible after this puzzle is solved")

class ClueListOutput(BaseModel):
    clues: List[ClueOutput]
