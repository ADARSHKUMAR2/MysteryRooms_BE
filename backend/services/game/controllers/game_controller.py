from fastapi import HTTPException
from ..models.mystery import GenerateMysteryRequest, MysteryConfig
from ..generators.mock_generator import MockMysteryGenerator
from ..validators.mystery_validator import MysteryValidator

class GameController:
    """Controller for game-related operations"""
    
    def __init__(self):
        self.generator = MockMysteryGenerator()
        self.validator = MysteryValidator()
    
    async def generate_mystery(self, request: GenerateMysteryRequest) -> MysteryConfig:
        """Generate a new mystery configuration"""
        
        # Generate mystery
        mystery = self.generator.generate(
            room=request.room,
            difficulty=request.difficulty,
            player_count=request.player_count or 1
        )
        
        # Validate mystery
        validation_result = self.validator.validate(mystery)
        
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Generated mystery failed validation",
                    "errors": validation_result.errors
                }
            )
        
        # Log warnings if any
        if validation_result.warnings:
            print(f"⚠️  Mystery validation warnings: {validation_result.warnings}")
        
        return mystery
