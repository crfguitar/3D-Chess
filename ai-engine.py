import random
import time
from copy import deepcopy
from chess3d import Chess3D, Position, PieceType, Color, Move

class ChessAI:
    """Minimax-based AI engine with alpha-beta pruning for 3D chess"""
    
    # Piece value tables for evaluation
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }
    
    # Position evaluation tables (standard 2D chess)
    PAWN_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]
    
    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]
    
    BISHOP_TABLE = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5,  5,  5,  5,  5,-10],
        [-10,  0,  5,  0,  0,  5,  0,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]
    
    ROOK_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ]
    
    QUEEN_TABLE = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]
    
    KING_MIDDLE_TABLE = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]
    
    KING_END_TABLE = [
        [-50,-40,-30,-20,-20,-30,-40,-50],
        [-30,-20,-10,  0,  0,-10,-20,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-30,  0,  0,  0,  0,-30,-30],
        [-50,-30,-30,-30,-30,-30,-30,-50]
    ]
    
    def __init__(self, game, max_depth=3, time_limit=None):
        """Initialize the AI engine with game state and parameters"""
        self.game = game
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0
        self.start_time = 0
    
    def get_best_move(self, color=None):
        """Find the best move for the current position"""
        if color is None:
            color = self.game.current_player
            
        self.nodes_evaluated = 0
        self.start_time = time.time()
        
        # Create a copy of the game to avoid modifying the original
        temp_game = deepcopy(self.game)
        
        # Consider all valid moves for the current player
        best_move = None
        best_value = float('-inf') if color == Color.WHITE else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Find all valid moves for the current player
        all_moves = []
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    pos = Position(level, rank, file)
                    piece = temp_game.get_piece(pos)
                    if piece and piece.color == color:
                        moves = temp_game.get_valid_moves(pos)
                        all_moves.extend(moves)
        
        # Randomize move order for more varied play
        random.shuffle(all_moves)
        
        for move in all_moves:
            # Make move
            captured_piece = temp_game.get_piece(move.to_pos)
            piece = temp_game.get_piece(move.from_pos)
            temp_game.make_move(move)
            
            # Evaluate position after move
            if color == Color.WHITE:
                value = self.minimax(temp_game, self.max_depth - 1, alpha, beta, False)
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, value)
            else:
                value = self.minimax(temp_game, self.max_depth - 1, alpha, beta, True)
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, value)
            
            # Undo move
            temp_game.undo_move()
            
            # Check time limit
            if self.time_limit and time.time() - self.start_time > self.time_limit:
                break
        
        end_time = time.time()
        elapsed = end_time - self.start_time
        
        print(f"AI evaluation: {self.nodes_evaluated} nodes in {elapsed:.2f}s ({self.nodes_evaluated/elapsed:.0f} nodes/s)")
        print(f"Best move: {best_move}, Eval: {best_value}")
        
        return best_move
    
    def minimax(self, game, depth, alpha, beta, maximizing):
        """Minimax search with alpha-beta pruning"""
        self.nodes_evaluated += 1
        
        # Check if we've hit the time limit
        if self.time_limit and time.time() - self.start_time > self.time_limit:
            return 0
        
        # Base case: leaf node or terminal position
        if depth == 0:
            return self.evaluate_position(game)
        
        if maximizing:
            value = float('-inf')
            for level in range(3):
                for rank in range(8):
                    for file in range(8):
                        pos = Position(level, rank, file)
                        piece = game.get_piece(pos)
                        if piece and piece.color == Color.WHITE:
                            moves = game.get_valid_moves(pos)
                            for move in moves:
                                game.make_move(move)
                                value = max(value, self.minimax(game, depth - 1, alpha, beta, False))
                                game.undo_move()
                                
                                alpha = max(alpha, value)
                                if beta <= alpha:
                                    return value
            return value
        else:
            value = float('inf')
            for level in range(3):
                for rank in range(8):
                    for file in range(8):
                        pos = Position(level, rank, file)
                        piece = game.get_piece(pos)
                        if piece and piece.color == Color.BLACK:
                            moves = game.get_valid_moves(pos)
                            for move in moves:
                                game.make_move(move)
                                value = min(value, self.minimax(game, depth - 1, alpha, beta, True))
                                game.undo_move()
                                
                                beta = min(beta, value)
                                if beta <= alpha:
                                    return value
            return value
    
    def evaluate_position(self, game):
        """Evaluate the current board position"""
        if game.is_checkmate(Color.WHITE):
            return -10000
        elif game.is_checkmate(Color.BLACK):
            return 10000
        
        # Material evaluation
        score = 0
        
        # Count endgame status (for king evaluation)
        piece_count = 0
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    piece = game.get_piece(Position(level, rank, file))
                    if piece and piece.type != PieceType.KING:
                        piece_count += 1
        
        is_endgame = piece_count <= 10
        
        # Evaluate all pieces
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    pos = Position(level, rank, file)
                    piece = game.get_piece(pos)
                    if not piece:
                        continue
                    
                    # Base material value
                    value = self.PIECE_VALUES[piece.type]
                    
                    # Position evaluation for 2D chess (modified for 3D)
                    if piece.color == Color.BLACK:
                        rank_mirror = 7 - rank  # Mirror for black pieces
                    else:
                        rank_mirror = rank
                    
                    # Add positional value based on piece type
                    if piece.type == PieceType.PAWN:
                        value += self.PAWN_TABLE[rank_mirror][file]
                    elif piece.type == PieceType.KNIGHT:
                        value += self.KNIGHT_TABLE[rank_mirror][file]
                    elif piece.type == PieceType.BISHOP:
                        value += self.BISHOP_TABLE[rank_mirror][file]
                    elif piece.type == PieceType.ROOK:
                        value += self.ROOK_TABLE[rank_mirror][file]
                    elif piece.type == PieceType.QUEEN:
                        value += self.QUEEN_TABLE[rank_mirror][file]
                    elif piece.type == PieceType.KING:
                        if is_endgame:
                            value += self.KING_END_TABLE[rank_mirror][file]
                        else:
                            value += self.KING_MIDDLE_TABLE[rank_mirror][file]
                    
                    # 3D chess specific evaluation
                    if level == 1:  # Middle level is usually more valuable
                        value += 10
                    
                    # Add to score (positive for white, negative for black)
                    if piece.color == Color.WHITE:
                        score += value
                    else:
                        score -= value
        
        # Mobility evaluation (number of legal moves)
        white_mobility = 0
        black_mobility = 0
        
        for level in range(3):
            for rank in range(8):
                for file in range(8):
                    pos = Position(level, rank, file)
                    piece = game.get_piece(pos)
                    if not piece:
                        continue
                    
                    moves = game.get_valid_moves(pos)
                    if piece.color == Color.WHITE:
                        white_mobility += len(moves)
                    else:
                        black_mobility += len(moves)
        
        # Add mobility score (scaled down)
        score += (white_mobility - black_mobility) * 2
        
        # Check status
        if game.is_check(Color.WHITE):
            score -= 50
        if game.is_check(Color.BLACK):
            score += 50
        
        return score

class AIPlayer:
    """AI player implementation for easy integration with the game"""
    
    def __init__(self, game, difficulty=1):
        """Initialize AI player with game state and difficulty level"""
        self.game = game
        self.set_difficulty(difficulty)
    
    def set_difficulty(self, level):
        """Set AI difficulty (1-5)"""
        if level == 1:
            self.ai = ChessAI(self.game, max_depth=1)
        elif level == 2:
            self.ai = ChessAI(self.game, max_depth=2)
        elif level == 3:
            self.ai = ChessAI(self.game, max_depth=3)
        elif level == 4:
            self.ai = ChessAI(self.game, max_depth=3, time_limit=5)
        else:  # level 5
            self.ai = ChessAI(self.game, max_depth=4, time_limit=10)
    
    def make_move(self, color=None):
        """Make the best move for the specified color"""
        if color is None:
            color = self.game.current_player
            
        move = self.ai.get_best_move(color)
        if move:
            return self.game.make_move(move)
        return False
