from fastapi import HTTPException
from ..models.mystery import GenerateMysteryRequest, MysteryConfig, MysteryDocument
# from ..generators.mock_generator import MockMysteryGenerator
from ..generators.ai_generator import AIGenerator
from ..validators.mystery_validator import MysteryValidator
from rich import print

class GameController:
    """Controller for game-related operations"""
    
    def __init__(self):
        # self.generator = MockMysteryGenerator()
        self.generator = AIGenerator()
        self.validator = MysteryValidator()
    
    async def generate_mystery(self, request: GenerateMysteryRequest) -> MysteryConfig:
        """Generate a new mystery configuration"""
        
        # Generate mystery
        mystery = self.generator.generate(
            room=request.room,
            difficulty=request.difficulty,
            player_count=request.player_count or 1
        )

        print(f"\n[BACKEND] 🎲 Received Request: Room='{request.room}', Diff={request.difficulty}, Players={request.player_count}")
        
        
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
        
        print(f"[BACKEND] 📤 Sending Payload to Unity:\n{mystery.model_dump_json(indent=2)}\n")
        
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

    async def get_mystery_by_share_code(self, share_code: str) -> MysteryConfig:
        """Retrieve a mystery using its 6-character share code"""
        # Ensure it's uppercase for consistent searching
        code = share_code.upper()
        
        mystery_doc = await MysteryDocument.find_one(
            MysteryDocument.share_code == code
        )
        
        if not mystery_doc:
            raise HTTPException(
                status_code=404,
                detail=f"No mystery found with share code {code}"
            )
        
        return MysteryConfig(**mystery_doc.model_dump())