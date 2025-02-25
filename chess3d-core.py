import numpy as np
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set

class PieceType(Enum):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()
    
class Color(Enum):
    WHITE = auto()
    BLACK = auto()

@dataclass
class Piece:
    type: PieceType
    color: Color
    
    def __repr__(self):
        return f"{self.color.name[0]}{self.type.name[0]}"

@dataclass
class Position:
    level: int  # Z coordinate (0-2)
    rank: int   # Y coordinate (0-7)
    file: int   # X coordinate (0-7)
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return (self.level == other.level and 
                self.rank == other.rank and 
                self.file == other.file)
    
    def __hash__(self):
        return hash((self.level, self.rank, self.file))
    
    def __repr__(self):
        level_char = chr(ord('A') + self.level)
        file_char = chr(ord('a') + self.file)
        rank_char = str(self.rank + 1)
        return f"{level_char}{file_char}{rank_char}"

@dataclass
class Move:
    from_pos: Position
    to_pos: Position
    promotion: Optional[PieceType] = None
    
    def __repr__(self):
        result = f"{self.from_pos}->{self.to_pos}"
        if self.promotion:
            result += f"={self.promotion.name[0]}"
        return result

class Chess3D:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Initialize 3D board: 3 levels, 8 ranks, 8 files
        self.board = np.full((3, 8, 8), None, dtype=object)
        self.current_player = Color.WHITE
        self.move_history = []
        self.setup_pieces()
    
    def setup_pieces(self):
        # Level 0 (bottom) - White pieces
        self.setup_standard_board(0, Color.WHITE)
        
        # Level 2 (top) - Black pieces
        self.setup_standard_board(2, Color.BLACK)
    
    def setup_standard_board(self, level: int, color: Color):
        back_rank = 0 if color == Color.WHITE else 7
        pawn_rank = 1 if color == Color.WHITE else 6
        
        # Back rank pieces
        piece_order = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        
        for file in range(8):
            # Set back rank
            self.board[level, back_rank, file] = Piece(piece_order[file], color)
            
            # Set pawns
            self.board[level, pawn_rank, file] = Piece(PieceType.PAWN, color)
    
    def get_piece(self, pos: Position) -> Optional[Piece]:
        return self.board[pos.level, pos.rank, pos.file]
    
    def set_piece(self, pos: Position, piece: Optional[Piece]):
        self.board[pos.level, pos.rank, pos.file] = piece
    
    def is_valid_position(self, pos: Position) -> bool:
        return (0 <= pos.level < 3 and 
                0 <= pos.rank < 8 and 
                0 <= pos.file < 8)
    
    def make_move(self, move: Move) -> bool:
        piece = self.get_piece(move.from_pos)
        
        if not piece or piece.color != self.current_player:
            return False
        
        valid_moves = self.get_valid_moves(move.from_pos)
        if move not in valid_moves:
            return False
        
        # Execute move
        captured_piece = self.get_piece(move.to_pos)
        self.set_piece(move.to_pos, piece)
        self.set_piece(move.from_pos, None)
        
        # Handle promotion
        if (move.promotion and 
            piece.type == PieceType.PAWN and 
            ((piece.color == Color.WHITE and move.to_pos.rank == 7) or
             (piece.color == Color.BLACK and move.to_pos.rank == 0))):
            self.set_piece(move.to_pos, Piece(move.promotion, piece.color))
        
        # Record move
        self.move_history.append((move, captured_piece))
        
        # Switch player
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
        return True
    
    def undo_move(self) -> bool:
        if not self.move_history:
            return False
        
        move, captured_piece = self.move_history.pop()
        piece = self.get_piece(move.to_pos)
        
        # Restore board state
        self.set_piece(move.from_pos, piece)
        self.set_piece(move.to_pos, captured_piece)
        
        # Switch back to previous player
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
        return True
    
    def get_valid_moves(self, pos: Position) -> List[Move]:
        piece = self.get_piece(pos)
        if not piece:
            return []
        
        moves = []
        
        if piece.type == PieceType.PAWN:
            moves.extend(self._get_pawn_moves(pos, piece))
        elif piece.type == PieceType.KNIGHT:
            moves.extend(self._get_knight_moves(pos, piece))
        elif piece.type == PieceType.BISHOP:
            moves.extend(self._get_bishop_moves(pos, piece))
        elif piece.type == PieceType.ROOK:
            moves.extend(self._get_rook_moves(pos, piece))
        elif piece.type == PieceType.QUEEN:
            moves.extend(self._get_queen_moves(pos, piece))
        elif piece.type == PieceType.KING:
            moves.extend(self._get_king_moves(pos, piece))
        
        # Add special 3D moves between levels
        moves.extend(self._get_3d_moves(pos, piece))
        
        return moves
    
    def _get_pawn_moves(self, pos: Position, piece: Piece) -> List[Move]:
        moves = []
        direction = 1 if piece.color == Color.WHITE else -1
        start_rank = 1 if piece.color == Color.WHITE else 6
        
        # Forward move
        new_pos = Position(pos.level, pos.rank + direction, pos.file)
        if self.is_valid_position(new_pos) and not self.get_piece(new_pos):
            # Check for promotion
            if (new_pos.rank == 7 and piece.color == Color.WHITE) or (new_pos.rank == 0 and piece.color == Color.BLACK):
                for promotion_type in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                    moves.append(Move(pos, new_pos, promotion_type))
            else:
                moves.append(Move(pos, new_pos))
            
            # Double move from starting position
            if pos.rank == start_rank:
                new_pos = Position(pos.level, pos.rank + 2 * direction, pos.file)
                if self.is_valid_position(new_pos) and not self.get_piece(new_pos):
                    moves.append(Move(pos, new_pos))
        
        # Capture moves
        for file_offset in [-1, 1]:
            new_pos = Position(pos.level, pos.rank + direction, pos.file + file_offset)
            if self.is_valid_position(new_pos):
                target = self.get_piece(new_pos)
                if target and target.color != piece.color:
                    if (new_pos.rank == 7 and piece.color == Color.WHITE) or (new_pos.rank == 0 and piece.color == Color.BLACK):
                        for promotion_type in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                            moves.append(Move(pos, new_pos, promotion_type))
                    else:
                        moves.append(Move(pos, new_pos))
        
        return moves
    
    def _get_knight_moves(self, pos: Position, piece: Piece) -> List[Move]:
        moves = []
        offsets = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
        
        for rank_offset, file_offset in offsets:
            new_pos = Position(pos.level, pos.rank + rank_offset, pos.file + file_offset)
            if self.is_valid_position(new_pos):
                target = self.get_piece(new_pos)
                if not target or target.color != piece.color:
                    moves.append(Move(pos, new_pos))
        
        return moves
    
    def _get_sliding_moves(self, pos: Position, piece: Piece, directions) -> List[Move]:
        moves = []
        
        for direction in directions:
            for distance in range(1, 8):
                new_pos = Position(
                    pos.level,
                    pos.rank + direction[0] * distance,
                    pos.file + direction[1] * distance
                )
                
                if not self.is_valid_position(new_pos):
                    break
                
                target = self.get_piece(new_pos)
                if not target:
                    moves.append(Move(pos, new_pos))
                elif target.color != piece.color:
                    moves.append(Move(pos, new_pos))
                    break
                else:
                    break
        
        return moves
    
    def _get_bishop_moves(self, pos: Position, piece: Piece) -> List[Move]:
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._get_sliding_moves(pos, piece, directions)
    
    def _get_rook_moves(self, pos: Position, piece: Piece) -> List[Move]:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return self._get_sliding_moves(pos, piece, directions)
    
    def _get_queen_moves(self, pos: Position, piece: Piece) -> List[Move]:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self._get_sliding_moves(pos, piece, directions)
    
    def _get_king_moves(self, pos: Position, piece: Piece) -> List[Move]:
        moves = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for direction in directions:
            new_pos = Position(
                pos.level,
                pos.rank + direction[0],
                pos.file + direction[1]
            )
            
            if self.is_valid_position(new_pos):
                target = self.get_piece(new_pos)
                if not target or target.color != piece.color:
                    moves.append(Move(pos, new_pos))
        
        return moves
    
    def _get_3d_moves(self, pos: Position, piece: Piece) -> List[Move]:
        moves = []
        level_offsets = []
        
        # Define which pieces can move between levels and how
        if piece.type == PieceType.KNIGHT:
            # Knights can jump between adjacent levels with a modified L-move
            if pos.level < 2:
                level_offsets.append(1)  # Up one level
            if pos.level > 0:
                level_offsets.append(-1)  # Down one level
                
            for level_offset in level_offsets:
                for rank_offset, file_offset in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    new_pos = Position(pos.level + level_offset, pos.rank + rank_offset, pos.file + file_offset)
                    if self.is_valid_position(new_pos):
                        target = self.get_piece(new_pos)
                        if not target or target.color != piece.color:
                            moves.append(Move(pos, new_pos))
        
        elif piece.type == PieceType.BISHOP or piece.type == PieceType.QUEEN:
            # Bishops and Queens can move diagonally between levels
            if pos.level < 2:  # Can move up
                for rank_offset, file_offset in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    new_pos = Position(pos.level + 1, pos.rank + rank_offset, pos.file + file_offset)
                    if self.is_valid_position(new_pos):
                        target = self.get_piece(new_pos)
                        if not target or target.color != piece.color:
                            moves.append(Move(pos, new_pos))
            
            if pos.level > 0:  # Can move down
                for rank_offset, file_offset in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    new_pos = Position(pos.level - 1, pos.rank + rank_offset, pos.file + file_offset)
                    if self.is_valid_position(new_pos):
                        target = self.get_piece(new_pos)
                        if not target or target.color != piece.color:
                            moves.append(Move(pos, new_pos))
        
        elif piece.type == PieceType.ROOK or piece.type == PieceType.QUEEN:
            # Rooks and Queens can move vertically between levels
            if pos.level < 2:  # Can move up
                new_pos = Position(pos.level + 1, pos.rank, pos.file)
                if not self.get_piece(new_pos) or self.get_piece(new_pos).color != piece.color:
                    moves.append(Move(pos, new_pos))
            
            if pos.level > 0:  # Can move down
                new_pos = Position(pos.level - 1, pos.rank, pos.file)
                if not self.get_piece(new_pos) or self.get_piece(new_pos).color != piece.color:
                    moves.append(Move(pos, new_pos))
        
        return moves
    
    def is_check(self, color: Color) -> bool:
        king_pos = None
        
        # Find the king
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    piece = self.board[level, rank, file]
                    if piece and piece.type == PieceType.KING and piece.color == color:
                        king_pos = Position(level, rank, file)
                        break
                if king_pos:
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
        
        # Check if any opponent piece can capture the king
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    pos = Position(level, rank, file)
                    piece = self.get_piece(pos)
                    if piece and piece.color == opponent_color:
                        for move in self.get_valid_moves(pos):
                            if move.to_pos == king_pos:
                                return True
        
        return False
    
    def is_checkmate(self, color: Color) -> bool:
        if not self.is_check(color):
            return False
        
        # Try all possible moves to see if any can get out of check
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    pos = Position(level, rank, file)
                    piece = self.get_piece(pos)
                    if piece and piece.color == color:
                        for move in self.get_valid_moves(pos):
                            # Try the move
                            captured_piece = self.get_piece(move.to_pos)
                            self.set_piece(move.to_pos, piece)
                            self.set_piece(pos, None)
                            
                            # Check if still in check
                            still_in_check = self.is_check(color)
                            
                            # Undo the move
                            self.set_piece(pos, piece)
                            self.set_piece(move.to_pos, captured_piece)
                            
                            if not still_in_check:
                                return False
        
        return True
    
    def get_board_state(self) -> Dict:
        pieces = {}
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    piece = self.board[level, rank, file]
                    if piece:
                        pos = Position(level, rank, file)
                        pieces[str(pos)] = str(piece)
        
        return {
            "pieces": pieces,
            "current_player": self.current_player.name,
            "move_count": len(self.move_history)
        }
