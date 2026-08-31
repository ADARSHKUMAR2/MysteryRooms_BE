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

SPECIAL RULES FOR CARD DECK RIDDLE PUZZLES:
These puzzles use a 4x4 grid of playing cards where players must count specific suits in each column to form a code.

Your clues for these puzzles MUST:
1. Reference the card suits and their Egyptian/mystical associations:
   - Spades: Death, the underworld, darkness
   - Hearts: Life, blood, sacrifice, the heart weighed by Ma'at
   - Diamonds: Wealth, treasures, golden pyramids, riches of the pharaohs
   - Clubs: Growth, vegetation, rebirth
2. Provide riddles that describe WHICH suit to count in WHICH column
3. Use directional language: "first column", "second path", "third pillar", "final gateway"
4. Hint that players need to COUNT the matching cards in each column
5. Suggest the answer is a numerical code formed by the counts

EXAMPLE CLUES FOR CARD DECK RIDDLE:
- "The Pharaoh's game lies before you, four columns of fate. In the first column, count the symbols of death and darkness. In the second, tally the gems of eternal wealth. In the third, number the marks of life's crimson flow. In the final column, sum the signs of the Nile's bounty. Speak these counts as one, and the lock shall yield."
- "Ancient cards whisper secrets: Where Anubis walks in the leftmost path, mark his steps. Where golden pyramids shimmer in the second way, count their peaks. Where hearts beat in the third passage, measure their rhythm. Where the river's growth blooms in the final column, number its flourish. Unite these numbers to unlock the door."

SPECIAL RULES FOR PRESSURE PLATE PUZZLES:
These puzzles consist of exactly 5 large stone tiles on the floor. 
Each tile has a specific Egyptian carving representing its ID (1 to 5):
- Plate 1 = The Pyramid (Greatness, monuments, reaching the sky)
- Plate 2 = The Mummy (The sleeping dead, bandages, eternal rest)
- Plate 3 = The Egyptian Cat (Bastet, the feline guardian, the watcher)
- Plate 4 = The Coffin / Sarcophagus (The golden vessel, the final bed)
- Plate 5 = Ankh Khonsu (The moon god, time, the traveler of the night sky)

Your clues for pressure_plate puzzles MUST:
1. Be written as an ancient poem, stanza, or mythological story.
2. Reference the exact carvings (Pyramid, Mummy, Cat, Coffin, Khonsu) in the exact order specified by the `correctPattern` array.
   (For example, if the pattern is [3, 1, 5, 2, 4], the poem MUST mention the Cat first, the Pyramid second, Khonsu third, the Mummy fourth, and the Coffin last).
3. The story must clearly imply a sequence of events so the player knows the exact order to step on the tiles.

EXAMPLE CLUES FOR PRESSURE PLATES:
- If pattern is [1, 3, 5, 2, 4]: "To cross the abyss, follow the path of the ancients. Begin where the great stone peaks touch the heavens (Pyramid). From there, seek the gaze of the sacred watcher with golden eyes (Cat). Let the moon traveler guide your next step (Khonsu), before honoring those bound in eternal slumber (Mummy). Only then may you rest your foot upon the golden vessel of the afterlife (Coffin)."
- If pattern is [4, 2, 3, 1, 5]: " Honor the golden vessel that cradles the dead (Coffin), then step where the linen-wrapped kings lie sleeping (Mummy). The feline guardian (Cat) will watch your third step. Ascend to the monument of the sun (Pyramid), and finally, walk in the light of the moon god (Khonsu) to find safe passage."

SPECIAL RULES FOR LIGHT/MIRROR PUZZLES:
These puzzles involve rotating standing mirrors to bounce a laser-like beam of light across the room to hit a crystal target.

Your clues for these puzzles MUST:
1. Use language about "guiding the light", "bending the sun", or "reflecting the beam".
2. Mention that the path is not straight and requires reflection.

EXAMPLE CLUES FOR LIGHT PUZZLES:
- "The true path is never straight. Let the sun's gaze strike the polished glass, and bend its light until it finds the resting star."
- "Four sentinels of glass stand in the dark. Turn their faces to catch the dawn, passing the blazing torch from one to the next until the crystal awakens."
- "The light of the sun is a beacon of hope. It guides the way, bending the path until it reaches the crystal."

SPECIAL RULES FOR COMBINATION LOCK (ELEMENTAL NUMBER):
These puzzles require the player to type a 4-digit code into a keypad. The player discovers the code by reading an elemental story, and matching the elements to numbers found elsewhere in the room.

Your clues for combination_lock MUST:
1. Be written as an ancient poem, prophecy, or mythological story.
2. Reference the 4 elements (Fire, Leaf, Water, Sun) in the exact order specified by the `elementSequence` array in the puzzle config.
3. Use poetic synonyms (e.g., for Fire: "blazing inferno", "crimson spark", "flame").
4. Imbue a clear chronological sequence (first, then, before, finally) so the player knows the order to read the elements.
5. DO NOT mention the actual numbers in the story. The player will find the numbers engraved on a cylinder in the room.

EXAMPLE CLUES FOR ELEMENTAL LOCK:
- If elementSequence is ["Water", "Leaf", "Sun", "Fire"]: "First, the great river flowed (Water), giving drink to the barren dirt. From the mud sprang the emerald harvest (Leaf), stretching upwards to greet the golden dawn (Sun). But all that grows must eventually return to ash in the scorching heat of the crimson flame (Fire)."
- If combination is "Water,Leaf,Sun,Fire": "First, the great river flowed (Water), giving drink to the barren dirt. From the mud sprang the emerald harvest (Leaf), stretching upwards to greet the golden dawn (Sun). But all that grows must eventually return to ash in the scorching heat of the crimson flame (Fire)."
- If combination is "Fire,Sun,Leaf,Water": "First, the fire burned (Fire), scorching the earth. Then, the sun shone (Sun), illuminating the land. And the leaf fell (Leaf), bringing life to the barren soil. But the waters must flow (Water) to nourish the plant."

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
