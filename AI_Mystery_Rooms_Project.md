# AI-Powered 3D Mystery Rooms

## 1. Project Overview

An AI-powered multiplayer 3D mystery/escape-room game where every playthrough can generate a different mystery, clue arrangement, puzzle sequence, environmental event, and solution.

The core promise:

> **No mystery is ever the same twice.**

Players enter themed 3D rooms and work together to investigate clues, solve puzzles, uncover a mystery, and escape.

The AI is not just a conversational NPC. It acts as a **Mystery Generator and Game Director**, dynamically assembling valid mysteries from reusable game systems.

---

## 2. Core Gameplay Loop

```text
Create / Join Lobby
        ↓
Select Mystery Room
        ↓
AI Generates Mystery
        ↓
Unity Builds / Configures Room
        ↓
Players Explore
        ↓
Discover Dynamic Clues
        ↓
Solve Puzzles
        ↓
AI Director Monitors Progress
        ↓
Hints / Events / Difficulty Adaptation
        ↓
Final Mystery / Puzzle
        ↓
Escape / Fail
        ↓
Results + Statistics
```

---

## 3. Main Differentiator

Existing escape-room games commonly use:

```text
Static room
    ↓
Static clues
    ↓
Fixed puzzle sequence
    ↓
Fixed solution
```

This project aims for:

```text
Reusable 3D room
      ↓
AI-generated mystery
      ↓
Dynamic clue placement
      ↓
Dynamic puzzle configuration
      ↓
Dynamic environmental events
      ↓
Adaptive difficulty
      ↓
Different solution
```

The same room can therefore support many different experiences.

---

# 4. Initial MVP

Do NOT start with multiple rooms.

Build one highly polished room first:

## Mummy / Ancient Egypt Mystery Room

### MVP environment

- Egyptian tomb
- Sarcophagus
- Statues
- Ancient walls
- Hieroglyphics
- Torches
- Secret passages
- Locked doors
- Chests
- Artifacts
- Maps
- Hidden compartments

### MVP multiplayer

- 1–4 players
- Shared room
- Player movement
- Object interaction
- Shared puzzle state
- Voice/text communication
- Game timer

### MVP puzzle types

1. Symbol sequence
2. Hidden object
3. Combination lock
4. Rotating statue
5. Map/coordinate puzzle
6. Light/shadow puzzle
7. Pressure plate puzzle
8. Hidden compartment

Target:

> Generate at least 20 meaningfully different playable mysteries from one room.

---

# 5. Future Mystery Rooms

After the Mummy Room is stable:

## Geography Room

Possible themes:

- World map
- Countries
- Capitals
- Coordinates
- Mountains
- Rivers
- Flags
- Exploration
- Lost expedition

Example:

> A missing explorer left a trail of clues across different countries.

---

## Horror Room

Possible environments:

- Abandoned hospital
- Haunted mansion
- Underground facility
- Abandoned village
- Prison
- Asylum-inspired fictional location

Dynamic events:

- Lights turning off
- Doors opening
- Sounds
- Shadows
- Objects moving
- Hidden passages
- AI-controlled entities
- Unexpected events

The AI Director decides when predefined events should occur.

---

## Historical Mystery Room

Historical themes can include:

- Ancient Rome
- Ancient Egypt
- Medieval kingdoms
- Mughal-era inspired fictional mysteries
- Maritime history
- Archaeological mysteries

Historical facts should be clearly separated from fictional gameplay.

---

## Koh-i-Noor Inspired Mystery Room

A historical mystery inspired by the documented history of the Koh-i-Noor.

Possible environment:

- Royal archive
- Persian manuscripts
- Maps
- Royal seals
- Historical documents
- Artifact replicas
- Locked vault
- Paintings
- Timelines

The game should clearly distinguish fictional gameplay from real historical claims.

Example fictional objective:

> Find a missing royal document containing a clue about the diamond's journey before the archive is sealed.

---

# 6. AI System

The AI should be responsible for **content generation and orchestration**, not direct low-level Unity control.

## AI responsibilities

- Generate mystery premise
- Select objectives
- Select puzzle types
- Configure puzzle parameters
- Generate clues
- Determine clue relationships
- Create false leads
- Determine solution path
- Adjust difficulty
- Monitor player progress
- Decide when to reveal hints
- Trigger predefined environmental events
- Generate different endings
- Analyze player performance

---

# 7. AI Mystery Generator

The AI generates a structured mystery configuration.

Example:

```json
{
  "room": "mummy_tomb",
  "difficulty": 4,
  "theme": "missing_artifact",
  "objective": "recover_the_pharaoh_mask",
  "time_limit_seconds": 1800,
  "puzzles": [
    {
      "type": "hieroglyph_sequence",
      "id": "puzzle_01"
    },
    {
      "type": "hidden_compartment",
      "id": "puzzle_02"
    },
    {
      "type": "map_coordinates",
      "id": "puzzle_03"
    },
    {
      "type": "final_lock",
      "id": "puzzle_04"
    }
  ],
  "twist": "the_first_artifact_is_fake"
}
```

Unity validates this configuration and constructs the playable mystery.

---

# 8. Important Design Principle

## Do NOT let the LLM directly control Unity.

Avoid:

```text
LLM
 ↓
Instantiate GameObject
Move GameObject
Open Door
Change Light
```

Instead:

```text
LLM
 ↓
Validated Mystery JSON
 ↓
Game Rules Validator
 ↓
Unity Mystery/World Builder
 ↓
Predefined Game Systems
```

This makes the system:

- More reliable
- Easier to debug
- Safer
- Deterministic
- Easier to test
- Easier to scale

---

# 9. Puzzle Prefab Library

Create reusable Unity puzzle prefabs.

```text
PuzzlePrefabs/
├── CombinationLock
├── SymbolLock
├── RotatingStatues
├── PressurePlates
├── HiddenDrawer
├── MovingWall
├── LightPuzzle
├── ShadowPuzzle
├── MirrorPuzzle
├── MapPuzzle
├── ScalePuzzle
├── LeverPuzzle
├── SequencePuzzle
└── ArtifactPuzzle
```

Each prefab exposes configurable parameters.

Example:

```csharp
public class RotatingStatuePuzzle : MonoBehaviour
{
    public Statue[] statues;
    public string[] correctSequence;

    public void ConfigurePuzzle(string[] solution)
    {
        // Configure puzzle
    }
}
```

The AI can choose:

```text
Falcon → Ankh → Scarab → Eye
```

for one playthrough and:

```text
Eye → Cobra → Sun → Ankh
```

for another.

---

# 10. Dynamic Graphical Clues

The goal is not to generate brand-new 3D assets every game.

Instead, use a library of high-quality reusable assets and dynamically change:

- Position
- Rotation
- Scale
- Materials
- Textures
- Symbols
- Lighting
- Object states
- Hidden/visible state
- Animation
- Environmental effects
- Puzzle configuration

---

## Example: Dynamic Statue Puzzle

Game A:

```text
Statue 1 → Falcon
Statue 2 → Ankh
Statue 3 → Eye
Statue 4 → Scarab
```

Game B:

```text
Statue 1 → Scarab
Statue 2 → Sun
Statue 3 → Cobra
Statue 4 → Ankh
```

Same 3D environment.

Different puzzle.

---

# 11. Dynamic Lighting

Lighting can become a clue.

Example:

```text
Player activates torch
        ↓
Lighting changes
        ↓
Statue shadow appears
        ↓
Shadow forms hidden symbol
        ↓
Player discovers clue
```

The AI can dynamically configure:

- Torch positions
- Light states
- Light intensity
- Statue orientation
- Target symbol
- Required sequence

---

# 12. Dynamic Environmental Events

Build events once in Unity and let the AI decide when they happen.

Examples:

```text
Puzzle solved
    ↓
Torch goes out
    ↓
Room becomes dark
    ↓
Secret wall opens
```

Or:

```text
Player opens sarcophagus
    ↓
Dust effect
    ↓
Animation
    ↓
Hidden object revealed
    ↓
New clue
```

Or:

```text
Player discovers artifact
    ↓
Alarm
    ↓
Door locks
    ↓
New puzzle becomes available
```

The AI chooses the event; Unity executes a predefined event.

---

# 13. Dynamic Clue Types

Possible clue systems:

### Text clues

- Diaries
- Letters
- Inscriptions
- Journals
- Maps
- Documents

### Visual clues

- Symbols
- Paintings
- Statues
- Shadows
- Lighting
- Object arrangements

### Environmental clues

- Broken objects
- Blood trails
- Footprints
- Scratches
- Open drawers
- Moved furniture

### Audio clues

- Whisper
- Footsteps
- Hidden recording
- Mechanical sounds
- Environmental audio

### Interactive clues

- Rotate object
- Move object
- Combine objects
- Activate mechanism
- Align symbols

---

# 14. Multiplayer Design

Target 1–4 players initially.

Players can have asymmetric information.

Example:

```text
Player A
→ discovers direction clue

Player B
→ discovers symbol clue

Player C
→ discovers historical clue

Player D
→ discovers mechanical clue
```

No single player has the complete solution.

The team must communicate.

This creates genuine multiplayer gameplay rather than simply placing multiple players in the same room.

---

# 15. Player Skill Modeling

The AI Director can track:

```text
Puzzle solve time
Wrong attempts
Hint usage
Objects inspected
Areas visited
Communication
Puzzle success rate
```

Example:

```text
Player/team struggles with map puzzles
        ↓
AI lowers future map complexity
```

Or:

```text
Player/team solves puzzles too quickly
        ↓
AI increases complexity
```

The goal is adaptive difficulty.

---

# 16. AI Director

The AI Director continuously observes game state.

Example:

```text
GAME STATE

Time remaining: 12:32
Puzzles solved: 3/6
Hints used: 1
Players stuck: 2
Current puzzle duration: 6m 41s
```

AI Director may decide:

```text
Action:
Reveal subtle environmental clue
```

rather than immediately giving the answer.

Possible actions:

- Reveal clue
- Activate visual cue
- Trigger environmental event
- Unlock optional area
- Reduce puzzle complexity
- Increase puzzle complexity
- Change pacing
- Trigger story event

---

# 17. Game State

Maintain authoritative game state on the server where appropriate.

Example:

```json
{
  "match_id": "abc123",
  "room": "mummy_tomb",
  "players": 4,
  "current_puzzle": "puzzle_03",
  "solved_puzzles": [
    "puzzle_01",
    "puzzle_02"
  ],
  "time_remaining": 752,
  "hints_used": 1,
  "difficulty": 4
}
```

---

# 18. Proposed Architecture

```text
                     UNITY CLIENT
                          │
                    Multiplayer Layer
                          │
                          ▼
                     GAME SERVER
                        FastAPI
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
     Game State       AI Director       Players
          │               │
          │               ▼
          │          AI / LLM Layer
          │               │
          │               ▼
          │        Mystery Generator
          │               │
          └───────────────┼───────────────┐
                          ▼               ▼
                    MongoDB          Vector DB
```

---

# 19. Suggested Technology Stack

## Client

- Unity 6
- C#
- Unity Input System
- Unity Addressables if needed
- Unity UI
- 3D physics/interactions

## Multiplayer

Possible options:

- Photon Fusion
- Unity Netcode for GameObjects
- FishNet

For a first prototype, choose one networking framework and keep it simple.

## Backend

- FastAPI
- Python
- WebSockets where appropriate
- REST APIs for non-real-time operations

## Database

- MongoDB

Potential data:

- Player profiles
- Match history
- Mystery configurations
- Puzzle performance
- Player difficulty profile
- Room metadata

## AI

Potential components:

- LLM for mystery generation
- Structured output / JSON schema
- AI Director
- Optional embeddings/vector database for historical/lore knowledge
- Deterministic procedural algorithms for puzzle generation

---

# 20. AI + Procedural Generation

The best approach is hybrid.

Use LLM for:

- Story
- Mystery premise
- Clue text
- Narrative relationships
- Puzzle selection
- High-level configuration

Use deterministic code for:

- Puzzle validity
- Randomization
- Coordinates
- Passwords
- Number sequences
- Object placement
- Collision
- Game rules
- Win/loss conditions

This prevents impossible puzzles.

---

# 21. Puzzle Validation

Every generated mystery should pass validation before being sent to players.

```text
Generate Mystery
      ↓
Validate Story
      ↓
Validate Puzzle Dependencies
      ↓
Validate Solution
      ↓
Validate Object Availability
      ↓
Validate Difficulty
      ↓
Generate World
      ↓
Start Match
```

If validation fails:

```text
Regenerate / Repair
```

---

# 22. Example Mystery Generation

## Mystery A

```text
Room:
Mummy Tomb

Objective:
Recover Pharaoh's missing mask

Puzzle chain:

Hieroglyph clue
      ↓
Statue sequence
      ↓
Hidden compartment
      ↓
Map puzzle
      ↓
Fake artifact
      ↓
Final lock
```

## Mystery B

```text
Room:
Mummy Tomb

Objective:
Discover what happened to the missing archaeologist

Puzzle chain:

Diary
      ↓
Blood trail
      ↓
Torch/shadow puzzle
      ↓
Secret passage
      ↓
Ancient map
      ↓
Final chamber
```

Same room.

Different mystery.

---

# 23. Long-Term Room Roadmap

### Phase 1

Mummy Room

### Phase 2

Horror Room

### Phase 3

Geography Room

### Phase 4

Historical Mystery Room

### Phase 5

Koh-i-Noor Inspired Room

### Phase 6

Pirate Mystery

### Phase 7

Ancient Rome

### Phase 8

Space Station

### Phase 9

User-generated / AI-generated mystery scenarios

---

# 24. Monetization Possibilities

Potential model:

```text
FREE
├── Mummy Room
├── Limited daily mysteries
└── Basic difficulty

PREMIUM
├── Horror
├── Historical
├── Geography
├── Koh-i-Noor Inspired
├── Pirate
└── Advanced difficulty
```

Other possibilities:

- Cosmetic player items
- Room packs
- Seasonal mysteries
- Special events
- Premium mystery difficulty
- Competitive leaderboards

Avoid making core puzzle solving pay-to-win.

---

# 25. Competitive Advantage

Do not compete only on graphics.

Compete on:

### Existing escape-room model

```text
Beautiful room
↓
Static clues
↓
Fixed puzzle
↓
Fixed solution
```

### This project

```text
Beautiful 3D room
↓
AI-generated mystery
↓
Dynamic clues
↓
Dynamic puzzle configuration
↓
Dynamic environment
↓
Adaptive difficulty
↓
Different ending
```

The strongest product statement is:

> **Enter the same room twice. Get a completely different mystery.**

---

# 26. MVP Development Plan

## Milestone 1 — Core Unity Room

- [ ] Create Mummy Room
- [ ] Player controller
- [ ] Camera
- [ ] Interaction system
- [ ] Doors
- [ ] Basic inventory
- [ ] Basic UI
- [ ] Timer

## Milestone 2 — Puzzle Framework

- [ ] Puzzle base class
- [ ] Puzzle state system
- [ ] Combination lock
- [ ] Symbol puzzle
- [ ] Hidden object puzzle
- [ ] Rotating statue puzzle
- [ ] Map puzzle

## Milestone 3 — Dynamic World

- [ ] Dynamic object placement
- [ ] Dynamic symbols
- [ ] Dynamic materials
- [ ] Dynamic lighting
- [ ] Dynamic hidden objects
- [ ] Environmental events
- [ ] Secret doors

## Milestone 4 — Mystery Generator

- [ ] Mystery schema
- [ ] LLM integration
- [ ] Structured JSON output
- [ ] Puzzle dependency generation
- [ ] Clue generation
- [ ] Mystery validation
- [ ] Automatic regeneration on failure

## Milestone 5 — Multiplayer

- [ ] Lobby
- [ ] Room creation
- [ ] Player synchronization
- [ ] Object interaction synchronization
- [ ] Puzzle synchronization
- [ ] Match completion

## Milestone 6 — AI Director

- [ ] Player progress tracking
- [ ] Stuck detection
- [ ] Hint generation
- [ ] Difficulty adjustment
- [ ] Environmental event selection
- [ ] Player/team profiling

## Milestone 7 — Polish

- [ ] Audio
- [ ] VFX
- [ ] Animations
- [ ] UI polish
- [ ] Tutorial
- [ ] Results screen
- [ ] Match statistics

---

# 27. First Technical Prototype

The first proof-of-concept should NOT be the complete game.

Build:

```text
1 room
+
3 puzzles
+
1 AI-generated mystery
+
1 dynamic clue
+
1 dynamic environmental event
```

Example:

```text
AI generates:
"Recover the Pharaoh's missing artifact."

↓

Puzzle 1:
Hieroglyph sequence

↓

Puzzle 2:
Rotating statues

↓

Puzzle 3:
Final combination

↓

Dynamic event:
Secret wall opens

↓

Player escapes
```

Then run the generator 20 times.

Success criteria:

> At least 15–20 generated configurations should be valid and solvable without manually editing the mystery.

---

# 28. Ultimate Vision

The long-term product can become a platform where:

```text
Player chooses:

ROOM
  ↓
THEME
  ↓
DIFFICULTY
  ↓
PLAYERS
  ↓
AI GENERATES MYSTERY
  ↓
3D WORLD CONFIGURED
  ↓
PLAY
  ↓
AI ADAPTS
  ↓
UNIQUE ENDING
```

The game is not just a collection of rooms.

It is an:

> **AI-generated mystery engine wrapped inside a multiplayer 3D escape-room game.**

---

# 29. Project North Star

### Core promise

> **No mystery is ever the same twice.**

### MVP promise

> **One beautiful room. 20+ possible mysteries. 1–4 players.**

### Long-term promise

> **An infinite library of AI-generated 3D mysteries.**
