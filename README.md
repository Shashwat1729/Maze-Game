﻿# Maze Runner Game

A modern, minimalist maze game built with Python and Pygame. Navigate through increasingly challenging mazes while collecting coins and avoiding enemies.

## Features

- **Modern UI Design**
  - Clean, minimalist interface
  - Separate UI area for game information
  - Smooth animations and transitions
  - Neon blue color scheme

- **Gameplay**
  - Progressive difficulty with increasing levels
  - Collect coins to increase your score
  - Power-ups for temporary immunity
  - Enemy AI that adapts to player movement
  - High score tracking

- **Visual Effects**
  - Player trail effects
  - Smooth movement animations
  - Modern UI elements
  - Clear visual feedback for game states

## Controls

- **Movement**: WASD or Arrow keys
- **Start Game**: SPACE
- **Pause/Resume**: ESC
- **Restart**: R
- **Quit**: ESC (in menu) or window close button

## Game States

1. **Menu**
   - Displays game title and controls
   - Press SPACE to start

2. **Playing**
   - Shows current score, level, and high score
   - Displays countdown timer when starting level
   - Shows immunity timer when power-up is active

3. **Paused**
   - Game pauses with semi-transparent overlay
   - Options to resume or restart

4. **Game Over**
   - Shows final score
   - Option to restart or return to menu

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Shashwat1729/Maze-Game.git
cd maze-runner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python -m src.main
```

## Project Structure

```
maze-runner/
├── src/
│   ├── assets/
│   │   ├── images/
│   │   └── sounds/
│   ├── game/
│   │   ├── __init__.py
│   │   ├── game.py
│   │   ├── maze.py
│   │   ├── player.py
│   │   └── enemy.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── constants.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Dependencies

- Python 3.8+
- Pygame 2.5.2

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
