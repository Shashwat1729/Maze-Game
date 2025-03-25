import random
import pygame
import math
from src.utils.constants import *

class Particle:
    def __init__(self, x, y, color, size, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.fade_speed = random.uniform(0.5, 1.5)

    def update(self, dt):
        self.age += dt * self.fade_speed
        self.x += self.dx * dt * 30
        self.y += self.dy * dt * 30
        return self.age < self.lifetime

    def draw(self, screen, cell_size, padding):
        alpha = int(255 * (1 - self.age / self.lifetime))
        color = (*self.color[:3], min(self.color[3], alpha))
        pos = (padding + int(self.x * cell_size), padding + int(self.y * cell_size))
        
        # Draw particle with fade effect
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, 
                         (int(self.size), int(self.size)), self.size)
        screen.blit(particle_surface, 
                   (pos[0] - int(self.size), pos[1] - int(self.size)))

class Enemy:
    def __init__(self, level):
        self.reset()
        self.level = level
        self.update_speed()
        self.path = []
        self.current_path_index = 0
        self.animation_progress = 0
        self.target_x = self.x
        self.target_y = self.y
        self.current_direction = None
        self.last_valid_direction = None
        self.glow_size = GLOW_RADIUS
        self.glow_direction = 1
        self.waiting_at_intersection = False
        self.pulse_alpha = 255
        self.pulse_direction = -1
        self.optimal_path_to_exit = []
        self.wrong_path_threshold = 3
        self.particles = []
        self.trail_points = []
        self.trail_fade = 1.0
        self.shake_offset = (0, 0)
        self.shake_intensity = 0
        self.rotation = 0
        self.target_rotation = 0
        self.scale = 1.0
        self.target_scale = 1.0

    def reset(self):
        self.x = 1
        self.y = 1
        self.target_x = self.x
        self.target_y = self.y
        self.speed = INITIAL_ENEMY_SPEED
        self.path = []
        self.current_path_index = 0
        self.animation_progress = 0
        self.current_direction = None
        self.last_valid_direction = None
        self.waiting_at_intersection = False
        self.optimal_path_to_exit = []
        self.glow_size = GLOW_RADIUS
        self.pulse_alpha = 255
        self.particles = []
        self.trail_points = []
        self.trail_fade = 1.0
        self.shake_offset = (0, 0)
        self.shake_intensity = 0
        self.rotation = 0
        self.target_rotation = 0
        self.scale = 1.0
        self.target_scale = 1.0

    def update_speed(self):
        # Always maintain at least half of player's speed
        base_speed = max(PLAYER_SPEED / 2, INITIAL_ENEMY_SPEED + (self.level * SPEED_INCREASE_PER_LEVEL))
        self.speed = min(base_speed, MAX_ENEMY_SPEED)

    def find_optimal_path_to_exit(self, maze, start_pos):
        """Find the optimal path to the exit from any position"""
        def manhattan_distance(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # Find exit position
        exit_pos = None
        for y in range(maze.grid.shape[0]):
            for x in range(maze.grid.shape[1]):
                if maze.grid[y, x] == Cell.EXIT:
                    exit_pos = (x, y)
                    break
            if exit_pos:
                break

        if not exit_pos:
            return []

        open_set = {start_pos}
        closed_set = set()
        came_from = {}
        g_score = {start_pos: 0}
        f_score = {start_pos: manhattan_distance(start_pos, exit_pos)}

        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == exit_pos:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_pos)
                return path[::-1]

            open_set.remove(current)
            closed_set.add(current)

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x = current[0] + dx
                new_y = current[1] + dy
                neighbor = (new_x, new_y)
                
                if (neighbor in closed_set or 
                    not maze.is_valid_move(new_x, new_y)):
                    continue

                tentative_g_score = g_score[current] + 1

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, exit_pos)

        return []

    def should_wait_at_intersection(self, maze, player_pos):
        """Determine if we should wait at the current intersection"""
        if not self.optimal_path_to_exit:
            self.optimal_path_to_exit = self.find_optimal_path_to_exit(maze, player_pos)
            return False

        if not self.optimal_path_to_exit:
            return False

        # Check if player is on wrong path
        min_distance = float('inf')
        for point in self.optimal_path_to_exit:
            dist = abs(point[0] - player_pos[0]) + abs(point[1] - player_pos[1])
            min_distance = min(min_distance, dist)

        # Count available directions at current position
        current_pos = (int(self.x), int(self.y))
        available_directions = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if maze.is_valid_move(current_pos[0] + dx, current_pos[1] + dy):
                available_directions += 1

        # Wait if:
        # 1. We're at an intersection (3 or more directions)
        # 2. Player is off the optimal path but not too far
        # 3. Player is moving away from optimal path
        return (available_directions >= 3 and 
                min_distance > 0 and 
                min_distance <= self.wrong_path_threshold)

    def find_path_to_player(self, maze, player_pos):
        """Find path to player using A* with momentum preservation"""
        # Check if we should wait at intersection
        if self.should_wait_at_intersection(maze, player_pos):
            self.waiting_at_intersection = True
            return [(int(self.x), int(self.y))]  # Stay in place
        else:
            self.waiting_at_intersection = False

        def manhattan_distance(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        start_pos = (int(self.x), int(self.y))
        if start_pos == player_pos:
            return []

        # Rest of the pathfinding code remains the same
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        if self.last_valid_direction:
            if self.last_valid_direction in directions:
                directions.remove(self.last_valid_direction)
                directions.insert(0, self.last_valid_direction)

        open_set = {start_pos}
        closed_set = set()
        came_from = {}
        g_score = {start_pos: 0}
        f_score = {start_pos: manhattan_distance(start_pos, player_pos)}

        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == player_pos:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_pos)
                return path[::-1]

            open_set.remove(current)
            closed_set.add(current)

            for dx, dy in directions:
                new_x = current[0] + dx
                new_y = current[1] + dy
                neighbor = (new_x, new_y)
                
                if (neighbor in closed_set or 
                    not maze.is_valid_move(new_x, new_y)):
                    continue

                direction_change_cost = 0
                if self.last_valid_direction and (dx, dy) != self.last_valid_direction:
                    direction_change_cost = 0.5

                tentative_g_score = g_score[current] + 1 + direction_change_cost

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, player_pos)

        return self.get_fallback_move(maze, player_pos)

    def get_fallback_move(self, maze, player_pos):
        """Get a valid move towards the player when no path is found"""
        current_pos = (int(self.x), int(self.y))
        dx = player_pos[0] - current_pos[0]
        dy = player_pos[1] - current_pos[1]
        
        # Try to maintain current direction if it's valid
        if self.last_valid_direction:
            new_x = current_pos[0] + self.last_valid_direction[0]
            new_y = current_pos[1] + self.last_valid_direction[1]
            if maze.is_valid_move(new_x, new_y):
                return [(new_x, new_y)]

        # Try primary direction
        if abs(dx) > abs(dy):
            if dx != 0:
                new_x = current_pos[0] + (1 if dx > 0 else -1)
                if maze.is_valid_move(new_x, current_pos[1]):
                    return [(new_x, current_pos[1])]
        else:
            if dy != 0:
                new_y = current_pos[1] + (1 if dy > 0 else -1)
                if maze.is_valid_move(current_pos[0], new_y):
                    return [(current_pos[0], new_y)]

        # Try any valid move
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = current_pos[0] + dx
            new_y = current_pos[1] + dy
            if maze.is_valid_move(new_x, new_y):
                return [(new_x, new_y)]

        return []

    def add_particles(self, amount, size_range=(2, 4)):
        for _ in range(amount):
            size = random.uniform(*size_range)
            if self.waiting_at_intersection:
                color = (*RED, random.randint(100, 200))
            else:
                color = (*RED, random.randint(50, 150))
            particle = Particle(self.x, self.y, color, size)
            self.particles.append(particle)

    def update_particles(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def update_trail(self):
        # Add current position to trail
        current_pos = (self.x, self.y)
        if not self.trail_points or (abs(current_pos[0] - self.trail_points[-1][0]) > 0.1 or 
                                   abs(current_pos[1] - self.trail_points[-1][1]) > 0.1):
            self.trail_points.append(current_pos)
        
        # Limit trail length
        if len(self.trail_points) > 8:
            self.trail_points.pop(0)

        # Update trail fade
        self.trail_fade = max(0, self.trail_fade - 0.02)
        if self.trail_fade <= 0:
            self.trail_points = self.trail_points[-2:]
            self.trail_fade = 1.0

    def update_shake(self, dt):
        if self.shake_intensity > 0:
            self.shake_intensity *= 0.9
            angle = random.uniform(0, math.pi * 2)
            self.shake_offset = (
                math.cos(angle) * self.shake_intensity,
                math.sin(angle) * self.shake_intensity
            )
        else:
            self.shake_offset = (0, 0)

    def update(self, dt, maze, player):
        player_pos = (int(player.x), int(player.y))
        
        # Update trail
        self.update_trail()
        
        # Always try to move
        if self.animation_progress < 1:
            # Smooth movement
            move_speed = self.speed * dt * 60
            
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
                self.animation_progress = 1
                self.current_direction = None

        else:
            # Path finding and movement logic
            if not self.path or self.current_path_index >= len(self.path):
                self.path = self.find_path_to_player(maze, player_pos)
                self.current_path_index = 0

            if self.path and self.current_path_index < len(self.path):
                next_pos = self.path[self.current_path_index]
                if maze.is_valid_move(next_pos[0], next_pos[1]):
                    self.target_x = next_pos[0]
                    self.target_y = next_pos[1]
                    self.animation_progress = 0
                    self.current_direction = (
                        next_pos[0] - int(self.x),
                        next_pos[1] - int(self.y)
                    )
                    if self.current_direction != (0, 0):
                        self.last_valid_direction = self.current_direction
                    self.current_path_index += 1
            else:
                fallback_path = self.get_fallback_move(maze, player_pos)
                if fallback_path:
                    next_pos = fallback_path[0]
                    self.target_x = next_pos[0]
                    self.target_y = next_pos[1]
                    self.animation_progress = 0
                    self.current_direction = (
                        next_pos[0] - int(self.x),
                        next_pos[1] - int(self.y)
                    )
                    if self.current_direction != (0, 0):
                        self.last_valid_direction = self.current_direction

    def draw(self, screen, cell_size, padding):
        # Draw simple trail
        if self.trail_points:
            for i in range(len(self.trail_points) - 1):
                start = self.trail_points[i]
                end = self.trail_points[i + 1]
                progress = i / len(self.trail_points)
                alpha = int(50 * progress * self.trail_fade)
                
                start_pos = (padding + int(start[0] * cell_size + cell_size/2),
                            padding + int(start[1] * cell_size + cell_size/2))
                end_pos = (padding + int(end[0] * cell_size + cell_size/2),
                          padding + int(end[1] * cell_size + cell_size/2))
                
                pygame.draw.line(screen, (*ENEMY_COLOR[:3], alpha),
                               start_pos, end_pos,
                               max(1, int(cell_size/8 * progress)))

        # Calculate position
        center_x = padding + int(self.x * cell_size + cell_size/2)
        center_y = padding + int(self.y * cell_size + cell_size/2)

        # Draw simple circular enemy
        radius = int(cell_size/3)
        pygame.draw.circle(screen, ENEMY_COLOR, (center_x, center_y), radius)
        pygame.draw.circle(screen, (*ENEMY_COLOR, 255), (center_x, center_y), radius, 2)

    def get_position(self):
        return [int(self.x), int(self.y)] 