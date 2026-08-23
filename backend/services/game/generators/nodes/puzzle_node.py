"""Puzzle Generation Node using Structured Output"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List
from ..prompts.puzzle_prompts import PuzzlePromptBuilder
from ..models.schemas import PuzzleListOutput, PuzzleConfigListOutput

class PuzzleNode:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.structured_structure_llm = self.llm.with_structured_output(PuzzleListOutput)
        self.structured_config_llm = self.llm.with_structured_output(PuzzleConfigListOutput)
        self.prompt_builder = PuzzlePromptBuilder()
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Step 1: Select puzzle types and structure
        puzzles = self._generate_puzzle_structure(state)
        
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
            # Convert Pydantic objects back to dicts for internal state processing
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
            
            # Merge configs into puzzles safely
            configs = [c.model_dump()["config"] for c in result.configs]
            
            for i, puzzle in enumerate(puzzles):
                if i < len(configs):
                    puzzle["config"] = configs[i]
                else:
                    puzzle["config"] = {}
                    
            return puzzles
        except Exception as e:
            print(f"⚠️ Puzzle config generation error: {e}")
            for puzzle in puzzles:
                puzzle["config"] = {}
            return puzzles
            
    def _get_fallback_puzzles(self) -> List[Dict]:
        return [
            {
                "id": "entrance_statue", "type": "rotating_statue", "position": "entrance_hall",
                "dependencies": [], "unlocks": ["final_door"], "hint": "Face the guardian"
            },
            {
                "id": "final_door", "type": "combination_lock", "position": "treasure_room",
                "dependencies": ["entrance_statue"], "unlocks": ["victory"], "hint": "The code awaits"
            }
        ]
