import pygame
import math
from src.utils.constants import *

class Player:
    def __init__(self):
        self.reset()
        self.trail_points = []
        self.trail_fade = 1.0
        self.rotation = 0
        self.target_rotation = 0
        self.scale = 1.0
        self.target_scale = 1.0
        self.glow_size = GLOW_RADIUS
        self.glow_direction = 1
        self.power_up_active = False
        self.power_up_timer = 0

    def reset(self):
        self.x = 1
        self.y = 1
        self.target_x = self.x
        self.target_y = self.y
        self.speed = PLAYER_SPEED
        self.animation_progress = 0
        self.current_direction = None
        self.trail_points = []
        self.trail_fade = 1.0
        self.rotation = 0
        self.target_rotation = 0
        self.scale = 1.0
        self.target_scale = 1.0
        self.power_up_active = False
        self.power_up_timer = 0

    def update_trail(self):
        current_pos = (self.x, self.y)
        if not self.trail_points or (abs(current_pos[0] - self.trail_points[-1][0]) > 0.1 or 
                                   abs(current_pos[1] - self.trail_points[-1][1]) > 0.1):
            self.trail_points.append(current_pos)
        
        if len(self.trail_points) > 8:
            self.trail_points.pop(0)

        self.trail_fade = max(0, self.trail_fade - 0.02)
        if self.trail_fade <= 0:
            self.trail_points = self.trail_points[-2:]
            self.trail_fade = 1.0

    def move(self, dx, dy, maze):
        # Calculate target position
        new_x = int(self.x) + dx
        new_y = int(self.y) + dy

        # Check if the move is valid
        if maze.is_valid_move(new_x, new_y):
            # Update target position
            self.target_x = new_x
            self.target_y = new_y
            self.current_direction = (dx, dy)
            return True
        return False

    def update(self, dt):
        # Update trail
        self.update_trail()
        
        # Update position with smooth movement
        if self.current_direction:
            # Calculate movement speed
            move_speed = PLAYER_SPEED * dt * 60
            
            # Calculate distance to target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            
            # Move towards target with linear interpolation
            if abs(dx) > 0.01:
                self.x += dx * move_speed
            else:
                self.x = self.target_x
                
            if abs(dy) > 0.01:
                self.y += dy * move_speed
            else:
                self.y = self.target_y
            
            # Check if we've reached the target
            if abs(dx) < 0.01 and abs(dy) < 0.01:
                self.x = self.target_x
                self.y = self.target_y
                self.current_direction = None

        # Update power-up timer
        if self.power_up_active:
            self.power_up_timer -= dt
            if self.power_up_timer <= 0:
                self.power_up_active = False

    def draw(self, screen, cell_size, padding):
        # Draw trail
        if self.trail_points:
            for i in range(len(self.trail_points) - 1):
                start = self.trail_points[i]
                end = self.trail_points[i + 1]
                progress = i / len(self.trail_points)
                alpha = int(80 * progress * self.trail_fade)
                
                start_pos = (padding + int(start[0] * cell_size + cell_size/2),
                            padding + int(start[1] * cell_size + cell_size/2))
                end_pos = (padding + int(end[0] * cell_size + cell_size/2),
                          padding + int(end[1] * cell_size + cell_size/2))
                
                trail_surface = pygame.Surface((cell_size * 3, cell_size * 3), pygame.SRCALPHA)
                pygame.draw.line(trail_surface, (*PLAYER_TRAIL_COLOR[:3], alpha), 
                               (cell_size * 1.5, cell_size * 1.5),
                               (end_pos[0] - start_pos[0] + cell_size * 1.5,
                                end_pos[1] - start_pos[1] + cell_size * 1.5),
                               max(1, int(cell_size/8 * progress)))
                
                screen.blit(trail_surface,
                           (start_pos[0] - cell_size * 1.5,
                            start_pos[1] - cell_size * 1.5))

        # Draw glow effect
        glow_surface = pygame.Surface((cell_size * 3, cell_size * 3), pygame.SRCALPHA)
        glow_color = PLAYER_GLOW if not self.power_up_active else (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 160)
        
        # Outer glow
        pygame.draw.circle(glow_surface, glow_color,
                         (cell_size * 1.5, cell_size * 1.5), self.glow_size * 1.2)
        
        # Inner glow
        inner_glow = (*PLAYER_COLOR, 150)
        pygame.draw.circle(glow_surface, inner_glow,
                         (cell_size * 1.5, cell_size * 1.5), self.glow_size * 0.8)

        # Calculate position
        center_x = padding + int(self.x * cell_size + cell_size/2)
        center_y = padding + int(self.y * cell_size + cell_size/2)

        # Apply glow
        screen.blit(glow_surface, 
                   (center_x - cell_size * 1.5,
                    center_y - cell_size * 1.5))

        # Create player surface
        size = int(cell_size * self.scale)
        player_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Draw main body (octagon shape for modern look)
        radius = size // 3
        points = []
        for i in range(8):
            angle = math.pi / 4 * i
            points.append((
                size//2 + math.cos(angle) * radius,
                size//2 + math.sin(angle) * radius
            ))
        pygame.draw.polygon(player_surface, PLAYER_COLOR, points)
        
        # Draw outline
        outline_width = 2
        if self.power_up_active:
            pygame.draw.polygon(player_surface, NEON_BLUE, points, outline_width)
        else:
            pygame.draw.polygon(player_surface, LIGHT_BLUE, points, outline_width)

        # Add direction indicator
        if self.current_direction:
            indicator_length = size//4
            start_pos = (size//2, size//2)
            end_pos = (size//2 + indicator_length, size//2)
            if self.power_up_active:
                indicator_color = NEON_BLUE
            else:
                indicator_color = LIGHT_BLUE
            pygame.draw.line(player_surface, indicator_color,
                           start_pos, end_pos, 2)

        # Rotate and draw player
        if self.current_direction:
            rotated_surface = pygame.transform.rotate(player_surface, -self.rotation)
            new_rect = rotated_surface.get_rect(center=(center_x, center_y))
            screen.blit(rotated_surface, new_rect)
        else:
            new_rect = player_surface.get_rect(center=(center_x, center_y))
            screen.blit(player_surface, new_rect)

    def get_position(self):
        return [int(self.x), int(self.y)]

    def activate_power_up(self, duration):
        self.power_up_active = True
        self.power_up_timer = duration 