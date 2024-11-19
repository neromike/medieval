import pygame
import sys
import heapq  # For priority queue in A* algorithm
import math

# Initialize pygame
pygame.init()

# Screen settings
screen_info = pygame.display.Info()  # Get screen resolution
screen_width, screen_height = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Medieval")

# Load the background image (original size)
background_image_original = pygame.image.load("map.jpg")
original_width, original_height = background_image_original.get_size()

# Scale the background image to full screen
background_image = pygame.transform.scale(background_image_original, (screen_width, screen_height))

# Grid settings
grid_size = 100  # Size of each grid cell in pixels

# Define allowed movement positions with names based on the original image's coordinates
allowed_positions_original = [
    {"name": "Farm", "pos": pygame.Vector2(1300, 2500)},
    {"name": "Miller", "pos": pygame.Vector2(1100, 5000)},
    {"name": "Tavern", "pos": pygame.Vector2(4100, 630)},
    {"name": "Bakery", "pos": pygame.Vector2(5300, 630)},
    {"name": "Brewery", "pos": pygame.Vector2(6600, 630)},
    {"name": "Butcher", "pos": pygame.Vector2(7900, 630)},
    {"name": "Herbalist", "pos": pygame.Vector2(4300, 2600)},
    {"name": "Cartwright", "pos": pygame.Vector2(4200, 4800)},
    {"name": "Carpenter", "pos": pygame.Vector2(5000, 5800)},
    {"name": "Blacksmith", "pos": pygame.Vector2(6400, 5800)},
    {"name": "Elder", "pos": pygame.Vector2(7600, 5800)},
    {"name": "Manor", "pos": pygame.Vector2(9700, 5900)},
    {"name": "Church", "pos": pygame.Vector2(9500, 4300)},
    {"name": "Market", "pos": pygame.Vector2(9300, 1800)},
]
modal_coors_original = [pygame.Vector2(4800, 1720), pygame.Vector2(3000, 3380)]

# Scale the allowed positions to the current screen resolution
def scale_position(pos):
    # Scale a position from the original image size to the scaled display size.
    x_scale = screen_width / original_width
    y_scale = screen_height / original_height
    return pygame.Vector2(pos.x * x_scale, pos.y * y_scale)

allowed_positions = []
for loc in allowed_positions_original:
    scaled_pos = scale_position(loc["pos"])
    allowed_positions.append({"name": loc["name"], "pos": scaled_pos})

modal_coors = [scale_position(pos) for pos in modal_coors_original]



# Define the graph nodes and edges
class Graph:
    def __init__(self):
        self.nodes = {}  # key: node id, value: position
        self.edges = {}  # key: node id, value: list of tuples (neighbor_id, cost)

    def add_node(self, node_id, position):
        self.nodes[node_id] = position
        self.edges[node_id] = []

    def add_edge(self, from_node, to_node, cost):
        self.edges[from_node].append((to_node, cost))

# Create the graph
graph = Graph()

# Add nodes to the graph
# Assign an id to each node
node_id_counter = 0
node_ids = {}  # Map positions to node ids

for loc in allowed_positions:
    node_id = node_id_counter
    node_id_counter += 1
    graph.add_node(node_id, loc['pos'])
    node_ids[loc['name']] = node_id

# Example intermediate nodes (you should define actual paths)
# For simplicity, let's assume direct paths between some locations
# In a real game, you'd define paths that follow roads or other constraints

# Add edges (paths) between nodes
def distance(pos1, pos2):
    return (pos1 - pos2).length()

# Define connections
connections = [
    ("Farm", "Herbalist"),
    ("Herbalist", "Tavern"),
    ("Tavern", "Bakery"),
    ("Bakery", "Brewery"),
    ("Brewery", "Butcher"),
    ("Herbalist", "Cartwright"),
    ("Cartwright", "Miller"),
    ("Miller", "Carpenter"),
    ("Carpenter", "Blacksmith"),
    ("Blacksmith", "Elder"),
    ("Elder", "Manor"),
    ("Manor", "Church"),
    ("Church", "Market"),
    ("Market", "Butcher"),
    ("Butcher", "Elder"),  # Loop back to Elder
    # ... add more connections as needed
]

# Add edges to the graph
for from_loc_name, to_loc_name in connections:
    from_node = node_ids[from_loc_name]
    to_node = node_ids[to_loc_name]
    from_pos = graph.nodes[from_node]
    to_pos = graph.nodes[to_node]
    cost = distance(from_pos, to_pos)
    graph.add_edge(from_node, to_node, cost)
    graph.add_edge(to_node, from_node, cost)  # Assuming bidirectional paths

# A* Pathfinding algorithm
def heuristic(a, b):
    return (graph.nodes[a] - graph.nodes[b]).length()

def astar_search(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor, cost in graph.edges[current]:
            new_cost = cost_so_far[current] + cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    # Reconstruct path
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path



# Function to load a specific row of sprites from a sprite sheet
def load_sprites(sprite_sheet, row, num_columns, sprite_width=32, sprite_height=32, scale_factor=2, flip=False):
    sprites = []
    for col in range(num_columns):
        sprite = sprite_sheet.subsurface((col * sprite_width, row * sprite_height, sprite_width, sprite_height))
        sprite = pygame.transform.scale(sprite, (sprite_width * scale_factor, sprite_height * scale_factor))
        if flip:
            sprite = pygame.transform.flip(sprite, True, False)
        sprites.append(sprite)
    return sprites

# Draw an "X" on the screen at the given position
def draw_x(position, size=20, color=(255, 0, 0)):
    pygame.draw.line(screen, color, (position.x - size, position.y - size), (position.x + size, position.y + size), 3)
    pygame.draw.line(screen, color, (position.x + size, position.y - size), (position.x - size, position.y + size), 3)

# TimeManager class to handle the game's time
class TimeManager:
    def __init__(self):
        self.total_minutes = 8 * 60  # Start at Day 1, 8:00 AM

    def advance_time(self, minutes):
        self.total_minutes += minutes

    def get_current_time(self):
        total_minutes = int(self.total_minutes)
        current_day = total_minutes // (24 * 60) + 1
        minutes_in_day = total_minutes % (24 * 60)
        current_hour = minutes_in_day // 60
        current_minute = minutes_in_day % 60
        return current_day, current_hour, current_minute

    def draw_time(self, surface):
        current_day, current_hour, current_minute = self.get_current_time()
        font = pygame.font.Font(None, 36)
        time_text = f"Day {current_day}, {current_hour:02d}:{current_minute:02d}"
        time_surf = font.render(time_text, True, (255, 255, 255))
        # Position at top-left corner
        surface.blit(time_surf, (10, 10))

# Unified Character class
class Character:
    def __init__(self, character_name, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction="down", is_player=False):
        self.character_name = character_name
        self.image = pygame.image.load(sprite_sheet_path)
        self.animations = self.load_animations(animations_config)
        self.idle_animations = self.load_animations(idle_config)
        self.pos = pygame.Vector2(initial_pos)
        self.speed = speed
        self.path = []
        self.direction = direction
        self.frame_index = 0
        self.animation_speed = 0.1
        self.idle_timer = 0  # Time since last movement
        self.is_idle = False  # Flag to check if character is idle
        self.is_player = is_player  # Flag to check if character is controlled by player
        self.hunger = 80
        self.energy = 100
        self.current_location_name = None
        self.target_location_name = None
        self.previous_location_name = None  # Added to track previous location

    def load_animations(self, config):
        animations = {}
        for direction, params in config.items():
            row, num_columns, flip = params
            animations[direction] = load_sprites(self.image, row, num_columns, flip=flip)
        return animations

    def move_along_path(self):
        distance_moved = 0  # Initialize distance moved
        if self.path:
            target_node = self.path[0]
            target_pos = graph.nodes[target_node]

            move_direction = target_pos - self.pos
            distance = move_direction.length()
            if distance > self.speed:
                move_direction = move_direction.normalize()
                old_pos = self.pos.copy()
                self.pos += move_direction * self.speed
                self.update_direction(move_direction)
                distance_moved = (self.pos - old_pos).length()

                # Reset idle timer and flag when moving
                self.idle_timer = 0
                self.is_idle = False

                # Update frame index for movement animation
                self.frame_index += self.animation_speed
                if self.frame_index >= len(self.animations[self.direction]):
                    self.frame_index = 0
            else:
                self.pos = target_pos.copy()
                self.path.pop(0)
                distance_moved = distance

                if not self.path:
                    # Arrived at destination
                    self.previous_location_name = self.current_location_name
                    self.current_location_name = self.target_location_name

        else:
            # Increment idle timer and ensure idle animation updates
            self.idle_timer += 1
            if self.idle_timer > 100:  # Adjust the threshold as needed
                self.is_idle = True
                self.frame_index += self.animation_speed
                if self.frame_index >= len(self.idle_animations[self.direction]):
                    self.frame_index = 0
            else:
                self.is_idle = False
                self.frame_index = 0  # Reset frame index if not idle
        return distance_moved

    def update_direction(self, move_direction):
        if abs(move_direction.x) > abs(move_direction.y):
            self.direction = "right" if move_direction.x > 0 else "left"
        else:
            self.direction = "down" if move_direction.y > 0 else "up"

    def get_current_sprite(self):
        if self.is_idle:
            return self.idle_animations[self.direction][int(self.frame_index)]
        else:
            return self.animations[self.direction][int(self.frame_index)]

    def draw(self, surface):
        sprite = self.get_current_sprite()

        # Adjust position for center alignment
        adjusted_pos = (self.pos.x - sprite.get_width() // 2, self.pos.y - sprite.get_height() // 2)
        surface.blit(sprite, adjusted_pos)

        """
        # Debug text
        font = pygame.font.Font(None, 24)

        # Draw character name above the character
        name_text = font.render(self.character_name, True, (255, 255, 255))
        name_text_pos = (self.pos.x - name_text.get_width() // 2, self.pos.y - sprite.get_height() // 2 - 20)
        surface.blit(name_text, name_text_pos)

        # Draw hunger level next to the character
        hunger_text = font.render(f"hunger: {self.hunger}", True, (255, 255, 255))
        hunger_text_pos = (self.pos.x + sprite.get_width() // 2 + 5, self.pos.y - sprite.get_height() // 2)
        surface.blit(hunger_text, hunger_text_pos)

        # Draw energy level below the character
        energy_text = font.render(f"energy: {self.energy}", True, (255, 255, 255))
        energy_text_pos = (self.pos.x + sprite.get_width() // 2 + 5, self.pos.y + 24 - sprite.get_height() // 2)
        surface.blit(energy_text, energy_text_pos)
        """

    def handle_input(self, click_pos):
        if self.is_player:  # Only update target if this character is the player
            # Find the closest allowed position to the click
            closest_location = min(allowed_positions, key=lambda loc: loc['pos'].distance_to(click_pos))
            if closest_location['pos'].distance_to(click_pos) < grid_size * 2:  # Allow a certain proximity threshold
                self.target_location_name = closest_location['name']  # Store the name of the location
                self.compute_path()

    def compute_path(self):
        # Find the closest node to current position
        closest_node = None
        min_distance = float('inf')
        for node_id, node_pos in graph.nodes.items():
            dist = (self.pos - node_pos).length()
            if dist < min_distance:
                min_distance = dist
                closest_node = node_id

        # Get target node
        target_node = node_ids[self.target_location_name]

        # Compute path using A*
        self.path = astar_search(closest_node, target_node)

        # Insert current position as the starting point
        if self.pos != graph.nodes[closest_node]:
            self.path.insert(0, closest_node)

    def check_for_allowed_position(self):
        for loc in allowed_positions:
            if self.pos.distance_to(loc['pos']) < grid_size // 2:
                self.current_location_name = loc['name']
                return True
        return False

    def has_arrived_at_new_location(self):
        # Check if the player has moved to a new location
        if self.previous_location_name != self.current_location_name and self.current_location_name is not None:
            return True
        else:
            return False

# NPC Manager to handle multiple NPCs and player
class CharacterManager:
    def __init__(self):
        self.NPC = {}
        self.player = None

    def add_character(self, character_name, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction="down", is_player=False):
        character = Character(character_name, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction, is_player)
        if is_player:
            self.player = character
        else:
            self.NPC[character_name] = character

    def update(self):
        for character_name in self.NPC:
            self.NPC[character_name].move_along_path()
        distance_moved = self.player.move_along_path()
        return distance_moved

    def draw(self):
        for character_name in self.NPC:
            self.NPC[character_name].draw(screen)
        self.player.draw(screen)

# Animation configurations for player and NPC
player_animations_config = {
    "down": (3, 6, False),
    "up": (5, 6, False),
    "right": (4, 6, False),
    "left": (4, 6, True)
}
player_idle_config = {
    "down": (0, 6, False),
    "up": (2, 6, False),
    "right": (1, 6, False),
    "left": (1, 6, True)
}
npc_animations_config = player_animations_config
npc_idle_config = player_idle_config

# Initialize the CharacterManager and add characters
character_manager = CharacterManager()
initial_pos = allowed_positions[0]['pos']
character_manager.add_character("player", "Cute_Fantasy_Free/Player/player.png", player_animations_config, player_idle_config,
                                initial_pos=initial_pos, speed=20, is_player=True)
character_manager.add_character("enemy1", "Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=(scale_position(pygame.Vector2(2990, 3860))), direction="left", speed=1)
character_manager.add_character("enemy2", "Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=(scale_position(pygame.Vector2(3000, 4350))), direction="left", speed=1)
character_manager.add_character("butcher", "Cute_Fantasy_Free/Player/player.png", npc_animations_config, npc_idle_config,
                                initial_pos=allowed_positions[5]['pos'], speed=1)
character_manager.add_character("brewer", "Cute_Fantasy_Free/Player/player.png", npc_animations_config, npc_idle_config,
                                initial_pos=allowed_positions[4]['pos'], speed=1)

# Initialize the TimeManager
time_manager = TimeManager()

def draw_modal():
    # Calculate modal rectangle in the center of the screen
    rect = pygame.Rect(modal_coors[0][0], modal_coors[0][1], modal_coors[1][0], modal_coors[1][1])

    # Draw the rectangle
    pygame.draw.rect(screen, (255, 255, 255), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 3)

    # Display text in the modal
    font = pygame.font.Font(None, 36)
    text_surf = font.render(character_manager.player.current_location_name, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    return

# Function to draw everything on the screen
def draw():
    # Draw background
    screen.blit(background_image, (0, 0))

    # Draw allowed positions as "X" marks
    for loc in allowed_positions:
        draw_x(loc['pos'])

    # Draw edges (paths) between nodes
    for node_id, edges in graph.edges.items():
        for neighbor_id, _ in edges:
            start_pos = graph.nodes[node_id]
            end_pos = graph.nodes[neighbor_id]
            pygame.draw.line(screen, (255, 255, 0), start_pos, end_pos, 2)

    # Draw all characters
    character_manager.draw()

    # Draw the modal if active
    if modal_active:
        draw_modal()

    # Draw current time
    time_manager.draw_time(screen)

    # Update the display
    pygame.display.flip()

# Main game loop
running = True
modal_active = False  # Initialize modal_active
curr_location = ""       # Initialize modal_text
in_game_movement_speed = 200  # Pixels per in-game minute

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            character_manager.player.handle_input(pygame.Vector2(event.pos))

    # Update character positions and get distance moved by player
    distance_moved = character_manager.update()

    if distance_moved > 0:
        # Player is moving, advance time
        time_increment_in_minutes = distance_moved / in_game_movement_speed
        time_manager.advance_time(time_increment_in_minutes)
    else:
        # Player is idle; time does not advance
        pass

    # Check if player has arrived at a new location
    if character_manager.player.has_arrived_at_new_location():
        # Display modal
        modal_active = True
    elif not character_manager.player.path:
        modal_active = False

    # Draw everything
    draw()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Clean up and quit pygame
pygame.quit()
sys.exit()