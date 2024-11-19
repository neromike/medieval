import pygame
from graph import astar_search
from utils import load_sprites

# Unified Character class
class Character:
    def __init__(self, character_name, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction="down", is_player=False, graph=None, allowed_positions=None, node_ids=None):
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
        self.current_location_name = "Farm"
        self.target_location_name = None
        self.previous_location_name = None
        self.graph = graph
        self.allowed_positions = allowed_positions
        self.node_ids = node_ids

    def load_animations(self, config):
        animations = {}
        for direction, params in config.items():
            row, num_columns, flip = params
            animations[direction] = load_sprites(self.image, row, num_columns, flip=flip)
        return animations

    def move_along_path(self):
        distance_moved = 0  # Initialize distance moved
        if self.path:
            self.current_location_name = None
            target_node = self.path[0]
            target_pos = self.graph.nodes[target_node]

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

    def handle_input(self, click_pos):
        if self.is_player:
            # Only consider allowed_positions for destinations
            closest_location = min(
                self.allowed_positions,
                key=lambda loc: loc['pos'].distance_to(click_pos)
            )
            if closest_location['pos'].distance_to(click_pos) < 40:
                self.target_location_name = closest_location['name']
                self.compute_path()

    def compute_path(self):
        # Find the closest node to current position (could be an intermediate node)
        closest_node = min(
            self.graph.nodes.keys(),
            key=lambda node_id: (self.pos - self.graph.nodes[node_id]).length()
        )

        # Get target node (must be a named location)
        target_node = self.node_ids[self.target_location_name]

        # Compute path using A*
        self.path = astar_search(closest_node, target_node, self.graph)

        # Ensure the path starts from the current position
        if self.pos != self.graph.nodes[closest_node]:
            self.path.insert(0, closest_node)

    def check_for_allowed_position(self):
        for loc in self.allowed_positions:
            if self.pos.distance_to(loc['pos']) < 10:
                self.current_location_name = loc['name']
                return True
        return False

    def has_arrived_at_new_location(self):
        # Check if the player is at an allowed position (named location)
        for loc in self.allowed_positions:
            if self.pos.distance_to(loc['pos']) < 10:
                if self.current_location_name != loc['name']:
                    self.previous_location_name = self.current_location_name
                    self.current_location_name = loc['name']
                    return True
        return False

# NPC Manager to handle multiple NPCs and player
class CharacterManager:
    def __init__(self, graph, allowed_positions, node_ids):
        self.NPC = {}
        self.player = None
        self.graph = graph
        self.allowed_positions = allowed_positions
        self.node_ids = node_ids

    def add_character(self, character_name, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction="down", is_player=False):
        character = Character(character_name, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction, is_player,
                              graph=self.graph, allowed_positions=self.allowed_positions, node_ids=self.node_ids)
        if is_player:
            self.player = character
        else:
            self.NPC[character_name] = character

    def update(self):
        for character_name in self.NPC:
            self.NPC[character_name].move_along_path()
        distance_moved = self.player.move_along_path()
        return distance_moved

    def draw(self, surface):
        for character_name in self.NPC:
            self.NPC[character_name].draw(surface)
        self.player.draw(surface)
