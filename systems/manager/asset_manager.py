import pygame

def image_load(file_path):
    try:
        icon = pygame.image.load(file_path)
        pygame.display.set_icon(icon)
        return icon
    except pygame.error:
        pass  # Continue without icon if file not found

    return
