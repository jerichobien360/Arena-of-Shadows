import pygame
from dataclasses import dataclass
from typing import Optional


@dataclass
class LightingConfig:
    """Lighting system configuration."""
    ambient: float = 0.4
    variation_speed: float = 0.8
    variation_amp: float = 0.05
    background_dim: float = 0.25
