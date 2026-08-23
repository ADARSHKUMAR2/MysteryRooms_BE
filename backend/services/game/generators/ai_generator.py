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
        """Initialize LLM, nodes, and build graph"""
        
        # Initialize LLM
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
            timeout=settings.GROQ_TIMEOUT
        )
        
        # Initialize validator
        self.validator = MysteryValidator()
        
        # Initialize nodes
        self.story_node = StoryNode(self.llm)
        self.puzzle_node = PuzzleNode(self.llm)
        self.clue_node = ClueNode(self.llm)
        self.validation_node = ValidationNode(self.validator)
        
        # Fallback generator
        self.fallback_generator = MockMysteryGenerator() if settings.ENABLE_FALLBACK_GENERATOR else None
        
        # Build workflow graph
        self.graph = self._build_graph()
    
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
    
    def generate(self, room: str, difficulty: int, player_count: int = 1) -> MysteryConfig:
        """
        Generate a mystery using AI workflow
        
        Args:
            room: Room type (e.g., "mummy_tomb")
            difficulty: Difficulty level 1-5
            player_count: Number of players
        
        Returns:
            MysteryConfig object
        
        Raises:
            Exception: If generation fails after retries
        """
        
        print(f"🤖 AI Generator: Starting mystery generation (difficulty={difficulty})...")
        
        # Initial state
        initial_state = {
            "room": room,
            "difficulty": difficulty,
            "player_count": player_count,
            "retry_count": 0
        }
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Check if validation passed
            validation_result = final_state.get("validation_result")
            
            if validation_result and validation_result.is_valid:
                print("✅ AI generation successful!")
                return self._build_mystery_from_state(final_state)
            else:
                print("⚠️ AI generation validation failed after retries")
                
                # Use fallback if enabled
                if self.fallback_generator:
                    print("🔄 Using fallback MockMysteryGenerator...")
                    return self.fallback_generator.generate(room, difficulty, player_count)
                else:
                    raise Exception("Mystery generation failed validation")
        
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            
            # Use fallback if enabled
            if self.fallback_generator:
                print("🔄 Using fallback MockMysteryGenerator...")
                return self.fallback_generator.generate(room, difficulty, player_count)
            else:
                raise
    
    def _build_mystery_from_state(self, state: Dict[str, Any]) -> MysteryConfig:
        """Build final MysteryConfig from workflow state"""
        
        from ..models.mystery import PuzzleConfig, ClueConfig
        
        # Convert puzzles
        puzzles = [PuzzleConfig(**p) for p in state["puzzles"]]
        
        # Convert clues
        clues = [ClueConfig(**c) for c in state.get("clues", [])]
        
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
