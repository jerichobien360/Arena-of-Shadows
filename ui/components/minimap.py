import pygame

class MiniMap:
    def __init__(self, world_width, world_height, width=180, height=120, margin=16):
        self.world_width = world_width
        self.world_height = world_height
        self.width = width
        self.height = height
        self.margin = margin
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def draw(self, screen, player, enemies, camera=None):
        # Clear minimap
        self.surface.fill((0, 0, 0, 120))  # semi-transparent background
        # Draw world border
        pygame.draw.rect(self.surface, (200, 200, 200), (0, 0, self.width, self.height), 2)

        # Draw player
        px = int((player.x / self.world_width) * self.width)
        py = int((player.y / self.world_height) * self.height)
        pygame.draw.circle(self.surface, (0, 255, 0), (px, py), 5)

        # Draw enemies
        for enemy in enemies:
            ex = int((enemy.x / self.world_width) * self.width)
            ey = int((enemy.y / self.world_height) * self.height)
            pygame.draw.circle(self.surface, (255, 0, 0), (ex, ey), 3)

        # Optionally, draw camera viewport
        if camera:
            cam_x = int((camera.x / self.world_width) * self.width)
            cam_y = int((camera.y / self.world_height) * self.height)
            cam_w = int((camera.screen_width / self.world_width) * self.width)
            cam_h = int((camera.screen_height / self.world_height) * self.height)
            pygame.draw.rect(self.surface, (0, 120, 255), (cam_x, cam_y, cam_w, cam_h), 1)

        # Blit minimap to screen (top-right corner by default)
        screen.blit(self.surface, (screen.get_width() - self.width - self.margin, self.margin))
