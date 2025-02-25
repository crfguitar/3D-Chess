# 3D Chess

Multi-level chess implementation with isometric visualization and AI opponent.

## Architecture

System integrates four core modules:
- `chess3d.py`: Game logic, rules, move validation
- `chess3d_visualization.py`: Rendering and user interaction
- `ai_engine.py`: AI opponent using minimax with alpha-beta pruning
- `main_application.py`: Application coordination and menu system

## Features

- Three-level 8×8 chessboard (192 total squares)
- Standard chess pieces with 3D movement capabilities
- Isometric visualization with piece highlighting
- Customizable AI opponent with 5 difficulty levels
- Multiple game modes (Human vs Human, Human vs AI, AI vs AI)

## Requirements

- Python 3.7+
- Pygame 2.0+
- NumPy

## Installation

```bash
# Clone repository
git clone https://github.com/username/3d-chess.git
cd 3d-chess

# Install dependencies
pip install pygame numpy
```

## Usage

```bash
# Launch game
python main_application.py
```

## Game Controls

- **Mouse**: Select and move pieces
- **Esc**: New game
- **U**: Undo move
- **A**: Toggle AI
- **1-5**: Set AI difficulty

## Game Rules

Standard chess rules apply with additional 3D movement capabilities:
- Knights move between adjacent levels with modified L-pattern
- Rooks move vertically between levels in same file/rank
- Bishops move diagonally between levels
- Queens combine rook and bishop 3D movements
- Kings move to adjacent squares including between levels
- Pawns move and capture normally within their level

## Implementation Details

**Game State Representation**
- 3×8×8 numpy array for board state
- Position class tracks level, rank, and file coordinates
- Move validation implements standard chess rules plus 3D extensions

**Visualization System**
- Isometric projection using Pygame
- Piece and board rendering with dynamic highlights
- Coordinate conversion between 3D and 2D space

**AI Engine**
- Minimax algorithm with alpha-beta pruning
- Position evaluation using piece values and position tables
- Configurable search depth and time constraints
