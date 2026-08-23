"""
Story Generation Prompt Templates

Single Responsibility: Build prompts for theme, objective, and twist generation.
Uses LangChain structured outputs, so no JSON formatting instructions are needed.
"""

class StoryPromptBuilder:
    THEME_EXAMPLES = {
        1: {"theme": "stolen_artifact", "objective": "Recover the stolen Eye of Horus before the tomb seals"},
        2: {"theme": "missing_person", "objective": "Discover what happened to the missing archaeologist Dr. Hassan"},
        3: {"theme": "ancient_curse", "objective": "Break the Pharaoh's curse and escape the tomb alive"},
        4: {"theme": "deception", "objective": "Navigate the false tomb and find the real treasure chamber"},
        5: {"theme": "legendary_treasure", "objective": "Unlock the legendary hidden chamber of Pharaoh Khufu"},
    }
    
    @staticmethod
    def build_story_prompt(room: str, difficulty: int, player_count: int) -> str:
        example = StoryPromptBuilder.THEME_EXAMPLES.get(difficulty, StoryPromptBuilder.THEME_EXAMPLES[3])
        
        return f"""You are creating a mystery story for an Egyptian tomb escape room game.

CONTEXT:
- Room: {room}
- Difficulty: {difficulty}/5
- Players: {player_count}

REQUIREMENTS:
1. Generate a compelling THEME (one or two words).
2. Create a clear OBJECTIVE that players must achieve.
3. Add an optional TWIST for drama (or leave empty for lower difficulties).

DIFFICULTY GUIDELINES:
- Difficulty 1-2: Simple, straightforward themes (theft, lost item)
- Difficulty 3: Medium complexity (curses, secrets)
- Difficulty 4-5: Complex narratives (deception, multiple layers)

EXAMPLE FOR DIFFICULTY {difficulty}:
Theme: {example['theme']}
Objective: {example['objective']}

Generate a UNIQUE story (do not copy the exact example)."""
    
    @staticmethod
    def get_system_message() -> str:
        return (
            "You are a creative game designer specializing in Egyptian mystery adventures. "
            "Generate engaging, thematic stories that fit the required difficulty level."
        )
