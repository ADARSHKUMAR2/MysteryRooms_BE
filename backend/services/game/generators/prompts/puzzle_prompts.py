"""
Puzzle Generation Prompt Templates

Single Responsibility: Build prompts for puzzle selection and configuration.
Uses LangChain structured outputs, so no JSON formatting instructions are needed.
"""

from typing import List, Dict

class PuzzlePromptBuilder:
    VALID_PUZZLE_TYPES = [
        "rotating_statue", "symbol_sequence", "hieroglyph_sequence",
        "combination_lock", "hidden_compartment", "map_coordinates",
        "pressure_plate", "light_puzzle"
    ]
    
    VALID_POSITIONS = [
        "entrance_hall", "main_chamber", "west_chamber", "east_chamber",
        "secret_passage", "burial_chamber", "treasure_room", "antechamber"
    ]
    
    PUZZLE_COUNT_RANGES = {
        1: (2, 2), 2: (3, 4), 3: (4, 5), 4: (5, 6), 5: (6, 8)
    }
    
    @staticmethod
    def build_puzzle_selection_prompt(difficulty: int, theme: str) -> str:
        min_puzzles, max_puzzles = PuzzlePromptBuilder.PUZZLE_COUNT_RANGES.get(difficulty, (3, 5))
        
        return f"""You are designing puzzles for an Egyptian tomb mystery game.

THEME: {theme}
DIFFICULTY: {difficulty}/5
REQUIRED PUZZLES: exactly {min_puzzles} puzzles.

AVAILABLE PUZZLE TYPES:
{', '.join(PuzzlePromptBuilder.VALID_PUZZLE_TYPES)}

AVAILABLE POSITIONS:
{', '.join(PuzzlePromptBuilder.VALID_POSITIONS)}

CRITICAL RULES:
1. At least ONE puzzle must have empty dependencies [] (the starting puzzle).
2. At least ONE puzzle must unlock ["victory"] (the ending puzzle).
3. Each puzzle must have a unique ID (e.g., "entrance_statue", "hieroglyph_wall").
4. Dependencies must reference existing puzzle IDs you have created.
5. No circular dependencies allowed.

DIFFICULTY {difficulty} DESIGN PATTERNS:
- Difficulty 1-2: Linear chain (A → B → victory)
- Difficulty 3: Branching (A → B,C → D → victory)
- Difficulty 4-5: Complex parallel paths with convergence"""
    
    @staticmethod
    def build_puzzle_config_prompt(puzzles: List[Dict], validation_errors: List[str] = None) -> str:
        retry_context = ""
        if validation_errors:
            retry_context = f"\nPREVIOUS ATTEMPT HAD ERRORS:\n" + "\n".join(f"- {e}" for e in validation_errors) + "\nPlease fix these issues."
        
        return f"""You are configuring specific parameters for each puzzle.{retry_context}

PUZZLE LIST TO CONFIGURE:
{puzzles}

CONFIGURATION RULES BY TYPE:
- rotating_statue: requires `correctRotationSteps` (integer 0-3)
- combination_lock: requires `correctCombination` (string of 3-4 digits)
- symbol_sequence / hieroglyph_sequence: requires `correctSequence` (list of strings)
- hidden_compartment: requires `requiresKey` (boolean)
- map_coordinates: requires `correctCoordinates` (string, e.g., "N23-E45")
- pressure_plate: requires `correctPattern` (list of integers, e.g., [1, 2, 3, 4])
- light_puzzle: requires `correctTorchOrder` (list of integers) OR `requiresAlignment` (boolean)

Generate exactly one configuration object for each puzzle in the list provided, in the exact same order."""
    
    @staticmethod
    def get_system_message() -> str:
        return "You are a puzzle designer for escape room games. Create logical, solvable puzzle chains."
