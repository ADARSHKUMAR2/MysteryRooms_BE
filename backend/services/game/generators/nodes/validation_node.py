"""Validation Node"""

from typing import Dict, Any
from ...validators.mystery_validator import MysteryValidator
from ...models.mystery import MysteryConfig, PuzzleConfig, ClueConfig

class ValidationNode:
    def __init__(self, validator: MysteryValidator):
        self.validator = validator
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        mystery = self._build_mystery_config(state)
        validation_result = self.validator.validate(mystery)
        
        state["validation_result"] = validation_result
        state["validation_errors"] = validation_result.errors
        
        return state
    
    def _build_mystery_config(self, state: Dict[str, Any]) -> MysteryConfig:
        puzzles = [PuzzleConfig(**p) for p in state.get("puzzles", [])]
        clues = [ClueConfig(**c) for c in state.get("clues", [])]
        
        return MysteryConfig(
            room=state["room"],
            difficulty=state["difficulty"],
            theme=state["theme"],
            objective=state["objective"],
            time_limit_seconds=1800, # Simplified for brevity
            puzzles=puzzles,
            clues=clues,
            twist=state.get("twist")
        )
    
    @staticmethod
    def should_retry(state: Dict[str, Any]) -> str:
        validation_result = state.get("validation_result")
        retry_count = state.get("retry_count", 0)
        max_retries = 3
        
        if validation_result and not validation_result.is_valid:
            if retry_count < max_retries:
                state["retry_count"] = retry_count + 1
                print(f"🔄 Validation failed, retrying ({retry_count + 1}/{max_retries})...")
                return "retry"
            else:
                print(f"❌ Max retries reached, using fallback")
                return "done"
        return "done"
