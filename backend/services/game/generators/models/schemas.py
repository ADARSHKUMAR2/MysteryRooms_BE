from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

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

# ====================
# Puzzle Configuration Models
# ====================

class RotatingStatueConfig(BaseModel):
    correctRotationSteps: int = Field(description="Number of 90-degree rotations (0-3)")

class CombinationLockConfig(BaseModel):
    elementalMapping: Dict[str, int] = Field(description="Maps 'Fire', 'Leaf', 'Water', 'Sun' to random digits (1-5)")
    elementSequence: List[str] = Field(description="The sequence of the 4 elements")
    clueStyle: str = Field(description="Must be 'cylinder' (story-based) or 'scales' (weight-based)")
    correctCombination: str = Field(description="4 digit combination code derived from the mapping")


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
    latitude: str = Field(description="Latitude (e.g., 'N23', 'S45')")
    longitude: str = Field(description="Longitude (e.g., 'E12', 'W99')")

class LightPuzzleConfig(BaseModel):
    # correctTorchOrder: Optional[List[int]] = Field(default=None, description="Order of torches")
    requiresAlignment: bool = Field(default=None, description="Whether alignment is needed")

# NEW: Card Deck Riddle Models
class RiddleRule(BaseModel):
    column: int = Field(description="Column index (0-3)")
    suit: str = Field(description="Card suit to count (Spades, Hearts, Diamonds, Clubs)")
    count: int = Field(description="Number of cards of this suit in the column (1-4)")

class CardData(BaseModel):
    suit: str = Field(description="Card suit (Spades, Hearts, Diamonds, Clubs)")
    rank: str = Field(description="Card rank (A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K)")

class CardDeckRiddleConfig(BaseModel):
    riddleRules: List[RiddleRule] = Field(description="Exactly 4 rules, one per column")
    correctCode: str = Field(description="4-digit solution code formed by concatenating counts")
    gridCards: List[CardData] = Field(description="List of exactly 16 cards (read left-to-right, top-to-bottom for the 4x4 grid)")


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
    # FIX: Allows the LLM to output a single string or a list of strings
    requires_puzzle_solved: Optional[Union[str, List[str]]] = Field(default=None, description="Only visible after this puzzle is solved (string or list of strings)")

class ClueListOutput(BaseModel):
    clues: List[ClueOutput]
