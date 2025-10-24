# Welcome to Pypong!
# This is a project made by Nihal (Beta 0.11 - Update)
# Just hit run to start. Enjoy!

import pygame
import sys
import random
import time
import math 

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

# --- Game Events & Timers ---
BALL_ACTIVATE_EVENT = pygame.USEREVENT + 1
ARENA_LOAD_EVENT = pygame.USEREVENT + 2
LOADING_TIME_MS = 2000 # 2 seconds for the loading screen

# --- Colors (RGB tuples) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
DARK_GRAY = (30, 30, 30) 
GRAY = (70, 70, 70)
LIGHT_GRAY = (150, 150, 150)
ACCENT_COLOR = (0, 200, 200) # Cyan
ACCENT_DARK = (0, 150, 150) 
PARTICLE_COLOR = (255, 100, 0) # Orange-red for particles

# --- Arena Colors ---
BASKETBALL_ORANGE = (255, 140, 0) 
TABLE_TENNIS_BLUE = (0, 128, 255) 
ARENA_LINE_COLOR = (255, 255, 255) 

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
        """Draws the paddle on the screen with a slight border radius for style."""
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=5)

class Ball:
    """Represents the ball in the Pong game, now with a trail."""
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2,
                                     SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
                                     BALL_SIZE, BALL_SIZE)
        self.speed_x = 0
        self.speed_y = 0
        self.game_active = False
        self.current_speed_magnitude = BALL_INITIAL_SPEED 
        self.trail = [] 
        self.max_trail_length = 20 
        self.trail_segment_size = 5 
        
        self.reset_speeds() 

    def reset_speeds(self):
        """Calculates initial speed vectors with varied angles."""
        self.current_speed_magnitude = BALL_INITIAL_SPEED 
        angle = random.uniform(math.pi/6, math.pi/3) 
        direction_x = random.choice([-1, 1]) 
        direction_y = random.choice([-1, 1])
        
        self.speed_x = direction_x * math.cos(angle) * self.current_speed_magnitude
        self.speed_y = direction_y * math.sin(angle) * self.current_speed_magnitude

    def move(self):
        """Moves the ball and updates its trail if the game is active."""
        if self.game_active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.trail.append(self.rect.center) 
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0) 

    def check_collision(self, paddle1, paddle2, particles_list):
        """Handles ball collisions and generates particles on paddle hits."""
        # Wall collisions
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1

        # Paddle collisions
        if self.rect.colliderect(paddle1.rect) or self.rect.colliderect(paddle2.rect):
            
            for _ in range(10): 
                particles_list.append(Particle(self.rect.centerx, self.rect.centery))

            self.speed_x *= -1 

            self.current_speed_magnitude += 0.3
            
            current_vector_length = (self.speed_x**2 + self.speed_y**2)**0.5
            
            if current_vector_length > 0:
                self.speed_x = (self.speed_x / current_vector_length) * self.current_speed_magnitude
                self.speed_y = (self.speed_y / current_vector_length) * self.current_speed_magnitude
            else:
                self.reset_speeds()

            max_abs_speed = 20 
            if abs(self.speed_x) > max_abs_speed:
                self.speed_x = max_abs_speed * (1 if self.speed_x > 0 else -1)
            if abs(self.speed_y) > max_abs_speed:
                self.speed_y = max_abs_speed * (1 if self.speed_y > 0 else -1)

    def reset(self):
        """Resets the ball to the center and clears its trail."""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.reset_speeds() 
        self.game_active = False
        self.trail = [] 
        pygame.time.set_timer(BALL_ACTIVATE_EVENT, 1500)

    def draw(self):
        """Draws the ball and its trail using surfaces for transparency."""
        # Draw trail segments, fading out
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / self.max_trail_length)) 
            
            s = pygame.Surface((self.trail_segment_size * 2, self.trail_segment_size * 2), pygame.SRCALPHA)
            trail_color_with_alpha = (WHITE[0], WHITE[1], WHITE[2], alpha)
            pygame.draw.circle(s, trail_color_with_alpha, (self.trail_segment_size, self.trail_segment_size),
                                 self.trail_segment_size)
            screen.blit(s, (pos[0] - self.trail_segment_size, pos[1] - self.trail_segment_size))

        # Draw the main ball
        pygame.draw.ellipse(screen, WHITE, self.rect)


class Particle:
    """Represents a small particle for visual effects."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 7) 
        self.color = PARTICLE_COLOR
        self.velocity_x = random.uniform(-3, 3) 
        self.velocity_y = random.uniform(-3, 3) 
        self.lifetime = random.randint(20, 40) 
        self.age = 0 

    def move(self):
        """Updates particle position and age."""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.age += 1

    def draw(self):
        """Draws the particle, fading out over its lifetime using surfaces for alpha."""
        alpha = max(0, 255 - int(255 * (self.age / self.lifetime))) 
        current_color = (self.color[0], self.color[1], self.color[2], alpha)
        
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

# Arena Management 
ARENA_STYLES = ["original", "basketball", "table_tennis"]
current_arena = "original" 

# Game State Management
game_state = "menu" 

# Specific game mode details
current_game_mode = None
ai_difficulty_level = None 
current_ai_speed = 0 

# Survival Mode specific variables
survival_start_time = 0
survival_time_elapsed = 0

winning_player = None

# --- Button Class for Interactive Menu Elements ---
class Button:
    """A clickable button for menu navigation and game state changes."""
    def __init__(self, x, y, width, height, text, font, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action 
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
single_player_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, 300, 70, "Single Player", font_medium, "single_player_difficulty_select")
two_player_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20, 300, 70, "Two Player", font_medium, "two_player")
quit_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 120, 300, 70, "Quit", font_medium, "quit")

# AI Modes Sub-Menu Buttons 
easy_ai_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150, 300, 70, "Easy AI", font_medium, "easy")
medium_ai_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 70, "Medium AI", font_medium, "medium")
hard_ai_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 70, "Hard AI", font_medium, "hard")
survival_mode_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150, 300, 70, "Survival Mode", font_medium, "survival")
back_to_main_menu_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 250, 300, 70, "Back", font_medium, "menu")

# Game Over Screen Buttons 
play_again_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 70, "Play Again", font_medium, "play_again")
game_over_back_to_menu_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 130, 300, 70, "Back to Menu", font_medium, "menu")


# --- Drawing Functions for Different Game States ---

def draw_background():
    """Draws a subtle gradient background."""
    for i in range(SCREEN_HEIGHT // 2):
        color_val = max(0, int(BLACK[0] + (DARK_GRAY[0] - BLACK[0]) * (i / (SCREEN_HEIGHT // 2))))
        pygame.draw.line(screen, (color_val, color_val, color_val), (0, i), (SCREEN_WIDTH, i))
        pygame.draw.line(screen, (color_val, color_val, color_val), (0, SCREEN_HEIGHT - 1 - i), (SCREEN_WIDTH, SCREEN_HEIGHT - 1 - i))


def draw_arena_elements():
    """Draws the arena-specific elements based on the current_arena."""
    
    if current_arena == "basketball":
        # Orange themed basketball court
        line_color = BASKETBALL_ORANGE
        
        # Keys (half-court)
        pygame.draw.rect(screen, line_color, (50, SCREEN_HEIGHT//2 - 100, 150, 200), 5)
        pygame.draw.rect(screen, line_color, (SCREEN_WIDTH - 200, SCREEN_HEIGHT//2 - 100, 150, 200), 5)
        
        # Center circle 
        pygame.draw.circle(screen, line_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 100, 5)
        
        # Hoops
        pygame.draw.circle(screen, PARTICLE_COLOR, (40, SCREEN_HEIGHT//2), 10, 5)
        pygame.draw.circle(screen, PARTICLE_COLOR, (SCREEN_WIDTH - 40, SCREEN_HEIGHT//2), 10, 5)
        
    elif current_arena == "table_tennis":
        # Table Tennis style: solid blue table area with white lines
        
        # 1. Fill the playing area with the Table Tennis Blue
        pygame.draw.rect(screen, TABLE_TENNIS_BLUE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 2. Draw the white boundary lines (the "table" edge)
        pygame.draw.rect(screen, ARENA_LINE_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 10)
        
        # 3. Draw the center line/net (thick white line)
        pygame.draw.line(screen, ARENA_LINE_COLOR, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 5)
        
        # 4. Draw the court dividing line for doubles (the small line per side, usually only in half-court)
        pygame.draw.line(screen, ARENA_LINE_COLOR, (SCREEN_WIDTH // 2 - 2, 0), (SCREEN_WIDTH // 2 - 2, SCREEN_HEIGHT), 1)
        pygame.draw.line(screen, ARENA_LINE_COLOR, (SCREEN_WIDTH // 2 + 2, 0), (SCREEN_WIDTH // 2 + 2, SCREEN_HEIGHT), 1)
        
    else: # "original" (Default/Fallback)
        # Draw the original middle line and center circle
        pygame.draw.line(screen, GRAY, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 5)
        pygame.draw.circle(screen, GRAY, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 100, 5)


def draw_arena_loading_screen():
    """Draws the screen that randomly selects and displays the next arena."""
    draw_background() 

    arena_name = current_arena.replace("_", " ").title()
    
    # 1. Loading Text 
    loading_text = font_large.render("LOADING ARENA...", True, WHITE)
    loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(loading_text, loading_rect)
    
    # 2. Arena Name Reveal
    arena_text = font_medium.render(f"Arena: {arena_name}", True, ACCENT_COLOR)
    arena_rect = arena_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(arena_text, arena_rect)
    
    # 3. Simple Animation (Loading dots)
    dots = int(time.time() * 3) % 4 
    dots_text = font_medium.render("." * dots, True, LIGHT_GRAY)
    screen.blit(dots_text, (loading_rect.right + 10, loading_rect.centery - 10))


def draw_menu():
    """Draws the main menu screen."""
    draw_background()

    title_text = font_large.render("PyPong", True, ACCENT_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
    screen.blit(title_text, title_rect)

    controls_text = font_small.render("Player 1: UP/DOWN Arrows | Player 2: W/S Keys (2P mode)", True, LIGHT_GRAY)
    controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140))
    screen.blit(controls_text, controls_rect)

    single_player_button.draw(screen) 
    two_player_button.draw(screen)
    quit_button.draw(screen)

def draw_single_player_difficulty_select_menu():
    """Draws the Single Player menu (formerly AI Modes)."""
    draw_background()

    # CLEANED UP HEADER TEXT
    title_text = font_large.render("Single Player", True, ACCENT_COLOR) 
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250))
    screen.blit(title_text, title_rect)

    easy_ai_button.draw(screen)
    medium_ai_button.draw(screen)
    hard_ai_button.draw(screen)
    survival_mode_button.draw(screen)
    back_to_main_menu_button.draw(screen)


def draw_game():
    """Draws the main game screen, including particles and survival info."""
    # Only draw the gradient background if it's not the solid-color ping pong table
    if current_arena != "table_tennis":
        draw_background()
    
    draw_arena_elements() 

    # Draw paddles and ball
    paddle1.draw()
    paddle2.draw()
    ball.draw()

    # Draw scores for classic modes, or time for survival mode
    if current_game_mode == "survival":
        time_text = font_medium.render(f"Time: {int(survival_time_elapsed)}s", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 20))
        speed_text = font_small.render(f"Speed: {ball.current_speed_magnitude:.1f}", True, LIGHT_GRAY)
        screen.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, 80))
    else:
        # Score text is black on the bright blue table, white otherwise
        score_color = BLACK if current_arena == "table_tennis" else WHITE 
        score_text1 = font_medium.render(str(player1_score), True, score_color)
        screen.blit(score_text1, (SCREEN_WIDTH // 4 - score_text1.get_width() // 2, 20))
        score_text2 = font_medium.render(str(player2_score), True, score_color)
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
    particles = [] 
    ball.reset()
    paddle1.rect.midleft = (50, SCREEN_HEIGHT // 2)
    paddle2.rect.midright = (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)
    paddle1.speed = 0
    paddle2.speed = 0
    ball.game_active = False 

# --- Game Start Handler (Helper function for transition logic) ---
def start_game_transition():
    """Selects the arena, resets the game, and starts the loading timer."""
    global current_arena, game_state, survival_start_time
    
    # 1. Pick Arena
    current_arena = random.choice(ARENA_STYLES)
    
    # 2. Reset Game objects 
    reset_game() 
    
    # 3. Set the state and start the timer
    game_state = "arena_loading"
    pygame.time.set_timer(ARENA_LOAD_EVENT, LOADING_TIME_MS)
    survival_start_time = time.time() 


# --- Main Game Loop ---
clock = pygame.time.Clock()
running = True

while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if event.type == BALL_ACTIVATE_EVENT: 
            if not ball.game_active:
                ball.game_active = True
                pygame.time.set_timer(BALL_ACTIVATE_EVENT, 0) 

        if event.type == ARENA_LOAD_EVENT: 
            if game_state == "arena_loading":
                pygame.time.set_timer(ARENA_LOAD_EVENT, 0)
                game_state = "game_running"


        # Handle button clicks based on current game state
        if game_state == "menu":
            if single_player_button.is_clicked(event): 
                game_state = "single_player_difficulty_select"
            elif two_player_button.is_clicked(event):
                current_game_mode = "two_player"
                start_game_transition()
            elif quit_button.is_clicked(event):
                running = False
                sys.exit()

        elif game_state == "single_player_difficulty_select":
            if easy_ai_button.is_clicked(event):
                current_game_mode = "classic_ai"
                ai_difficulty_level = "easy"
                current_ai_speed = AI_SPEEDS["easy"]
                start_game_transition()
            elif medium_ai_button.is_clicked(event):
                current_game_mode = "classic_ai"
                ai_difficulty_level = "medium"
                current_ai_speed = AI_SPEEDS["medium"]
                start_game_transition()
            elif hard_ai_button.is_clicked(event):
                current_game_mode = "classic_ai"
                ai_difficulty_level = "hard"
                current_ai_speed = AI_SPEEDS["hard"]
                start_game_transition()
            elif survival_mode_button.is_clicked(event):
                current_game_mode = "survival"
                # Survival AI speed is set here, but the perfection is implemented in the AI logic
                ai_difficulty_level = "medium" 
                current_ai_speed = AI_SPEEDS["medium"]
                start_game_transition()
            elif back_to_main_menu_button.is_clicked(event):
                game_state = "menu"

        elif game_state == "game_over":
            if play_again_button.is_clicked(event):
                # Restarts with the same game mode/difficulty but a new arena
                start_game_transition()
            
            elif game_over_back_to_menu_button.is_clicked(event):
                game_state = "menu"
                reset_game() 

        # Handle keyboard input for paddles during active game states.
        if game_state == "game_running":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    paddle1.speed = -PADDLE_SPEED
                if event.key == pygame.K_DOWN:
                    paddle1.speed = PADDLE_SPEED
                if current_game_mode == "two_player":
                    if event.key == pygame.K_w:
                        paddle2.speed = -PADDLE_SPEED
                    if event.key == pygame.K_s:
                        paddle2.speed = PADDLE_SPEED
            if event.type == pygame.KEYUP:
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
            
            # --- AI Difficulty Parameters ---
            ai_lag = 0      # Reaction delay (higher value = slower reaction)
            ai_inaccuracy = 0 # Random vertical offset (higher value = more misses)
            
            # Set parameters based on difficulty level for CLASSIC AI MODE
            if current_game_mode == "classic_ai":
                if ai_difficulty_level == "easy":
                    current_ai_speed = AI_SPEEDS["easy"]
                    ai_lag = 40 
                    ai_inaccuracy = random.randint(-40, 40) 
                elif ai_difficulty_level == "medium":
                    current_ai_speed = AI_SPEEDS["medium"]
                    ai_lag = 15 
                    ai_inaccuracy = random.randint(-20, 20) 
                elif ai_difficulty_level == "hard":
                    current_ai_speed = AI_SPEEDS["hard"]
                    ai_lag = 5 
                    ai_inaccuracy = random.randint(-5, 5) # Almost perfect, but still a small chance of error

            # Set parameters for SURVIVAL MODE (PERFECT AI)
            elif current_game_mode == "survival":
                # Uses medium speed, but with NO delay and NO inaccuracy.
                current_ai_speed = AI_SPEEDS["medium"]
                ai_lag = 0        # Perfect reaction
                ai_inaccuracy = 0 # Perfect aim

            
            # --- AI Movement Logic ---
            if ball.game_active:
                
                # AI targets the center of the ball (perfectly centered when inaccuracy is 0)
                target_position = ball.rect.centery + ai_inaccuracy
                
                # Move the paddle if the ball is outside the 'lag' zone
                if target_position < paddle2.rect.centery - ai_lag:
                    paddle2.speed = -current_ai_speed
                elif target_position > paddle2.rect.centery + ai_lag:
                    paddle2.speed = current_ai_speed
                else:
                    paddle2.speed = 0 
            else:
                paddle2.speed = 0 
            
            paddle2.move()
        elif current_game_mode == "two_player":
            paddle2.move() 

        ball.move()
        ball.check_collision(paddle1, paddle2, particles) 

        # Update and remove dead particles
        for particle in particles[:]: 
            particle.move()
            if particle.is_dead():
                particles.remove(particle)

        # Scoring Logic
        if ball.rect.left <= 0: 
            if current_game_mode == "survival":
                winning_player = "You" 
                game_state = "game_over" # Game over because the ball got past the player
            else: 
                player2_score += 1
                ball.reset()
        elif ball.rect.right >= SCREEN_WIDTH: 
            if current_game_mode == "survival":
                # AI misses are impossible, so this can only happen on initial spawn or if ball goes out 
                # a strange way (which shouldn't happen). If it happens, we assume the AI got it.
                # In Survival mode, we generally don't penalize the player if the AI 'misses' 
                # the goal is to survive the ball's speed, not the AI's mistakes.
                ball.reset()
            else: 
                player1_score += 1
                ball.reset()

        # Game Win Condition
        if current_game_mode in ["classic_ai", "two_player"]:
            if player1_score >= MAX_SCORE:
                winning_player = "Player 1"
                game_state = "game_over"
            elif player2_score >= MAX_SCORE:
                winning_player = "Player 2"
                game_state = "game_over"

        # Survival Mode Specific Logic (time tracking)
        if current_game_mode == "survival" and survival_start_time != 0:
            survival_time_elapsed = time.time() - survival_start_time

    # --- Drawing ---
    if game_state == "menu":
        draw_menu()
    elif game_state == "single_player_difficulty_select":
        draw_single_player_difficulty_select_menu()
    elif game_state == "arena_loading": 
        draw_arena_loading_screen()
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