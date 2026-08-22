# Generate a mystery (difficulty 1 - easy)
curl -X POST http://localhost:8002/game/generate \
  -H "Content-Type: application/json" \
  -d '{"room": "mummy_tomb", "difficulty": 1, "player_count": 1}'

# Save the mystery_id from response, then start a session
curl -X POST http://localhost:8002/game/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "mystery_id": "<MYSTERY_ID>",
    "player_ids": ["player_123"],
    "max_players": 1
  }'

# Update session (puzzle solved)
curl -X PUT http://localhost:8002/game/sessions/update \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<SESSION_ID>",
    "puzzle_solved": "entrance_statue",
    "player_id": "player_123",
    "time_elapsed_seconds": 120
  }'

# Complete session
curl -X POST http://localhost:8002/game/sessions/complete \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<SESSION_ID>",
    "status": "completed",
    "difficulty_rating": 3
  }'
