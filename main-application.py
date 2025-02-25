import pygame
import sys
import time
import os
from chess3d import Chess3D, Position, PieceType, Color, Move
from chess3d_visualization import Chess3DRenderer
from ai_engine import AIPlayer

class Chess3DApplication:
    """Main application integrating game logic, rendering, and AI"""
    
    def __init__(self):
        """Initialize application components"""
        self.game = Chess3D()
        self.renderer = Chess3DRenderer(width=1200, height=800)
        self.ai_player = AIPlayer(self.game, difficulty=3)
        
        # Application state
        self.ai_enabled = False
        self.ai_color = Color.BLACK
        self.ai_thinking = False
        self.last_move_time = 0
        self.game_mode = "human_vs_human"
        
        # UI elements
        self.setup_ui()
        
    def setup_ui(self):
        """Configure UI elements beyond the board"""
        self.renderer.game = self.game
        
        # Add buttons and controls to renderer
        self.add_control_panel()
        
    def add_control_panel(self):
        """Add control panel to renderer"""
        # Control panel is managed in the Chess3DRenderer class
        # This method ensures the game reference is set correctly
        # and initializes any application-specific UI components
        pass
        
    def toggle_ai(self):
        """Toggle AI player on/off"""
        self.ai_enabled = not self.ai_enabled
        return self.ai_enabled
        
    def set_ai_color(self, color):
        """Set which color the AI plays"""
        self.ai_color = color
        
    def set_ai_difficulty(self, level):
        """Set AI difficulty level (1-5)"""
        self.ai_player.set_difficulty(level)
        
    def set_game_mode(self, mode):
        """Set game mode: human_vs_human, human_vs_ai, ai_vs_ai"""
        self.game_mode = mode
        
        if mode == "human_vs_ai":
            self.ai_enabled = True
            # By default AI plays black
            self.ai_color = Color.BLACK
        elif mode == "ai_vs_ai":
            self.ai_enabled = True
        else:  # human_vs_human
            self.ai_enabled = False
            
    def handle_ai_move(self):
        """Process AI move if it's the AI's turn"""
        # Check if AI should make a move
        current_time = time.time()
        
        if (self.ai_enabled and
            self.game.current_player == self.ai_color and
            not self.ai_thinking and
            current_time - self.last_move_time > 0.5):  # Minimum delay between moves
            
            self.ai_thinking = True
            
            # Run AI in a non-blocking way
            self.ai_player.make_move()
            
            self.ai_thinking = False
            self.last_move_time = current_time
            
            # Clear any selection after AI move
            self.renderer.selected_pos = None
            self.renderer.valid_moves = []
            
    def handle_events(self):
        """Process user input and pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Reset game
                    self.game.reset()
                    self.renderer.selected_pos = None
                    self.renderer.valid_moves = []
                    self.last_move_time = time.time()
                elif event.key == pygame.K_u:
                    # Undo move
                    self.game.undo_move()
                    if self.ai_enabled:
                        # Undo AI move as well to get back to human turn
                        self.game.undo_move()
                    self.renderer.selected_pos = None
                    self.renderer.valid_moves = []
                elif event.key == pygame.K_a:
                    # Toggle AI
                    self.toggle_ai()
                    print(f"AI {'enabled' if self.ai_enabled else 'disabled'}")
                elif event.key == pygame.K_1:
                    # Set AI difficulty
                    self.set_ai_difficulty(1)
                    print("AI difficulty set to 1 (Easy)")
                elif event.key == pygame.K_2:
                    self.set_ai_difficulty(2)
                    print("AI difficulty set to 2 (Medium)")
                elif event.key == pygame.K_3:
                    self.set_ai_difficulty(3)
                    print("AI difficulty set to 3 (Hard)")
                elif event.key == pygame.K_4:
                    self.set_ai_difficulty(4)
                    print("AI difficulty set to 4 (Expert)")
                elif event.key == pygame.K_5:
                    self.set_ai_difficulty(5)
                    print("AI difficulty set to 5 (Master)")
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if not self.ai_thinking and (
                        not self.ai_enabled or 
                        self.game.current_player != self.ai_color
                    ):
                        # If it's human's turn, process the click
                        self.renderer.handle_click(event.pos)
                        self.last_move_time = time.time()
                        
        return True
        
    def update_status(self):
        """Update and display game status"""
        # Check for game end conditions
        if self.game.is_checkmate(Color.WHITE):
            print("Black wins by checkmate!")
        elif self.game.is_checkmate(Color.BLACK):
            print("White wins by checkmate!")
        
    def run(self):
        """Main application loop"""
        running = True
        self.last_move_time = time.time()
        
        while running:
            # Process events
            running = self.handle_events()
            
            # Handle AI moves if needed
            if running and self.ai_enabled:
                self.handle_ai_move()
            
            # Update game status
            self.update_status()
            
            # Render the game
            self.renderer.draw_board()
            
            # Add AI status indicator if applicable
            if self.ai_thinking:
                font = pygame.font.SysFont("arial", 24, bold=True)
                text = font.render("AI thinking...", True, (255, 100, 100))
                self.renderer.screen.blit(text, (20, 80))
                
            if self.ai_enabled:
                ai_text = f"AI playing as {'Black' if self.ai_color == Color.BLACK else 'White'}"
                font = pygame.font.SysFont("arial", 20)
                text = font.render(ai_text, True, (200, 200, 255))
                self.renderer.screen.blit(text, (20, self.renderer.height - 60))
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.renderer.clock.tick(60)
        
        pygame.quit()
        sys.exit()

class MenuScreen:
    """Game menu screen for mode selection"""
    
    def __init__(self, width=800, height=600):
        """Initialize menu screen"""
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("3D Chess")
        
        # Fonts and colors
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.option_font = pygame.font.SysFont("arial", 36)
        self.info_font = pygame.font.SysFont("arial", 24)
        
        self.bg_color = (40, 40, 40)
        self.title_color = (255, 215, 0)
        self.option_color = (255, 255, 255)
        self.highlight_color = (100, 200, 255)
        
        # Menu options
        self.options = [
            "Human vs Human",
            "Human vs AI",
            "AI vs AI",
            "Options",
            "Exit"
        ]
        self.selected_option = 0
        
        # Difficulty setting
        self.difficulty = 3
        
    def draw(self):
        """Draw menu screen"""
        self.screen.fill(self.bg_color)
        
        # Draw title
        title_surf = self.title_font.render("3D Chess", True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.width//2, 100))
        self.screen.blit(title_surf, title_rect)
        
        # Draw options
        for i, option in enumerate(self.options):
            color = self.highlight_color if i == self.selected_option else self.option_color
            option_surf = self.option_font.render(option, True, color)
            option_rect = option_surf.get_rect(center=(self.width//2, 200 + i*60))
            self.screen.blit(option_surf, option_rect)
        
        # Draw info
        info_text = "Arrow keys: Navigate | Enter: Select | 1-5: Set AI difficulty"
        info_surf = self.info_font.render(info_text, True, (180, 180, 180))
        info_rect = info_surf.get_rect(center=(self.width//2, self.height - 60))
        self.screen.blit(info_surf, info_rect)
        
        # Draw current difficulty
        diff_text = f"AI Difficulty: {self.difficulty}"
        diff_surf = self.info_font.render(diff_text, True, (180, 180, 180))
        diff_rect = diff_surf.get_rect(center=(self.width//2, self.height - 30))
        self.screen.blit(diff_surf, diff_rect)
        
        pygame.display.flip()
        
    def run(self):
        """Run menu loop and return selected option"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "Exit"
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        return self.options[self.selected_option]
                    elif event.key >= pygame.K_1 and event.key <= pygame.K_5:
                        self.difficulty = event.key - pygame.K_0
                        
            self.draw()
            pygame.time.delay(30)
            
        return "Exit"

def main():
    """Main entry point"""
    # First show menu
    menu = MenuScreen()
    menu_result = menu.run()
    
    if menu_result == "Exit":
        pygame.quit()
        sys.exit()
    
    # Create main application
    app = Chess3DApplication()
    
    # Set game mode based on menu selection
    if menu_result == "Human vs Human":
        app.set_game_mode("human_vs_human")
    elif menu_result == "Human vs AI":
        app.set_game_mode("human_vs_ai")
        app.set_ai_difficulty(menu.difficulty)
    elif menu_result == "AI vs AI":
        app.set_game_mode("ai_vs_ai")
        app.set_ai_difficulty(menu.difficulty)
    
    # Run the application
    app.run()

if __name__ == "__main__":
    main()
