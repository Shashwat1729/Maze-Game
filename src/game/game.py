import pygame
import sys
import os
from .maze import Maze
from .player import Player
from .enemy import Enemy
from ..utils.constants import *

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Calculate window size based on grid size
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Modern Maze Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        
        self.level = 1
        self.score = 0
        self.high_score = self.load_high_score()
        self.state = MENU
        self.countdown = COUNTDOWN_DURATION
        self.immunity = IMMUNITY_DURATION
        
        # Initialize sounds dictionary
        self.sounds = {}
        
        # Try to load sounds if available, but don't fail if they're missing
        for name, file in SOUND_EFFECTS.items():
            try:
                sound_path = os.path.join(SOUNDS_DIR, file)
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(VOLUME)
                    self.sounds[name] = sound
            except Exception as e:
                print(f"Could not load sound: {file} - {str(e)}")
        
        self.reset_game()
        
        # Start background music if available
        if 'background' in self.sounds:
            self.sounds['background'].play(-1)  # Loop indefinitely

    def reset_game(self):
        self.maze = Maze(self.level)
        self.player = Player()
        self.enemy = Enemy(self.level)
        self.score = 0
        self.state = PLAYING
        self.countdown = COUNTDOWN_DURATION
        self.immunity = IMMUNITY_DURATION

    def load_high_score(self):
        try:
            with open(os.path.join(ASSETS_DIR, 'high_score.txt'), 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        try:
            with open(os.path.join(ASSETS_DIR, 'high_score.txt'), 'w') as f:
                f.write(str(self.high_score))
        except:
            pass  # Silently fail if we can't save the high score

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if self.state == PLAYING:
            # Movement keys (WASD and Arrow keys)
            dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
            
            # Only move if one direction is pressed at a time
            if dx != 0 and dy == 0:
                self.player.move(dx, 0, self.maze)
            elif dy != 0 and dx == 0:
                self.player.move(0, dy, self.maze)
            
            # Pause game
            if keys[pygame.K_ESCAPE]:
                self.state = PAUSED
        
        elif self.state == PAUSED:
            # Resume game
            if keys[pygame.K_ESCAPE]:
                self.state = PLAYING
            # Restart game
            elif keys[pygame.K_r]:
                self.reset_game()
        
        elif self.state == GAME_OVER:
            # Restart game
            if keys[pygame.K_r]:
                self.level = 1
                self.score = 0
                self.reset_game()

    def update(self, dt):
        if self.state != PLAYING:
            return

        # Update countdown and immunity
        if self.countdown > 0:
            self.countdown -= dt
            return

        if self.immunity > 0:
            self.immunity -= dt

        # Update player and enemy
        self.player.update(dt)
        self.enemy.update(dt, self.maze, self.player)

        # Check collisions
        player_pos = self.player.get_position()
        enemy_pos = self.enemy.get_position()

        # Check enemy collision
        if (player_pos == enemy_pos and 
            self.immunity <= 0 and 
            not self.player.power_up_active):
            self.state = GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            if 'game_over' in self.sounds:
                self.sounds['game_over'].play()

        # Check item collection
        item = self.maze.collect_item(*player_pos)
        if item == 'coin':
            self.score += 10
            if 'coin' in self.sounds:
                self.sounds['coin'].play()
        elif item == 'power_up':
            self.player.activate_power_up(POWER_UP_DURATION)
            if 'powerup' in self.sounds:
                self.sounds['powerup'].play()

        # Check level completion
        if self.maze.get_cell(*player_pos) == Cell.EXIT:
            self.level += 1
            self.score += 50
            if 'level_complete' in self.sounds:
                self.sounds['level_complete'].play()
            self.reset_game()

    def draw_maze_cell(self, x, y, cell_type):
        rect = pygame.Rect(
            PADDING + x * CELL_SIZE,
            PADDING + y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        
        if cell_type == Cell.WALL:
            pygame.draw.rect(self.screen, GRID_BLUE, rect)
        elif cell_type == Cell.START:
            # Draw start cell with arrow
            pygame.draw.rect(self.screen, DARK_BLUE, rect)
            pygame.draw.rect(self.screen, NEON_BLUE, rect, 2)
            
            # Draw arrow
            arrow_points = [
                (rect.centerx - 8, rect.centery),
                (rect.centerx + 4, rect.centery - 6),
                (rect.centerx + 4, rect.centery - 2),
                (rect.centerx + 8, rect.centery - 2),
                (rect.centerx + 8, rect.centery + 2),
                (rect.centerx + 4, rect.centery + 2),
                (rect.centerx + 4, rect.centery + 6),
            ]
            pygame.draw.polygon(self.screen, NEON_BLUE, arrow_points)
            
        elif cell_type == Cell.EXIT:
            # Draw exit cell with X
            pygame.draw.rect(self.screen, DARK_BLUE, rect)
            pygame.draw.rect(self.screen, LIGHT_BLUE, rect, 2)
            
            # Draw X
            margin = 6
            pygame.draw.line(self.screen, LIGHT_BLUE,
                           (rect.left + margin, rect.top + margin),
                           (rect.right - margin, rect.bottom - margin), 2)
            pygame.draw.line(self.screen, LIGHT_BLUE,
                           (rect.right - margin, rect.top + margin),
                           (rect.left + margin, rect.bottom - margin), 2)
            
        elif cell_type == Cell.COIN:
            # Draw coin
            pygame.draw.rect(self.screen, DARK_BLUE, rect)
            center = rect.center
            radius = CELL_SIZE // 4
            
            # Draw glow
            glow_surface = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*NEON_BLUE, 50), 
                             (CELL_SIZE, CELL_SIZE), radius * 1.5)
            self.screen.blit(glow_surface, 
                           (center[0] - CELL_SIZE,
                            center[1] - CELL_SIZE))
            
            # Draw coin
            pygame.draw.circle(self.screen, NEON_BLUE, center, radius)
            pygame.draw.circle(self.screen, LIGHT_BLUE, center, radius, 2)
            
        elif cell_type == Cell.POWER_UP:
            # Draw power-up
            pygame.draw.rect(self.screen, DARK_BLUE, rect)
            center = rect.center
            size = CELL_SIZE // 3
            
            # Draw glow
            glow_surface = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*LIGHT_BLUE, 50), 
                           pygame.Rect(CELL_SIZE - size, CELL_SIZE - size,
                                     size * 2, size * 2))
            self.screen.blit(glow_surface, 
                           (center[0] - CELL_SIZE,
                            center[1] - CELL_SIZE))
            
            # Draw power-up
            pygame.draw.rect(self.screen, LIGHT_BLUE,
                           pygame.Rect(center[0] - size, center[1] - size,
                                     size * 2, size * 2))
            pygame.draw.rect(self.screen, NEON_BLUE,
                           pygame.Rect(center[0] - size, center[1] - size,
                                     size * 2, size * 2), 2)
        else:
            pygame.draw.rect(self.screen, DARK_BLUE, rect)

    def draw(self):
        # Clear screen
        self.screen.fill(DARK_BLUE)
        
        # Draw maze
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_type = self.maze.get_cell(x, y)
                self.draw_maze_cell(x, y, cell_type)
        
        # Draw player and enemy
        self.player.draw(self.screen, CELL_SIZE, PADDING)
        self.enemy.draw(self.screen, CELL_SIZE, PADDING)
        
        # Draw UI in separate area below maze
        ui_y = GRID_SIZE * CELL_SIZE + 2 * PADDING
        ui_rect = pygame.Rect(0, ui_y, WINDOW_WIDTH, UI_HEIGHT)
        
        # Draw UI background
        ui_surface = pygame.Surface((WINDOW_WIDTH, UI_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(ui_surface, UI_BG_COLOR, ui_surface.get_rect())
        self.screen.blit(ui_surface, (0, ui_y))
        
        # Draw UI elements
        if self.state == MENU:
            # Draw menu text
            title = self.font.render("MAZE RUNNER", True, UI_TEXT_COLOR)
            start_text = self.small_font.render("Press SPACE to Start", True, UI_TEXT_COLOR)
            controls_text = self.small_font.render("WASD or Arrow keys to move | ESC to pause", True, UI_TEXT_COLOR)
            
            self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, ui_y + 10))
            self.screen.blit(start_text, (WINDOW_WIDTH//2 - start_text.get_width()//2, ui_y + 40))
            self.screen.blit(controls_text, (WINDOW_WIDTH//2 - controls_text.get_width()//2, ui_y + 60))
            
        elif self.state == PLAYING:
            # Draw game info
            score_text = self.font.render(f"Score: {self.score}", True, UI_TEXT_COLOR)
            level_text = self.font.render(f"Level: {self.level}", True, UI_TEXT_COLOR)
            high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, UI_TEXT_COLOR)
            
            self.screen.blit(score_text, (UI_PADDING, ui_y + 10))
            self.screen.blit(level_text, (WINDOW_WIDTH//2 - level_text.get_width()//2, ui_y + 10))
            self.screen.blit(high_score_text, (WINDOW_WIDTH - high_score_text.get_width() - UI_PADDING, ui_y + 10))
            
            # Draw countdown if active
            if self.countdown > 0:
                countdown_text = self.font.render(f"Get Ready: {int(self.countdown)}", True, UI_TEXT_COLOR)
                self.screen.blit(countdown_text, (WINDOW_WIDTH//2 - countdown_text.get_width()//2, ui_y + 40))
            
            # Draw immunity timer if active
            if self.immunity > 0:
                immunity_text = self.small_font.render(f"Immunity: {int(self.immunity)}s", True, UI_TEXT_COLOR)
                self.screen.blit(immunity_text, (WINDOW_WIDTH//2 - immunity_text.get_width()//2, ui_y + 40))
            
        elif self.state == PAUSED:
            # Draw pause text
            pause_text = self.font.render("PAUSED", True, UI_TEXT_COLOR)
            resume_text = self.small_font.render("Press ESC to Resume", True, UI_TEXT_COLOR)
            restart_text = self.small_font.render("Press R to Restart", True, UI_TEXT_COLOR)
            
            self.screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, ui_y + 10))
            self.screen.blit(resume_text, (WINDOW_WIDTH//2 - resume_text.get_width()//2, ui_y + 40))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, ui_y + 60))
            
        elif self.state == GAME_OVER:
            # Draw game over text
            game_over_text = self.font.render("GAME OVER", True, UI_TEXT_COLOR)
            score_text = self.font.render(f"Final Score: {self.score}", True, UI_TEXT_COLOR)
            restart_text = self.small_font.render("Press R to Play Again", True, UI_TEXT_COLOR)
            
            self.screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, ui_y + 10))
            self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, ui_y + 40))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, ui_y + 60))
        
        # Update display
        pygame.display.flip()

    def run(self):
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Get delta time
            dt = self.clock.tick(60) / 1000.0

            # Handle input
            self.handle_input()

            # Update game state
            self.update(dt)

            # Draw everything
            self.draw() 