from enum import Enum
from typing import List, Callable, Optional
from dataclasses import dataclass, field
import pygame

class ElementType(Enum):
    BUTTON = "button"
    LABEL = "label"
    INPUT = "input"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    SEPARATOR = "separator"

@dataclass
class PanelElement:
    type: ElementType
    id: str = ""
    text: str = ""
    value: str = ""
    options: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None
    rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))
    active: bool = False
    enabled: bool = True
    min_val: float = 0
    max_val: float = 100
    checked: bool = False
    dropdown_open: bool = False
    selected_option: int = 0
    dragging: bool = False
    placeholder: str = ""
    cursor_pos: int = 0
    selection_start: int = 0
    selection_end: int = 0
    cursor_timer: int = 0
    selecting: bool = False  # Track if user is selecting text with mouse

COLORS = {
        'bg': (40, 40, 40), 'panel': (60, 60, 60), 'button': (80, 80, 80),
        'button_hover': (100, 100, 100), 'button_active': (120, 120, 120),
        'text': (255, 255, 255), 'input': (30, 30, 30), 'input_active': (50, 50, 50),
        'separator': (100, 100, 100), 'slider': (120, 120, 120),
        'checkbox': (200, 200, 200), 'placeholder': (150, 150, 150),
        'selection': (100, 150, 255)
    }
