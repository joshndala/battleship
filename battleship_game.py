import pygame
import random
import time

# --- Pygame Initialization ---
pygame.init()

# --- Configuration ---
BOARD_SIZE = 5       # 5x5 grid
NUM_SHIPS = 3        # <--- ADDED THIS (Number of ships per player)
CELL_SIZE = 60       # Size of each cell in pixels
BOARD_OFFSET_X = 50  # X-offset for the first board
BOARD_OFFSET_Y = 50  # Y-offset for the first board
BOARD_GAP = 100      # Gap between the two boards

SCREEN_WIDTH = (BOARD_OFFSET_X * 2) + (CELL_SIZE * BOARD_SIZE * 2) + BOARD_GAP
SCREEN_HEIGHT = (BOARD_OFFSET_Y * 2) + (CELL_SIZE * BOARD_SIZE) + 50 # Added extra height for text
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship")

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 200)       # Water
LIGHT_BLUE = (0, 0, 255) # Hover color
GRAY = (150, 150, 150)   # Ship color
RED = (200, 0, 0)        # Hit
GREEN = (0, 200, 0)      # Miss

# --- Fonts ---
# Using None uses the default pygame font, which avoids macOS sysfont timeouts
FONT = pygame.font.Font(None, 30)
GAME_OVER_FONT = pygame.font.Font(None, 60)

# --- Game Class ---
class BattleshipGame:
    def __init__(self, size, num_ships):
        self.size = size
        self.num_ships = num_ships
        
        # Player boards
        self.player_board = [['~' for _ in range(size)] for _ in range(size)] # Where player's ships are
        self.player_guess_board = [['~' for _ in range(size)] for _ in range(size)] # Player's shots on AI
        self.player_ships = [] # List of (row, col) for player's ship locations
        
        # AI boards
        self.ai_board = [['~' for _ in range(size)] for _ in range(size)] # Where AI's ships are (hidden from player)
        self.ai_guesses = set() # Tracks AI moves to prevent duplicate shots
        self.ai_ships = [] # List of (row, col) for AI's ship locations

        self.game_over = False
        self.winner = None # 'Player' or 'AI'

        self.place_ships_randomly(self.player_board, self.player_ships)
        self.place_ships_randomly(self.ai_board, self.ai_ships)

    def place_ships_randomly(self, board, ship_list):
        ships_placed = 0
        while ships_placed < self.num_ships:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            if board[r][c] == '~':
                board[r][c] = 'S'
                ship_list.append((r, c))
                ships_placed += 1

    def check_hit(self, r, c, target_board, ship_list):
        if target_board[r][c] == 'S':
            # Mark the hit on the target board
            target_board[r][c] = 'X'
            # Remove from ship_list (meaning this part of ship is sunk)
            if (r, c) in ship_list: # Check if it's still considered a living part of a ship
                ship_list.remove((r, c))
            return True
        elif target_board[r][c] == '~':
            target_board[r][c] = 'O'
        return False

    def ai_turn(self):
        # Prevent AI from shooting at already hit/missed spots
        # Safety check: if board is full, don't loop forever
        if len(self.ai_guesses) >= self.size * self.size:
            return False, (0,0)

        while True:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            if (r, c) not in self.ai_guesses:
                self.ai_guesses.add((r, c))
                break
        
        # Check if AI hit player's ship
        is_hit = self.check_hit(r, c, self.player_board, self.player_ships)
        
        if not self.player_ships:
            self.game_over = True
            self.winner = 'AI'
        
        return is_hit, (r,c) # Return hit status and coordinates for display

    def draw_board(self, screen, board, offset_x, offset_y, show_ships=False):
        for r in range(self.size):
            for c in range(self.size):
                cell_x = offset_x + c * CELL_SIZE
                cell_y = offset_y + r * CELL_SIZE
                rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)

                # Draw cell background
                pygame.draw.rect(screen, BLUE, rect)
                pygame.draw.rect(screen, BLACK, rect, 1) # Border

                # Draw content
                if board[r][c] == 'S' and show_ships:
                    pygame.draw.rect(screen, GRAY, rect.inflate(-10, -10)) # Ship
                elif board[r][c] == 'X':
                    pygame.draw.line(screen, RED, rect.topleft, rect.bottomright, 3)
                    pygame.draw.line(screen, RED, rect.topright, rect.bottomleft, 3)
                elif board[r][c] == 'O':
                    pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 4, 3)
    
    def get_cell_from_mouse(self, mouse_pos, offset_x, offset_y):
        x, y = mouse_pos
        if offset_x <= x < offset_x + self.size * CELL_SIZE and \
           offset_y <= y < offset_y + self.size * CELL_SIZE:
            
            c = (x - offset_x) // CELL_SIZE
            r = (y - offset_y) // CELL_SIZE
            return r, c
        return None, None

    def display_message(self, screen, message, color, y_offset=0, font=FONT):
        text_surface = font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50 + y_offset))
        screen.blit(text_surface, text_rect)

# --- Main Game Loop ---
def main():
    game = BattleshipGame(BOARD_SIZE, NUM_SHIPS)
    running = True
    player_turn = True
    message = "Your Turn! Click on the right board."
    message_color = BLACK

    # AI turn variables for delayed display
    ai_last_shot = None
    ai_last_shot_time = 0
    ai_message = ""
    ai_message_color = BLACK
    show_ai_message_duration = 1.5 # seconds

    clock = pygame.time.Clock()

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game.game_over and player_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    # Target board for player is the AI's (right) board
                    target_r, target_c = game.get_cell_from_mouse(
                        mouse_pos,
                        BOARD_OFFSET_X + CELL_SIZE * game.size + BOARD_GAP,
                        BOARD_OFFSET_Y
                    )

                    if target_r is not None and target_c is not None:
                        # Check if player already shot here
                        if game.player_guess_board[target_r][target_c] != '~':
                            message = "You already shot there!"
                            message_color = RED
                        else:
                            # Player shoots
                            is_hit = game.check_hit(target_r, target_c, game.ai_board, game.ai_ships)
                            game.player_guess_board[target_r][target_c] = 'X' if is_hit else 'O'

                            if is_hit:
                                message = f"BOOM! Hit at {target_r+1}, {target_c+1}!"
                                message_color = RED
                            else:
                                message = f"Splash. Miss at {target_r+1}, {target_c+1}."
                                message_color = BLUE

                            if not game.ai_ships: # Player wins
                                game.game_over = True
                                game.winner = 'Player'
                            else:
                                player_turn = False # End player turn, start AI's
                                ai_message = "AI is thinking..."
                                ai_message_color = BLACK
                                ai_last_shot = None 
                                ai_last_shot_time = pygame.time.get_ticks() 
        
        # --- AI Turn Logic ---
        if not game.game_over and not player_turn:
            current_time = pygame.time.get_ticks()
            
            # 1. Wait for delay before AI shoots
            if current_time - ai_last_shot_time > 1000 and ai_last_shot is None:
                ai_hit, ai_coords = game.ai_turn()
                ai_last_shot = ai_coords
                ai_last_shot_time = current_time # Reset timer for reading the result

                r, c = ai_coords
                if ai_hit:
                    ai_message = f"DANGER! AI hit you at {r+1}, {c+1}!"
                    ai_message_color = RED
                else:
                    ai_message = f"The AI missed at {r+1}, {c+1}."
                    ai_message_color = GREEN

            # 2. Wait for delay so player can read what happened before turn swaps back
            elif ai_last_shot is not None and current_time - ai_last_shot_time > show_ai_message_duration * 1000:
                if not game.game_over:
                    player_turn = True
                    message = "Your Turn!"
                    message_color = BLACK
                    ai_message = "" 

        # --- Drawing ---
        SCREEN.fill(WHITE)

        # Draw Player's Board (Left)
        game.draw_board(SCREEN, game.player_board, BOARD_OFFSET_X, BOARD_OFFSET_Y, show_ships=True)
        player_board_text = FONT.render("Your Ships", True, BLACK)
        SCREEN.blit(player_board_text, (BOARD_OFFSET_X, BOARD_OFFSET_Y - 30))

        # Draw AI's Board (Right)
        ai_board_offset_x = BOARD_OFFSET_X + CELL_SIZE * game.size + BOARD_GAP
        game.draw_board(SCREEN, game.player_guess_board, ai_board_offset_x, BOARD_OFFSET_Y, show_ships=False)
        ai_board_text = FONT.render("Enemy Radar", True, BLACK)
        SCREEN.blit(ai_board_text, (ai_board_offset_x, BOARD_OFFSET_Y - 30))

        # Highlight cell on AI's board
        if not game.game_over and player_turn:
            mouse_pos = pygame.mouse.get_pos()
            hover_r, hover_c = game.get_cell_from_mouse(mouse_pos, ai_board_offset_x, BOARD_OFFSET_Y)
            if hover_r is not None and hover_c is not None and game.player_guess_board[hover_r][hover_c] == '~':
                hover_rect = pygame.Rect(
                    ai_board_offset_x + hover_c * CELL_SIZE,
                    BOARD_OFFSET_Y + hover_r * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(SCREEN, LIGHT_BLUE, hover_rect, 3)

        # Messages
        if not game.game_over:
            game.display_message(SCREEN, message, message_color)
            if ai_message:
                game.display_message(SCREEN, ai_message, ai_message_color, y_offset=30)
        else:
            if game.winner == 'Player':
                game.display_message(SCREEN, "YOU WIN!", RED, font=GAME_OVER_FONT)
            else:
                game.display_message(SCREEN, "GAME OVER! AI WINS!", BLACK, font=GAME_OVER_FONT)
            game.display_message(SCREEN, "Press 'R' to Restart", BLACK, y_offset=50)
            
            # Restart Logic
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                game = BattleshipGame(BOARD_SIZE, NUM_SHIPS)
                player_turn = True
                message = "Your Turn!"
                message_color = BLACK
                ai_message = ""
                ai_last_shot = None

        pygame.display.flip()
        clock.tick(60) # Limit to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()