from systems.manager.decorator_manager import *
import pygame

def image_icon_load(file_path):
    '''This will be used to import the image/sprite'''
    try:
        icon = pygame.image.load(file_path).convert_alpha()
        pygame.display.set_icon(icon)
        return icon
    except pygame.error:
        error_message(file_path, name="File")
        pass

    return

def image_background_load(file_path, SCREEN_WIDTH, SCREEN_HEIGHT):
    '''This will be used to import the resized background onto the screen'''
    try:
        background = pygame.image.load(file_path)
        return pygame.transform.scale(background,(SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        error_message(file_path, name="File")
        pass

    return

def create_font(file_path, size=12):
    try:
        font = pygame.font.Font(file_path, size)
    except pygame.error:
        error_message(file_path, name="Font")
        pass

    return font
