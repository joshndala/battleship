# Battleship (Pygame)

A lightweight single-player Battleship clone built with [Pygame](https://www.pygame.org/). Face off against an AI opponent on a compact 5×5 ocean grid, watch the action play out with simple visuals, and restart instantly to chase a better score.

## Features
- Two side-by-side boards that clearly separate your fleet from the targets you're scanning.
- Random ship placement for both player and AI so every round plays differently.
- Visual feedback for hits, misses, and hover previews on the enemy radar.
- Turn-based pacing with short AI delays so you can read each update.

## Requirements
- Python 3.8+
- `pygame`

## Setup
```bash
# (optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate

# install dependencies
python -m pip install pygame
```

## Run the Game
```bash
python3 battleship_game.py
```

## Gameplay Basics
- **Boards:** Your ships appear on the left board; the right board is your firing radar. AI ships stay hidden.
- **Player turn:** Hover over a tile on the right board to see the highlight, then click to fire. Hits turn into red Xs, misses get green circles.
- **AI turn:** After you shoot, the AI takes a moment to decide and then fires back at your board. Messages at the bottom describe what happened.
- **Win/Loss:** Sink all enemy ships before the AI sinks yours. When the game ends, press `R` to restart immediately.

## Customizing the Experience
You can tweak the constants at the top of `battleship_game.py`:
- `BOARD_SIZE`: change the grid size (e.g., 6 or 7) for longer battles.
- `NUM_SHIPS`: adjust how many single-cell ships are placed per side.
- `CELL_SIZE`, `BOARD_GAP`, and color definitions control the visual layout.

Increase the board size and ship count together to keep things balanced. Larger boards may require a higher screen resolution.

## Troubleshooting
- **Missing Pygame:** If you see `ModuleNotFoundError: No module named 'pygame'`, rerun `python -m pip install pygame`.
- **Display issues on macOS:** Running `python battleship_game.py` from a terminal (instead of an IDE console) avoids window focus problems.
- **Performance hiccups:** Disable other applications using the GPU, or reduce `BOARD_SIZE` to lessen the rendering load.

Have fun sinking ships!
