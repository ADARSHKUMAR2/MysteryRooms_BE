"""Puzzle Generation Node using Structured Output"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List
from ..prompts.puzzle_prompts import PuzzlePromptBuilder
from ..models.schemas import PuzzleListOutput, PuzzleConfigListOutput
import random

class PuzzleNode:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.structured_structure_llm = self.llm.with_structured_output(PuzzleListOutput)
        self.structured_config_llm = self.llm.with_structured_output(PuzzleConfigListOutput)
        self.prompt_builder = PuzzlePromptBuilder()
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Step 1: Select puzzle types and structure
        puzzles = self._generate_puzzle_structure(state)
        
        # Step 1.5: Programmatic Enforcement - Ensure card deck puzzle exists!
        has_card_puzzle = any(p["type"] == "card_deck_riddle" for p in puzzles)
        if not has_card_puzzle and len(puzzles) > 0:
            print("⚠️ LLM forgot card_deck_riddle. Injecting it programmatically.")
            # Convert a non-starting, non-ending puzzle to card deck, or just add one
            target_index = len(puzzles) - 2 if len(puzzles) > 2 else 0
            puzzles[target_index]["type"] = "card_deck_riddle"
            puzzles[target_index]["id"] = "injected_card_riddle"
        
        # Step 2: Generate specific configurations
        validation_errors = state.get("validation_errors", [])
        puzzles_with_config = self._generate_puzzle_configs(puzzles, validation_errors)
        
        state["puzzles"] = puzzles_with_config
        return state
    
    def _generate_puzzle_structure(self, state: Dict[str, Any]) -> List[Dict]:
        system_msg = SystemMessage(content=self.prompt_builder.get_system_message())
        human_msg = HumanMessage(
            content=self.prompt_builder.build_puzzle_selection_prompt(
                difficulty=state["difficulty"],
                theme=state["theme"]
            )
        )
        
        try:
            result: PuzzleListOutput = self.structured_structure_llm.invoke([system_msg, human_msg])
            return [p.model_dump() for p in result.puzzles]
        except Exception as e:
            print(f"⚠️ Puzzle structure generation error: {e}")
            return self._get_fallback_puzzles()
    
    def _generate_puzzle_configs(self, puzzles: List[Dict], validation_errors: List[str]) -> List[Dict]:
        if not puzzles:
            return puzzles
            
        system_msg = SystemMessage(content=self.prompt_builder.get_system_message())
        human_msg = HumanMessage(
            content=self.prompt_builder.build_puzzle_config_prompt(
                puzzles=puzzles,
                validation_errors=validation_errors
            )
        )
        
        try:
            result: PuzzleConfigListOutput = self.structured_config_llm.invoke([system_msg, human_msg])
            
            # Create a mapping of puzzle ID to config
            config_map = {}
            for config_item in result.configs:
                config_dict = config_item.model_dump()
                puzzle_id = config_dict.get("id")
                config_data = config_dict.get("config", {})
                if puzzle_id:
                    config_map[puzzle_id] = config_data
            
            # Merge configs into puzzles by matching IDs
            for puzzle in puzzles:
                puzzle_id = puzzle.get("id")
                if puzzle_id in config_map:
                    puzzle["config"] = config_map[puzzle_id]
                else:
                    print(f"⚠️ No config found for puzzle: {puzzle_id}")
                    puzzle["config"] = {}
                    
            return puzzles
        except Exception as e:
            print(f"⚠️ Puzzle config generation error: {e}")
            # Provide empty configs as fallback
            for puzzle in puzzles:
                puzzle["config"] = {}
            return puzzles
            
    def _get_fallback_puzzles(self) -> List[Dict]:
        return [
            {
                "id": "entrance_statue", "type": "rotating_statue", "position": "entrance_hall",
                "dependencies": [], "unlocks": ["card_riddle"], "hint": "Face the guardian"
            },
            {
                "id": "card_riddle", "type": "card_deck_riddle", "position": "main_chamber",
                "dependencies": ["entrance_statue"], "unlocks": ["final_door"], "hint": "Count the suits."
            },
            {
                "id": "final_door", "type": "combination_lock", "position": "treasure_room",
                "dependencies": ["card_riddle"], "unlocks": ["victory"], "hint": "The code awaits"
            }
        ]
