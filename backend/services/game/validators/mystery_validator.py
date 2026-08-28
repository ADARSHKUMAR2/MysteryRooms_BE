from typing import List, Set, Dict
from ..models.mystery import MysteryConfig, PuzzleConfig, ValidationResult

class MysteryValidator:
    """Validates that a generated mystery is solvable and properly configured"""
    
    # Valid puzzle types that Unity supports
    VALID_PUZZLE_TYPES = {
        "rotating_statue",
        "symbol_sequence",
        "hieroglyph_sequence",
        "combination_lock",
        "hidden_compartment",
        "map_coordinates",
        "pressure_plate",
        "light_puzzle",
        "card_deck_riddle",
        "final_lock"
    }
    
    # Valid room locations
    VALID_ROOM_LOCATIONS = {
        "mummy_tomb": {
            "entrance_hall",
            "main_chamber",
            "west_chamber",
            "east_chamber",
            "secret_passage",
            "burial_chamber",
            "treasure_room",
            "antechamber"
        }
    }
    
    def validate(self, mystery: MysteryConfig) -> ValidationResult:
        """Main validation method"""
        errors: List[str] = []
        warnings: List[str] = []
        
        # Run all validation checks
        errors.extend(self._validate_puzzle_types(mystery))
        errors.extend(self._validate_puzzle_dependencies(mystery))
        errors.extend(self._validate_room_locations(mystery))
        errors.extend(self._validate_solution_path(mystery))
        
        warnings.extend(self._validate_difficulty(mystery))
        warnings.extend(self._validate_time_limit(mystery))
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_puzzle_types(self, mystery: MysteryConfig) -> List[str]:
        """Check that all puzzle types are valid"""
        errors = []
        for puzzle in mystery.puzzles:
            if puzzle.type not in self.VALID_PUZZLE_TYPES:
                errors.append(f"Invalid puzzle type '{puzzle.type}' in puzzle '{puzzle.id}'")
        return errors
    
    def _validate_puzzle_dependencies(self, mystery: MysteryConfig) -> List[str]:
        """Check for circular dependencies and ensure all dependencies exist"""
        errors = []
        
        # Build puzzle ID set
        puzzle_ids = {p.id for p in mystery.puzzles}
        
        # Check dependencies exist
        for puzzle in mystery.puzzles:
            for dep in puzzle.dependencies:
                if dep not in puzzle_ids:
                    errors.append(f"Puzzle '{puzzle.id}' depends on non-existent puzzle '{dep}'")
        
        # Check for circular dependencies using DFS
        if self._has_circular_dependencies(mystery.puzzles):
            errors.append("Circular dependency detected in puzzle chain")
        
        return errors
    
    def _has_circular_dependencies(self, puzzles: List[PuzzleConfig]) -> bool:
        """Detect circular dependencies using DFS"""
        graph = {p.id: p.dependencies for p in puzzles}
        visited = set()
        rec_stack = set()
        
        def visit(node: str) -> bool:
            if node in rec_stack:
                return True  # Circular dependency found
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if visit(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for puzzle_id in graph:
            if visit(puzzle_id):
                return True
        
        return False
    
    def _validate_room_locations(self, mystery: MysteryConfig) -> List[str]:
        """Check that all puzzle positions are valid for the room"""
        errors = []
        valid_locations = self.VALID_ROOM_LOCATIONS.get(mystery.room, set())
        
        if not valid_locations:
            errors.append(f"Unknown room type '{mystery.room}'")
            return errors
        
        for puzzle in mystery.puzzles:
            if puzzle.position not in valid_locations:
                errors.append(
                    f"Invalid position '{puzzle.position}' for puzzle '{puzzle.id}' "
                    f"in room '{mystery.room}'"
                )
        
        return errors
    
    def _validate_solution_path(self, mystery: MysteryConfig) -> List[str]:
        """Ensure there's at least one valid solution path"""
        errors = []
        
        if not mystery.puzzles:
            errors.append("Mystery has no puzzles")
            return errors
        
        # Check that there's at least one puzzle with no dependencies (starting point)
        starting_puzzles = [p for p in mystery.puzzles if not p.dependencies]
        if not starting_puzzles:
            errors.append("No starting puzzle found (all puzzles have dependencies)")
        
        # Check that there's at least one puzzle that unlocks something (ending)
        ending_puzzles = [p for p in mystery.puzzles if p.unlocks]
        if not ending_puzzles:
            errors.append("No ending puzzle found (no puzzle unlocks anything)")
        
        return errors
    
    def _validate_difficulty(self, mystery: MysteryConfig) -> List[str]:
        """Check if puzzle count matches difficulty level"""
        warnings = []
        puzzle_count = len(mystery.puzzles)
        
        # Expected puzzle counts by difficulty
        expected_ranges = {
            1: (1, 3),   # Easy: 1-3 puzzles
            2: (2, 4),   # Medium-Easy: 2-4 puzzles
            3: (3, 5),   # Medium: 3-5 puzzles
            4: (4, 6),   # Medium-Hard: 4-6 puzzles
            5: (5, 8),   # Hard: 5-8 puzzles
        }
        
        min_puzzles, max_puzzles = expected_ranges.get(mystery.difficulty, (1, 10))
        
        if puzzle_count < min_puzzles:
            warnings.append(
                f"Difficulty {mystery.difficulty} typically has {min_puzzles}-{max_puzzles} puzzles, "
                f"but only {puzzle_count} provided"
            )
        elif puzzle_count > max_puzzles:
            warnings.append(
                f"Difficulty {mystery.difficulty} typically has {min_puzzles}-{max_puzzles} puzzles, "
                f"but {puzzle_count} provided"
            )
        
        return warnings
    
    def _validate_time_limit(self, mystery: MysteryConfig) -> List[str]:
        """Check if time limit is reasonable for puzzle count"""
        warnings = []
        puzzle_count = len(mystery.puzzles)
        
        # Estimate: ~5-10 minutes per puzzle on average
        min_time = puzzle_count * 300  # 5 min per puzzle
        max_time = puzzle_count * 600  # 10 min per puzzle
        
        if mystery.time_limit_seconds < min_time:
            warnings.append(
                f"Time limit ({mystery.time_limit_seconds}s) may be too short for {puzzle_count} puzzles. "
                f"Consider at least {min_time}s"
            )
        elif mystery.time_limit_seconds > max_time * 2:
            warnings.append(
                f"Time limit ({mystery.time_limit_seconds}s) may be too generous for {puzzle_count} puzzles"
            )
        
        return warnings
