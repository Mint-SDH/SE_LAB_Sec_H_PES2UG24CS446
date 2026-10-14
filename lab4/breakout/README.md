# Breakout Game

An enhanced, object-oriented Breakout / Brick Breaker game built with Python and Pygame (`pygame-ce`).

---

## Features Implemented

### 1. Brick Destruction & Accurate Collision
- Fixed the brick removal bug in the game engine: bricks now properly track their remaining hits and are permanently removed from play once their durability reaches zero.
- Improved collision physics in `game/collision.py` to calculate exact overlap depths, correctly resolving vertical vs. horizontal bounces and preventing ball clipping/tunneling.

### 2. 3-Life System & Game Over
- Players start with **3 lives**, visually displayed with heart icons on the top HUD (`Lives: ♥ ♥ ♥`).
- When the ball falls below the paddle, the player loses 1 life, the ball/paddle reset to the starting position, and any active combo is reset.
- Once all 3 lives are exhausted, a **GAME OVER** screen is displayed showing the final score.
- Pressing **`[R]`**, **`[SPACE]`**, or **`[ENTER]`** restarts the game with a fresh board, score, and lives.

### 3. Three Distinct Brick Types
The playfield includes three distinct brick varieties, each with unique visual appearances and mechanics:
- **Normal Brick** (1 hit):
  - Uniform vibrant coral red blocks with beveled edge highlights.
  - Consistent single color representing 1-hit toughness across the board.
  - Destroyed immediately upon a single hit.
- **Strong Brick** (2 hits):
  - Reinforced metallic deep blue blocks with double borders.
  - Takes 2 hits to destroy.
  - Upon taking damage (1 hit remaining), it visually changes color to light cyan and displays a visible crack pattern across its surface.
- **Unbreakable Brick** (Indestructible):
  - Heavy dark slate steel blocks featuring silver borders, center divider bar, and 4 corner steel rivets.
  - Never destroyed regardless of how many times it is hit; serves as strategic obstacle requiring skillful paddle deflection.
  - Does not prevent victory: the win condition only requires clearing all destructible bricks!

### 4. Score & Combo Multiplier
- **Scoring**: Hitting and destroying bricks awards points:
  - Damaging a strong brick: `50 × Multiplier`
  - Destroying a brick: `100 × Multiplier`
- **Combo Multiplier**:
  - Hitting destructible bricks back-to-back without losing the ball builds up the combo multiplier (`1x`, `2x`, `3x`, etc.).
  - The multiplier is displayed prominently in gold on the HUD.
  - Missing the ball (falling below paddle) resets the combo back to `1x`.

---

## Folder Structure

```
breakout/
├── main.py
├── requirements.txt
├── game/
│   ├── game_engine.py
│   ├── paddle.py
│   ├── ball.py
│   ├── brick.py
│   ├── collision.py
│   └── renderer.py
└── README.md
```

---

## Controls

| Key | Action |
|---|---|
| **Left Arrow (`←`)** | Move paddle left |
| **Right Arrow (`→`)** | Move paddle right |
| **`R`** | Restart game at any time |
| **`SPACE` / `ENTER`** | Restart game from Game Over or Victory screens |

---

## Running the Game

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the game**:
   ```bash
   python main.py
   ```
