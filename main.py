import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
screen_width, screen_height = 3309, 1886
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Medieval")

# Load the background image
background_image = pygame.image.load("map.jpg")

# Grid settings
grid_size = 100  # Size of each grid cell in pixels

# Function to load a specific row of sprites from a sprite sheet
def load_sprites(sprite_sheet, row, num_columns, sprite_width=32, sprite_height=32, scale_factor=4, flip=False):
    sprites = []
    for col in range(num_columns):
        sprite = sprite_sheet.subsurface((col * sprite_width, row * sprite_height, sprite_width, sprite_height))
        sprite = pygame.transform.scale(sprite, (sprite_width * scale_factor, sprite_height * scale_factor))
        if flip:
            sprite = pygame.transform.flip(sprite, True, False)
        sprites.append(sprite)
    return sprites

# Unified Character class
class Character:
    def __init__(self, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction="down", is_player=False):
        self.image = pygame.image.load(sprite_sheet_path)
        self.animations = self.load_animations(animations_config)
        self.idle_animations = self.load_animations(idle_config)
        self.pos = pygame.Vector2(initial_pos)
        self.speed = speed
        self.target_pos = None
        self.direction = direction
        self.frame_index = 0
        self.animation_speed = 0.1
        self.idle_timer = 0  # Time since last movement
        self.is_idle = False  # Flag to check if character is idle
        self.is_player = is_player  # Flag to check if character is controlled by player

    def load_animations(self, config):
        animations = {}
        for direction, params in config.items():
            row, num_columns, flip = params
            animations[direction] = load_sprites(self.image, row, num_columns, flip=flip)
        return animations

    def move_toward_target(self):
        if self.target_pos:
            move_direction = self.target_pos - self.pos
            distance = move_direction.length()
            if distance > self.speed:
                move_direction = move_direction.normalize()
                self.pos += move_direction * self.speed
                self.update_direction(move_direction)

                # Reset idle timer and flag when moving
                self.idle_timer = 0
                self.is_idle = False

                # Update frame index for movement animation
                self.frame_index += self.animation_speed
                if self.frame_index >= len(self.animations[self.direction]):
                    self.frame_index = 0
            else:
                self.pos = self.target_pos
                self.target_pos = None
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
        if self.is_player:  # Only update target if this character is the player
            # Calculate the center of the grid cell clicked
            grid_x = int(click_pos.x // grid_size) * grid_size + grid_size // 2
            grid_y = int(click_pos.y // grid_size) * grid_size + grid_size // 2
            self.target_pos = pygame.Vector2(grid_x, grid_y)

# NPC Manager to handle multiple NPCs and player
class CharacterManager:
    def __init__(self):
        self.characters = []
        self.player = None  # Initialize player attribute to avoid defining it outside __init__

    def add_character(self, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction, is_player=False):
        character = Character(sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction, is_player)
        self.characters.append(character)
        if is_player:
            self.player = character  # Assign the player character if is_player is True

    def update_and_draw(self, surface):
        for character in self.characters:
            character.move_toward_target()
            character.draw(surface)


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
character_manager.add_character("Cute_Fantasy_Free/Player/player.png", player_animations_config, player_idle_config,
                                initial_pos=(100, 100), speed=2, direction="down", is_player=True)
character_manager.add_character("Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=(300, 300), speed=1, direction="down")
character_manager.add_character("Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=(500, 500), speed=1, direction="left")
character_manager.add_character("Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=(700, 700), speed=1, direction="up")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Send the click position to the player character only
            character_manager.player.handle_input(pygame.Vector2(event.pos))

    # Clear the screen and draw the background image
    screen.blit(background_image, (0, 0))

    # Draw the grid lines for debugging
    for x in range(0, screen_width, grid_size):
        pygame.draw.line(screen, (0, 0, 0), (x, 0), (x, screen_height), 1)  # Vertical lines
    for y in range(0, screen_height, grid_size):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (screen_width, y), 1)  # Horizontal lines

    # Update and draw all characters
    character_manager.update_and_draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Clean up and quit pygame
pygame.quit()
sys.exit()
