# Terminal Line Rider CLI

Draw insane tracks and watch physics do its thing!

## Features

- Draw custom tracks with a simple editor
- Realistic physics (gravity, momentum, friction, crashes)
- Save/load your maps as JSON
- 3 default maps included: Beginner Hill, Death Drop, Loop-de-Loop
- ASCII rider that tilts based on velocity

## How to Run

```bash
python main.py
```

## Controls

### Menu
- `1` - New Track (Editor)
- `2` - Load Track
- `3-5` - Play default maps
- `Q` - Quit

### Editor Mode
- `WASD` - Move cursor
- `SPACE` - Place point and connect to previous
- `R` - Reset rider to start
- `P` - Play your track
- `S` - Save track to maps folder
- `M` - Back to menu

### Playing Mode
- `SPACE` - Pause/unpause
- `R` - Reset rider
- `E` - Back to editor
- `M` - Back to menu

## How to Create Tracks

1. Start editor (option 1 from menu)
2. Move cursor with WASD
3. Press SPACE to place points
4. Points auto-connect as you place them
5. Press P to test your track
6. Press S to save it

## Tips

- Start high and go low for speed
- Sharp angles = crashes
- Smooth curves = sick runs
- The rider starts at your first point

## Map Format

Maps are saved as JSON in the `maps/` folder:

```json
{
  "points": [[x1, y1], [x2, y2], ...],
  "lines": [[0, 1], [1, 2], ...]
}
```

Build something gnarly!
