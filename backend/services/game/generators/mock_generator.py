import random
from typing import List
from ..models.mystery import MysteryConfig, PuzzleConfig, ClueConfig

class MockMysteryGenerator:
    """Generates pre-configured mystery templates for testing"""
    
    def generate(self, room: str, difficulty: int, player_count: int = 1) -> MysteryConfig:
        """Generate a mock mystery based on difficulty"""
        
        # Select template based on difficulty
        templates = {
            1: self._template_stolen_artifact_easy,
            2: self._template_archaeologist_disappearance,
            3: self._template_pharaoh_curse,
            4: self._template_false_tomb,
            5: self._template_hidden_chamber_expert,
        }
        
        template_func = templates.get(difficulty, self._template_pharaoh_curse)
        mystery = template_func(room)
        
        # Add some randomization to make each generation slightly different
        self._randomize_puzzle_parameters(mystery)
        
        return mystery
    
    def _template_stolen_artifact_easy(self, room: str) -> MysteryConfig:
        """Difficulty 1: Linear puzzle chain, beginner-friendly"""
        return MysteryConfig(
            room=room,
            difficulty=1,
            theme="stolen_artifact",
            objective="Recover the stolen Eye of Horus before the tomb seals",
            time_limit_seconds=900,  # 15 minutes
            puzzles=[
                PuzzleConfig(
                    id="entrance_statue",
                    type="rotating_statue",
                    position="entrance_hall",
                    config={"correctRotationSteps": 2},
                    dependencies=[],
                    unlocks=["final_door"],
                    hint="Face the rising sun"
                ),
                PuzzleConfig(
                    id="final_door",
                    type="combination_lock",
                    position="treasure_room",
                    config={"correctCombination": "382"},
                    dependencies=["entrance_statue"],
                    unlocks=["victory"],
                    hint="The numbers are carved on the statue's base"
                )
            ],
            clues=[
                ClueConfig(
                    id="wall_inscription",
                    type="inscription",
                    location="entrance_hall",
                    content="When Ra's light touches the guardian, the path reveals itself",
                    related_puzzle="entrance_statue"
                ),
                ClueConfig(
                    id="statue_carving",
                    type="visual",
                    location="entrance_hall",
                    content="Numbers carved on base: 3-8-2",
                    related_puzzle="final_door",
                    requires_puzzle_solved="entrance_statue"
                )
            ],
            twist=None
        )
    
    def _template_archaeologist_disappearance(self, room: str) -> MysteryConfig:
        """Difficulty 2: Branching paths, medium difficulty"""
        return MysteryConfig(
            room=room,
            difficulty=2,
            theme="missing_person",
            objective="Discover what happened to the missing archaeologist Dr. Hassan",
            time_limit_seconds=1200,  # 20 minutes
            puzzles=[
                PuzzleConfig(
                    id="diary_puzzle",
                    type="hidden_compartment",
                    position="antechamber",
                    config={"requiresKey": False},
                    dependencies=[],
                    unlocks=["west_statue", "east_statue"]
                ),
                PuzzleConfig(
                    id="west_statue",
                    type="rotating_statue",
                    position="west_chamber",
                    config={"correctRotationSteps": 1},
                    dependencies=["diary_puzzle"],
                    unlocks=["burial_chamber_door"]
                ),
                PuzzleConfig(
                    id="east_statue",
                    type="rotating_statue",
                    position="east_chamber",
                    config={"correctRotationSteps": 3},
                    dependencies=["diary_puzzle"],
                    unlocks=["burial_chamber_door"]
                ),
                PuzzleConfig(
                    id="burial_chamber_door",
                    type="symbol_sequence",
                    position="main_chamber",
                    config={"correctSequence": ["Ankh", "HorusFalcon", "WingedScarab"]},
                    dependencies=["west_statue", "east_statue"],
                    unlocks=["victory"]
                )
            ],
            clues=[
                ClueConfig(
                    id="diary_entry",
                    type="inscription",
                    location="antechamber",
                    content="Day 47: The twin guardians hold the secret. Both must face their destinies.",
                    related_puzzle="diary_puzzle"
                ),
                ClueConfig(
                    id="blood_trail",
                    type="environmental",
                    location="west_chamber",
                    content="A trail of dried blood leads to the burial chamber",
                    related_puzzle="burial_chamber_door",
                    requires_puzzle_solved="west_statue"
                )
            ],
            twist="the_archaeologist_was_cursed"
        )
    
    def _template_pharaoh_curse(self, room: str) -> MysteryConfig:
        """Difficulty 3: Multiple parallel puzzles, medium-hard"""
        return MysteryConfig(
            room=room,
            difficulty=3,
            theme="ancient_curse",
            objective="Break the Pharaoh's curse and escape the tomb alive",
            time_limit_seconds=1800,  # 30 minutes
            puzzles=[
                PuzzleConfig(
                    id="entrance_hieroglyphs",
                    type="hieroglyph_sequence",
                    position="entrance_hall",
                    config={"correctSequence": ["sun", "water", "bird"]},
                    dependencies=[],
                    unlocks=["torch_puzzle", "map_puzzle"]
                ),
                PuzzleConfig(
                    id="torch_puzzle",
                    type="light_puzzle",
                    position="main_chamber",
                    config={"correctTorchOrder": [1, 3, 2, 4]},
                    dependencies=["entrance_hieroglyphs"],
                    unlocks=["sarcophagus"]
                ),
                PuzzleConfig(
                    id="map_puzzle",
                    type="map_coordinates",
                    position="west_chamber",
                    config={"correctCoordinates": "N23-E45"},
                    dependencies=["entrance_hieroglyphs"],
                    unlocks=["sarcophagus"]
                ),
                PuzzleConfig(
                    id="sarcophagus",
                    type="combination_lock",
                    position="burial_chamber",
                    config={"correctCombination": "1352"},
                    dependencies=["torch_puzzle", "map_puzzle"],
                    unlocks=["curse_tablet"]
                ),
                PuzzleConfig(
                    id="curse_tablet",
                    type="symbol_sequence",
                    position="burial_chamber",
                    config={"correctSequence": ["EyeOfHorus", "Ankh", "GoldenFeather", "ScalesOfJustice"]},
                    dependencies=["sarcophagus"],
                    unlocks=["victory"]
                )
            ],
            clues=[
                ClueConfig(
                    id="entrance_warning",
                    type="inscription",
                    location="entrance_hall",
                    content="He who disturbs the Pharaoh's rest shall face eternal darkness",
                    related_puzzle="entrance_hieroglyphs"
                ),
                ClueConfig(
                    id="torch_hint",
                    type="visual",
                    location="main_chamber",
                    content="Shadows cast by torches form numbers on the wall",
                    related_puzzle="torch_puzzle",
                    requires_puzzle_solved="entrance_hieroglyphs"
                ),
                ClueConfig(
                    id="map_fragment",
                    type="visual",
                    location="west_chamber",
                    content="Ancient map fragment showing coordinates",
                    related_puzzle="map_puzzle",
                    requires_puzzle_solved="entrance_hieroglyphs"
                )
            ],
            twist="breaking_the_curse_requires_sacrifice"
        )
    
    def _template_false_tomb(self, room: str) -> MysteryConfig:
        """Difficulty 4: Includes fake clues and misdirection"""
        return MysteryConfig(
            room=room,
            difficulty=4,
            theme="deception",
            objective="Navigate the false tomb and find the real treasure chamber",
            time_limit_seconds=2100,  # 35 minutes
            puzzles=[
                PuzzleConfig(
                    id="false_entrance",
                    type="rotating_statue",
                    position="entrance_hall",
                    config={"correctRotationSteps": 0},  # Don't rotate!
                    dependencies=[],
                    unlocks=["pressure_plates"]
                ),
                PuzzleConfig(
                    id="pressure_plates",
                    type="pressure_plate",
                    position="antechamber",
                    config={"correctPattern": [1, 4, 2, 3]},
                    dependencies=["false_entrance"],
                    unlocks=["hieroglyph_wall", "false_door"]
                ),
                PuzzleConfig(
                    id="false_door",
                    type="combination_lock",
                    position="west_chamber",
                    config={"correctCombination": "999"},  # Trap door
                    dependencies=["pressure_plates"],
                    unlocks=[]  # Dead end!
                ),
                PuzzleConfig(
                    id="hieroglyph_wall",
                    type="hieroglyph_sequence",
                    position="east_chamber",
                    config={"correctSequence": ["cobra", "sun", "ankh", "eye"]},
                    dependencies=["pressure_plates"],
                    unlocks=["secret_passage"]
                ),
                PuzzleConfig(
                    id="secret_passage",
                    type="hidden_compartment",
                    position="secret_passage",
                    config={"requiresKey": True},
                    dependencies=["hieroglyph_wall"],
                    unlocks=["final_chamber"]
                ),
                PuzzleConfig(
                    id="final_chamber",
                    type="symbol_sequence",
                    position="treasure_room",
                    config={"correctSequence": ["AncientScroll", "HieroglyphTablet", "ScalesOfJustice"]},
                    dependencies=["secret_passage"],
                    unlocks=["victory"]
                )
            ],
            clues=[
                ClueConfig(
                    id="fake_inscription",
                    type="inscription",
                    location="entrance_hall",
                    content="Turn the guardian to face the west for passage",
                    related_puzzle="false_entrance"  # Misleading!
                ),
                ClueConfig(
                    id="real_hint",
                    type="inscription",
                    location="antechamber",
                    content="The guardian who does not move guards the truth",
                    related_puzzle="false_entrance"
                ),
                ClueConfig(
                    id="false_map",
                    type="visual",
                    location="west_chamber",
                    content="Map pointing to the west chamber as treasure location",
                    related_puzzle="false_door"  # Trap!
                ),
                ClueConfig(
                    id="secret_key_location",
                    type="environmental",
                    location="east_chamber",
                    content="A hidden key behind the hieroglyph wall",
                    related_puzzle="secret_passage",
                    requires_puzzle_solved="hieroglyph_wall"
                )
            ],
            twist="the_first_treasure_is_fake"
        )
    
    def _template_hidden_chamber_expert(self, room: str) -> MysteryConfig:
        """Difficulty 5: Complex dependencies, expert level"""
        return MysteryConfig(
            room=room,
            difficulty=5,
            theme="legendary_treasure",
            objective="Unlock the legendary hidden chamber of Pharaoh Khufu",
            time_limit_seconds=2400,  # 40 minutes
            puzzles=[
                PuzzleConfig(
                    id="entrance_riddle",
                    type="hieroglyph_sequence",
                    position="entrance_hall",
                    config={"correctSequence": ["morning", "noon", "evening", "night"]},
                    dependencies=[],
                    unlocks=["north_statue", "south_statue"]
                ),
                PuzzleConfig(
                    id="north_statue",
                    type="rotating_statue",
                    position="main_chamber",
                    config={"correctRotationSteps": 1},
                    dependencies=["entrance_riddle"],
                    unlocks=["light_beam_puzzle"]
                ),
                PuzzleConfig(
                    id="south_statue",
                    type="rotating_statue",
                    position="main_chamber",
                    config={"correctRotationSteps": 3},
                    dependencies=["entrance_riddle"],
                    unlocks=["light_beam_puzzle"]
                ),
                PuzzleConfig(
                    id="light_beam_puzzle",
                    type="light_puzzle",
                    position="main_chamber",
                    config={"requiresAlignment": True},
                    dependencies=["north_statue", "south_statue"],
                    unlocks=["map_room", "scroll_room"]
                ),
                PuzzleConfig(
                    id="map_room",
                    type="map_coordinates",
                    position="west_chamber",
                    config={"correctCoordinates": "29.9792-N, 31.1342-E"},
                    dependencies=["light_beam_puzzle"],
                    unlocks=["master_lock"]
                ),
                PuzzleConfig(
                    id="scroll_room",
                    type="symbol_sequence",
                    position="east_chamber",
                    config={"correctSequence": ["Ankh", "AnubisStanding", "SunDisk", "AncientScroll"]},
                    dependencies=["light_beam_puzzle"],
                    unlocks=["master_lock"]
                ),
                PuzzleConfig(
                    id="master_lock",
                    type="combination_lock",
                    position="secret_passage",
                    config={"correctCombination": "29311342"},  # Coordinates combined
                    dependencies=["map_room", "scroll_room"],
                    unlocks=["final_seal"]
                ),
                PuzzleConfig(
                    id="final_seal",
                    type="pressure_plate",
                    position="treasure_room",
                    config={"correctPattern": [2, 4, 1, 3, 5]},
                    dependencies=["master_lock"],
                    unlocks=["victory"]
                )
            ],
            clues=[
                ClueConfig(
                    id="sphinx_riddle",
                    type="inscription",
                    location="entrance_hall",
                    content="What walks on four legs at dawn, two at noon, and three at dusk?",
                    related_puzzle="entrance_riddle"
                ),
                ClueConfig(
                    id="alignment_hint",
                    type="visual",
                    location="main_chamber",
                    content="When both guardians face their true north, light reveals the way",
                    related_puzzle="light_beam_puzzle",
                    requires_puzzle_solved="entrance_riddle"
                ),
                ClueConfig(
                    id="pyramid_coordinates",
                    type="inscription",
                    location="west_chamber",
                    content="The Great Pyramid's exact location holds the key",
                    related_puzzle="map_room",
                    requires_puzzle_solved="light_beam_puzzle"
                ),
                ClueConfig(
                    id="cycle_of_life",
                    type="inscription",
                    location="east_chamber",
                    content="The eternal cycle: birth, death, resurrection, infinity",
                    related_puzzle="scroll_room",
                    requires_puzzle_solved="light_beam_puzzle"
                ),
                ClueConfig(
                    id="master_lock_hint",
                    type="visual",
                    location="secret_passage",
                    content="The coordinates speak as one voice",
                    related_puzzle="master_lock",
                    requires_puzzle_solved="map_room"
                )
            ],
            twist="the_chamber_contains_a_portal_to_another_tomb"
        )
    
    def _randomize_puzzle_parameters(self, mystery: MysteryConfig) -> None:
        """Add slight randomization to puzzle parameters"""
        for puzzle in mystery.puzzles:
            if puzzle.type == "rotating_statue":
                # Randomize rotation steps (0-3)
                puzzle.config["correctRotationSteps"] = random.randint(0, 3)
            elif puzzle.type == "combination_lock":
                # Keep structure but could randomize digits
                pass  # Keep as-is for now
            elif puzzle.type in ["symbol_sequence", "hieroglyph_sequence"]:
                # Could shuffle sequence order, but keep deterministic for testing
                pass
