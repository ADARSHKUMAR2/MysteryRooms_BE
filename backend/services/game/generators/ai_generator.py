"""
AI Mystery Generator

Main orchestrator that builds a LangGraph workflow for mystery generation.
Single Responsibility: Coordinate the generation pipeline.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

from ..models.mystery import MysteryConfig
from ..validators.mystery_validator import MysteryValidator
from ..config.settings import settings

from .nodes.story_node import StoryNode
from .nodes.puzzle_node import PuzzleNode
from .nodes.clue_node import ClueNode
from .nodes.validation_node import ValidationNode
from .mock_generator import MockMysteryGenerator


class AIGenerator:
    """
    AI-powered mystery generator using LangGraph workflow.
    
    Workflow: Story → Puzzles → Clues → Validation → (Retry if needed)
    """
    
    def __init__(self):
        """Initialize LLMs, nodes, and build graph"""
        
        # Initialize a list of fallback LLMs
        self.llm_chain = []
        for model_name in settings.GROQ_MODELS:
            self.llm_chain.append(
                ChatGroq(
                    api_key=settings.GROQ_API_KEY,
                    model=model_name,
                    temperature=settings.GROQ_TEMPERATURE,
                    max_tokens=settings.GROQ_MAX_TOKENS,
                    timeout=settings.GROQ_TIMEOUT,
                    max_retries=1 # We handle retries ourselves by swapping models
                )
            )
            
        # We start with the first model in the chain
        self.current_model_index = 0
        self._initialize_nodes_and_graph(self.llm_chain[self.current_model_index])
        
        self.validator = MysteryValidator()
        self.fallback_generator = MockMysteryGenerator() if settings.ENABLE_FALLBACK_GENERATOR else None
        
    def _initialize_nodes_and_graph(self, active_llm):
        """Re-initializes the nodes with the current active LLM"""
        self.story_node = StoryNode(active_llm)
        self.puzzle_node = PuzzleNode(active_llm)
        self.clue_node = ClueNode(active_llm)
        self.validation_node = ValidationNode(MysteryValidator())
        self.graph = self._build_graph()

    def generate(self, room: str, difficulty: int, player_count: int = 1) -> MysteryConfig:
        
        print(f"🤖 AI Generator: Starting mystery generation (difficulty={difficulty})...")
        
        # Reset to the best model at the start of a new generation request
        self.current_model_index = 0
        self._initialize_nodes_and_graph(self.llm_chain[self.current_model_index])

        # Loop through our fallback chain of models
        while self.current_model_index < len(self.llm_chain):
            current_model_name = settings.GROQ_MODELS[self.current_model_index]
            print(f"🧠 Attempting generation with model: {current_model_name}")
            
            initial_state = {
                "room": room,
                "difficulty": difficulty,
                "player_count": player_count,
                "retry_count": 0
            }
            
            try:
                # Run the graph with the current model
                final_state = self.graph.invoke(initial_state)
                
                validation_result = final_state.get("validation_result")
                
                if validation_result and validation_result.is_valid:
                    print(f"✅ AI generation successful with {current_model_name}!")
                    return self._build_mystery_from_state(final_state)
                else:
                    print(f"⚠️ Validation failed for {current_model_name}, but no API crash. Skipping to next model...")
                    
            except Exception as e:
                # If we get a 429 Rate Limit, JSON Parse error, or Timeout, it catches here!
                error_msg = str(e)
                print(f"❌ API/Generation error with {current_model_name}: {error_msg[:100]}...")
            
            # If we reached here, the current model failed. Move to the next one!
            self.current_model_index += 1
            if self.current_model_index < len(self.llm_chain):
                print(f"🔄 Swapping LLM engine to {settings.GROQ_MODELS[self.current_model_index]}...")
                self._initialize_nodes_and_graph(self.llm_chain[self.current_model_index])
                
        # If we exhausted all models in the list...
        print("🚨 ALL AI MODELS FAILED. Falling back to MockMysteryGenerator.")
        if self.fallback_generator:
            return self.fallback_generator.generate(room, difficulty, player_count)
        else:
            raise Exception("Mystery generation failed across all models, and fallback is disabled.")
    
    def _build_graph(self) -> Any:
        """Build the LangGraph workflow"""
        
        # Define state graph
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("story", self.story_node.execute)
        workflow.add_node("puzzles", self.puzzle_node.execute)
        workflow.add_node("clues", self.clue_node.execute)
        workflow.add_node("validation", self.validation_node.execute)
        
        # Set entry point
        workflow.set_entry_point("story")
        
        # Add edges (linear flow)
        workflow.add_edge("story", "puzzles")
        workflow.add_edge("puzzles", "clues")
        workflow.add_edge("clues", "validation")
        
        # Add conditional edge for retry logic
        workflow.add_conditional_edges(
            "validation",
            ValidationNode.should_retry,
            {
                "retry": "puzzles",  # Loop back to puzzles
                "done": END          # Finish
            }
        )
        
        return workflow.compile()    
    
    def _build_mystery_from_state(self, state: Dict[str, Any]) -> MysteryConfig:
        """Build final MysteryConfig from workflow state"""

        from ..models.mystery import PuzzleConfig, ClueConfig

        # Convert puzzles
        puzzles = [PuzzleConfig(**p) for p in state["puzzles"]]

        # Convert clues
        clues = []
        for c in state.get("clues", []):
            # FIX: If requires_puzzle_solved is a list, convert it to a comma-separated string
            # so it passes validation in ClueConfig (which expects Optional[str])
            req_puz = c.get("requires_puzzle_solved")
            if isinstance(req_puz, list):
                c["requires_puzzle_solved"] = ",".join(str(p) for p in req_puz)
            
            clues.append(ClueConfig(**c))

        # Calculate time limit
        time_limits = {1: 900, 2: 1200, 3: 1800, 4: 2100, 5: 2400}
        time_limit = time_limits.get(state["difficulty"], 1800)

        # Build mystery
        mystery = MysteryConfig(
            room=state["room"],
            difficulty=state["difficulty"],
            theme=state["theme"],
            objective=state["objective"],
            time_limit_seconds=time_limit,
            puzzles=puzzles,
            clues=clues,
            twist=state.get("twist")
        )

        return mystery
