"""Prompt templates for AI mystery generation"""

from .story_prompts import StoryPromptBuilder
from .puzzle_prompts import PuzzlePromptBuilder
from .clue_prompts import CluePromptBuilder

__all__ = [
    "StoryPromptBuilder",
    "PuzzlePromptBuilder", 
    "CluePromptBuilder"
]
