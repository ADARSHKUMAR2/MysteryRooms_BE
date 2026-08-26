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
