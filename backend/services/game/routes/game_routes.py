from fastapi import APIRouter, HTTPException, Query
from ..controllers.game_controller import GameController
from ..models.mystery import GenerateMysteryRequest, MysteryConfig

router = APIRouter(prefix="/game", tags=["Mystery"])

game_controller = GameController()

@router.post("/generate", response_model=MysteryConfig)
async def generate_mystery(request: GenerateMysteryRequest):
    """
    Generate a new mystery configuration
    
    - **room**: Room type (default: mummy_tomb)
    - **difficulty**: Difficulty level 1-5 (default: 3)
    - **player_count**: Number of players 1-8 (default: 1)
    
    Returns a complete mystery configuration with puzzles, clues, and validation.
    """
    try:
        mystery = await game_controller.generate_mystery(request)
        return mystery
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mystery generation failed: {str(e)}")

@router.get("/mysteries/{mystery_id}", response_model=MysteryConfig)
async def get_mystery(mystery_id: str):
    """
    Retrieve a specific mystery by ID
    
    - **mystery_id**: The mystery UUID
    """
    return await game_controller.get_mystery(mystery_id)

@router.get("/mysteries", response_model=list[MysteryConfig])
async def list_mysteries(
    room: str = Query(None, description="Filter by room type"),
    difficulty: int = Query(None, ge=1, le=5, description="Filter by difficulty"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    List generated mysteries with optional filters
    
    - **room**: Optional room filter
    - **difficulty**: Optional difficulty filter (1-5)
    - **limit**: Maximum results (default: 20, max: 100)
    """
    return await game_controller.list_mysteries(room, difficulty, limit)

@router.get("/mysteries/shared/{share_code}", response_model=MysteryConfig)
async def get_mystery_by_code(share_code: str):
    """Get an existing mystery by its share code"""
    return await game_controller.get_mystery_by_share_code(share_code)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "game"}
