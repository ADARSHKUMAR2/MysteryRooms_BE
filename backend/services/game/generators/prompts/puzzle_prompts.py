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
        "pressure_plate", "light_puzzle", "card_deck_riddle"
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

CRITICAL RULES:
1. You ABSOLUTELY MUST include exactly ONE "map_coordinates" puzzle, one "light_puzzle" puzzle and one "combination_lock" puzzle in your response. These are mandatory.
2. At least ONE puzzle must have empty dependencies [] (the starting puzzle).
3. At least ONE puzzle must unlock ["victory"] (the ending puzzle).
4. Each puzzle must have a unique ID (e.g., "entrance_statue", "pharaoh_cards").
5. Dependencies must reference existing puzzle IDs you have created.
6. No circular dependencies allowed.

AVAILABLE POSITIONS:
{', '.join(PuzzlePromptBuilder.VALID_POSITIONS)}

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

Generate the configuration for each puzzle in the exact same order. Make sure the "id" field strictly matches the puzzle ID.

CONFIGURATION RULES BY TYPE:

- rotating_statue:
  Example: {{"id": "entrance_statue", "config": {{"correctRotationSteps": 2}}}}

- combination_lock: This is an ELEMENTAL NUMBER lock.
  REQUIRED FIELDS in config:
  • clueStyle: Randomly choose either "cylinder" OR "scales"
  • elementalMapping: A dictionary mapping ["Fire", "Leaf", "Water", "Sun"] to 4 UNIQUE random digits between 1 and 5.
  • elementSequence: A list of the 4 elements. If clueStyle is 'scales', sequence is strictly ordered from smallest digit to largest digit.
  • correctCombination: A string of EXACTLY 4 digits matching the sequence.

  Example: {{"id": "main_lock", "config": {{"clueStyle": "scales", "elementalMapping": {{"Fire": 4, "Leaf": 1, "Water": 9, "Sun": 2}}, "elementSequence": ["Leaf", "Sun", "Fire", "Water"], "correctCombination": "1249"}}}}


  RULES:
  1. Assign a unique random digit (0-9) to each of the 4 elements in `elementalMapping`.
  2. Decide the sequence of the 4 elements (e.g., ["Water", "Fire", "Leaf", "Sun"]). This is `elementSequence`.
  3. The `correctCombination` MUST perfectly match the digits mapped to the `elementSequence`.
     (e.g., If Water=9, Fire=4, Leaf=1, Sun=2, the combination is "9412").

  Example: {{
    "id": "main_lock", 
    "config": {{
      "elementalMapping": {{"Fire": 4, "Leaf": 1, "Water": 9, "Sun": 2}},
      "elementSequence": ["Water", "Fire", "Leaf", "Sun"],
      "correctCombination": "9412"
    }}
  }}

- light_puzzle: This is a LASER REFLECTION puzzle where a beam of light must bounce off mirrors to hit a target.
  
  REQUIRED FIELDS in config:
  • requiresAlignment: Must be true
  • mirrorCount: Integer between 2 and 4 (how many mirrors the player must use)
  
Example: {{"id": "sun_beam_chamber", "config": {{"requiresAlignment": true, "mirrorCount": 3}}}}


- symbol_sequence / hieroglyph_sequence: These are GRID-BASED pattern matching puzzles

  GRID LAYOUT: 40 symbols arranged in 8 columns × 5 rows displayed on a wall

  REQUIRED FIELDS in config:
  • correctSequence: List of EXACTLY 4 symbols chosen from [{valid_symbols}]. Each symbol MUST be used only ONCE.
  • patternType: Either "horizontal_row" or "vertical_column"
  • patternStartPosition: Object with "row" (integer 0-4) and "col" (integer 0-7)

  PATTERN RULES:
  - If "horizontal_row": The 4 symbols appear consecutively in the same row
  - If "vertical_column": The 4 symbols appear consecutively in the same column

  Example: {{
    "id": "main_symbol",
    "config": {{
      "correctSequence": ["EyeOfHorus", "Sphinx", "Cobra", "SunDisk"],
      "patternType": "horizontal_row",
      "patternStartPosition": {{"row": 2, "col": 1}}
    }}
  }}

- card_deck_riddle: This is a CARD-BASED riddle puzzle using a 4×4 grid of playing cards

  GRID LAYOUT: 16 playing cards arranged in 4 columns × 4 rows
  CARD SUITS: Spades, Hearts, Diamonds, Clubs
  CARD RANKS: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K

  REQUIRED FIELDS in config:
  • riddleRules: List of EXACTLY 4 rule objects (one per column), each with:
    - "column": Column index (0-3)
    - "suit": The suit to count ("Spades", "Hearts", "Diamonds", or "Clubs")
    - "count": How many cards of that suit are in the column (1-4)
  • correctCode: String of 4 digits representing the answer (e.g., "2341")
  • gridCards: Array of exactly 16 card objects (read left-to-right, top-to-bottom for the 4x4 grid), each with "suit" and "rank"

  EXAMPLE:
  {{
    "id": "pharaoh_cards",
    "config": {{
      "riddleRules": [
        {{"column": 0, "suit": "Spades", "count": 2}},
        {{"column": 1, "suit": "Diamonds", "count": 3}},
        {{"column": 2, "suit": "Hearts", "count": 4}},
        {{"column": 3, "suit": "Clubs", "count": 1}}
      ],
      "correctCode": "2341",
      "gridCards": [
        {{"suit": "Spades", "rank": "A"}}, {{"suit": "Diamonds", "rank": "7"}}, {{"suit": "Hearts", "rank": "K"}}, {{"suit": "Clubs", "rank": "5"}},
        {{"suit": "Spades", "rank": "Q"}}, {{"suit": "Diamonds", "rank": "3"}}, {{"suit": "Hearts", "rank": "2"}}, {{"suit": "Hearts", "rank": "9"}},
        {{"suit": "Hearts", "rank": "J"}}, {{"suit": "Diamonds", "rank": "10"}}, {{"suit": "Hearts", "rank": "6"}}, {{"suit": "Diamonds", "rank": "4"}},
        {{"suit": "Diamonds", "rank": "8"}}, {{"suit": "Hearts", "rank": "A"}}, {{"suit": "Hearts", "rank": "3"}}, {{"suit": "Spades", "rank": "K"}}
      ]
    }}
  }}


- hidden_compartment:
  Example: {{"id": "secret_door", "config": {{"requiresKey": true}}}}

- map_coordinates: This is an ASTROLABE GLOBE puzzle.
  REQUIRED FIELDS in config:
  • latitude: A short string representing North/South (e.g., "N29", "S45")
  • longitude: A short string representing East/West (e.g., "E31", "W12")
  
  Example: {{"id": "astrolabe_puzzle", "config": {{"latitude": "N29", "longitude": "E31"}}}}

- pressure_plate:
  Example: {{"id": "floor_puzzle", "config": {{"correctPattern": [1, 2, 3, 4]}}}}

- light_puzzle:
  Example: {{"id": "torch_room", "config": {{"correctTorchOrder": [3, 1, 4, 2]}}}}

Generate exactly one configuration object for each puzzle in the list provided, in the exact same order."""

    @staticmethod
    def get_system_message() -> str:
        return "You are a puzzle designer for escape room games. Create logical, solvable puzzle chains."
