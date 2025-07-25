# Welcome to Pypong!
# This is a project made by Nihal
# Just hit run to start. Enjoy!

import pygame
import sys
import random
import time 

# Initialize Pygame
pygame.init()

# --- Game Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 120
BALL_SIZE = 20
FPS = 60
MAX_SCORE = 5 

# Initial speeds
BALL_INITIAL_SPEED = 7
PADDLE_SPEED = 8

# AI Speeds for different difficulties
AI_SPEEDS = {
    "easy": 6,
    "medium": 7,
    "hard": 8
}

# --- Colors (RGB tuples) ---
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
DARK_GRAY = (30, 30, 30) # For background
GRAY = (70, 70, 70)
LIGHT_GRAY = (150, 150, 150)
ACCENT_COLOR = (0, 200, 200) # Cyan
ACCENT_DARK = (0, 150, 150) # Darker cyan
PARTICLE_COLOR = (255, 100, 0) # Orange-red for particles

# --- Set up the display screen ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyPong - The Classic Arcade Game")

# --- Fonts ---
font_large = pygame.font.Font(None, 100)
font_medium = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 35)

class Paddle:
    """Represents a player's or AI's paddle in the Pong game."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def move(self):
        """Updates the paddle's vertical position and keeps it within screen bounds."""
        self.rect.y += self.speed
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self):
        """Draws the paddle on the screen (no border_radius)."""
        pygame.draw.rect(screen, WHITE, self.rect)

class Ball:
    """Represents the ball in the Pong game, now with a trail."""
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2,
                                SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
                                BALL_SIZE, BALL_SIZE)
        self.speed_x = random.choice([-1, 1]) * BALL_INITIAL_SPEED
        self.speed_y = random.choice([-1, 1]) * BALL_INITIAL_SPEED
        self.game_active = False
        self.current_speed_magnitude = BALL_INITIAL_SPEED # Tracks current total speed
        self.trail = [] # List to store past positions for the trail
        self.max_trail_length = 20 # Number of past positions to store
        self.trail_segment_size = 5 # Size of each trail segment

    def move(self):
        """Moves the ball and updates its trail if the game is active."""
        if self.game_active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.trail.append(self.rect.center) # Add current position to trail
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0) # Remove oldest position if trail is too long

    def check_collision(self, paddle1, paddle2, particles_list):
        """Handles ball collisions and generates particles on paddle hits."""
        # Wall collisions
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1

        # Paddle collisions
        if self.rect.colliderect(paddle1.rect) or self.rect.colliderect(paddle2.rect):
            # Determine which paddle was hit to generate particles near it
            hit_paddle_rect = None
            if self.rect.colliderect(paddle1.rect):
                hit_paddle_rect = paddle1.rect
            else: # Must be paddle2
                hit_paddle_rect = paddle2.rect

            # Generate particles at the collision point
            for _ in range(10): # Create 10 particles
                particles_list.append(Particle(self.rect.centerx, self.rect.centery))

            self.speed_x *= -1 # Reverse horizontal direction

            # Gradually increase ball speed (magnitude) after each paddle hit
            # This applies to all modes, but survival mode has additional speed increase
            self.current_speed_magnitude += 0.3
            # Recalculate speed_x and speed_y while maintaining direction
            # Normalize speed vectors to current_speed_magnitude
            current_direction_x = 1 if self.speed_x > 0 else -1
            current_direction_y = 1 if self.speed_y > 0 else -1
            # Avoid division by zero if both speeds somehow become zero (unlikely but safe)
            if self.speed_x == 0 and self.speed_y == 0:
                self.speed_x = self.current_speed_magnitude * current_direction_x
                self.speed_y = self.current_speed_magnitude * current_direction_y
            else:
                # Calculate the current vector's length
                current_vector_length = (self.speed_x**2 + self.speed_y**2)**0.5
                if current_vector_length > 0:
                    # Scale current speed components to the new desired magnitude
                    self.speed_x = (self.speed_x / current_vector_length) * self.current_speed_magnitude
                    self.speed_y = (self.speed_y / current_vector_length) * self.current_speed_magnitude
                else:
                    # Fallback if current_vector_length is zero (shouldn't happen with initial speeds)
                    self.speed_x = self.current_speed_magnitude * random.choice([-1, 1])
                    self.speed_y = self.current_speed_magnitude * random.choice([-1, 1])


            # Cap the maximum speed to prevent it from becoming uncontrollably fast.
            max_abs_speed = 20 # Increased max speed for more dynamic gameplay
            if abs(self.speed_x) > max_abs_speed:
                self.speed_x = max_abs_speed * (1 if self.speed_x > 0 else -1)
            if abs(self.speed_y) > max_abs_speed:
                self.speed_y = max_abs_speed * (1 if self.speed_y > 0 else -1)

    def reset(self):
        """Resets the ball to the center and clears its trail."""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = random.choice([-1, 1]) * BALL_INITIAL_SPEED
        self.speed_y = random.choice([-1, 1]) * BALL_INITIAL_SPEED
        self.current_speed_magnitude = BALL_INITIAL_SPEED # Reset speed magnitude
        self.game_active = False
        self.trail = [] # Clear the trail on reset
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)

    def draw(self):
        """Draws the ball and its trail."""
        # Draw trail segments, fading out
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / self.max_trail_length)) # Fade effect
            trail_color = (WHITE[0], WHITE[1], WHITE[2], alpha) # Pygame draw functions don't support alpha directly like this for surfaces
            
            # Create a semi-transparent surface for each trail segment
            s = pygame.Surface((self.trail_segment_size, self.trail_segment_size), pygame.SRCALPHA)
            pygame.draw.circle(s, trail_color, (self.trail_segment_size // 2, self.trail_segment_size // 2),
                               self.trail_segment_size // 2)
            screen.blit(s, (pos[0] - self.trail_segment_size // 2, pos[1] - self.trail_segment_size // 2))

        # Draw the main ball
        pygame.draw.ellipse(screen, WHITE, self.rect)


class Particle:
    """Represents a small particle for visual effects."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 7) # Random size for variety
        self.color = PARTICLE_COLOR
        self.velocity_x = random.uniform(-3, 3) # Random horizontal velocity
        self.velocity_y = random.uniform(-3, 3) # Random vertical velocity
        self.lifetime = random.randint(20, 40) # How many frames it will live
        self.age = 0 # Current age

    def move(self):
        """Updates particle position and age."""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.age += 1

    def draw(self):
        """Draws the particle, fading out over its lifetime."""
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime))) # Fade effect
        current_color = (self.color[0], self.color[1], self.color[2], alpha)
        
        # Create a surface for the particle to handle alpha transparency
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, current_color, (self.radius, self.radius), self.radius)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))

    def is_dead(self):
        """Checks if the particle's lifetime has expired."""
        return self.age >= self.lifetime


# --- Initialize Game Objects ---
paddle1 = Paddle(50, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
paddle2 = Paddle(SCREEN_WIDTH - 50 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
ball = Ball()

# List to hold active particles
particles = []

# --- Game Variables ---
player1_score = 0
player2_score = 0

# Game State Management
# "menu": main menu
# "single_player_difficulty_select": sub-menu for AI difficulty/survival mode
# "game_running": encompasses all active game modes (1P, 2P, Survival)
# "game_over": game over screen
game_state = "menu"

# Specific game mode details when in "game_running" state
# Can be "two_player", "classic_ai", "survival"
current_game_mode = None
ai_difficulty_level = None # "easy", "medium", "hard"
current_ai_speed = 0 # Will be set based on ai_difficulty_level

# Survival Mode specific variables
survival_start_time = 0
survival_time_elapsed = 0
ball_speed_increase_interval = 5 # Increase ball speed every 5 seconds
ball_speed_increase_amount = 0.5 # How much to increase speed each interval

winning_player = None

# --- Button Class for Interactive Menu Elements ---
class Button:
    """A clickable button for menu navigation and game state changes."""
    def __init__(self, x, y, width, height, text, font, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action # The action to perform when clicked (e.g., "single_player", "quit")
        self.color = ACCENT_COLOR
        self.hover_color = ACCENT_DARK
        self.text_color = WHITE

    def draw(self, surface):
        """Draws the button on the given surface."""
        current_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 5) # Border

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Checks if the button was clicked by the left mouse button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# --- Menu Buttons Instances ---
# Main Menu Buttons
ai_modes_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, 300, 70, "AI Modes", font_medium, "single_player_difficulty_select")
two_player_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20, 300, 70, "Two Player", font_medium, "two_player")
quit_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 120, 300, 70, "Quit", font_medium, "quit")

# AI Modes Sub-Menu Buttons
easy_ai_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150, 300, 70, "Easy AI", font_medium, "easy")
medium_ai_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 70, "Medium AI", font_medium, "medium")
hard_ai_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 70, "Hard AI", font_medium, "hard")
survival_mode_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150, 300, 70, "Survival Mode", font_medium, "survival")
back_to_main_menu_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 250, 300, 70, "Back", font_medium, "menu")

# Game Over Screen Buttons (adjusted positions for the new back button)
play_again_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 70, "Play Again", font_medium, "play_again")
game_over_back_to_menu_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 130, 300, 70, "Back to Menu", font_medium, "menu")


# --- Drawing Functions for Different Game States ---

def draw_background():
    """Draws a subtle radial gradient background."""
    for i in range(SCREEN_HEIGHT // 2):
        # Create a gradient from darker to slightly less dark towards the center
        color_val = max(0, int(BLACK[0] + (DARK_GRAY[0] - BLACK[0]) * (i / (SCREEN_HEIGHT // 2))))
        pygame.draw.line(screen, (color_val, color_val, color_val), (0, i), (SCREEN_WIDTH, i))
        pygame.draw.line(screen, (color_val, color_val, color_val), (0, SCREEN_HEIGHT - 1 - i), (SCREEN_WIDTH, SCREEN_HEIGHT - 1 - i))


def draw_menu():
    """Draws the main menu screen."""
    draw_background()

    title_text = font_large.render("PyPong", True, ACCENT_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
    screen.blit(title_text, title_rect)

    controls_text = font_small.render("Player 1: UP/DOWN Arrows | Player 2: W/S Keys (2P mode)", True, LIGHT_GRAY)
    controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140))
    screen.blit(controls_text, controls_rect)

    ai_modes_button.draw(screen)
    two_player_button.draw(screen)
    quit_button.draw(screen)

def draw_single_player_difficulty_select_menu():
    """Draws the AI difficulty selection sub-menu."""
    draw_background()

    title_text = font_large.render("AI Modes", True, ACCENT_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250))
    screen.blit(title_text, title_rect)

    easy_ai_button.draw(screen)
    medium_ai_button.draw(screen)
    hard_ai_button.draw(screen)
    survival_mode_button.draw(screen)
    back_to_main_menu_button.draw(screen)


def draw_game():
    """Draws the main game screen, including particles and survival info."""
    draw_background()

    # Draw the middle line and center circle
    pygame.draw.line(screen, GRAY, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 5)
    pygame.draw.circle(screen, GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 100, 5)

    # Draw paddles and ball
    paddle1.draw()
    paddle2.draw()
    ball.draw()

    # Draw scores for classic modes, or time for survival mode
    if current_game_mode == "survival":
        time_text = font_medium.render(f"Time: {int(survival_time_elapsed)}s", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 20))
        # Display current ball speed in survival mode
        speed_text = font_small.render(f"Speed: {ball.current_speed_magnitude:.1f}", True, LIGHT_GRAY)
        screen.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, 80))
    else:
        score_text1 = font_medium.render(str(player1_score), True, WHITE)
        screen.blit(score_text1, (SCREEN_WIDTH // 4 - score_text1.get_width() // 2, 20))
        score_text2 = font_medium.render(str(player2_score), True, WHITE)
        screen.blit(score_text2, (SCREEN_WIDTH * 3 // 4 - score_text2.get_width() // 2, 20))


    # Draw particles
    for particle in particles:
        particle.draw()

    # If the ball is not active, display "GET READY!"
    if not ball.game_active:
        countdown_text = font_large.render("GET READY!", True, LIGHT_GRAY)
        countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(countdown_text, countdown_rect)

def draw_game_over():
    """Draws the game over screen."""
    draw_background()

    if current_game_mode == "survival":
        game_over_text = font_large.render("Time's Up!", True, ACCENT_COLOR)
        score_text = font_medium.render(f"Survived: {int(survival_time_elapsed)} seconds", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(score_text, score_rect)
    else:
        if winning_player:
            game_over_text = font_large.render(f"{winning_player} Wins!", True, ACCENT_COLOR)
        else:
            game_over_text = font_large.render("Game Over", True, ACCENT_COLOR)

    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(game_over_text, game_over_rect)

    play_again_button.draw(screen)
    game_over_back_to_menu_button.draw(screen)

# --- Game Reset Function ---
def reset_game():
    """Resets all game parameters for a new game."""
    global player1_score, player2_score, winning_player, survival_start_time, survival_time_elapsed, particles
    player1_score = 0
    player2_score = 0
    winning_player = None
    survival_start_time = 0
    survival_time_elapsed = 0
    particles = [] # Clear all particles
    ball.reset()
    # Reset paddle positions
    paddle1.rect.midleft = (50, SCREEN_HEIGHT // 2)
    paddle2.rect.midright = (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)
    paddle1.speed = 0
    paddle2.speed = 0
    ball.game_active = False # Ensure ball starts inactive after a reset

# --- Main Game Loop ---
clock = pygame.time.Clock()
running = True

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if event.type == pygame.USEREVENT + 1: # Ball activation timer event
            if not ball.game_active:
                ball.game_active = True
                pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Stop the timer

        # Handle button clicks based on current game state
        if game_state == "menu":
            if ai_modes_button.is_clicked(event):
                game_state = "single_player_difficulty_select"
            elif two_player_button.is_clicked(event):
                current_game_mode = "two_player"
                game_state = "game_running"
                reset_game()
                survival_start_time = time.time() # Start timer for new game
            elif quit_button.is_clicked(event):
                running = False
                sys.exit()

        elif game_state == "single_player_difficulty_select":
            if easy_ai_button.is_clicked(event):
                current_game_mode = "classic_ai"
                ai_difficulty_level = "easy"
                current_ai_speed = AI_SPEEDS["easy"]
                game_state = "game_running"
                reset_game()
                survival_start_time = time.time()
            elif medium_ai_button.is_clicked(event):
                current_game_mode = "classic_ai"
                ai_difficulty_level = "medium"
                current_ai_speed = AI_SPEEDS["medium"]
                game_state = "game_running"
                reset_game()
                survival_start_time = time.time()
            elif hard_ai_button.is_clicked(event):
                current_game_mode = "classic_ai"
                ai_difficulty_level = "hard"
                current_ai_speed = AI_SPEEDS["hard"]
                game_state = "game_running"
                reset_game()
                survival_start_time = time.time()
            elif survival_mode_button.is_clicked(event):
                current_game_mode = "survival"
                ai_difficulty_level = "medium" # Survival mode uses medium AI speed initially
                current_ai_speed = AI_SPEEDS["medium"]
                game_state = "game_running"
                reset_game()
                survival_start_time = time.time() # Important: start time for survival mode
            elif back_to_main_menu_button.is_clicked(event):
                game_state = "menu"

        elif game_state == "game_over":
            if play_again_button.is_clicked(event):
                # When "Play Again" is clicked, return to the AI difficulty select
                # or immediately restart 2P if that was the mode.
                if current_game_mode == "two_player":
                    game_state = "game_running"
                    reset_game()
                    survival_start_time = time.time()
                else: # Classic AI or Survival mode will go back to difficulty select
                    game_state = "single_player_difficulty_select"
                    reset_game()
            elif game_over_back_to_menu_button.is_clicked(event):
                game_state = "menu"
                reset_game() # Ensures game is clean if returning to main menu

        # Handle keyboard input for paddles during active game states.
        if game_state == "game_running":
            if event.type == pygame.KEYDOWN:
                # Player 1 controls (UP and DOWN arrow keys)
                if event.key == pygame.K_UP:
                    paddle1.speed = -PADDLE_SPEED
                if event.key == pygame.K_DOWN:
                    paddle1.speed = PADDLE_SPEED
                # Player 2 controls (W and S keys), only active in two-player mode.
                if current_game_mode == "two_player":
                    if event.key == pygame.K_w:
                        paddle2.speed = -PADDLE_SPEED
                    if event.key == pygame.K_s:
                        paddle2.speed = PADDLE_SPEED
            if event.type == pygame.KEYUP:
                # Stop paddle movement when keys are released.
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    paddle1.speed = 0
                if current_game_mode == "two_player":
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        paddle2.speed = 0

    # --- Game Logic Updates (only if in an active game state) ---
    if game_state == "game_running":
        paddle1.move()

        # AI Logic for paddle 2
        if current_game_mode in ["classic_ai", "survival"]:
            if ball.game_active:
                if ball.rect.centery < paddle2.rect.centery:
                    paddle2.speed = -current_ai_speed
                elif ball.rect.centery > paddle2.rect.centery:
                    paddle2.speed = current_ai_speed
                else:
                    paddle2.speed = 0
            else:
                paddle2.speed = 0 # AI paddle stops when ball is inactive.
            paddle2.move()
        elif current_game_mode == "two_player":
            paddle2.move() # Player 2 moves based on input

        ball.move()
        ball.check_collision(paddle1, paddle2, particles) # Pass particles list for generation

        # Update and remove dead particles
        for particle in particles[:]: # Iterate over a slice to allow modification during iteration
            particle.move()
            if particle.is_dead():
                particles.remove(particle)

        # Scoring Logic
        if ball.rect.left <= 0: # Ball passed left (Player 2 scores / Player 1 misses)
            if current_game_mode == "survival":
                # In survival mode, missing means game over
                winning_player = "You" # Player is implied as player 1
                game_state = "game_over"
            else: # Classic AI or Two Player
                player2_score += 1
                ball.reset()
        elif ball.rect.right >= SCREEN_WIDTH: # Ball passed right (Player 1 scores / AI misses)
            if current_game_mode == "survival":
                # In survival mode, AI missing means ball is reset for player to continue
                ball.reset()
            else: # Classic AI or Two Player
                player1_score += 1
                ball.reset()

        # Game Win Condition (for classic modes)
        if current_game_mode in ["classic_ai", "two_player"]:
            if player1_score >= MAX_SCORE:
                winning_player = "Player 1"
                game_state = "game_over"
            elif player2_score >= MAX_SCORE:
                winning_player = "Player 2"
                game_state = "game_over"

        # Survival Mode Specific Logic (time tracking and ball speed increase)
        if current_game_mode == "survival" and ball.game_active:
            survival_time_elapsed = time.time() - survival_start_time
            # Increase ball speed gradually based on elapsed time
            # The initial speed increase is handled by ball.check_collision
            # This handles a continuous increase over time
            if int(survival_time_elapsed) > 0 and int(survival_time_elapsed) % ball_speed_increase_interval == 0 and ball.current_speed_magnitude < ball.initial_speed + 15: # Cap additional speed increase
                 # Increase speed only once per interval
                if (int(survival_time_elapsed) // ball_speed_increase_interval) != (int(survival_time_elapsed - clock.get_rawtime()/1000) // ball_speed_increase_interval): # Check if we just crossed a new interval
                    ball.current_speed_magnitude += ball_speed_increase_amount
                    # Recalculate ball speeds to reflect the new magnitude
                    current_vector_length = (ball.speed_x**2 + ball.speed_y**2)**0.5
                    if current_vector_length > 0:
                        ball.speed_x = (ball.speed_x / current_vector_length) * ball.current_speed_magnitude
                        ball.speed_y = (ball.speed_y / current_vector_length) * ball.current_speed_magnitude


    # --- Drawing ---
    if game_state == "menu":
        draw_menu()
    elif game_state == "single_player_difficulty_select":
        draw_single_player_difficulty_select_menu()
    elif game_state == "game_running":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()

    # --- Update Display ---
    pygame.display.flip()

    # --- Frame Rate Control ---
    clock.tick(FPS)

# --- Game Exit ---
pygame.quit()
sys.exit()
