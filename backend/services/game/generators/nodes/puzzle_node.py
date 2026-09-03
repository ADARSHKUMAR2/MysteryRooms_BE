"""Puzzle Generation Node using Structured Output"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List
from ..prompts.puzzle_prompts import PuzzlePromptBuilder
from ..models.schemas import PuzzleListOutput, PuzzleConfigListOutput
import random
from langchain_core.language_models import BaseChatModel

class PuzzleNode:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.structured_structure_llm = self.llm.with_structured_output(PuzzleListOutput, method="function_calling")
        self.structured_config_llm = self.llm.with_structured_output(PuzzleConfigListOutput, method="function_calling")
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
        
        result: PuzzleListOutput = self.structured_structure_llm.invoke([system_msg, human_msg])
        return [p.model_dump() for p in result.puzzles]
    
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
        
        result: PuzzleConfigListOutput = self.structured_config_llm.invoke([system_msg, human_msg])
        
        # Create a mapping of puzzle ID to config
        config_map = {}
        for config_item in result.configs:
            config_dict = config_item.model_dump()
            puzzle_id = config_dict.get("id")
            config_data = config_dict.get("config", {})
            if puzzle_id:
                config_map[puzzle_id] = config_data
        
            # --- FIX 1: FLATTEN GRID CARDS ---
            if "gridCards" in config_data:
                cards = config_data["gridCards"]
                if len(cards) > 0 and isinstance(cards[0], list):
                    print(f"Flattening 2D gridCards array from LLM for {puzzle_id}...")
                    flat_cards = []
                    for row in cards:
                        flat_cards.extend(row)
                    config_data["gridCards"] = flat_cards

            # --- FIX 2: FORCE CORRECT MATH FOR CARD RIDDLE CODE ---
            if "riddleRules" in config_data:
                rules = config_data["riddleRules"]
                rules.sort(key=lambda x: x.get("column", 0))
                config_data["correctCode"] = "".join(str(rule.get("count", 0)) for rule in rules)
                
                suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
                ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
                flat_cards = []
                
                for col in range(4):
                    if col < len(rules):
                        rule = rules[col]
                        target_suit = rule.get("suit", "Spades")
                        target_count = rule.get("count", 0)
                        
                        col_cards = [{"suit": target_suit, "rank": random.choice(ranks)} for _ in range(target_count)]
                        other_suits = [s for s in suits if s != target_suit]
                        while len(col_cards) < 4:
                            col_cards.append({"suit": random.choice(other_suits), "rank": random.choice(ranks)})
                        
                        random.shuffle(col_cards)
                        flat_cards.extend(col_cards)
                        
                config_data["gridCards"] = flat_cards

            # 2. PYTHON GENERATES ELEMENTAL LOCK MATH
            if "elementalMapping" in config_data:
                mapping = config_data["elementalMapping"]
                style = config_data.get("clueStyle", "cylinder")
                
                if style == "scales":
                    # For scales, don't sort — use AI's narrative sequence if provided
                    if "elementSequence" not in config_data:
                        elements = list(mapping.keys())
                        random.shuffle(elements)
                        config_data["elementSequence"] = elements
                else:  # cylinder style
                    # For cylinder, also respect AI's sequence if already provided
                    if "elementSequence" not in config_data:
                        elements = list(mapping.keys())
                        random.shuffle(elements)
                        config_data["elementSequence"] = elements

                config_data["correctCombination"] = "".join(str(mapping[el]) for el in config_data["elementSequence"])

            if puzzle_id:
                config_map[puzzle_id] = config_data
        
        # Merge configs into puzzles by matching IDs
        for puzzle in puzzles:
            puzzle_id = puzzle.get("id")
            if puzzle_id in config_map:
                puzzle["config"] = config_map[puzzle_id]
                p_type = puzzle.get("type", "")

                cfg = puzzle["config"]
                
                direct_hint = "Interact with the object to solve it."
                
                if p_type == "combination_lock":
                        style = cfg.get("clueStyle", "cylinder")
                        seq = cfg.get("elementSequence", [])
                        if style == "scales":
                            seq = cfg.get("elementSequence", [])
                            seq_str = ", ".join(seq)
                            direct_hint = f"Look at the scales. Count the iron weights on each pan. Enter the numbers in this order: {seq_str}."
                        else:
                            direct_hint = f"Read the story to find the element order: {', '.join(seq)}. Check the cylinder to see what number belongs to each element, then enter that code!"
                    
                elif p_type == "rotating_statue" and "correctRotationSteps" in cfg:
                    direct_hint = f"Look at the visual clue nearby. You must rotate this statue {cfg['correctRotationSteps']} times to align it properly."
                
                elif p_type == "pressure_plate" and "correctPattern" in cfg:
                    direct_hint = "Read the poem on the wall. It mentions the symbols in a specific order. You must step on the floor plates matching that exact story."
                
                elif p_type == "map_coordinates":
                    direct_hint = "Find the physical papyrus scroll map in the room. Pick it up to read the coordinates, then interact with the Bronze Astrolabe Globe to enter them."
                
                elif p_type in ["symbol_sequence", "hieroglyph_sequence"] and "correctSequence" in cfg:
                    direct_hint = f"Look for a grid of symbols. You must press these exact symbols in this order: {', '.join(cfg['correctSequence'])}."
                
                elif p_type == "card_deck_riddle" and "riddleRules" in cfg:
                    try:
                        rules = cfg["riddleRules"]
                        rules.sort(key=lambda x: x.get("column", 0))
                        hint_parts = [f"Col {r['column']+1}: Count {r['suit']}" for r in rules]
                        direct_hint = f"Look at the 4x4 card grid. To get the code, follow this rule: {', '.join(hint_parts)}. Then type those 4 numbers into the keypad!"
                    except Exception:
                        direct_hint = "Count the specific card suits in each column of the grid to get a 4-digit code."
                
                elif p_type == "light_puzzle":
                    direct_hint = "Interact with the tall standing mirrors. Left-click them while holding them to rotate the glass until the laser beam bounces into the target crystal."
                
                elif p_type == "hidden_compartment":
                    direct_hint = "This compartment is sealed tight. You must search the tomb until you find a physical Tomb Key to unlock it."
                    
                # Overwrite the vague AI hint with our direct, explicit answer
                puzzle["hint"] = direct_hint
                # --------------------------------------------
            else:
                print(f"⚠️ No config found for puzzle: {puzzle_id}")
                puzzle["config"] = {}
                
        return puzzles
            
    def _get_fallback_puzzles(self) -> List[Dict]:

        print(f"⚠️ FALLBACK PUZZLES !! ERRRROOOORRRRR")
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
