# AI-Powered 3D Mystery Rooms - Project Phases

The core promise of this project: **No mystery is ever the same twice.**
The game is an AI-powered multiplayer 3D mystery/escape-room where the AI acts as a Mystery Generator and Game Director.

---

### **Phase 1: Core Unity Environment & Backend Foundation (MVP)**
*Goal: Establish the base 3D environment, player controls, and the secure microservice architecture.*
* **Backend:**
  * Scaffold FastAPI services (Gateway, Auth, Game).
  * Configure MongoDB Atlas for player profiles and match history.
  * Build basic Auth Service and API Gateway.
* **Unity:**
  * Initialize the 3D Unity Project.
  * Create the base "Mummy/Ancient Egypt" Room environment.
  * Implement Player Controller, Camera, and basic Interaction System.
  * Build basic Inventory and UI (Timer, Objectives).

### **Phase 2: Puzzle Framework & Dynamic World Configuration**
*Goal: Build a library of reusable puzzle prefabs that can be dynamically configured by the backend.*
* **Unity:**
  * Create Puzzle Base classes and State Systems.
  * Implement specific puzzle prefabs: Combination Lock, Symbol Sequence, Hidden Object, Rotating Statue, Map/Coordinate puzzle.
  * Implement dynamic object placement, lighting, materials, and secret doors.
* **Backend:**
  * Define the JSON schemas for the dynamic puzzle configurations and game state structures.
  * Create endpoints to serve deterministic puzzle states for testing.

### **Phase 2.1: Egyptian Symbol Sprite Integration**
*Goal: Integrate 40 Egyptian symbol sprites into both the frontend Unity environment and the backend AI mystery generator to ensure visual consistency and correct puzzle generation.*

* **Backend - Define Symbol Vocabulary:**
  * Create a Python list/Enum in the backend containing the exact string names of the 40 Egyptian symbols.
  * Update the AI prompts (`puzzle_prompts.py`) to restrict the LLM to only output sequences using symbols from this specific list.
  * Update the clue generation prompts (`clue_prompts.py`) so the AI can reference these specific symbol names in its riddles.

* **Frontend - Symbol Database (ScriptableObject):**
  * Create a Unity `ScriptableObject` named `SymbolDatabase` to act as a central dictionary mapping string names (e.g., "EyeOfHorus") to their corresponding `Sprite` assets.
  * Populate this database in the Unity Editor with the 40 sliced sprites.

* **Frontend - Puzzle UI and Logic Updates:**
  * Refactor `SymbolSequencePuzzle.cs` to query the `SymbolDatabase` for sprites instead of using plain text or hardcoded images.
  * Implement a UI pool (e.g., 5-10 buttons) for players to input their sequence attempt.
  * Sync the current sequence attempt visually across all clients using `NetworkList` so late-joiners and active players see real-time input.
  * Provide visual feedback (e.g., flashing red/green) when a sequence is submitted.

### **Phase 3: AI Mystery Generator (LangChain & LangGraph)**
*Goal: The AI generates a structured, valid mystery configuration.*
* **AI/Backend:**
  * Integrate LangChain and LangGraph for mystery generation workflows.
  * Build the Generator to select objective, theme, puzzles, twists, and clues.
  * Build the **Validation Engine**: Ensure generated puzzles have valid dependencies, correct solutions, and appropriate difficulty. Regenerate if validation fails.
  * Output a validated `Mystery JSON` for Unity to consume.

### **Phase 4: Multiplayer Integration**
*Goal: Allow 1-8 players to co-op in the dynamically generated room.*
* **Unity:**
  * Integrate a networking framework (e.g., Photon Fusion, Netcode for GameObjects, or FishNet).
  * Implement Lobby and Room creation.
  * Synchronize Player movement, Object interactions, and Puzzle states.
* **Backend:**
  * Manage authoritative game state on the server (match ID, players, solved puzzles, time remaining).

### **Phase 5: AI Director & Adaptive Gameplay**
*Goal: The AI observes live game state and adapts the experience.*
* **AI/Backend:**
  * Build the AI Director to monitor player progress (time, failed attempts, hints used, areas visited).
  * Implement logic to adapt difficulty, reveal hints, or trigger predefined environmental events.
* **Unity:**
  * Listen for AI Director events (e.g., turning off lights, revealing a hidden clue, playing a sound) and execute the corresponding visual/audio cues.

### **Phase 6: Polish & The "20 Valid Mysteries" Prototype**
*Goal: Prove the core concept by generating at least 20 meaningfully different, playable, and solvable mysteries from the single Mummy Room.*
* **Full Stack:** Add VFX, audio, UI polish, Tutorial, Results screen, and Match Statistics.
* **Testing:** Run the generator to produce 20+ valid configurations. Verify all are fully playable and solvable without manual editing.

### **Phase 7+: Future Room Expansions**
*Goal: Expand the game with new environments and themes.*
* **New Rooms:** Horror Room, Geography Room, Historical Mystery Room, Koh-i-Noor Inspired Room.
* **Monetization/Scaling:** Implement premium rooms, difficulty settings, and cosmetic items.