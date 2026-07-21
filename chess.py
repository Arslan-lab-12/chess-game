"""
Chess Game Implementation in Python
A complete chess game with board representation, move validation, and game logic.
"""

from enum import Enum
from typing import List, Tuple, Optional

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Color(Enum):
    WHITE = 1
    BLACK = 2

class Piece:
    """Represents a chess piece."""
    
    def __init__(self, piece_type: PieceType, color: Color):
        self.type = piece_type
        self.color = color
    
    def __repr__(self):
        symbols = {
            PieceType.PAWN: '♟' if self.color == Color.BLACK else '♙',
            PieceType.KNIGHT: '♞' if self.color == Color.BLACK else '♘',
            PieceType.BISHOP: '♝' if self.color == Color.BLACK else '♗',
            PieceType.ROOK: '♜' if self.color == Color.BLACK else '♖',
            PieceType.QUEEN: '♛' if self.color == Color.BLACK else '♕',
            PieceType.KING: '♚' if self.color == Color.BLACK else '♔',
        }
        return symbols[self.type]

class Board:
    """Represents the chess board."""
    
    def __init__(self):
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
    
    def setup_board(self):
        """Initialize the chess board with pieces in starting position."""
        # Place pawns
        for col in range(8):
            self.squares[1][col] = Piece(PieceType.PAWN, Color.WHITE)
            self.squares[6][col] = Piece(PieceType.PAWN, Color.BLACK)
        
        # Define back row pieces
        back_row = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP,
            PieceType.QUEEN, PieceType.KING, PieceType.BISHOP,
            PieceType.KNIGHT, PieceType.ROOK
        ]
        
        # Place white back row
        for col, piece_type in enumerate(back_row):
            self.squares[0][col] = Piece(piece_type, Color.WHITE)
        
        # Place black back row
        for col, piece_type in enumerate(back_row):
            self.squares[7][col] = Piece(piece_type, Color.BLACK)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.squares[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            self.squares[row][col] = piece
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is valid."""
        return 0 <= row < 8 and 0 <= col < 8
    
    def display(self):
        """Display the board."""
        print("\n    0   1   2   3   4   5   6   7")
        print("  " + "+" + "-" * 31 + "+")
        
        for row in range(7, -1, -1):
            print(f"{row} |", end="")
            for col in range(8):
                piece = self.squares[row][col]
                if piece:
                    print(f" {piece} |", end="")
                else:
                    print("   |", end="")
            print()
            print("  " + "+" + "-" * 31 + "+")

class ChessGame:
    """Main chess game class."""
    
    def __init__(self):
        self.board = Board()
        self.current_player = Color.WHITE
        self.move_history = []
        self.captured_pieces = []
    
    def switch_player(self):
        """Switch to the other player."""
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
    
    def is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a move is valid."""
        # Check if source position is valid
        if not self.board.is_valid_position(from_row, from_col):
            return False
        
        piece = self.board.get_piece(from_row, from_col)
        if not piece or piece.color != self.current_player:
            return False
        
        # Check if destination is valid
        if not self.board.is_valid_position(to_row, to_col):
            return False
        
        # Can't capture own piece
        target = self.board.get_piece(to_row, to_col)
        if target and target.color == self.current_player:
            return False
        
        # Check piece-specific move rules
        return self.is_legal_move(piece, from_row, from_col, to_row, to_col)
    
    def is_legal_move(self, piece: Piece, from_row: int, from_col: int, 
                     to_row: int, to_col: int) -> bool:
        """Check if move is legal based on piece type."""
        
        if piece.type == PieceType.PAWN:
            return self.is_legal_pawn_move(piece.color, from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.KNIGHT:
            return self.is_legal_knight_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.BISHOP:
            return self.is_legal_bishop_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.ROOK:
            return self.is_legal_rook_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.QUEEN:
            return self.is_legal_queen_move(from_row, from_col, to_row, to_col)
        elif piece.type == PieceType.KING:
            return self.is_legal_king_move(from_row, from_col, to_row, to_col)
        
        return False
    
    def is_legal_pawn_move(self, color: Color, from_row: int, from_col: int,
                          to_row: int, to_col: int) -> bool:
        """Check legal pawn moves."""
        direction = -1 if color == Color.WHITE else 1
        start_row = 1 if color == Color.WHITE else 6
        
        # Forward move
        if from_col == to_col:
            if to_row == from_row + direction:
                return self.board.get_piece(to_row, to_col) is None
            
            # Two squares forward from start
            if from_row == start_row and to_row == from_row + 2 * direction:
                return (self.board.get_piece(to_row, to_col) is None and
                        self.board.get_piece(from_row + direction, from_col) is None)
        
        # Capture diagonally
        if abs(to_col - from_col) == 1 and to_row == from_row + direction:
            target = self.board.get_piece(to_row, to_col)
            return target is not None and target.color != self.current_player
        
        return False
    
    def is_legal_knight_move(self, from_row: int, from_col: int,
                            to_row: int, to_col: int) -> bool:
        """Check legal knight moves."""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
    def is_legal_bishop_move(self, from_row: int, from_col: int,
                            to_row: int, to_col: int) -> bool:
        """Check legal bishop moves."""
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        return self.is_path_clear(from_row, from_col, to_row, to_col)
    
    def is_legal_rook_move(self, from_row: int, from_col: int,
                          to_row: int, to_col: int) -> bool:
        """Check legal rook moves."""
        if from_row != to_row and from_col != to_col:
            return False
        return self.is_path_clear(from_row, from_col, to_row, to_col)
    
    def is_legal_queen_move(self, from_row: int, from_col: int,
                           to_row: int, to_col: int) -> bool:
        """Check legal queen moves."""
        # Queen moves like rook or bishop
        if from_row == to_row or from_col == to_col:
            return self.is_legal_rook_move(from_row, from_col, to_row, to_col)
        elif abs(to_row - from_row) == abs(to_col - from_col):
            return self.is_legal_bishop_move(from_row, from_col, to_row, to_col)
        return False
    
    def is_legal_king_move(self, from_row: int, from_col: int,
                          to_row: int, to_col: int) -> bool:
        """Check legal king moves."""
        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
    
    def is_path_clear(self, from_row: int, from_col: int,
                     to_row: int, to_col: int) -> bool:
        """Check if path between two squares is clear."""
        row_step = 0 if to_row == from_row else (1 if to_row > from_row else -1)
        col_step = 0 if to_col == from_col else (1 if to_col > from_col else -1)
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while (current_row, current_col) != (to_row, to_col):
            if self.board.get_piece(current_row, current_col) is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Make a move on the board."""
        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            return False
        
        piece = self.board.get_piece(from_row, from_col)
        target = self.board.get_piece(to_row, to_col)
        
        # Record move
        self.move_history.append((from_row, from_col, to_row, to_col, piece, target))
        
        # Capture piece if target exists
        if target:
            self.captured_pieces.append(target)
        
        # Move piece
        self.board.set_piece(from_row, from_col, None)
        self.board.set_piece(to_row, to_col, piece)
        
        self.switch_player()
        return True
    
    def undo_move(self) -> bool:
        """Undo the last move."""
        if not self.move_history:
            return False
        
        from_row, from_col, to_row, to_col, piece, target = self.move_history.pop()
        
        # Restore piece to original position
        self.board.set_piece(from_row, from_col, piece)
        self.board.set_piece(to_row, to_col, target)
        
        # Remove from captured pieces if there was a capture
        if target:
            self.captured_pieces.pop()
        
        self.switch_player()
        return True
    
    def get_possible_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all possible moves for a piece at given position."""
        moves = []
        piece = self.board.get_piece(row, col)
        
        if not piece or piece.color != self.current_player:
            return moves
        
        for to_row in range(8):
            for to_col in range(8):
                if self.is_valid_move(row, col, to_row, to_col):
                    moves.append((to_row, to_col))
        
        return moves
    
    def display_game(self):
        """Display current game state."""
        print("\n" + "="*35)
        print(f"Current Player: {self.current_player.name}")
        print("="*35)
        self.board.display()
        print(f"\nCaptured pieces: {[str(p) for p in self.captured_pieces]}")
        print(f"Moves played: {len(self.move_history)}")

def parse_position(pos_str: str) -> Optional[Tuple[int, int]]:
    """Parse position string like 'a1' to coordinates."""
    if len(pos_str) != 2:
        return None
    
    col = ord(pos_str[0].lower()) - ord('a')
    row = int(pos_str[1]) - 1
    
    if 0 <= col < 8 and 0 <= row < 8:
        return (row, col)
    return None

def play_game():
    """Main game loop for playing chess."""
    game = ChessGame()
    game.display_game()
    
    while True:
        try:
            command = input("\nEnter move (e.g., 'e2 e4') or command: ").strip().lower()
            
            if command == 'quit' or command == 'q':
                print("Thanks for playing!")
                break
            
            if command == 'undo':
                if game.undo_move():
                    print("Move undone.")
                    game.display_game()
                else:
                    print("No moves to undo.")
                continue
            
            if command == 'help':
                print("Commands:")
                print("  'e2 e4' - Move piece from e2 to e4")
                print("  'undo'  - Undo last move")
                print("  'help'  - Show this help")
                print("  'quit'  - Exit game")
                continue
            
            parts = command.split()
            if len(parts) != 2:
                print("Invalid command. Use 'e2 e4' format or 'help' for commands.")
                continue
            
            from_pos = parse_position(parts[0])
            to_pos = parse_position(parts[1])
            
            if not from_pos or not to_pos:
                print("Invalid positions. Use a-h for columns and 1-8 for rows.")
                continue
            
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            if game.make_move(from_row, from_col, to_row, to_col):
                game.display_game()
            else:
                print("Invalid move. Try again.")
                possible = game.get_possible_moves(from_row, from_col)
                if possible:
                    print(f"Possible moves: {[(8-r, chr(97+c)) for r, c in possible]}")
        
        except KeyboardInterrupt:
            print("\nGame interrupted. Thanks for playing!")
            break
        except Exception as e:
            print(f"Error: {e}. Please try again.")

if __name__ == "__main__":
    play_game()
