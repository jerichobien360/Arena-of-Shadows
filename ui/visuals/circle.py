from settings import *
import pygame, random


class Circle:
    def __init__(self, x, y, radius, color, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.alpha = random.randint(100, 255)  # For transparency effect
        
        self.origin = (x, y, self.alpha)
    
    def update(self):
        # Move diagonally down-right
        self.x += self.speed
        self.y += self.speed
        
        # Updating alpha
        if self.alpha < self.origin[2]:
            self.alpha += 5
        
        # Reset position when circle moves off screen
        # Add some padding to ensure smooth transition
        if self.x > SCREEN_WIDTH + self.radius or self.y > SCREEN_HEIGHT + self.radius:
            # Reset to a random position on the top-left edge
            self.x = self.origin[0] #random.randint(-self.radius * 2, -self.radius)
            self.y = self.origin[1] #random.randint(-self.radius * 2, -self.radius)
            self.alpha = 0
    
    def draw(self, surface):
        # Create a surface with alpha for transparency
        circle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        alpha_color = (*self.color, self.alpha)
        pygame.draw.circle(circle_surface, alpha_color, (self.radius, self.radius), self.radius)
        surface.blit(circle_surface, (self.x - self.radius, self.y - self.radius))
