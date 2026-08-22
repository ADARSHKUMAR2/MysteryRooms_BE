from fastapi import HTTPException
from ..models.game_session import (
    GameSessionDocument, GameSession, StartSessionRequest, 
    UpdateSessionRequest, CompleteSessionRequest, GameStatus,
    PlayerProgress, PuzzleAttempt
)
from ..models.player_analytics import PlayerStatsDocument
from ..models.mystery import MysteryDocument
from datetime import datetime
import uuid
from typing import List
from backend.services.auth.models.user import User

class SessionController:
    """Controller for game session operations"""
    
    async def start_session(self, request: StartSessionRequest) -> GameSession:
        """Start a new game session"""
        
        # Verify mystery exists
        mystery = await MysteryDocument.find_one(
            MysteryDocument.mystery_id == request.mystery_id
        )
        if not mystery:
            raise HTTPException(status_code=404, detail="Mystery not found")
        
        # Create player progress objects
        players = []
        for player_id in request.player_ids:
            username = await self._get_username(player_id)
            players.append(
                PlayerProgress(
                    user_id=player_id,
                    username=username
                )
            )
        
        # Create session
        session = GameSession(
            session_id=str(uuid.uuid4()),
            mystery_id=request.mystery_id,
            room=mystery.room,
            status=GameStatus.IN_PROGRESS,
            players=players,
            max_players=request.max_players,
            time_limit_seconds=mystery.time_limit_seconds,
            started_at=datetime.utcnow()
        )
        
        # Save to database
        session_doc = GameSessionDocument(**session.model_dump())
        await session_doc.insert()
        
        print(f"✅ Game session {session.session_id} started")
        return session

    async def update_session(self, request: UpdateSessionRequest) -> GameSession:
        """Update session progress"""
        
        # Find session
        session = await GameSessionDocument.find_one(
            GameSessionDocument.session_id == request.session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update fields
        if request.puzzle_solved:
            if request.puzzle_solved not in session.puzzles_solved:
                session.puzzles_solved.append(request.puzzle_solved)
                
                # Update player progress
                if request.player_id:
                    for player in session.players:
                        if player.user_id == request.player_id:
                            player.puzzles_solved.append(request.puzzle_solved)
                            player.last_active = datetime.utcnow()
                
                # Record attempt
                session.puzzle_attempts.append(
                    PuzzleAttempt(
                        puzzle_id=request.puzzle_solved,
                        attempted_by=request.player_id or "unknown",
                        solved=True
                    )
                )
        
        if request.puzzle_attempted:
            # Record attempt
            session.puzzle_attempts.append(
                PuzzleAttempt(
                    puzzle_id=request.puzzle_attempted,
                    attempted_by=request.player_id or "unknown",
                    solved=False
                )
            )
        
        if request.hint_used and request.player_id:
            session.total_hints_used += 1
            for player in session.players:
                if player.user_id == request.player_id:
                    player.hints_used += 1
        
        if request.time_elapsed_seconds is not None:
            session.time_elapsed_seconds = request.time_elapsed_seconds
        
        session.updated_at = datetime.utcnow()
        
        # Save updates
        await session.save()
        
        return GameSession(**session.model_dump())
    
    async def complete_session(self, request: CompleteSessionRequest) -> GameSession:
        """Complete a game session"""
        
        # Find session
        session = await GameSessionDocument.find_one(
            GameSessionDocument.session_id == request.session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update status
        session.status = request.status
        session.completed_at = datetime.utcnow()
        session.difficulty_rating = request.difficulty_rating
        
        # Calculate completion time
        if session.started_at:
            session.completion_time_seconds = int(
                (session.completed_at - session.started_at).total_seconds()
            )
        
        session.updated_at = datetime.utcnow()
        await session.save()
        
        # Update player stats asynchronously
        await self._update_player_stats(session)
        
        print(f"✅ Game session {session.session_id} completed with status: {session.status}")
        return GameSession(**session.model_dump())
    
    async def get_session(self, session_id: str) -> GameSession:
        """Get a specific session"""
        session = await GameSessionDocument.find_one(
            GameSessionDocument.session_id == session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return GameSession(**session.model_dump())
    
    async def get_player_sessions(self, user_id: str, limit: int = 20) -> List[GameSession]:
        """Get sessions for a specific player"""
        sessions = await GameSessionDocument.find(
            {"players.user_id": user_id}
        ).sort("-created_at").limit(limit).to_list()
        
        return [GameSession(**s.model_dump()) for s in sessions]

    async def _get_username(self, user_id: str) -> str:
        """
        Fetch username from auth service or fallback to user_id prefix
        """
        try:
            # Query the users collection for the player's profile
            user_profile = await User.find_one(
                User.firebase_uid == user_id
            )
            
            if user_profile and user_profile.display_name:
                return user_profile.display_name
            elif user_profile and user_profile.email:
                # Fallback to email prefix if no display name
                return user_profile.email.split('@')[0]
                
            # Final fallback if user document isn't found
            return f"Player_{user_id[:8]}"
        
        except Exception as e:
            print(f"⚠️ Failed to fetch username for {user_id}: {e}")
            return f"Player_{user_id[:8]}"

    async def _update_player_stats(self, session: GameSessionDocument):
        """Update player statistics after game completion"""
        for player in session.players:
            # Update Detailed Analytics (player_stats collection)
            stats = await PlayerStatsDocument.find_one(
                PlayerStatsDocument.user_id == player.user_id
            )
            
            if not stats:
                stats = PlayerStatsDocument(
                    user_id=player.user_id,
                    username=player.username
                )
            
            # Update stats
            stats.total_games_played += 1
            if session.status == GameStatus.COMPLETED:
                stats.total_games_won += 1
            elif session.status == GameStatus.FAILED:
                stats.total_games_lost += 1
            
            stats.total_puzzles_solved += len(player.puzzles_solved)
            stats.total_puzzles_attempted += len(player.puzzles_attempted)
            stats.total_hints_used += player.hints_used
            
            if session.completion_time_seconds:
                stats.total_playtime_seconds += session.completion_time_seconds
            
            # Update rates
            if stats.total_games_played > 0:
                stats.win_rate = stats.total_games_won / stats.total_games_played
            
            if stats.total_puzzles_attempted > 0:
                stats.puzzle_success_rate = stats.total_puzzles_solved / stats.total_puzzles_attempted
            
            # Update fastest time
            if session.status == GameStatus.COMPLETED and session.completion_time_seconds:
                if not stats.fastest_escape_time_seconds or session.completion_time_seconds < stats.fastest_escape_time_seconds:
                    stats.fastest_escape_time_seconds = session.completion_time_seconds
            
            # Add mystery to history
            if session.mystery_id not in stats.mysteries_played:
                stats.mysteries_played.append(session.mystery_id)
            
            stats.last_played = datetime.utcnow()
            stats.updated_at = datetime.utcnow()
            
            await stats.save()
            print(f"📊 Updated detailed PlayerStats for {player.user_id}")

            # ---------------------------------------------------------
            # 2. Update Core User Profile (users collection)
            # ---------------------------------------------------------
            user = await User.find_one(User.firebase_uid == player.user_id)
            
            if user:
                user.games_played += 1
                
                if session.status == GameStatus.COMPLETED:
                    user.games_won += 1
                    user.coins += 50  # Reward for escaping
                    
                # Calculate simple score
                base_score = 1000
                time_penalty = session.completion_time_seconds or 0
                hint_penalty = session.total_hints_used * 50
                earned_score = max(10, base_score - time_penalty - hint_penalty)
                
                if session.status == GameStatus.COMPLETED:
                    user.total_score += earned_score
                
                user.last_login = datetime.utcnow()
                
                await user.save()
                print(f"✅ Updated core User profile for {user.display_name or user.email}")
            else:
                print(f"⚠️ Core User profile not found for {player.user_id}")

