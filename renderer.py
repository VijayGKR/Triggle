import pygame
import math
from game import HexGame
from minimax_agent import MinimaxAgent

class HexRenderer:
    def __init__(self):
        pygame.init()
        
        # Constants
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.HEX_SIZE = 40  # Distance from center to corner
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.PLAYER1_COLOR = (0, 0, 255)    # Blue
        self.PLAYER2_COLOR = (255, 0, 0)    # Red
        
        # Setup display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Hex Game")
        
        # Game state
        self.game = HexGame()
        self.selected_points = []
        
        # AI setup
        self.ai_enabled = True
        self.ai_agent = MinimaxAgent(player_number=2)  # AI plays as player 2
        
    def get_hex_center(self, row, col):
        """Calculate the center position of each hexagon"""
        x = col * (self.HEX_SIZE * 1.5)
        y = row * (self.HEX_SIZE * math.sqrt(3)) + (self.HEX_SIZE * math.sqrt(3) / 2) - col * (self.HEX_SIZE * math.sqrt(3) / 2)
        return (x + 200, y + 200)  # Offset from screen edge
        
    def get_nearest_hex_point(self, mouse_pos):
        """Find the nearest valid hex point to the mouse position"""
        min_dist = float('inf')
        nearest_coord = None
        
        for coord in self.game.valid_points:
            center = self.get_hex_center(*coord)
            dist = math.sqrt((mouse_pos[0] - center[0])**2 + (mouse_pos[1] - center[1])**2)
            if dist < min_dist:
                min_dist = dist
                nearest_coord = coord
        
        return nearest_coord if min_dist < self.HEX_SIZE else None
    
    def get_triangle_center(self, triangle_points):
        """Calculate the center point of a triangle"""
        centers = [self.get_hex_center(*p) for p in triangle_points]
        x = sum(c[0] for c in centers) / 3
        y = sum(c[1] for c in centers) / 3
        return (int(x), int(y))
    
    def draw(self):
        """Draw the game state"""
        self.screen.fill(self.BLACK)
        
        # Draw grid points
        for coord in self.game.valid_points:
            center = self.get_hex_center(*coord)
            pygame.draw.circle(self.screen, self.WHITE, (int(center[0]), int(center[1])), 3)
            
            # Draw coordinates
            coord_text = f"{coord[0]},{coord[1]}"
            font = pygame.font.Font(None, 20)
            text_surface = font.render(coord_text, True, self.WHITE)
            text_rect = text_surface.get_rect(center=(center[0], center[1] + 15))
            self.screen.blit(text_surface, text_rect)
        
        # Draw lines with player colors
        state = self.game.get_state()
        for (start, end), player in state['line_owners'].items():
            color = self.PLAYER1_COLOR if player == 1 else self.PLAYER2_COLOR
            pygame.draw.line(self.screen, color, 
                           self.get_hex_center(*start), 
                           self.get_hex_center(*end), 2)
        
        # Draw triangles
        for triangle, player in state['triangle_owners'].items():
            center = self.get_triangle_center(triangle)
            color = self.PLAYER1_COLOR if player == 1 else self.PLAYER2_COLOR
            pygame.draw.circle(self.screen, color, center, 4)
        
        # Draw selected point
        if self.selected_points:
            center = self.get_hex_center(*self.selected_points[0])
            pygame.draw.circle(self.screen, (255, 255, 0), (int(center[0]), int(center[1])), 5)
        
        # Draw current player indicator
        font = pygame.font.Font(None, 36)
        text = f"Player {state['current_player']}'s turn"
        color = self.PLAYER1_COLOR if state['current_player'] == 1 else self.PLAYER2_COLOR
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (10, 10))
        
        # Draw scores
        scores = self.game.get_scores()
        score_text = f"Blue: {scores[1]}  Red: {scores[2]}"
        score_surface = font.render(score_text, True, self.WHITE)
        self.screen.blit(score_surface, (10, 50))

        # Add instructions for AI toggle and reset
        ai_status = "ON" if self.ai_enabled else "OFF"
        instructions_text = f"Press 'A' to toggle AI ({ai_status}) | Press 'R' to reset game"
        instructions_surface = font.render(instructions_text, True, self.WHITE)
        self.screen.blit(instructions_surface, (10, self.WINDOW_HEIGHT - 30))

        # Game over text (existing code)
        if self.game.game_over:
            if(self.game.winner == 0):
                text = f"Game over! Draw"
            else:
                text = f"Game over! Winner: Player {self.game.winner}"
            text_surface = font.render(text, True, self.WHITE)
            self.screen.blit(text_surface, (10, 90))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            # If it's AI's turn, make AI move
            if self.ai_enabled and self.game.current_player == self.ai_agent.player_number and not self.game.game_over:
                best_move = self.ai_agent.get_move(self.game)
                if best_move:
                    point1, point2 = best_move
                    self.game.make_move(point1, point2)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:  # Reset game
                        self.game.reset()
                        self.selected_points = []
                    elif event.key == pygame.K_a:  # Toggle AI
                        self.ai_enabled = not self.ai_enabled
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Only process clicks if it's human's turn
                        if not self.ai_enabled or self.game.current_player != self.ai_agent.player_number and not self.game.game_over:
                            coord = self.get_nearest_hex_point(pygame.mouse.get_pos())
                            if coord:
                                if not self.selected_points:
                                    self.selected_points = [coord]
                                else:
                                    result = self.game.make_move(self.selected_points[0], coord)
                                    self.selected_points = []
                    elif event.button == 3:  # Right click
                        self.selected_points = []
            
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    renderer = HexRenderer()
    renderer.run()
