from backend.shared.database import get_database

from ..models.mystery import MysteryDocument
from ..models.game_session import GameSessionDocument
from ..models.player_analytics import PlayerStatsDocument

async def init_game_db():
    """
    Initialize the database with Game-specific models.
    """
    # Add all game-related Beanie documents here
    models = [
        MysteryDocument,
        GameSessionDocument,
        PlayerStatsDocument,
    ]
    await get_database(models)
