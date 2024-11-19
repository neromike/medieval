import pygame

# Define the FarmTile class for the farming mini-game
class FarmTile:
    def __init__(self, rect):
        self.rect = rect
        self.planted = False
        self.growth_stage = 0
        self.growth_time = 0
        self.max_growth_stage = 3
        self.growth_stage_durations = [5000, 5000, 5000]  # milliseconds for each stage
        self.last_update_time = pygame.time.get_ticks()

    def handle_click(self):
        if not self.planted:
            self.planted = True
            self.growth_stage = 1
            self.last_update_time = pygame.time.get_ticks()
        elif self.growth_stage == self.max_growth_stage:
            # Harvest the plant
            self.planted = False
            self.growth_stage = 0
            # Maybe add to player's inventory

    def update(self):
        if self.planted and self.growth_stage < self.max_growth_stage:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time > self.growth_stage_durations[self.growth_stage - 1]:
                self.growth_stage += 1
                self.last_update_time = current_time

    def draw(self, surface):
        # Draw the tile
        if self.planted:
            # Draw the plant image according to growth stage
            color = [(139,69,19), (85,107,47), (34,139,34), (0,128,0)][self.growth_stage]
            pygame.draw.rect(surface, color, self.rect)
        else:
            # Draw soil
            pygame.draw.rect(surface, (139,69,19), self.rect)
        # Draw tile border
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 1)

# Define the FarmGame class for the farming mini-game
class FarmGame:
    def __init__(self, modal_rect):
        self.modal_rect = modal_rect
        self.farm_rect = pygame.Rect(modal_rect.x + 20, modal_rect.y + 50, modal_rect.width - 40, modal_rect.height - 70)
        self.tiles = []  # List of tiles
        self.init_tiles()

    def init_tiles(self):
        # Initialize a grid of farm tiles
        tile_size = 100
        rows = self.farm_rect.height // tile_size
        cols = self.farm_rect.width // tile_size
        self.tiles = []
        for row in range(rows):
            for col in range(cols):
                tile_rect = pygame.Rect(self.farm_rect.x + col * tile_size, self.farm_rect.y + row * tile_size, tile_size, tile_size)
                tile = FarmTile(tile_rect)
                self.tiles.append(tile)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is within any tile
            for tile in self.tiles:
                if tile.rect.collidepoint(event.pos):
                    tile.handle_click()
                    break

    def update(self):
        # Update the growth of plants
        for tile in self.tiles:
            tile.update()

    def draw(self, surface):
        # Draw the farm tiles
        for tile in self.tiles:
            tile.draw(surface)
