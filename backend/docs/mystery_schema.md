# Mystery JSON Schema Documentation

## MysteryConfig

The root object returned by `/game/generate`

| Field | Type | Description |
|-------|------|-------------|
| mystery_id | string | Unique UUID for this mystery |
| room | string | Room type (e.g., "mummy_tomb") |
| difficulty | int | Difficulty level 1-5 |
| theme | string | Mystery theme |
| objective | string | Player's main goal |
| time_limit_seconds | int | Time limit in seconds |
| puzzles | PuzzleConfig[] | Array of puzzles |
| clues | ClueConfig[] | Array of clues |
| twist | string? | Optional plot twist |

## PuzzleConfig

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique puzzle identifier |
| type | string | Puzzle type (see types below) |
| position | string | Location in room |
| config | object | Puzzle-specific parameters |
| dependencies | string[] | Puzzle IDs that must be solved first |
| unlocks | string[] | What this puzzle unlocks |
| hint | string? | Optional hint text |

### Supported Puzzle Types

- `rotating_statue`: Rotate statue to correct angle
- `symbol_sequence`: Match correct symbol order
- `hieroglyph_sequence`: Solve hieroglyph pattern
- `combination_lock`: Enter correct number combination
- `hidden_compartment`: Find hidden object
- `map_coordinates`: Locate coordinates on map
- `pressure_plate`: Step on plates in correct order
- `light_puzzle`: Align light beams correctly

## ClueConfig

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique clue identifier |
| type | string | Clue type (inscription, visual, audio, environmental) |
| location | string | Where clue is located |
| content | string | The clue content/text |
| related_puzzle | string? | Which puzzle this helps with |
| requires_puzzle_solved | string? | Only visible after puzzle is solved |
