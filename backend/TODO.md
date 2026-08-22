# Task & To-Do Tracker: AI-Powered 3D Mystery Rooms

## Phase 1: Core Unity Environment & Backend Foundation (MVP)

### ✅ Completed Tasks
- [x] Backend: Scaffold Microservice Folder Structure (Auth, Game, Gateway, Shared) using `uv`.
- [x] Backend: Set up MVC architecture inside services.
- [x] Backend: Configure MongoDB Atlas credentials.
- [x] Backend: Create `shared/database.py` for global MongoDB connection using Motor/Beanie.

### ⏳ Pending Tasks
- [ ] **Backend (Auth/Gateway):** Complete user registration, login, JWT token generation, and API Gateway JWT validation middleware.
- [ ] **Unity:** Upgrade/Initialize 3D Unity 6 Project (transition from previous 2D setup).
- [ ] **Unity:** Block out the base "Mummy/Ancient Egypt" Room environment (walls, floors, key structures).
- [ ] **Unity:** Implement Player Controller (First-person or Third-person movement, Camera).
- [ ] **Unity:** Implement Raycast/Collider-based Interaction System (Pickup, Inspect, UI Prompts).
- [ ] **Unity:** Build basic UI (Timer, Inventory, Objectives, Hint display).

---

## Phase 2: Puzzle Framework & Dynamic World Configuration

### ⏳ Pending Tasks
- [ ] **Unity:** Create base `Puzzle` and `PuzzleState` C# scripts.
- [ ] **Unity:** Build *Combination Lock* Prefab.
- [ ] **Unity:** Build *Symbol Sequence* Prefab.
- [ ] **Unity:** Build *Hidden Object* / *Rotating Statue* Prefab.
- [ ] **Unity:** Implement dynamic environment tools (scripts to swap materials, turn lights on/off, open secret doors via code).
- [ ] **Backend (Game Service):** Define Pydantic/JSON schemas for `MysteryConfig` and `PuzzleConfig`.
- [ ] **Backend (Game Service):** Create mock API endpoint to serve a deterministic, hardcoded `MysteryConfig` JSON to test Unity's parsing.
- [ ] **Unity:** Write `MysteryBuilder.cs` to fetch JSON from Backend and spawn/configure the puzzles in the room based on the JSON.

---

## Phase 3: AI Mystery Generator (LangChain & LangGraph)

### ⏳ Pending Tasks
- [ ] **Backend:** Setup `langchain` and `langgraph` in the Game Service (or a dedicated AI Service).
- [ ] **Backend (AI):** Define the graph nodes: `GenerateTheme`, `SelectPuzzles`, `GenerateClues`, `Validate`.
- [ ] **Backend (AI - Prompts):** Write strict LLM prompts for outputting structured JSON according to the `MysteryConfig` schema.
- [ ] **Backend (Validation Engine):** Write deterministic python code to validate the LLM's output (check dependencies: e.g., "Clue A must exist before Puzzle B").
- [ ] **Backend (AI Workflow):** Implement retry logic if the validation engine rejects the LLM's JSON.
- [ ] **Backend (API):** Create `/game/generate` endpoint to trigger the graph and return the final validated JSON to the client.

---

## Phase 4: Multiplayer Integration

### ⏳ Pending Tasks
- [ ] **Unity (Network):** Import chosen framework (e.g., Photon Fusion or Netcode).
- [ ] **Unity (Network):** Build Lobby & Matchmaking UI.
- [ ] **Unity (Network):** Sync Player transforms (Movement/Rotation).
- [ ] **Unity (Network):** Sync Object Interactions (Player A picks up an item, it disappears for Player B).
- [ ] **Unity (Network):** Sync Puzzle States (Player A rotates a statue, Player B sees it rotate).
- [ ] **Backend:** Create authoritative game state endpoints/sockets (Match ID, active players, elapsed time).

---

## Phase 5: AI Director & Adaptive Gameplay

### ⏳ Pending Tasks
- [ ] **Backend (Director):** Create a listener endpoint/websocket to receive live metrics from Unity (puzzles solved, time spent, wrong attempts).
- [ ] **Backend (AI):** Build the AI Director logic to analyze metrics and decide on actions (Give Hint, Trigger Event, Change Difficulty).
- [ ] **Unity (Director Listener):** Implement systems to receive Director commands and execute them (e.g., `PlaySpookySound()`, `RevealGlowOnClue()`).

---

## Phase 6: Polish & The "20 Valid Mysteries" Prototype

### ⏳ Pending Tasks
- [ ] **Unity:** Add Audio (BGM, sound effects for puzzles/doors).
- [ ] **Unity:** Add Particle VFX (dust, magical glow).
- [ ] **Unity:** Polish UI/UX (Tutorial tooltips, Game Over screen, Results).
- [ ] **Full Stack:** Run 20 back-to-back AI generation tests. Manually playtest to ensure 100% solvability without manual code intervention.

---

## Phase 7: Future Expansions

### ⏳ Future Backlog
- [ ] **Content:** Horror Room.
- [ ] **Content:** Geography Room.
- [ ] **Content:** Historical / Koh-i-Noor Room.
- [ ] **Systems:** Premium rooms / Coin Economy.
- [ ] **Systems:** User Profiles and Global Leaderboards.