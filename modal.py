import pygame

# Define the Modal class to handle different modal windows
class Modal:
    def __init__(self, position, size):
        self.rect = pygame.Rect(position.x, position.y, size.x, size.y)
        self.active = False
        self.background_image = None
        self.interactive_elements = []
        self.location_name = ""
        self.curr_game = None  # Will hold the farming mini-game instance when at farm

    def set_content(self, location_name, farm_game):
        self.location_name = location_name
        self.curr_game = None
        # Load the background image and interactive components based on location
        if self.location_name == "Farm":
            self.background_image = pygame.Surface(self.rect.size)
            self.background_image.fill((200, 255, 200))  # Light green background
            self.curr_game = farm_game
        else:
            self.background_image = pygame.Surface(self.rect.size)
            self.background_image.fill((200, 200, 200))
            self.curr_game = None  # No farming game at other locations

    def handle_event(self, event, farm_game):
        if self.active:
            if self.curr_game == farm_game:
                farm_game.handle_event(event)

    def update(self):
        pass  # Add any updates if necessary

    def draw(self, surface, farm_game):
        if self.active:
            # Draw the modal background
            surface.blit(self.background_image, self.rect.topleft)
            # Draw the interactive elements
            if self.location_name == "Farm":
                farm_game.draw(surface)
            else:
                # For other locations, display the location name
                font = pygame.font.Font(None, 36)
                text_surf = font.render(self.location_name, True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=self.rect.center)
                surface.blit(text_surf, text_rect)
            # Draw the modal border
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 3)
