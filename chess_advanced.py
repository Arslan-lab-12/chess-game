"""
Advanced Chess Game Implementation in Python
Features: AI opponent, check/checkmate detection, castling, en passant, piece promotion,
save/load games, time controls, and more.
"""

import json
import os
from enum import Enum
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
import time
from copy import deepcopy

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

class GameMode(Enum):
    PVP = 1  # Player vs Player
    PVC = 2  # Player vs Computer
    TIMED = 3  # Timed game

class Piece:
    """Represents a chess piece."""
    
    def __init__(self, piece_type: PieceType, color: Color):
        self.type = piece_type
        self.color = color
        self.has_moved = False  # For castling and en passant
    
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
    
    def to_dict(self):
        return {
            'type': self.type.name,
            'color': self.color.name,
            'has_moved': self.has_moved
        }
    
    @staticmethod
    def from_dict(data):
        piece = Piece(PieceType[data['type']], Color[data['color']])
        piece.has_moved = data['has_moved']
        return piece

class Board:
    """Represents the chess board."""
    
    def __init__(self):
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.en_passant_target = None  # For en passant moves
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
        print("\n    a   b   c   d   e   f   g   h")
        print("  " + "+" + "-" * 31 + "+")
        
        for row in range(7, -1, -1):
            print(f"{row+1} |", end="")
            for col in range(8):
                piece = self.squares[row][col]
                if piece:
                    print(f" {piece} |", end="")
                else:
                    print("   |", end="")
            print()
            print("  " + "+" + "-" * 31 + "+")
    
    def to_dict(self):
        """Convert board to dictionary for saving."""
        board_data = []
        for row in self.squares:
            row_data = []
            for piece in row:
                if piece:
                    row_data.append(piece.to_dict())
                else:
                    row_data.append(None)
            board_data.append(row_data)
        return {
            'squares': board_data,
            'en_passant_target': self.en_passant_target
        }
    
    @staticmethod
    def from_dict(data):
        """Create board from dictionary."""
        board = Board()
        board.squares = [[None for _ in range(8)] for _ in range(8)]
        
        for row_idx, row in enumerate(data['squares']):
            for col_idx, piece_data in enumerate(row):
                if piece_data:
                    board.squares[row_idx][col_idx] = Piece.from_dict(piece_data)
        
        board.en_passant_target = data.get('en_passant_target')
        return board

class ChessGame:
    """Main chess game class with advanced features."""
    
    def __init__(self, game_mode: GameMode = GameMode.PVP, time_limit: int = 300):
        self.board = Board()
        self.current_player = Color.WHITE
        self.move_history = []
        self.captured_pieces = []
        self.game_mode = game_mode
        self.ai_color = Color.BLACK if game_mode == GameMode.PVC else None
        
        # Time controls
        self.time_limit = time_limit  # in seconds
        self.white_time = time_limit
        self.black_time = time_limit
        self.last_time_check = time.time()
        
        # Game state
        self.is_checkmate = False
        self.is_stalemate = False
        self.is_check = False
        self.game_over = False
        self.winner = None
    
    def switch_player(self):
        """Switch to the other player."""
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        self.last_time_check = time.time()
    
    def update_time(self):
        """Update remaining time for current player."""
        if self.game_mode != GameMode.TIMED:
            return
        
        elapsed = time.time() - self.last_time_check
        if self.current_player == Color.WHITE:
            self.white_time -= elapsed
        else:
            self.black_time -= elapsed
        
        self.last_time_check = time.time()
        
        if self.white_time <= 0 or self.black_time <= 0:
            self.end_game("Time's up!")
    
    def find_king(self, color: Color) -> Optional[Tuple[int, int]]:
        """Find king position on board."""
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.type == PieceType.KING and piece.color == color:
                    return (row, col)
        return None
    
    def is_square_attacked(self, row: int, col: int, by_color: Color) -> bool:
        """Check if a square is attacked by a color."""
        for attack_row in range(8):
            for attack_col in range(8):
                piece = self.board.get_piece(attack_row, attack_col)
                if piece and piece.color == by_color:
                    if self.can_piece_attack(attack_row, attack_col, row, col):
                        return True
        return False
    
    def can_piece_attack(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a piece can attack a square (ignoring turn rules)."""
        piece = self.board.get_piece(from_row, from_col)
        if not piece:
            return False
        
        target = self.board.get_piece(to_row, to_col)
        
        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            return (to_row == from_row + direction and 
                   abs(to_col - from_col) == 1)
        
        elif piece.type == PieceType.KNIGHT:
            row_diff = abs(to_row - from_row)
            col_diff = abs(to_col - from_col)
            return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
        
        elif piece.type == PieceType.BISHOP:
            if abs(to_row - from_row) != abs(to_col - from_col):
                return False
            return self.is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece.type == PieceType.ROOK:
            if from_row != to_row and from_col != to_col:
                return False
            return self.is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece.type == PieceType.QUEEN:
            if from_row == to_row or from_col == to_col:
                return self.is_path_clear(from_row, from_col, to_row, to_col)
            elif abs(to_row - from_row) == abs(to_col - from_col):
                return self.is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece.type == PieceType.KING:
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
        
        return False
    
    def is_in_check(self, color: Color) -> bool:
        """Check if a color's king is in check."""
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(king_pos[0], king_pos[1], enemy_color)
    
    def is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a move is valid."""
        if not self.board.is_valid_position(from_row, from_col):
            return False
        
        piece = self.board.get_piece(from_row, from_col)
        if not piece or piece.color != self.current_player:
            return False
        
        if not self.board.is_valid_position(to_row, to_col):
            return False
        
        target = self.board.get_piece(to_row, to_col)
        if target and target.color == self.current_player:
            return False
        
        # Check legal move
        if not self.is_legal_move(piece, from_row, from_col, to_row, to_col):
            return False
        
        # Make temporary move to check if king would be in check
        temp_board = deepcopy(self.board)
        temp_piece = self.board.get_piece(from_row, from_col)
        self.board.set_piece(from_row, from_col, None)
        self.board.set_piece(to_row, to_col, temp_piece)
        
        in_check = self.is_in_check(self.current_player)
        
        self.board = temp_board
        
        return not in_check
    
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
            return (self.is_legal_king_move(from_row, from_col, to_row, to_col) or
                   self.is_legal_castling(from_row, from_col, to_row, to_col))
        
        return False
    
    def is_legal_pawn_move(self, color: Color, from_row: int, from_col: int,
                          to_row: int, to_col: int) -> bool:
        """Check legal pawn moves (includes en passant)."""
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
            if target is not None:
                return target.color != self.current_player
            
            # En passant
            if self.board.en_passant_target == (to_row, to_col):
                return True
        
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
        if from_row == to_row or from_col == to_col:
            return self.is_legal_rook_move(from_row, from_col, to_row, to_col)
        elif abs(to_row - from_row) == abs(to_col - from_col):
            return self.is_legal_bishop_move(from_row, from_col, to_row, to_col)
        return False
    
    def is_legal_king_move(self, from_row: int, from_col: int,
                          to_row: int, to_col: int) -> bool:
        """Check legal king moves."""
        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
    
    def is_legal_castling(self, from_row: int, from_col: int,
                         to_row: int, to_col: int) -> bool:
        """Check legal castling moves."""
        king = self.board.get_piece(from_row, from_col)
        if king.has_moved or from_row != to_row or abs(to_col - from_col) != 2:
            return False
        
        # Check if king is in check
        if self.is_in_check(self.current_player):
            return False
        
        # Check rook
        rook_col = 7 if to_col > from_col else 0
        rook = self.board.get_piece(from_row, rook_col)
        if not rook or rook.type != PieceType.ROOK or rook.has_moved:
            return False
        
        # Check path is clear
        min_col, max_col = min(from_col, rook_col), max(from_col, rook_col)
        for col in range(min_col + 1, max_col):
            if self.board.get_piece(from_row, col) is not None:
                return False
        
        # Check if king passes through attacked square
        step = 1 if to_col > from_col else -1
        for col in range(from_col, to_col + step, step):
            if self.is_square_attacked(from_row, col, 
                                      Color.BLACK if self.current_player == Color.WHITE else Color.WHITE):
                return False
        
        return True
    
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
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> Tuple[bool, str]:
        """Make a move on the board."""
        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            return False, "Invalid move"
        
        piece = self.board.get_piece(from_row, from_col)
        target = self.board.get_piece(to_row, to_col)
        
        move_notation = f"{chr(97+from_col)}{from_row+1} {chr(97+to_col)}{to_row+1}"
        
        # Handle en passant
        if piece.type == PieceType.PAWN and self.board.en_passant_target == (to_row, to_col):
            capture_row = from_row
            capture_piece = self.board.get_piece(capture_row, to_col)
            self.board.set_piece(capture_row, to_col, None)
            self.captured_pieces.append(capture_piece)
            move_notation += " (en passant)"
        
        # Handle castling
        if piece.type == PieceType.KING and abs(to_col - from_col) == 2:
            rook_col = 7 if to_col > from_col else 0
            new_rook_col = 5 if to_col > from_col else 3
            rook = self.board.get_piece(from_row, rook_col)
            self.board.set_piece(from_row, rook_col, None)
            self.board.set_piece(from_row, new_rook_col, rook)
            rook.has_moved = True
            move_notation += " (castling)"
        
        # Record move
        self.move_history.append((from_row, from_col, to_row, to_col, deepcopy(piece), target))
        
        # Capture piece if target exists (and not en passant)
        if target:
            self.captured_pieces.append(target)
        
        # Move piece
        piece.has_moved = True
        self.board.set_piece(from_row, from_col, None)
        self.board.set_piece(to_row, to_col, piece)
        
        # Handle pawn promotion
        promotion_piece = None
        if piece.type == PieceType.PAWN:
            if (piece.color == Color.WHITE and to_row == 7) or (piece.color == Color.BLACK and to_row == 0):
                promotion_piece = self.promote_pawn(to_row, to_col)
                move_notation += f" (promoted to {promotion_piece.type.name})"
        
        # Set en passant target
        if piece.type == PieceType.PAWN and abs(to_row - from_row) == 2:
            self.board.en_passant_target = (from_row + (to_row - from_row) // 2, from_col)
        else:
            self.board.en_passant_target = None
        
        self.switch_player()
        
        # Check for check, checkmate, stalemate
        self.update_game_state()
        
        return True, move_notation
    
    def promote_pawn(self, row: int, col: int) -> Piece:
        """Promote pawn to another piece."""
        print("\nPawn promotion! Choose:")
        print("1. Queen")
        print("2. Rook")
        print("3. Bishop")
        print("4. Knight")
        
        choice = input("Enter choice (1-4): ").strip()
        
        piece_map = {
            '1': PieceType.QUEEN,
            '2': PieceType.ROOK,
            '3': PieceType.BISHOP,
            '4': PieceType.KNIGHT
        }
        
        piece_type = piece_map.get(choice, PieceType.QUEEN)
        pawn = self.board.get_piece(row, col)
        new_piece = Piece(piece_type, pawn.color)
        new_piece.has_moved = True
        self.board.set_piece(row, col, new_piece)
        
        return new_piece
    
    def update_game_state(self):
        """Update check, checkmate, and stalemate status."""
        if self.is_in_check(self.current_player):
            self.is_check = True
            if not self.has_legal_moves():
                self.is_checkmate = True
                self.game_over = True
                enemy = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
                self.winner = enemy
        else:
            self.is_check = False
            if not self.has_legal_moves():
                self.is_stalemate = True
                self.game_over = True
    
    def has_legal_moves(self) -> bool:
        """Check if current player has any legal moves."""
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == self.current_player:
                    for to_row in range(8):
                        for to_col in range(8):
                            if self.is_valid_move(row, col, to_row, to_col):
                                return True
        return False
    
    def undo_move(self) -> bool:
        """Undo the last move."""
        if not self.move_history:
            return False
        
        from_row, from_col, to_row, to_col, piece, target = self.move_history.pop()
        
        self.board.set_piece(from_row, from_col, piece)
        self.board.set_piece(to_row, to_col, target)
        
        if target:
            self.captured_pieces.pop()
        
        self.switch_player()
        self.is_check = False
        self.is_checkmate = False
        self.is_stalemate = False
        self.game_over = False
        
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
    
    def get_board_evaluation(self) -> float:
        """Evaluate the board position (for AI)."""
        piece_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 0
        }
        
        evaluation = 0
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    value = piece_values[piece.type]
                    if piece.color == self.ai_color:
                        evaluation += value
                    else:
                        evaluation -= value
        
        return evaluation
    
    def minimax(self, depth: int, maximizing: bool, alpha: float = float('-inf'), 
               beta: float = float('inf')) -> Tuple[float, Optional[Tuple]]:
        """Minimax algorithm with alpha-beta pruning for AI."""
        if depth == 0 or self.game_over:
            return self.get_board_evaluation(), None
        
        best_move = None
        
        if maximizing:
            max_eval = float('-inf')
            for row in range(8):
                for col in range(8):
                    piece = self.board.get_piece(row, col)
                    if piece and piece.color == self.ai_color:
                        for to_row, to_col in self.get_possible_moves(row, col):
                            # Make move
                            target = self.board.get_piece(to_row, to_col)
                            self.board.set_piece(row, col, None)
                            self.board.set_piece(to_row, to_col, piece)
                            self.switch_player()
                            self.update_game_state()
                            
                            eval, _ = self.minimax(depth - 1, False, alpha, beta)
                            
                            # Undo move
                            self.board.set_piece(to_row, to_col, target)
                            self.board.set_piece(row, col, piece)
                            self.switch_player()
                            self.is_check = False
                            self.is_checkmate = False
                            self.is_stalemate = False
                            self.game_over = False
                            
                            if eval > max_eval:
                                max_eval = eval
                                best_move = (row, col, to_row, to_col)
                            
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            enemy_color = Color.BLACK if self.ai_color == Color.WHITE else Color.WHITE
            for row in range(8):
                for col in range(8):
                    piece = self.board.get_piece(row, col)
                    if piece and piece.color == enemy_color:
                        for to_row, to_col in self.get_possible_moves(row, col):
                            # Make move
                            target = self.board.get_piece(to_row, to_col)
                            self.board.set_piece(row, col, None)
                            self.board.set_piece(to_row, to_col, piece)
                            self.switch_player()
                            self.update_game_state()
                            
                            eval, _ = self.minimax(depth - 1, True, alpha, beta)
                            
                            # Undo move
                            self.board.set_piece(to_row, to_col, target)
                            self.board.set_piece(row, col, piece)
                            self.switch_player()
                            self.is_check = False
                            self.is_checkmate = False
                            self.is_stalemate = False
                            self.game_over = False
                            
                            if eval < min_eval:
                                min_eval = eval
                                best_move = (row, col, to_row, to_col)
                            
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
            
            return min_eval, best_move
    
    def ai_move(self, depth: int = 3) -> Tuple[bool, str]:
        """Get AI's best move using minimax."""
        _, best_move = self.minimax(depth, True)
        
        if best_move:
            from_row, from_col, to_row, to_col = best_move
            return self.make_move(from_row, from_col, to_row, to_col)
        
        return False, "No moves available"
    
    def save_game(self, filename: str = "chess_game.json"):
        """Save game to file."""
        game_data = {
            'board': self.board.to_dict(),
            'current_player': self.current_player.name,
            'move_history': [(r, c, tr, tc, p.to_dict() if p else None, t.to_dict() if t else None)
                           for r, c, tr, tc, p, t in self.move_history],
            'captured_pieces': [p.to_dict() for p in self.captured_pieces],
            'game_mode': self.game_mode.name,
            'is_checkmate': self.is_checkmate,
            'is_stalemate': self.is_stalemate,
            'is_check': self.is_check,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(game_data, f, indent=2)
        
        print(f"Game saved to {filename}")
    
    @staticmethod
    def load_game(filename: str = "chess_game.json") -> 'ChessGame':
        """Load game from file."""
        if not os.path.exists(filename):
            print(f"File {filename} not found")
            return None
        
        with open(filename, 'r') as f:
            game_data = json.load(f)
        
        game = ChessGame(GameMode[game_data['game_mode']])
        game.board = Board.from_dict(game_data['board'])
        game.current_player = Color[game_data['current_player']]
        game.is_checkmate = game_data['is_checkmate']
        game.is_stalemate = game_data['is_stalemate']
        game.is_check = game_data['is_check']
        
        print(f"Game loaded from {filename} (saved at {game_data['timestamp']})")
        return game
    
    def display_game(self):
        """Display current game state."""
        print("\n" + "="*50)
        print(f"Current Player: {self.current_player.name}")
        
        if self.is_check:
            print("⚠️  CHECK!")
        if self.is_checkmate:
            print("🏆 CHECKMATE! Game Over!")
        if self.is_stalemate:
            print("⚖️  STALEMATE! Game is a draw.")
        
        if self.game_mode == GameMode.TIMED:
            print(f"Time - White: {self.white_time:.1f}s | Black: {self.black_time:.1f}s")
        
        print("="*50)
        self.board.display()
        print(f"\nCaptured pieces: {[str(p) for p in self.captured_pieces]}")
        print(f"Moves: {len(self.move_history)}")

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
    print("♟️  Welcome to Advanced Chess! ♟️")
    print("\nGame Modes:")
    print("1. Player vs Player")
    print("2. Player vs Computer (AI)")
    print("3. Timed Game (5 min each)")
    
    mode_choice = input("Choose game mode (1-3): ").strip()
    
    game_mode = {
        '1': GameMode.PVP,
        '2': GameMode.PVC,
        '3': GameMode.TIMED
    }.get(mode_choice, GameMode.PVP)
    
    game = ChessGame(game_mode, time_limit=300)
    game.display_game()
    
    while not game.game_over:
        try:
            game.update_time()
            
            if game.game_mode == GameMode.PVC and game.current_player == game.ai_color:
                print(f"\n{game.current_player.name} (AI) is thinking...")
                time.sleep(1)
                success, move = game.ai_move(depth=2)
                if success:
                    print(f"AI played: {move}")
                else:
                    print("AI has no legal moves")
                game.display_game()
                continue
            
            command = input("\nEnter move (e.g., 'a2 a4') or command: ").strip().lower()
            
            if command == 'quit' or command == 'q':
                save_choice = input("Save game before quitting? (y/n): ").strip().lower()
                if save_choice == 'y':
                    game.save_game()
                print("Thanks for playing!")
                break
            
            if command == 'save':
                game.save_game()
                continue
            
            if command == 'load':
                loaded_game = ChessGame.load_game()
                if loaded_game:
                    game = loaded_game
                    game.display_game()
                continue
            
            if command == 'undo':
                if game.undo_move():
                    print("Move undone.")
                    game.display_game()
                else:
                    print("No moves to undo.")
                continue
            
            if command == 'help':
                print("\nCommands:")
                print("  'a2 a4'    - Move piece from a2 to a4")
                print("  'undo'     - Undo last move")
                print("  'save'     - Save game")
                print("  'load'     - Load game")
                print("  'help'     - Show this help")
                print("  'quit'     - Exit game")
                continue
            
            parts = command.split()
            if len(parts) != 2:
                print("Invalid command. Use 'a2 a4' format or 'help' for commands.")
                continue
            
            from_pos = parse_position(parts[0])
            to_pos = parse_position(parts[1])
            
            if not from_pos or not to_pos:
                print("Invalid positions. Use a-h for columns and 1-8 for rows.")
                continue
            
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            success, message = game.make_move(from_row, from_col, to_row, to_col)
            if success:
                game.display_game()
                
                if game.is_checkmate:
                    print(f"\n🏆 Checkmate! {game.winner.name if game.winner else 'Draw'} wins!")
                elif game.is_stalemate:
                    print("\n⚖️  Stalemate! Game is a draw.")
                elif game.is_check:
                    print("\n⚠️  Check!")
            else:
                print(f"Invalid move: {message}")
                possible = game.get_possible_moves(from_row, from_col)
                if possible:
                    print(f"Possible moves: {[chr(97+c)+str(r+1) for r, c in possible]}")
        
        except KeyboardInterrupt:
            print("\nGame interrupted.")
            save_choice = input("Save game before quitting? (y/n): ").strip().lower()
            if save_choice == 'y':
                game.save_game()
            print("Thanks for playing!")
            break
        except Exception as e:
            print(f"Error: {e}. Please try again.")

if __name__ == "__main__":
    play_game()
