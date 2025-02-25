import pygame
import pygame.gfxdraw
import numpy as np
import math
from chess3d import Chess3D, Position, PieceType, Color, Move

class Chess3DRenderer:
    """Renders 3D chess game state using pygame isometric projection"""
    
    def __init__(self, width=1200, height=800):
        # Initialize pygame
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("3D Chess")
        
        # Game state and selection tracking
        self.game = Chess3D()
        self.selected_pos = None
        self.valid_moves = []
        self.running = True
        
        # Asset loading and caching
        self.piece_cache = {}
        self.load_assets()
        
        # Board dimensions and drawing parameters
        self.cell_size = 60
        self.level_height = 120
        self.x_offset = width // 2
        self.y_offset = 150
        self.iso_angle = math.pi / 6  # 30 degrees
        
        # Animation and frame timing
        self.clock = pygame.time.Clock()
        self.fps = 60

    def load_assets(self):
        """Load and cache piece sprites"""
        piece_symbols = {
            (PieceType.PAWN, Color.WHITE): "WP",
            (PieceType.KNIGHT, Color.WHITE): "WN",
            (PieceType.BISHOP, Color.WHITE): "WB",
            (PieceType.ROOK, Color.WHITE): "WR",
            (PieceType.QUEEN, Color.WHITE): "WQ",
            (PieceType.KING, Color.WHITE): "WK",
            (PieceType.PAWN, Color.BLACK): "BP",
            (PieceType.KNIGHT, Color.BLACK): "BN",
            (PieceType.BISHOP, Color.BLACK): "BB",
            (PieceType.ROOK, Color.BLACK): "BR",
            (PieceType.QUEEN, Color.BLACK): "BQ",
            (PieceType.KING, Color.BLACK): "BK",
        }
        
        try:
            for piece_type, symbol in piece_symbols.items():
                self.piece_cache[piece_type] = pygame.image.load(f"assets/{symbol}.png")
                self.piece_cache[piece_type] = pygame.transform.scale(
                    self.piece_cache[piece_type], 
                    (self.cell_size, self.cell_size)
                )
        except pygame.error:
            # Fallback to simple colored circles for pieces
            self.create_fallback_pieces()
            
    def create_fallback_pieces(self):
        """Generate simple piece representations"""
        colors = {
            Color.WHITE: (230, 230, 230),
            Color.BLACK: (30, 30, 30)
        }
        
        piece_symbols = {
            PieceType.PAWN: "P",
            PieceType.KNIGHT: "N", 
            PieceType.BISHOP: "B",
            PieceType.ROOK: "R",
            PieceType.QUEEN: "Q",
            PieceType.KING: "K"
        }
        
        for color in [Color.WHITE, Color.BLACK]:
            for piece_type, symbol in piece_symbols.items():
                # Create surface for piece
                surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                
                # Draw circle
                pygame.draw.circle(
                    surf, 
                    colors[color], 
                    (self.cell_size // 2, self.cell_size // 2),
                    self.cell_size // 2 - 5
                )
                
                # Add symbol
                font = pygame.font.SysFont("arial", self.cell_size // 2, bold=True)
                text = font.render(symbol, True, (255, 255, 255) if color == Color.BLACK else (0, 0, 0))
                text_rect = text.get_rect(center=(self.cell_size // 2, self.cell_size // 2))
                surf.blit(text, text_rect)
                
                self.piece_cache[(piece_type, color)] = surf

    def to_isometric(self, file, rank, level):
        """Convert 3D chess coordinates to 2D screen coordinates"""
        # Adjust for isometric view
        iso_x = (file - rank) * math.cos(self.iso_angle) * self.cell_size
        iso_y = (file + rank) * math.sin(self.iso_angle) * self.cell_size - level * self.level_height
        
        # Apply offsets to center the board
        screen_x = self.x_offset + iso_x
        screen_y = self.y_offset + iso_y
        
        return screen_x, screen_y

    def from_isometric(self, screen_x, screen_y):
        """Convert screen coordinates to closest chess position"""
        # Adjust for screen offset
        iso_x = screen_x - self.x_offset
        iso_y = screen_y - self.y_offset
        
        # Approximate level based on Y position
        level_approx = max(0, min(2, -iso_y // self.level_height))
        iso_y += level_approx * self.level_height
        
        # Solve for file and rank
        cos_a = math.cos(self.iso_angle)
        sin_a = math.sin(self.iso_angle)
        
        file_plus_rank = iso_y / (sin_a * self.cell_size)
        file_minus_rank = iso_x / (cos_a * self.cell_size)
        
        file = (file_plus_rank + file_minus_rank) / 2
        rank = (file_plus_rank - file_minus_rank) / 2
        
        # Round to nearest integer and clamp to valid range
        file = max(0, min(7, round(file)))
        rank = max(0, min(7, round(rank)))
        level = int(level_approx)
        
        return Position(level, rank, file)

    def draw_board(self):
        """Draw 3D chessboard with grid and pieces"""
        self.screen.fill((40, 40, 40))
        
        # Draw boards for each level (bottom to top)
        for level in range(3):
            self.draw_level(level)
        
        # Draw selection highlight
        if self.selected_pos:
            self.draw_selection()
        
        # Draw valid moves from selection
        for move in self.valid_moves:
            self.draw_valid_move(move)
            
        # Draw status information
        self.draw_status()

    def draw_level(self, level):
        """Draw a single level of the 3D board"""
        for rank in range(8):
            for file in range(8):
                is_light_square = (rank + file) % 2 == 0
                color = (240, 217, 181) if is_light_square else (181, 136, 99)
                
                # Calculate corners of the square in isometric projection
                corners = [
                    self.to_isometric(file, rank, level),
                    self.to_isometric(file + 1, rank, level),
                    self.to_isometric(file + 1, rank + 1, level),
                    self.to_isometric(file, rank + 1, level),
                ]
                
                # Draw the square
                pygame.draw.polygon(self.screen, color, corners)
                
                # Draw gridlines
                pygame.draw.polygon(self.screen, (0, 0, 0), corners, 1)
                
                # Draw piece if present
                piece = self.game.get_piece(Position(level, rank, file))
                if piece:
                    piece_center = self.to_isometric(file + 0.5, rank + 0.5, level)
                    piece_img = self.piece_cache.get((piece.type, piece.color))
                    if piece_img:
                        img_rect = piece_img.get_rect(center=piece_center)
                        self.screen.blit(piece_img, img_rect)
                        
        # Draw level indicator
        label_pos = self.to_isometric(-1, 3.5, level)
        font = pygame.font.SysFont("arial", 24, bold=True)
        level_label = font.render(f"Level {level+1}", True, (255, 255, 255))
        self.screen.blit(level_label, label_pos)

    def draw_selection(self):
        """Highlight the selected position"""
        if not self.selected_pos:
            return
            
        level, rank, file = self.selected_pos.level, self.selected_pos.rank, self.selected_pos.file
        corners = [
            self.to_isometric(file, rank, level),
            self.to_isometric(file + 1, rank, level),
            self.to_isometric(file + 1, rank + 1, level),
            self.to_isometric(file, rank + 1, level),
        ]
        
        # Draw highlight with semi-transparency
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(s, (255, 255, 0, 128), corners)
        self.screen.blit(s, (0, 0))

    def draw_valid_move(self, move):
        """Highlight a valid move destination"""
        level, rank, file = move.to_pos.level, move.to_pos.rank, move.to_pos.file
        
        center = self.to_isometric(file + 0.5, rank + 0.5, level)
        
        # Draw a semi-transparent circle
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 0, 128), center, self.cell_size // 3)
        self.screen.blit(s, (0, 0))

    def draw_status(self):
        """Draw game status information"""
        font = pygame.font.SysFont("arial", 24)
        turn_text = f"Current turn: {'White' if self.game.current_player == Color.WHITE else 'Black'}"
        turn_surface = font.render(turn_text, True, (255, 255, 255))
        self.screen.blit(turn_surface, (20, 20))
        
        # Check for check/checkmate
        white_in_check = self.game.is_check(Color.WHITE)
        black_in_check = self.game.is_check(Color.BLACK)
        white_in_checkmate = self.game.is_checkmate(Color.WHITE)
        black_in_checkmate = self.game.is_checkmate(Color.BLACK)
        
        status_text = ""
        if white_in_checkmate:
            status_text = "Black wins by checkmate!"
        elif black_in_checkmate:
            status_text = "White wins by checkmate!"
        elif white_in_check:
            status_text = "White is in check!"
        elif black_in_check:
            status_text = "Black is in check!"
            
        if status_text:
            status_surface = font.render(status_text, True, (255, 100, 100))
            self.screen.blit(status_surface, (20, 50))
            
        # Draw help text
        help_font = pygame.font.SysFont("arial", 16)
        help_text = "Click to select and move pieces | Esc: New Game | U: Undo"
        help_surface = help_font.render(help_text, True, (200, 200, 200))
        self.screen.blit(help_surface, (20, self.height - 30))

    def handle_click(self, pos):
        """Process mouse click and update game state"""
        click_pos = self.from_isometric(*pos)
        
        if not self.game.is_valid_position(click_pos):
            return
            
        # If no piece is selected, select one
        if not self.selected_pos:
            piece = self.game.get_piece(click_pos)
            if piece and piece.color == self.game.current_player:
                self.selected_pos = click_pos
                self.valid_moves = self.game.get_valid_moves(click_pos)
        else:
            # If a piece is already selected, try to move it
            for move in self.valid_moves:
                if move.to_pos == click_pos:
                    self.game.make_move(move)
                    self.selected_pos = None
                    self.valid_moves = []
                    return
                    
            # If clicked on a different piece of same color, select it instead
            piece = self.game.get_piece(click_pos)
            if piece and piece.color == self.game.current_player:
                self.selected_pos = click_pos
                self.valid_moves = self.game.get_valid_moves(click_pos)
            else:
                # Clicking elsewhere deselects
                self.selected_pos = None
                self.valid_moves = []

    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game.reset()
                        self.selected_pos = None
                        self.valid_moves = []
                    elif event.key == pygame.K_u:  # Undo
                        self.game.undo_move()
                        self.selected_pos = None
                        self.valid_moves = []
            
            # Draw everything
            self.draw_board()
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(self.fps)
        
        pygame.quit()

if __name__ == "__main__":
    renderer = Chess3DRenderer()
    renderer.run()
