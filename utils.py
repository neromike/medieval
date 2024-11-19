import pygame

def scale_position(pos, screen_width, screen_height, original_width, original_height):
    # Scale a position from the original image size to the scaled display size.
    x_scale = screen_width / original_width
    y_scale = screen_height / original_height
    return pygame.Vector2(pos.x * x_scale, pos.y * y_scale)

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
def draw_x(surface, position, size=20, color=(255, 0, 0)):
    pygame.draw.line(surface, color, (position.x - size, position.y - size), (position.x + size, position.y + size), 3)
    pygame.draw.line(surface, color, (position.x + size, position.y - size), (position.x - size, position.y + size), 3)
