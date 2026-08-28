"""
Puzzle Generation Prompt Templates

Single Responsibility: Build prompts for puzzle selection and configuration.
Uses LangChain structured outputs, so no JSON formatting instructions are needed.
"""

from typing import List, Dict
from ...models.symbols import EgyptianSymbol

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

        valid_symbols = ", ".join(EgyptianSymbol.list_all())

        return f"""You are configuring specific parameters for each puzzle.{retry_context}

PUZZLE LIST TO CONFIGURE:
{puzzles}

IMPORTANT: You must return a list of configuration objects. Each object MUST have:
- "id": the puzzle ID (matching the puzzle from the list above)
- "config": an object containing the configuration parameters for that puzzle type

CONFIGURATION RULES BY TYPE:

- rotating_statue: 
  Example: {{"id": "entrance_statue", "config": {{"correctRotationSteps": 2}}}}
  
- combination_lock: 
  Example: {{"id": "main_lock", "config": {{"correctCombination": "1234"}}}}

- symbol_sequence / hieroglyph_sequence: These are GRID-BASED pattern matching puzzles
  
  GRID LAYOUT: 40 symbols arranged in 8 columns × 5 rows displayed on a wall
  
  REQUIRED FIELDS in config:
  • correctSequence: List of EXACTLY 4 symbols chosen from [{valid_symbols}]. Each symbol MUST be used only ONCE.
  • patternType: Either "horizontal_row" or "vertical_column"
  • patternStartPosition: Object with "row" (integer 0-4) and "col" (integer 0-7)
  
  PATTERN RULES:
  - If "horizontal_row": The 4 symbols appear consecutively in the same row
  - If "vertical_column": The 4 symbols appear consecutively in the same column
  - Valid horizontal patterns: Must start at columns 0-4 (so 4 consecutive symbols fit within 8 columns)
  - Valid vertical patterns: Must start at rows 0-1 (so 4 consecutive symbols fit within 5 rows)
  
  Example: {{
    "id": "main_symbol",
    "config": {{
      "correctSequence": ["EyeOfHorus", "Sphinx", "Cobra", "SunDisk"],
      "patternType": "horizontal_row",
      "patternStartPosition": {{"row": 2, "col": 1}}
    }}
  }}
  
- hidden_compartment: requires `requiresKey` (boolean)
- map_coordinates: requires `correctCoordinates` (string, e.g., "N23-E45")
- pressure_plate: requires `correctPattern` (list of integers, e.g., [1, 2, 3, 4])
- light_puzzle: requires `correctTorchOrder` (list of integers) OR `requiresAlignment` (boolean)

Generate exactly one configuration object for each puzzle in the list provided, in the exact same order."""

    @staticmethod
    def get_system_message() -> str:
        return "You are a puzzle designer for escape room games. Create logical, solvable puzzle chains."
