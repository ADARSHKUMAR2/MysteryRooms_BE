"""
Victory Message Generator

This module generates dynamic victory messages for the winning screen.
Messages are customized based on:
- Mystery theme (ancient_curse, stolen_artifact, etc.)
- Difficulty level (1-5)
- Player performance (time, hints used)
- Number of players (solo vs multiplayer)
"""

from typing import Dict, List
import random


class VictoryMessageGenerator:
    """Generates contextual victory messages for completed mysteries"""
    
    # Theme-based victory messages
    THEME_MESSAGES: Dict[str, List[str]] = {
        "ancient_curse": [
            "The ancient curse has been lifted! You've escaped the tomb with your lives!",
            "You've broken the Pharaoh's curse and emerged victorious!",
            "The spirits are at peace. The tomb releases you from its grasp!",
            "Against all odds, you've survived the cursed tomb and claimed your freedom!"
        ],
        "stolen_artifact": [
            "Mission accomplished! You've recovered the stolen artifact!",
            "The artifact is secure! You've completed your mission!",
            "Victory! The precious relic has been returned to its rightful place!",
            "You've outsmarted the thieves and recovered the treasure!"
        ],
        "missing_person": [
            "Mystery solved! You've uncovered the truth and escaped!",
            "The missing archaeologist's fate is revealed. You've made it out alive!",
            "You've solved the disappearance and lived to tell the tale!",
            "The mystery is no more. You've found the answers and your way out!"
        ],
        "deception": [
            "You've seen through the deception and found the truth!",
            "The false tomb couldn't fool you! You've found the real treasure chamber!",
            "Illusions shattered! You've navigated the maze of lies and emerged victorious!",
            "You've outwitted the ancient deceivers and claimed your prize!"
        ],
        "legendary_treasure": [
            "Legendary! You've unlocked the hidden chamber of Pharaoh Khufu!",
            "The legendary treasure is yours! An epic victory!",
            "History will remember your name! You've found the impossible treasure!",
            "You've achieved what few dared to dream! The legendary chamber is yours!"
        ],
        "default": [
            "Congratulations! You've successfully escaped the mystery room!",
            "Victory! You've solved the mystery and made your escape!",
            "Well done! You've conquered the challenge!",
            "Success! You've outsmarted every puzzle and emerged victorious!"
        ]
    }
    
    # Performance-based suffixes
    PERFORMANCE_SUFFIXES: Dict[str, List[str]] = {
        "perfect": [  # No hints, fast completion
            "A flawless performance!",
            "Absolutely perfect execution!",
            "Master detective work!",
            "Legendary problem-solving!"
        ],
        "excellent": [  # Few hints, good time
            "Excellent work!",
            "Outstanding detective skills!",
            "Impressive problem-solving!",
            "Remarkable performance!"
        ],
        "good": [  # Some hints, decent time
            "Well done!",
            "Good teamwork!",
            "Solid performance!",
            "Nice work!"
        ],
        "completed": [  # Many hints or slow time
            "Mission accomplished!",
            "You made it out!",
            "Victory achieved!",
            "Challenge completed!"
        ]
    }
    
    # Rank titles based on performance
    RANK_TITLES: Dict[str, str] = {
        "perfect": "Master Detective",
        "excellent": "Expert Investigator",
        "good": "Skilled Adventurer",
        "completed": "Mystery Solver"
    }
    
    @staticmethod
    def generate_victory_message(
        theme: str,
        difficulty: int,
        completion_time_seconds: int,
        time_limit_seconds: int,
        hints_used: int,
        player_count: int = 1
    ) -> str:
        """
        Generate a contextual victory message
        
        Args:
            theme: Mystery theme (ancient_curse, stolen_artifact, etc.)
            difficulty: Difficulty level 1-5
            completion_time_seconds: Time taken to complete
            time_limit_seconds: Maximum allowed time
            hints_used: Number of hints used
            player_count: Number of players
            
        Returns:
            Complete victory message with performance suffix
        """
        # Get base message for theme
        theme_messages = VictoryMessageGenerator.THEME_MESSAGES.get(
            theme, 
            VictoryMessageGenerator.THEME_MESSAGES["default"]
        )
        base_message = random.choice(theme_messages)
        
        # Determine performance level
        performance = VictoryMessageGenerator._calculate_performance(
            completion_time_seconds,
            time_limit_seconds,
            hints_used,
            difficulty
        )
        
        # Get performance suffix
        suffix_list = VictoryMessageGenerator.PERFORMANCE_SUFFIXES[performance]
        suffix = random.choice(suffix_list)
        
        # Combine message
        full_message = f"{base_message} {suffix}"
        
        return full_message
    
    @staticmethod
    def _calculate_performance(
        completion_time: int,
        time_limit: int,
        hints_used: int,
        difficulty: int
    ) -> str:
        """
        Calculate performance tier based on multiple factors
        
        Returns: "perfect", "excellent", "good", or "completed"
        """
        time_ratio = completion_time / time_limit if time_limit > 0 else 1.0
        
        # Perfect: No hints, completed in < 60% of time
        if hints_used == 0 and time_ratio < 0.6:
            return "perfect"
        
        # Excellent: 0-1 hints, completed in < 75% of time
        if hints_used <= 1 and time_ratio < 0.75:
            return "excellent"
        
        # Good: 0-2 hints, completed in < 90% of time
        if hints_used <= 2 and time_ratio < 0.9:
            return "good"
        
        # Default: completed
        return "completed"
    
    @staticmethod
    def get_rank_title(
        completion_time: int,
        time_limit: int,
        hints_used: int,
        difficulty: int
    ) -> str:
        """
        Get rank title based on performance
        
        Returns: Rank title string (e.g., "Master Detective")
        """
        performance = VictoryMessageGenerator._calculate_performance(
            completion_time,
            time_limit,
            hints_used,
            difficulty
        )
        return VictoryMessageGenerator.RANK_TITLES[performance]
    
    @staticmethod
    def generate_multiplayer_message(player_count: int, top_contributor: str) -> str:
        """
        Generate additional message for multiplayer games
        
        Args:
            player_count: Number of players
            top_contributor: Username of top contributor
            
        Returns:
            Multiplayer-specific message
        """
        if player_count == 1:
            return "Solo victory! You conquered the mystery alone!"
        elif player_count == 2:
            return f"Dynamic duo! Great teamwork by both players!"
        else:
            return f"Team victory! {player_count} minds solved the mystery together!"
