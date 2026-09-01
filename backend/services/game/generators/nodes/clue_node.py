"""Clue Generation Node using Structured Output"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from ..prompts.clue_prompts import CluePromptBuilder
from ..models.schemas import ClueListOutput
from langchain_core.language_models import BaseChatModel

class ClueNode:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.structured_llm = self.llm.with_structured_output(ClueListOutput, method="function_calling")
        self.prompt_builder = CluePromptBuilder()
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate clues for the mystery"""
        system_msg = SystemMessage(content=self.prompt_builder.get_system_message())
        human_msg = HumanMessage(
            content=self.prompt_builder.build_clue_prompt(
                theme=state["theme"],
                objective=state["objective"],
                puzzles=state["puzzles"]
            )
        )
        
        result: ClueListOutput = self.structured_llm.invoke([system_msg, human_msg])
        state["clues"] = [c.model_dump() for c in result.clues]
        
        return state
