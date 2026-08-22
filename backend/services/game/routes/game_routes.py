from fastapi import APIRouter, HTTPException
from ..controllers.game_controller import GameController
from ..models.mystery import GenerateMysteryRequest, MysteryConfig

router = APIRouter()
game_controller = GameController()

@router.post("/generate", response_model=MysteryConfig)
async def generate_mystery(request: GenerateMysteryRequest):
    """
    Generate a new mystery configuration
    
    - **room**: Room type (default: mummy_tomb)
    - **difficulty**: Difficulty level 1-5 (default: 3)
    - **player_count**: Number of players 1-4 (default: 1)
    
    Returns a complete mystery configuration with puzzles, clues, and validation.
    """
    try:
        mystery = await game_controller.generate_mystery(request)
        return mystery
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mystery generation failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "game"}
