from fastapi import HTTPException
from ..models.mystery import GenerateMysteryRequest, MysteryConfig, MysteryDocument
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

         # Save validated mystery to database
        try:
            mystery_doc = MysteryDocument(**mystery.model_dump())
            await mystery_doc.insert()
            print(f"✅ Mystery {mystery.mystery_id} saved to database")
        except Exception as e:
            print(f"⚠️  Failed to save mystery to database: {e}")
            # Don't fail the request if DB save fails
            # Could add retry logic here
        
        return mystery

    async def get_mystery(self, mystery_id: str) -> MysteryConfig:
        """Retrieve a mystery by ID"""
        mystery_doc = await MysteryDocument.find_one(
            MysteryDocument.mystery_id == mystery_id
        )
        
        if not mystery_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Mystery {mystery_id} not found"
            )
        
        return MysteryConfig(**mystery_doc.model_dump())
    
    async def list_mysteries(
        self, 
        room: str = None, 
        difficulty: int = None, 
        limit: int = 20
    ) -> list[MysteryConfig]:
        """List generated mysteries with optional filters"""
        query = {}
        
        if room:
            query["room"] = room
        if difficulty:
            query["difficulty"] = difficulty
        
        mysteries = await MysteryDocument.find(query).limit(limit).to_list()
        
        return [MysteryConfig(**m.model_dump()) for m in mysteries]