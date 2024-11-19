import pygame

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
