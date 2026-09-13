from fastapi import HTTPException
from ..models.game_session import (
    GameSessionDocument, GameSession, StartSessionRequest, 
    UpdateSessionRequest, CompleteSessionRequest, GameStatus,
    PlayerProgress, PuzzleAttempt,
    WinningScreenData, ScoreBreakdown, RewardsData, 
    PlayerPerformance, SessionStatistics, MysteryInfo
)
from ..models.player_analytics import PlayerStatsDocument
from ..models.mystery import MysteryDocument
from datetime import datetime
import uuid
from typing import List
from backend.services.auth.models.user import User
from ..utils.victory_messages import VictoryMessageGenerator

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

                # ✨ NEW: Check if this puzzle triggers victory
                is_victory = await self._check_victory_condition(session, request.puzzle_solved)
                
                if is_victory:
                    # Auto-complete the session
                    print(f"🎉 Victory condition met for session {session.session_id}!")
                    session.status = GameStatus.COMPLETED
                    session.completed_at = datetime.utcnow()
                    
                    # Calculate completion time
                    if session.started_at:
                        session.completion_time_seconds = int(
                            (session.completed_at - session.started_at).total_seconds()
                        )
                    
                    # Update player stats
                    await self._update_player_stats(session)
        
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

    async def join_session(self, session_id: str, request: dict) -> GameSession:
        """Join an existing game session"""
        player_id = request.get("player_id")
        if not player_id:
            raise HTTPException(status_code=400, detail="player_id is required")

        session = await GameSessionDocument.find_one(
            GameSessionDocument.session_id == session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if already joined
        for player in session.players:
            if player.user_id == player_id:
                return GameSession(**session.model_dump())  # Already joined

        if len(session.players) >= session.max_players:
            raise HTTPException(status_code=400, detail="Session is full")

        # Fetch their username from the auth service profile
        username = await self._get_username(player_id)
        
        session.players.append(
            PlayerProgress(
                user_id=player_id,
                username=username
            )
        )
        session.updated_at = datetime.utcnow()
        await session.save()

        print(f"✅ Player {player_id} joined session {session_id}")
        return GameSession(**session.model_dump())


    async def _get_username(self, user_id: str) -> str:
        """
        Fetch username from auth service or fallback to user_id prefix
        """
        try:
            # Query the users collection for the player's profile
            user_profile = await User.find_one(
                {
                    "firebase_uid": user_id
                }
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

    async def _check_victory_condition(self, session: GameSessionDocument, puzzle_id: str) -> bool:
        """
        Check if solving this puzzle triggers victory
        
        Args:
            session: The game session
            puzzle_id: ID of the puzzle just solved
            
        Returns:
            True if this puzzle unlocks victory
        """
        # Get the mystery to check puzzle configuration
        mystery = await MysteryDocument.find_one(
            MysteryDocument.mystery_id == session.mystery_id
        )
        
        if not mystery:
            return False
        
        # Find the puzzle and check if it unlocks victory
        for puzzle in mystery.puzzles:
            if puzzle.id == puzzle_id:
                if "victory" in puzzle.unlocks:
                    return True
        
        return False
    
    async def get_victory_data(self, session_id: str) -> WinningScreenData:
        """
        Generate complete winning screen data for a completed session
        
        Args:
            session_id: The session ID
            
        Returns:
            Complete WinningScreenData with all statistics and rewards
            
        Raises:
            HTTPException: If session not found or not completed
        """
        # Find session
        session = await GameSessionDocument.find_one(
            GameSessionDocument.session_id == session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify session is completed
        if session.status != GameStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Session is not completed. Current status: {session.status}"
            )
        
        # Get mystery information
        mystery = await MysteryDocument.find_one(
            MysteryDocument.mystery_id == session.mystery_id
        )
        if not mystery:
            raise HTTPException(status_code=404, detail="Mystery not found")
        
        # Calculate statistics
        completion_time = session.completion_time_seconds or 0
        time_remaining = max(0, session.time_limit_seconds - completion_time)
        
        # Format completion time as MM:SS
        minutes = completion_time // 60
        seconds = completion_time % 60
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        
        # Calculate success rate
        total_attempts = len(session.puzzle_attempts)
        successful_attempts = len([a for a in session.puzzle_attempts if a.solved])
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 100.0
        
        # Generate victory messages
        primary_message = VictoryMessageGenerator.generate_victory_message(
            theme=mystery.theme,
            difficulty=mystery.difficulty,
            completion_time_seconds=completion_time,
            time_limit_seconds=session.time_limit_seconds,
            hints_used=session.total_hints_used,
            player_count=len(session.players)
        )
        
        secondary_message = VictoryMessageGenerator.generate_multiplayer_message(
            player_count=len(session.players),
            top_contributor=session.players[0].username if session.players else "Unknown"
        )
        
        rank_title = VictoryMessageGenerator.get_rank_title(
            completion_time=completion_time,
            time_limit=session.time_limit_seconds,
            hints_used=session.total_hints_used,
            difficulty=mystery.difficulty
        )
        
        # Calculate score breakdown
        base_score = 1000
        
        # Time bonus: more time remaining = higher bonus
        time_bonus = int(time_remaining * 0.5)  # 0.5 points per second remaining
        
        # Difficulty multiplier
        difficulty_multiplier = 1.0 + (mystery.difficulty - 1) * 0.25  # 1.0 to 2.0
        
        # Hint penalty
        hint_penalty = session.total_hints_used * 50
        
        # Team bonus for multiplayer
        team_bonus = 100 * (len(session.players) - 1) if len(session.players) > 1 else 0
        
        # Calculate final score
        score_before_multiplier = base_score + time_bonus - hint_penalty + team_bonus
        final_score = int(score_before_multiplier * difficulty_multiplier)
        
        score_breakdown = ScoreBreakdown(
            base_score=base_score,
            time_bonus=time_bonus,
            difficulty_multiplier=difficulty_multiplier,
            hint_penalty=-hint_penalty,
            team_bonus=team_bonus,
            final_score=final_score
        )
        
        # Calculate rewards
        coins_earned = 50  # Base reward
        if session.total_hints_used == 0:
            coins_earned += 25  # Bonus for no hints
        if completion_time < session.time_limit_seconds * 0.6:
            coins_earned += 30  # Speed bonus
        
        xp_earned = final_score // 10  # XP based on score
        
        # Detect achievements
        achievements = []
        if session.total_hints_used == 0:
            achievements.append("No Hints Master")
        if completion_time < session.time_limit_seconds * 0.5:
            achievements.append("Speed Demon")
        if len(session.players) >= 3:
            achievements.append("Team Player")
        
        rewards = RewardsData(
            coins_earned=coins_earned,
            xp_earned=xp_earned,
            achievements=achievements,
            badges=[]
        )
        
        # Generate player performances
        player_performances = []
        total_puzzles_solved = sum(len(p.puzzles_solved) for p in session.players)
        
        for player in session.players:
            contribution = (len(player.puzzles_solved) / total_puzzles_solved * 100) if total_puzzles_solved > 0 else 0
            
            player_perf = PlayerPerformance(
                user_id=player.user_id,
                username=player.username,
                puzzles_solved=len(player.puzzles_solved),
                puzzles_attempted=len(player.puzzles_attempted),
                hints_used=player.hints_used,
                contribution_percentage=round(contribution, 1),
                mvp=False  # Will set MVP below
            )
            player_performances.append(player_perf)
        
        # Mark MVP (player with highest contribution)
        if player_performances:
            mvp = max(player_performances, key=lambda p: p.contribution_percentage)
            mvp.mvp = True
        
        # Check if this is a new personal record
        is_new_record = False
        previous_best = None
        
        if session.players:
            first_player = session.players[0]
            stats = await PlayerStatsDocument.find_one(
                {"user_id": first_player.user_id}
            )
            if stats and stats.fastest_escape_time_seconds:
                previous_best = stats.fastest_escape_time_seconds
                if completion_time < previous_best:
                    is_new_record = True
            else:
                is_new_record = True  # First completion
        
        # Build mystery info
        mystery_info = MysteryInfo(
            mystery_id=mystery.mystery_id,
            theme=mystery.theme,
            difficulty=mystery.difficulty,
            room=mystery.room,
            objective=mystery.objective
        )
        
        # Build statistics
        statistics = SessionStatistics(
            completion_time_seconds=completion_time,
            completion_time_formatted=formatted_time,
            time_limit_seconds=session.time_limit_seconds,
            time_remaining_seconds=time_remaining,
            puzzles_solved=len(session.puzzles_solved),
            total_puzzles=len(mystery.puzzles),
            hints_used=session.total_hints_used,
            puzzle_attempts=total_attempts,
            success_rate=round(success_rate, 1)
        )
        
        # Build complete winning screen data
        winning_data = WinningScreenData(
            victory=True,
            victory_message=primary_message,
            secondary_message=secondary_message,
            rank_title=rank_title,
            session_id=session_id,
            mystery=mystery_info,
            statistics=statistics,
            score=score_breakdown,
            rewards=rewards,
            players=player_performances,
            completed_at=session.completed_at or datetime.utcnow(),
            is_new_record=is_new_record,
            previous_best_time=previous_best
        )
        
        return winning_data

    async def _update_player_stats(self, session: GameSessionDocument):
        """Update player statistics after game completion"""
        for player in session.players:
            # Update Detailed Analytics (player_stats collection)
            stats = await PlayerStatsDocument.find_one(
                {
                    "user_id": player.user_id
                }
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
            user = await User.find_one({"firebase_uid": player.user_id})
            
            if user:
                user.games_played += 1
                
                if session.status == GameStatus.COMPLETED:
                    user.games_won += 1
                    user.coins += 50  # Reward for escaping
                    
                # Calculate simple score
                base_score = 1000
                time_penalty = session.completion_time_seconds or 0
                hint_penalty = player.hints_used * 50
                earned_score = max(10, base_score - time_penalty - hint_penalty)
                
                if session.status == GameStatus.COMPLETED:
                    user.total_score += earned_score
                
                user.last_login = datetime.utcnow()
                
                await user.save()
                print(f"✅ Updated core User profile for {user.display_name or user.email}")
            else:
                print(f"⚠️ Core User profile not found for {player.user_id}")

