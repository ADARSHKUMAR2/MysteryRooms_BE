"""
Clue Generation Prompt Templates

Single Responsibility: Build prompts for generating clues that link puzzles.
"""

from typing import List, Dict
from ...models.symbols import EgyptianSymbol

class CluePromptBuilder:
    """Builds prompts for clue generation node"""

    @staticmethod
    def build_clue_prompt(
        theme: str,
        objective: str,
        puzzles: List[Dict]
    ) -> str:
        """Generate clue creation prompt"""

        puzzle_summary = "\n".join([
            f"- {p['id']} ({p['type']}) at {p['position']}"
            for p in puzzles
        ])

        valid_symbols = ", ".join(EgyptianSymbol.list_all())

        return f"""You are writing clues for an Egyptian tomb mystery game.

THEME: {theme}
OBJECTIVE: {objective}

PUZZLES IN THE MYSTERY:
{puzzle_summary}

CLUE REQUIREMENTS:
1. Generate 1-2 clues per puzzle (total: ~{len(puzzles) * 1.5} clues).
2. Clues should be cryptic but solvable.
3. Some clues should only appear after solving prerequisite puzzles (use requires_puzzle_solved).

AVAILABLE SYMBOLS TO REFERENCE:
If a clue relates to a symbol_sequence or hieroglyph_sequence puzzle, you MUST construct riddles that point to these specific symbol names: 
[{valid_symbols}]
(e.g., "The protector of the falcon (HorusFalcon) watches over the golden beacon (SunDisk).")

SPECIAL RULES FOR SYMBOL/HIEROGLYPH SEQUENCE PUZZLES:
These puzzles use a 40-symbol grid (8 columns × 5 rows) where players must find 4 specific symbols arranged in a pattern.

Your clues for these puzzles MUST:
1. Mention all 4 symbols from the correctSequence by their EXACT names from the valid symbols list
2. Include spatial hints about the pattern direction:
   - For horizontal patterns: Use phrases like "aligned in a row", "following the line", "side by side", "across the wall", "in a straight line horizontally"
   - For vertical patterns: Use phrases like "stacked vertically", "descending column", "one above the other", "rising upward", "in a vertical line"
3. Hint at the ORDER of the symbols using sequence language (first to last, beginning to end, etc.)
4. Maintain the cryptic, atmospheric Egyptian tomb theme

EXAMPLE CLUES FOR SYMBOL SEQUENCES:
- Horizontal: "Upon the sacred wall, four guardians stand as one: The Eye that sees all (EyeOfHorus), followed by the silent Sphinx, then the Cobra's deadly warning, and finally Ra's eternal light (SunDisk) - all aligned in a single row, waiting to be touched in order."
- Vertical: "Seek the vertical path descending from heaven to earth: The Falcon of Horus (HorusFalcon) soars highest, below it rests the sacred Lotus (BlueLotus), upon which the golden Feather (GoldenFeather) descends, and at the base stands the life-giving Palm (PalmTree). One above the other, they reveal the way."

CLUE TYPE GUIDELINES:
- inscription: Text carved on walls, tablets, scrolls
- visual: Symbols, drawings, patterns players observe
- environmental: Physical environment details (blood trails, footprints)
- audio: Not commonly used in written mysteries

EXAMPLE CLUE TONE:
"When Ra's light touches the guardian, the path reveals itself" (Helps solve entrance_statue)"""

    @staticmethod
    def get_system_message() -> str:
        """System message for clue generation"""
        return (
            "You are a mystery writer crafting atmospheric clues for an Egyptian tomb game. "
            "Write evocative, thematic clues that guide without being obvious."
        )
