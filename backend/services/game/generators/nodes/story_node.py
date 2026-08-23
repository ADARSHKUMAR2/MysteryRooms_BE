"""Story Generation Node using Structured Output"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any
from ..prompts.story_prompts import StoryPromptBuilder
from ..models.schemas import StoryOutput

class StoryNode:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.structured_llm = self.llm.with_structured_output(StoryOutput)
        self.prompt_builder = StoryPromptBuilder()
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate story elements and update state"""
        system_msg = SystemMessage(content=self.prompt_builder.get_system_message())
        human_msg = HumanMessage(
            content=self.prompt_builder.build_story_prompt(
                room=state["room"],
                difficulty=state["difficulty"],
                player_count=state["player_count"]
            )
        )
        
        try:
            # Structured output ensures we get a StoryOutput object
            story_result: StoryOutput = self.structured_llm.invoke([system_msg, human_msg])
            
            state["theme"] = story_result.theme
            state["objective"] = story_result.objective
            state["twist"] = story_result.twist
            
        except Exception as e:
            print(f"⚠️ Story generation structured output error: {e}")
            # Fallback values
            state["theme"] = "ancient_mystery"
            state["objective"] = "Escape the tomb before time runs out"
            state["twist"] = None
            
        return state
