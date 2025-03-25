import numpy as np
import random
from src.utils.constants import *

class Maze:
    def __init__(self, level):
        self.level = level
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.generate_maze()
        self.place_collectibles()

    def generate_maze(self):
        # Fill the grid with walls
        self.grid.fill(Cell.WALL)
        
        def carve_path(x, y):
            self.grid[y, x] = Cell.PATH
            
            # Define possible directions
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_SIZE and 
                    0 <= new_y < GRID_SIZE and 
                    self.grid[new_y, new_x] == Cell.WALL):
                    # Carve the wall between current and new position
                    self.grid[y + dy//2, x + dx//2] = Cell.PATH
                    carve_path(new_x, new_y)

        # Start from position (1, 1)
        carve_path(1, 1)
        
        # Set start and exit positions
        self.grid[1, 1] = Cell.START
        
        # Find a suitable exit position (far from start)
        max_distance = 0
        exit_pos = (GRID_SIZE-2, GRID_SIZE-2)
        
        for y in range(1, GRID_SIZE-1, 2):
            for x in range(1, GRID_SIZE-1, 2):
                if self.grid[y, x] == Cell.PATH:
                    distance = abs(x - 1) + abs(y - 1)
                    if distance > max_distance:
                        max_distance = distance
                        exit_pos = (x, y)
        
        self.grid[exit_pos[1], exit_pos[0]] = Cell.EXIT
        
        # Add some random connections to make the maze more interesting
        for _ in range(self.level):
            x = random.randrange(2, GRID_SIZE-2)
            y = random.randrange(2, GRID_SIZE-2)
            if self.grid[y, x] == Cell.WALL:
                # Check if connecting two paths
                paths_around = 0
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if (self.grid[y+dy, x+dx] == Cell.PATH or 
                        self.grid[y+dy, x+dx] == Cell.START or 
                        self.grid[y+dy, x+dx] == Cell.EXIT):
                        paths_around += 1
                if paths_around >= 2:
                    self.grid[y, x] = Cell.PATH

    def place_collectibles(self):
        # Place coins and power-ups
        empty_cells = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y, x] == Cell.PATH:
                    empty_cells.append((x, y))
        
        # Place more coins for higher levels
        num_coins = min(len(empty_cells) // 4, 5 + self.level)
        num_powerups = min(len(empty_cells) // 8, 2 + self.level // 3)
        
        if empty_cells:
            # Place coins
            for _ in range(num_coins):
                if empty_cells:
                    pos = random.choice(empty_cells)
                    empty_cells.remove(pos)
                    self.grid[pos[1], pos[0]] = Cell.COIN
            
            # Place power-ups
            for _ in range(num_powerups):
                if empty_cells:
                    pos = random.choice(empty_cells)
                    empty_cells.remove(pos)
                    self.grid[pos[1], pos[0]] = Cell.POWER_UP

    def is_valid_move(self, x, y):
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False
        return self.grid[y, x] != Cell.WALL

    def get_cell(self, x, y):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            return self.grid[y, x]
        return Cell.WALL

    def collect_item(self, x, y):
        # Add bounds checking
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return None
            
        if self.grid[y, x] == Cell.COIN:
            self.grid[y, x] = Cell.PATH
            return 'coin'
        elif self.grid[y, x] == Cell.POWER_UP:
            self.grid[y, x] = Cell.PATH
            return 'power_up'
        return None 