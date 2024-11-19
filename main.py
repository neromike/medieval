import pygame
import sys
from graph import Graph, distance, get_node_id
from character import CharacterManager
from time_manager import TimeManager
from modal import Modal
from farm_game import FarmGame
from utils import scale_position, draw_x

# Initialize pygame
pygame.init()

# Screen settings
screen_info = pygame.display.Info()
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Medieval")

# Load the background image (original size)
background_image_original = pygame.image.load("map.jpg")
original_width, original_height = background_image_original.get_size()

# Scale the background image to full screen
background_image = pygame.transform.scale(background_image_original, (screen_width, screen_height))

# Grid settings
grid_size = 20  # Size of each grid cell in pixels

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
# Define modal coordinates (position and size)
modal_position_original = pygame.Vector2(4800, 1720)
modal_size_original = pygame.Vector2(3000, 3380)

# Define intermediate nodes (positions the player passes through but can't stop at)
intermediate_positions_original = [
    {"pos": pygame.Vector2(2500, 4500)},
    {"pos": pygame.Vector2(3500, 2500)},
    {"pos": pygame.Vector2(4500, 2500)},
]

# Scale positions
allowed_positions = []
for loc in allowed_positions_original:
    scaled_pos = scale_position(loc["pos"], screen_width, screen_height, original_width, original_height)
    allowed_positions.append({"name": loc["name"], "pos": scaled_pos})

modal_position = scale_position(modal_position_original, screen_width, screen_height, original_width, original_height)
modal_size = scale_position(modal_size_original, screen_width, screen_height, original_width, original_height)
intermediate_positions = [scale_position(node['pos'], screen_width, screen_height, original_width, original_height) for node in intermediate_positions_original]

# Create the graph
graph = Graph()

# Add nodes to the graph
node_id_counter = 0
node_ids = {}  # Map positions to node ids

for loc in allowed_positions:
    node_id = node_id_counter
    node_id_counter += 1
    graph.add_node(node_id, loc['pos'])
    node_ids[loc['name']] = node_id

# Add intermediate nodes to the graph
for pos in intermediate_positions:
    node_id = node_id_counter
    node_id_counter += 1
    graph.add_node(node_id, pos)

# Update connections to include intermediate nodes
intermediate_node_ids = list(range(len(allowed_positions), len(allowed_positions) + len(intermediate_positions)))

# Define connections
connections = [
    ("Farm", intermediate_node_ids[0]),
    (intermediate_node_ids[0], "Herbalist"),
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
    ("Butcher", "Elder"),
    # ... add more connections as needed
]

# Add edges to the graph
for from_loc, to_loc in connections:
    from_node = get_node_id(from_loc, node_ids)
    to_node = get_node_id(to_loc, node_ids)
    from_pos = graph.nodes[from_node]
    to_pos = graph.nodes[to_node]
    cost = distance(from_pos, to_pos)
    graph.add_bidirectional_edge(from_node, to_node, cost)

# Initialize the CharacterManager and add characters
character_manager = CharacterManager(graph, allowed_positions, node_ids)

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

# Add characters
initial_pos = allowed_positions[0]['pos']
character_manager.add_character("player", "Cute_Fantasy_Free/Player/player.png", player_animations_config, player_idle_config,
                                initial_pos=initial_pos, speed=20, is_player=True)
character_manager.add_character("enemy1", "Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=scale_position(pygame.Vector2(2990, 3860), screen_width, screen_height, original_width, original_height), direction="left", speed=1)
character_manager.add_character("enemy2", "Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=scale_position(pygame.Vector2(3000, 4350), screen_width, screen_height, original_width, original_height), direction="left", speed=1)
character_manager.add_character("butcher", "Cute_Fantasy_Free/Player/player.png", npc_animations_config, npc_idle_config,
                                initial_pos=allowed_positions[5]['pos'], speed=1)
character_manager.add_character("brewer", "Cute_Fantasy_Free/Player/player.png", npc_animations_config, npc_idle_config,
                                initial_pos=allowed_positions[4]['pos'], speed=1)

# Initialize the TimeManager
time_manager = TimeManager()

# Initialize the Modal
modal = Modal(modal_position, modal_size)

# Initialize the FarmGame once when the program first runs
farm_game = FarmGame(modal.rect)

# Function to draw everything on the screen, other than modal content
def draw():
    # Draw background
    screen.blit(background_image, (0, 0))

    # Draw allowed positions as "X" marks
    for loc in allowed_positions:
        draw_x(screen, loc['pos'])

    # Draw edges (paths) between nodes
    for node_id, edges in graph.edges.items():
        for neighbor_id, _ in edges:
            start_pos = graph.nodes[node_id]
            end_pos = graph.nodes[neighbor_id]
            pygame.draw.line(screen, (255, 255, 0), start_pos, end_pos, 2)

    # Draw all characters
    character_manager.draw(screen)

    # Draw the modal if active
    if modal.active:
        modal.draw(screen, farm_game)

    # Draw current time
    time_manager.draw_time(screen)

    # Update the display
    pygame.display.flip()

# Main game loop
running = True
in_game_movement_speed = 200  # Pixels per in-game minute

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if modal.active:
                modal.handle_event(event, farm_game)
            character_manager.player.handle_input(pygame.Vector2(event.pos))

    if modal.active:
        modal.update()

    # Update mini-games
    farm_game.update()

    # Update character positions and get distance moved by player
    distance_moved = character_manager.update()

    # Advance time whenever Player is moving
    if distance_moved > 0:
        time_increment_in_minutes = distance_moved / in_game_movement_speed
        time_manager.advance_time(time_increment_in_minutes)

    # Check if player has arrived at a new location
    if character_manager.player.has_arrived_at_new_location():
        # Display modal
        modal.active = True
        modal.set_content(character_manager.player.current_location_name, farm_game)
    elif character_manager.player.current_location_name is None:
        modal.active = False

    # Draw everything
    draw()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Clean up and quit pygame
pygame.quit()
sys.exit()
