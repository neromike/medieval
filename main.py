import pygame
import sys

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

# Unified Character class
class Character:
    def __init__(self, character_name, sprite_sheet_path, animations_config, idle_config, initial_pos, speed, direction="down", is_player=False):
        self.character_name = character_name
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
        self.hunger = 80
        self.energy = 100
        self.current_location_name = None
        self.target_location_name = None

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

    def handle_input(self, click_pos):
        if self.is_player:  # Only update target if this character is the player
            # Find the closest allowed position to the click
            closest_location = min(allowed_positions, key=lambda loc: loc['pos'].distance_to(click_pos))
            if closest_location['pos'].distance_to(click_pos) < grid_size // 2:  # Allow a certain proximity threshold
                self.target_pos = closest_location['pos'].copy()
                self.target_location_name = closest_location['name']  # Store the name of the location

    def check_for_allowed_position(self):
        for loc in allowed_positions:
            if self.pos.distance_to(loc['pos']) < grid_size // 2:
                self.current_location_name = loc['name']
                return True
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

    def update_and_draw(self):
        for character_name in self.NPC:
            self.NPC[character_name].move_toward_target()
            self.NPC[character_name].draw(screen)
        self.player.move_toward_target()
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
character_manager.add_character("player", "Cute_Fantasy_Free/Player/player.png", player_animations_config, player_idle_config,
                                initial_pos=allowed_positions[0]['pos'], speed=20, is_player=True)
character_manager.add_character("enemy1", "Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=(scale_position(pygame.Vector2(2990, 3860))), direction="left", speed=1)
character_manager.add_character("enemy2", "Cute_Fantasy_Free/Enemies/Skeleton.png", npc_animations_config, npc_idle_config,
                                initial_pos=(scale_position(pygame.Vector2(3000, 4350))), direction="left", speed=1)
character_manager.add_character("butcher", "Cute_Fantasy_Free/Player/player.png", npc_animations_config, npc_idle_config,
                                initial_pos=allowed_positions[5]['pos'], speed=1)
character_manager.add_character("brewer", "Cute_Fantasy_Free/Player/player.png", npc_animations_config, npc_idle_config,
                                initial_pos=allowed_positions[4]['pos'], speed=1)

def draw_modal(text):
    # Calculate modal rectangle in the center of the screen
    rect = pygame.Rect(modal_coors[0][0], modal_coors[0][1], modal_coors[1][0], modal_coors[1][1])

    # Draw the rectangle
    pygame.draw.rect(screen, (255, 255, 255), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 3)

    # Display text in the modal
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, (0, 0, 0))
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

    # Update and draw all characters
    character_manager.update_and_draw()

    # Draw the modal if active
    if modal_active:
        draw_modal(modal_text)

    # Update the display
    pygame.display.flip()



# Main game loop
running = True
modal_active = False  # Initialize modal_active
modal_text = ""       # Initialize modal_text
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            character_manager.player.handle_input(pygame.Vector2(event.pos))

    # Check for modal activation
    if character_manager.player.check_for_allowed_position():
        modal_active = True
        modal_text = f"You have arrived at {character_manager.player.current_location_name}!"
    else:
        modal_active = False
        modal_text = ""

    # Draw everything
    draw()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Clean up and quit pygame
pygame.quit()
sys.exit()