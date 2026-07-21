# ♟️ Advanced Chess Game

A complete, feature-rich chess game implementation in Python with AI opponent, advanced game mechanics, and multiple game modes.

## 🎮 Features

### Core Chess Features
- ✅ **Full Chess Board** - 8x8 board with proper piece setup
- ✅ **All 6 Piece Types** - Pawn, Knight, Bishop, Rook, Queen, King
- ✅ **Piece-Specific Movement** - Accurate movement rules for each piece type
- ✅ **Move Validation** - Comprehensive legal move checking
- ✅ **Capture Mechanics** - Full capture support

### Advanced Features
- ✅ **Check/Checkmate Detection** - Automatic game state detection
- ✅ **Stalemate Detection** - Draw by stalemate
- ✅ **Castling** - Both kingside and queenside castling (with proper validation)
- ✅ **En Passant** - Special pawn capture move
- ✅ **Pawn Promotion** - Promote pawns to Queen, Rook, Bishop, or Knight
- ✅ **AI Opponent** - Minimax algorithm with alpha-beta pruning
- ✅ **Time Controls** - Timed game mode with countdown for each player
- ✅ **Move Undo** - Undo moves during gameplay
- ✅ **Save/Load Games** - Persist game state to JSON
- ✅ **Move History** - Track all moves and captured pieces

### Game Modes
1. **Player vs Player (PvP)** - Local multiplayer
2. **Player vs Computer (PvC)** - Play against AI
3. **Timed Game** - 5-minute rapid chess (customizable)

## 📁 Files

- **`chess.py`** - Basic chess game (no AI, simpler implementation)
- **`chess_advanced.py`** - Full-featured game with all advanced features
- **`index.html`** - Web-based UI for playing online
- **`style.css`** - Styling for web interface
- **`app.js`** - Frontend logic for web version

## 🚀 Quick Start

### Python Version

#### Installation
```bash
git clone https://github.com/Arslan-lab-12/chess-game.git
cd chess-game
```

#### Running the Game
```bash
# Basic version
python chess.py

# Advanced version with AI
python chess_advanced.py
```

### Web Version

```bash
# Start a simple HTTP server
python -m http.server 8000

# Open in browser
# http://localhost:8000
```

## 🎮 How to Play

### Command Format
```
[source] [destination]     # e.g., "e2 e4"
```

### Board Notation
- **Columns:** a-h (left to right)
- **Rows:** 1-8 (bottom to top for White, top to bottom for Black)
- **White pieces start** at rows 1-2
- **Black pieces start** at rows 7-8

### Commands
| Command | Action |
|---------|--------|
| `a2 a4` | Move piece from a2 to a4 |
| `undo` | Undo last move |
| `save` | Save game to JSON |
| `load` | Load game from JSON |
| `help` | Show available commands |
| `quit` | Exit game (option to save) |

### Example Game
```
♟️  Welcome to Advanced Chess! ♟️

Game Modes:
1. Player vs Player
2. Player vs Computer (AI)
3. Timed Game (5 min each)

Choose game mode (1-3): 2
Current Player: WHITE
====================================================
    a   b   c   d   e   f   g   h
  +-------------------------------+
8 | ♖ | ♘ | ♗ | ♕ | ♚ | ♗ | ♘ | ♖ |
  +-------------------------------+
7 | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ |
  +-------------------------------+
6 |   |   |   |   |   |   |   |   |
  +-------------------------------+
5 |   |   |   |   |   |   |   |   |
  +-------------------------------+
4 |   |   |   |   |   |   |   |   |
  +-------------------------------+
3 |   |   |   |   |   |   |   |   |
  +-------------------------------+
2 | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ |
  +-------------------------------+
1 | ♖ | ♘ | ♗ | ♕ | ♔ | ♗ | ♘ | ♖ |
  +-------------------------------+

Captured pieces: []
Moves: 0

Enter move (e.g., 'a2 a4') or command: e2 e4
```

## 🤖 AI Features

### Minimax Algorithm
- **Depth-based search** - Evaluates move sequences to given depth
- **Alpha-Beta Pruning** - Optimizes search by eliminating unnecessary branches
- **Board Evaluation** - Piece-based position scoring

### AI Difficulty
Controlled by search depth:
- `depth=1` - Easy (moves randomly)
- `depth=2` - Medium (default)
- `depth=3` - Hard (slower, better moves)
- `depth=4+` - Expert (very slow)

### Current Implementation
- **Default depth:** 2 (balanced speed/quality)
- **Response time:** ~1-2 seconds per move

## 💾 Save/Load System

### Save Game
```
save
Game saved to chess_game.json
```

### Load Game
```
load
Game loaded from chess_game.json (saved at 2024-01-15T10:30:45.123456)
```

### Save File Format
```json
{
  "board": { ... },
  "current_player": "WHITE",
  "move_history": [ ... ],
  "captured_pieces": [ ... ],
  "game_mode": "PVC",
  "is_checkmate": false,
  "is_stalemate": false,
  "is_check": false,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

## ⏱️ Time Controls

### Timed Game Mode
- **Duration:** 5 minutes per player (customizable)
- **Display:** Real-time countdown for each player
- **Win Condition:** Opponent's time runs out
- **Format:** MM:SS

### Usage
```python
game = ChessGame(GameMode.TIMED, time_limit=300)  # 5 minutes
game = ChessGame(GameMode.TIMED, time_limit=600)  # 10 minutes
```

## 🎯 Special Moves

### Castling
**Conditions:**
- King and Rook have not moved
- No pieces between King and Rook
- King is not in check
- King does not pass through attacked square

**Notation:** `e1 g1` (kingside) or `e1 c1` (queenside)

### En Passant
**Conditions:**
- Enemy pawn just moved 2 squares forward
- Your pawn is on the 5th rank (for White) or 4th rank (for Black)
- You can capture it "in passing"

**Notation:** `e5 d6` (captures en passant)

### Pawn Promotion
**Trigger:** Pawn reaches opposite end of board

**Options:**
1. Queen
2. Rook
3. Bishop
4. Knight

**Result:** Pawn is automatically replaced

## 📊 Game State Detection

### Check
- King is under direct attack
- Player must move to escape check
- Game continues

### Checkmate
- King is in check
- Player has no legal moves to escape
- **Game Over** - Opponent wins

### Stalemate
- King is NOT in check
- Player has no legal moves
- **Draw** - Game ends in tie

## 🌐 Web Interface

### Features
- **Interactive Board** - Click to select pieces and move
- **Visual Feedback** - Highlights legal moves
- **Move Display** - Shows last move made
- **Captured Pieces** - Shows all captured pieces
- **Game Status** - Displays check, checkmate, or stalemate

### Running Web Version
```bash
cd chess-game
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

## 🔧 Code Structure

### Classes

#### `Piece`
Represents individual chess pieces
- `type` - PieceType (Pawn, Knight, Bishop, Rook, Queen, King)
- `color` - Color (White, Black)
- `has_moved` - Boolean for castling/en passant tracking

#### `Board`
Manages the chess board
- `squares` - 8x8 grid of pieces
- `en_passant_target` - En passant target square
- Methods: `get_piece()`, `set_piece()`, `display()`

#### `ChessGame`
Main game logic and state management
- Move validation and execution
- Check/checkmate/stalemate detection
- AI opponent implementation
- Save/load functionality
- Time management

### Key Methods

| Method | Purpose |
|--------|---------|
| `is_valid_move()` | Check if move is legal |
| `make_move()` | Execute a move on the board |
| `is_in_check()` | Check if king is attacked |
| `has_legal_moves()` | Check for stalemate/checkmate |
| `minimax()` | AI decision-making algorithm |
| `ai_move()` | Get AI's best move |
| `save_game()` | Save to JSON file |
| `load_game()` | Load from JSON file |

## 🧪 Testing

### Basic Tests
```python
# Create a game
game = ChessGame(GameMode.PVP)

# Make a move
success, message = game.make_move(1, 4, 3, 4)  # e2 to e4
print(message)  # "e2 e4"

# Check for check
print(game.is_check)  # False

# Get possible moves
moves = game.get_possible_moves(1, 4)
print(len(moves))  # Number of legal moves

# Undo move
game.undo_move()

# Save game
game.save_game("test_game.json")

# Load game
loaded_game = ChessGame.load_game("test_game.json")
```

## 📈 Performance

| Aspect | Details |
|--------|---------|
| **Board Representation** | 8x8 2D array (64 squares) |
| **Move Generation** | O(n) where n = legal moves |
| **Validation** | Path checking, check detection |
| **AI Search** | Minimax with alpha-beta pruning |
| **Typical AI Response** | 1-2 seconds (depth=2) |

## 🎓 Learning Resources

### Concepts Implemented
- **Move Validation** - Complex piece movement rules
- **Game Theory** - Check, checkmate, stalemate
- **AI/Algorithms** - Minimax, alpha-beta pruning
- **Data Structures** - Board representation, move history
- **Serialization** - Save/load with JSON
- **Time Management** - Countdown timers

## 🐛 Known Limitations

- **AI Depth** - Limited to depth 3-4 for reasonable response time
- **No Opening Book** - AI doesn't use pre-computed openings
- **No Endgame Tables** - Could improve performance
- **Basic Evaluation** - Only uses piece count, no positional assessment

## 🚀 Future Enhancements

- [ ] **Stockfish Integration** - Use Stockfish engine for stronger AI
- [ ] **Opening Book** - Add opening database
- [ ] **Endgame Tablebases** - 7-piece endgame tables
- [ ] **Advanced Evaluation** - Positional scoring
- [ ] **Multiplayer Online** - Play over network
- [ ] **UI Improvements** - 3D board, animations
- [ ] **Move Hints** - Suggest best moves
- [ ] **Game Analysis** - Post-game analysis

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created by **Arslan-lab-12**

## 🙏 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

## Quick Reference

### Piece Values (for AI evaluation)
| Piece | Value |
|-------|-------|
| Pawn | 1 |
| Knight | 3 |
| Bishop | 3 |
| Rook | 5 |
| Queen | 9 |
| King | - |

### Starting Position
```
8 | ♖ | ♘ | ♗ | ♕ | ♚ | ♗ | ♘ | ♖ |  (Black)
7 | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ |
6 |   |   |   |   |   |   |   |   |
5 |   |   |   |   |   |   |   |   |
4 |   |   |   |   |   |   |   |   |
3 |   |   |   |   |   |   |   |   |
2 | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ |
1 | ♖ | ♘ | ♗ | ♕ | ♔ | ♗ | ♘ | ♖ |  (White)
  +---+---+---+---+---+---+---+---+
    a   b   c   d   e   f   g   h
```

**Enjoy playing! ♟️**
