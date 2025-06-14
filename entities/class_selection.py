# game_states/class_selection.py
from settings import *
from entities.character_classes import *
import pygame
import math

class ClassSelectionState:
    """State for selecting character class before starting the game"""
    
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 32)
        
        # Available classes
        self.classes = ['warrior', 'mage', 'fireshooter']
        self.class_objects = [CHARACTER_CLASSES[cls] for cls in self.classes]
