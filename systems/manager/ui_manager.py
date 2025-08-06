
import pygame
import sys
from typing import List, Callable, Optional
from settings import *
from game_function.ui import *
from systems.manager.asset_manager import *
from systems.manager.sound_manager import *


class UniversalPanel:
    def __init__(self, width: int = 400, height: int = 600, title: str = "Panel", sound_manager=None):
        """Initialize a UniversalPanel with given dimensions and title."""
        self.width = width
        self.height = height
        self.title = title
        self.elements: List[PanelElement] = []
        self.surface = pygame.Surface((width, height))
        self.sound_manager = sound_manager
        # Use try/except to load custom fonts, print result for testing, and do not use os
        try:
            self.font = create_font(CUSTOM_FONT_UI, 20) #20
            self.small_font = create_font(CUSTOM_FONT_UI, 16)
            print("[Font Test] Loaded custom font: Exo-Light.ttf")
            try:
                self.title_font = create_font(CUSTOM_FONT_UI_BOLD, 32)
                print("[Font Test] Loaded custom bold font: Exo-Medium.ttf")
            except Exception:
                self.title_font = create_font(CUSTOM_FONT_UI, 32)
                print("[Font Test] Bold font Exo-Medium.ttf not found, using Exo-Light for title font.")
        except Exception:
            self.font = pygame.font.SysFont("Exo", 24)
            self.small_font = pygame.font.SysFont("Exo", 20)
            self.title_font = pygame.font.SysFont("Exo", 32)
            print("[Font Test] Custom font Exo-Light not found, using system font Exo.")
        self.scroll_offset = 0
        self.max_scroll = 0
        self.keys_held = set()
        self.scrollbar_dragging = False
        self.scrollbar_drag_offset = 0
        self.button_hovered = None
        self.button_pressed = None
        self.dropdown_hovered_option = None
        self.COLORS = COLORS

    def add_label(self, text: str, **kwargs) -> PanelElement:
        return self.add_element(ElementType.LABEL, text=text, **kwargs)

    def add_button(self, text: str, callback: Optional[Callable] = None, **kwargs) -> PanelElement:
        return self.add_element(ElementType.BUTTON, text=text, callback=callback, **kwargs)

    def add_input(self, placeholder: str = "", value: str = "", **kwargs) -> PanelElement:
        return self.add_element(ElementType.INPUT, placeholder=placeholder, value=value, **kwargs)

    def add_slider(self, text: str, value: float = 50, min_val: float = 0, max_val: float = 100, **kwargs) -> PanelElement:
        return self.add_element(ElementType.SLIDER, text=text, value=value, min_val=min_val, max_val=max_val, **kwargs)

    def add_checkbox(self, text: str, checked: bool = False, **kwargs) -> PanelElement:
        return self.add_element(ElementType.CHECKBOX, text=text, checked=checked, **kwargs)

    def add_dropdown(self, text: str, options: list, selected: int = 0, **kwargs) -> PanelElement:
        return self.add_element(ElementType.DROPDOWN, text=text, options=options, selected_option=selected, **kwargs)

    def add_separator(self, **kwargs) -> PanelElement:
        return self.add_element(ElementType.SEPARATOR, **kwargs)
    
    def update_cursor(self, panel_position=(0, 0)):
        # Set cursor based on what is hovered: I-beam for input, hand for button/checkbox/slider/dropdown/scrollbar, arrow otherwise
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x = mouse_x - panel_position[0]
        rel_y = mouse_y - panel_position[1]
        hovered_type = None
        hovered_input = None
        hovered_scrollbar = False
        # Check if mouse is over the panel area
        if 0 <= rel_x < self.width and 0 <= rel_y < self.height:
            # Check scrollbar (if visible)
            if self.max_scroll > 0:
                scrollbar_rect = pygame.Rect(self.width - 10, 50, 8, self.height - 50)
                if scrollbar_rect.collidepoint((rel_x, rel_y)):
                    hovered_scrollbar = True
            for el in self.elements:
                if el.type == ElementType.INPUT and el.rect.collidepoint((rel_x, rel_y)) and el.enabled:
                    hovered_type = 'input'
                    hovered_input = el
                    break
                elif el.type in (ElementType.BUTTON, ElementType.CHECKBOX, ElementType.SLIDER, ElementType.DROPDOWN) and el.rect.collidepoint((rel_x, rel_y)) and el.enabled:
                    hovered_type = 'hand'
                    break
        try:
            if hovered_type == 'input':
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            elif hovered_type == 'hand' or hovered_scrollbar:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass  # Fallback for platforms without system cursors
        
    def add_element(self, element_type: ElementType, **kwargs) -> PanelElement:
        """Add a new element to the panel and return it."""
        element = PanelElement(element_type, **kwargs)
        if element_type == ElementType.INPUT:
            element.cursor_pos = len(element.value)
        self.elements.append(element)
        return element
    
    def update_layout(self):
        # First, calculate the total content height
        y_offset = 70
        padding = 10
        for element in self.elements:
            if element.type == ElementType.SEPARATOR:
                y_offset += 30
            elif element.type == ElementType.SLIDER:
                y_offset += 65
            elif element.type == ElementType.CHECKBOX:
                y_offset += 40
            elif element.type == ElementType.BUTTON:
                y_offset += 50
            else:  # LABEL, INPUT, DROPDOWN
                y_offset += 45

        content_height = y_offset
        self.max_scroll = max(0, content_height - self.height)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        # Now, position elements using the clamped scroll_offset
        y_offset = 70 - self.scroll_offset
        for element in self.elements:
            if element.type == ElementType.SEPARATOR:
                element.rect = pygame.Rect(20, y_offset + 10, self.width - 40, 2)
                y_offset += 30
            elif element.type == ElementType.SLIDER:
                element.rect = pygame.Rect(20, y_offset + 20, self.width - 40, 30)
                y_offset += 65
            elif element.type == ElementType.CHECKBOX:
                element.rect = pygame.Rect(20, y_offset, self.width - 40, 35)
                y_offset += 40
            elif element.type == ElementType.BUTTON:
                element.rect = pygame.Rect(20, y_offset, self.width - 40, 40)
                y_offset += 50
            else:  # LABEL, INPUT, DROPDOWN
                element.rect = pygame.Rect(20, y_offset, self.width - 40, 35)
                y_offset += 45
    
    def handle_event(self, event, panel_position=(0, 0)):
        if event.type == pygame.KEYDOWN:
            self.keys_held.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_held.discard(event.key)

        # Track mouse position for hover/click
        mouse_pos = None
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_pos = (event.pos[0] - panel_position[0], event.pos[1] - panel_position[1])

        # Reset hover/pressed state
        if event.type == pygame.MOUSEMOTION:
            self.button_hovered = None
            self.dropdown_hovered_option = None
            for element in self.elements:
                if element.type == ElementType.BUTTON and element.rect.collidepoint(mouse_pos) and element.enabled:
                    self.button_hovered = element
                if element.type == ElementType.DROPDOWN and element.dropdown_open and element.options:
                    for i in range(len(element.options)):
                        option_rect = pygame.Rect(element.rect.x, element.rect.bottom + i * 28, element.rect.width, 28)
                        if option_rect.collidepoint(mouse_pos):
                            self.dropdown_hovered_option = (element, i)
                            break

        if event.type == pygame.MOUSEBUTTONDOWN:
            # If click is outside the panel (not just outside input), deactivate all inputs and return
            if not pygame.Rect(0, 0, self.width, self.height).collidepoint(mouse_pos):
                for el in self.elements:
                    if el.type == ElementType.INPUT:
                        el.active = False
                return False

            # Scrollbar click/drag logic
            if self.max_scroll > 0:
                scrollbar_rect = pygame.Rect(self.width - 10, 50, 8, self.height - 50)
                handle_height = max(30, int((self.height - 50) * (self.height - 50) / (self.max_scroll + self.height - 50)))
                handle_y = 50 + int((self.scroll_offset / self.max_scroll) * ((self.height - 50) - handle_height)) if self.max_scroll > 0 else 50
                handle_rect = pygame.Rect(self.width - 10, handle_y, 8, handle_height)
                if handle_rect.collidepoint(mouse_pos):
                    self.scrollbar_dragging = True
                    self.scrollbar_drag_offset = mouse_pos[1] - handle_y
                    return True
                elif scrollbar_rect.collidepoint(mouse_pos):
                    # Clicked on scrollbar track (not handle): jump handle to mouse and scroll
                    new_handle_y = mouse_pos[1] - handle_height // 2
                    track_top = 50
                    track_bottom = 50 + (self.height - 50) - handle_height
                    new_handle_y = max(track_top, min(track_bottom, new_handle_y))
                    ratio = (new_handle_y - track_top) / (track_bottom - track_top) if (track_bottom - track_top) > 0 else 0
                    self.scroll_offset = int(self.max_scroll * ratio)
                    return True

            # Scrolling with mouse wheel
            if event.button in [4, 5]:
                scroll_amount = 30
                new_offset = self.scroll_offset + (-scroll_amount if event.button == 4 else scroll_amount)
                if (event.button == 4 and self.scroll_offset > 0) or (event.button == 5 and self.scroll_offset < self.max_scroll):
                    self.scroll_offset = max(0, min(self.max_scroll, new_offset))
                return True

            # Track pressed button
            self.button_pressed = None
            for element in self.elements:
                if element.type == ElementType.BUTTON and element.rect.collidepoint(mouse_pos) and element.enabled:
                    self.sound_manager.play_ui_sound('button_click')
                    self.button_pressed = element
                    break

            # Close all dropdowns first
            clicked_dropdown = False
            for element in self.elements:
                if element.type == ElementType.DROPDOWN and element.dropdown_open:
                    if element.rect.collidepoint(mouse_pos):
                        clicked_dropdown = True
                    else:
                        for i in range(len(element.options)):
                            option_rect = pygame.Rect(element.rect.x, element.rect.bottom + i * 28, element.rect.width, 28)
                            if option_rect.collidepoint(mouse_pos):
                                element.selected_option = i
                                element.dropdown_open = False
                                if element.callback:
                                    element.callback(element.options[i], i)
                                return True
                    if not clicked_dropdown:
                        element.dropdown_open = False

            # Element interactions
            clicked_input = False
            for element in self.elements:
                if element.rect.collidepoint(mouse_pos) and element.enabled:
                    self.sound_manager.play_ui_sound('button_hover')
                    if element.type == ElementType.INPUT:
                        activate_input(self, element, mouse_pos)
                        element.selecting = True
                        element.cursor_pos = get_cursor_from_mouse(self.font, element.value, element.rect, mouse_pos, self.COLORS['text'])
                        element.selection_start = element.selection_end = element.cursor_pos
                        clicked_input = True
                        return True
                    else:
                        return handle_element_click(self, element, mouse_pos)
            # If clicked on panel but not on any input, deactivate all inputs
            if not clicked_input:
                for el in self.elements:
                    if el.type == ElementType.INPUT:
                        el.active = False

        elif event.type == pygame.MOUSEBUTTONUP:
            # Clear pressed state
            self.button_pressed = None
            for el in self.elements:
                if el.type == ElementType.SLIDER:
                    el.dragging = False
                if el.type == ElementType.INPUT:
                    el.selecting = False
            # Stop dragging scrollbar
            self.scrollbar_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            mouse_buttons = pygame.mouse.get_pressed()
            # Handle scrollbar dragging
            if self.scrollbar_dragging and self.max_scroll > 0 and mouse_pos is not None:
                scrollbar_track_height = self.height - 50
                handle_height = max(30, int(scrollbar_track_height * scrollbar_track_height / (self.max_scroll + scrollbar_track_height)))
                track_top = 50
                track_bottom = 50 + scrollbar_track_height - handle_height
                # Calculate new handle y position
                new_handle_y = mouse_pos[1] - self.scrollbar_drag_offset
                new_handle_y = max(track_top, min(track_bottom, new_handle_y))
                # Map handle position to scroll offset
                ratio = (new_handle_y - track_top) / (track_bottom - track_top) if (track_bottom - track_top) > 0 else 0
                self.scroll_offset = int(self.max_scroll * ratio)
                return True

            for el in self.elements:
                if el.type == ElementType.SLIDER and el.dragging:
                    update_slider_value(el, mouse_pos)
                    return True
                if el.type == ElementType.INPUT and el.active:
                    # If mouse is down and inside the input, start selecting
                    if mouse_buttons[0]:
                        el.selecting = True
                        el.selection_end = get_cursor_from_mouse(self.font, el.value, el.rect, mouse_pos, self.COLORS['text'])
                        el.cursor_pos = el.selection_end
                        return True
                    else:
                        el.selecting = False

        elif event.type == pygame.KEYDOWN:
            for el in self.elements:
                if el.type == ElementType.INPUT and el.active:
                    return handle_input_key(self, el, event)

        return False

    def update(self):
        # Update cursor blink timer for active inputs
        for element in self.elements:
            if element.type == ElementType.INPUT and element.active:
                element.cursor_timer += 1
    
    def draw(self, screen, position=(100, 100)):
        self.update_layout()
        self.update()
        self.update_cursor(position)
        self.surface.fill(self.COLORS['panel'])

        # Title bar
        pygame.draw.rect(self.surface, self.COLORS['bg'], (0, 0, self.width, 50))
        title_text = self.title_font.render(self.title, True, self.COLORS['text'])
        self.surface.blit(title_text, ((self.width - title_text.get_width()) // 2, 3))

        # Content area with clipping
        content_rect = pygame.Rect(0, 50, self.width, self.height - 50)
        self.surface.set_clip(content_rect)

        # Draw elements (defer open dropdowns)
        open_dropdown = None
        for element in self.elements:
            if element.type == ElementType.DROPDOWN and element.dropdown_open:
                open_dropdown = element
            else:
                self._draw_element(element)

        # Draw open dropdown on top
        if open_dropdown:
            self.surface.set_clip(None)
            self._draw_element(open_dropdown)

        self.surface.set_clip(None)

        # Draw scrollbar if scrollable and mouse is hovering over panel
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x = mouse_x - position[0]
        rel_y = mouse_y - position[1]
        mouse_over_panel = 0 <= rel_x < self.width and 0 <= rel_y < self.height
        if self.max_scroll > 0 and mouse_over_panel:
            scrollbar_rect = pygame.Rect(self.width - 10, 50, 8, self.height - 50)
            # Calculate scrollbar handle height and position
            handle_height = max(30, int((self.height - 50) * (self.height - 50) / (self.max_scroll + self.height - 50)))
            handle_y = 50 + int((self.scroll_offset / self.max_scroll) * ((self.height - 50) - handle_height)) if self.max_scroll > 0 else 50
            handle_rect = pygame.Rect(self.width - 10, handle_y, 8, handle_height)
            # Draw scrollbar track
            pygame.draw.rect(self.surface, (80, 80, 80), scrollbar_rect)
            # Draw scrollbar handle
            pygame.draw.rect(self.surface, (160, 160, 160), handle_rect)
            pygame.draw.rect(self.surface, self.COLORS['text'], handle_rect, 1)

        pygame.draw.rect(self.surface, self.COLORS['text'], (0, 0, self.width, self.height), 2)
        screen.blit(self.surface, position)
    
    def _draw_element(self, element):
        # Skip elements outside visible area
        if element.rect.bottom < 50 or element.rect.top > self.height:
            return
        
        if element.type == ElementType.BUTTON:
            draw_button(self.surface, self.font, element, self.COLORS, getattr(self, 'button_pressed', None), getattr(self, 'button_hovered', None))
        elif element.type == ElementType.LABEL:
            draw_label(self.surface, self.font, element, self.COLORS)
        elif element.type == ElementType.INPUT:
            draw_input(self.surface, self.font, element, self.COLORS)
        elif element.type == ElementType.SLIDER:
            draw_slider(self.surface, self.font, element, self.COLORS)
        elif element.type == ElementType.CHECKBOX:
            draw_checkbox(self.surface, self.font, element, self.COLORS)
        elif element.type == ElementType.DROPDOWN:
            draw_dropdown(self.surface, self.font, element, self.COLORS, getattr(self, 'dropdown_hovered_option', None))
        elif element.type == ElementType.SEPARATOR:
            draw_separator(self.surface, element, self.COLORS)
    
    def _draw_button(self, el):
        # Determine button state
        color = self.COLORS['button']
        # Defensive: ensure attributes exist
        button_pressed = getattr(self, 'button_pressed', None)
        button_hovered = getattr(self, 'button_hovered', None)
        if el == button_pressed:
            color = self.COLORS['button_active']
        elif el == button_hovered:
            color = self.COLORS['button_hover']
        pygame.draw.rect(self.surface, color, el.rect)
        pygame.draw.rect(self.surface, self.COLORS['text'], el.rect, 2)
        text = self.font.render(el.text, True, self.COLORS['text'])
        text_pos = (el.rect.centerx - text.get_width()//2, el.rect.centery - text.get_height()//2)
        self.surface.blit(text, text_pos)
    
    def _draw_label(self, el):
        text = self.font.render(el.text, False, self.COLORS['text'])
        self.surface.blit(text, (el.rect.x + 5, el.rect.centery - text.get_height()//2))
    
    def _draw_input(self, el):
        color = self.COLORS['input_active'] if el.active else self.COLORS['input']
        pygame.draw.rect(self.surface, color, el.rect)
        pygame.draw.rect(self.surface, self.COLORS['text'] if el.active else self.COLORS['button'], el.rect, 2)

        text_x = el.rect.x + 8
        text_y = el.rect.centery

        # Draw selection highlight
        if el.active and el.selection_start != el.selection_end:
            start_pos = min(el.selection_start, el.selection_end)
            end_pos = max(el.selection_start, el.selection_end)

            if el.value:
                start_x = text_x + self.font.render(el.value[:start_pos], True, self.COLORS['text']).get_width()
                end_x = text_x + self.font.render(el.value[:end_pos], True, self.COLORS['text']).get_width()
                selection_rect = pygame.Rect(start_x, el.rect.y + 3, end_x - start_x, el.rect.height - 6)
                pygame.draw.rect(self.surface, self.COLORS['selection'], selection_rect)

        # Draw text
        if el.value:
            text = self.font.render(el.value, True, self.COLORS['text'])
            self.surface.blit(text, (text_x, text_y - text.get_height()//2))
        elif el.placeholder and not el.active:
            placeholder_text = self.font.render(el.placeholder, True, self.COLORS['placeholder'])
            self.surface.blit(placeholder_text, (text_x, text_y - placeholder_text.get_height()//2))

        # Draw cursor (blinks when idle, always visible for 0.5s after typing/moving)
        if el.active and not el.selecting and el.selection_start == el.selection_end:
            cursor_x = text_x
            if el.value and el.cursor_pos > 0:
                cursor_x += self.font.render(el.value[:el.cursor_pos], True, self.COLORS['text']).get_width()
            # Always show for 0.5s (30 frames) after typing/moving, then blink
            if el.cursor_timer < 30 or (el.cursor_timer // 30) % 2 == 0:
                pygame.draw.line(self.surface, self.COLORS['text'],
                               (cursor_x, el.rect.y + 5), (cursor_x, el.rect.bottom - 5), 2)
    
    def _draw_slider(self, el):
        # Label
        label = self.font.render(f"{el.text}: {int(el.value)}", False, self.COLORS['text'])
        self.surface.blit(label, (el.rect.x + 10, el.rect.y - 25))
        
        # Track
        track_rect = pygame.Rect(el.rect.x + 10, el.rect.centery - 2, el.rect.width - 20, 4)
        pygame.draw.rect(self.surface, self.COLORS['input'], track_rect)
        
        # Handle
        ratio = (el.value - el.min_val) / (el.max_val - el.min_val) if el.max_val != el.min_val else 0
        handle_x = el.rect.x + 10 + int(ratio * (el.rect.width - 20)) - 8
        handle_rect = pygame.Rect(handle_x, el.rect.centery - 8, 16, 16)
        pygame.draw.rect(self.surface, self.COLORS['slider'], handle_rect)
        pygame.draw.rect(self.surface, self.COLORS['text'], handle_rect, 2)
    
    def _draw_checkbox(self, el):
        cb_rect = pygame.Rect(el.rect.x, el.rect.centery - 9, 18, 18)
        pygame.draw.rect(self.surface, self.COLORS['input'], cb_rect)
        pygame.draw.rect(self.surface, self.COLORS['text'], cb_rect, 2)
        
        if el.checked:
            # Checkmark
            points = [(el.rect.x + 3, cb_rect.centery), 
                     (el.rect.x + 7, cb_rect.centery + 4), 
                     (el.rect.x + 15, cb_rect.centery - 4)]
            pygame.draw.lines(self.surface, self.COLORS['checkbox'], False, points, 2)
        
        # Label
        text = self.font.render(el.text, False, self.COLORS['text'])
        self.surface.blit(text, (el.rect.x + 26, el.rect.centery - text.get_height()//2))
    
    def _draw_dropdown(self, el):
        pygame.draw.rect(self.surface, self.COLORS['input'], el.rect)
        pygame.draw.rect(self.surface, self.COLORS['text'], el.rect, 2)

        # Selected text
        selected_text = el.options[el.selected_option] if el.options and 0 <= el.selected_option < len(el.options) else el.text
        text = self.font.render(selected_text, False, self.COLORS['text'])
        self.surface.blit(text, (el.rect.x + 8, el.rect.centery - text.get_height()//2))

        # Arrow
        arrow_x, arrow_y = el.rect.right - 20, el.rect.centery
        if el.dropdown_open:
            arrow_points = [(arrow_x, arrow_y + 3), (arrow_x - 6, arrow_y - 3), (arrow_x + 6, arrow_y - 3)]
        else:
            arrow_points = [(arrow_x - 6, arrow_y - 3), (arrow_x + 6, arrow_y - 3), (arrow_x, arrow_y + 3)]
        pygame.draw.polygon(self.surface, self.COLORS['text'], arrow_points)

        # Dropdown menu
        if el.dropdown_open and el.options:
            dropdown_height = len(el.options) * 28
            dropdown_rect = pygame.Rect(el.rect.x, el.rect.bottom, el.rect.width, dropdown_height)
            pygame.draw.rect(self.surface, self.COLORS['input'], dropdown_rect)
            pygame.draw.rect(self.surface, self.COLORS['text'], dropdown_rect, 2)

            for i, option in enumerate(el.options):
                option_y = el.rect.bottom + i * 28
                option_rect = pygame.Rect(el.rect.x + 2, option_y + 1, el.rect.width - 4, 26)

                # Highlight hovered or selected option
                highlight = False
                if self.dropdown_hovered_option is not None:
                    hovered_el, hovered_idx = self.dropdown_hovered_option
                    if hovered_el == el and hovered_idx == i:
                        highlight = True
                if highlight:
                    pygame.draw.rect(self.surface, self.COLORS['button_hover'], option_rect)
                elif i == el.selected_option:
                    pygame.draw.rect(self.surface, self.COLORS['button_active'], option_rect)

                # Option text
                option_text = self.font.render(option, False, self.COLORS['text'])
                text_y = option_y + 14 - option_text.get_height()//2
                self.surface.blit(option_text, (el.rect.x + 8, text_y))

                # Separator line
                if i < len(el.options) - 1:
                    line_y = option_y + 28
                    pygame.draw.line(self.surface, self.COLORS['separator'],
                                   (el.rect.x + 5, line_y), (el.rect.right - 5, line_y))
    
    def _draw_separator(self, el):
        pygame.draw.rect(self.surface, self.COLORS['separator'], el.rect)


# PanelTemplates: Efficient, extensible, and ready for deployment
class PanelTemplates:
    def __init__(self, sound_manager=None):
        self.sound_manager = sound_manager
    
    def game_settings_panel(self):
        panel = UniversalPanel(400, 500, "Game Settings", sound_manager=self.sound_manager)
        panel.add_label("Audio Settings")
        for name, val in [("Master Volume", 75), ("Music Volume", 50), ("SFX Volume", 80)]:
            panel.add_slider(name, val)
        panel.add_separator()
        panel.add_label("Graphics Settings")
        panel.add_dropdown("Resolution", ["1920x1080", "1280x720", "800x600"])
        panel.add_checkbox("Fullscreen", False)
        panel.add_checkbox("VSync", True)
        panel.add_separator()
        panel.add_label("Gameplay Settings")
        panel.add_checkbox("Auto-save", True)
        panel.add_slider("Difficulty", 2, 1, 5)
        panel.add_separator()
        panel.add_button("Apply Settings", lambda: print("Settings applied!"))
        panel.add_button("Reset to Default", lambda: print("Settings reset!"))
        return panel

    def quest_panel(self):
        panel = UniversalPanel(500, 600, "Quest Creator", sound_manager=self.sound_manager)
        panel.add_label("Basic Information")
        panel.add_input(placeholder="Quest Name", id="quest_name")
        panel.add_input(placeholder="Quest Description", id="quest_desc")
        panel.add_dropdown("Quest Type", ["Main", "Side", "Daily", "Hidden"], id="quest_type")
        panel.add_separator()
        panel.add_label("Objectives")
        for i in range(1, 4):
            panel.add_input(placeholder=f"Objective {i}", id=f"obj_{i}")
        panel.add_separator()
        panel.add_label("Rewards")
        panel.add_slider("Experience Points", 263, 0, 1000, id="exp_reward")
        panel.add_slider("Gold Reward", 50, 0, 500, id="gold_reward")
        panel.add_input(placeholder="Item Reward", id="item_reward")
        panel.add_separator()
        panel.add_button("Create Quest", lambda: print("Quest created!"))
        panel.add_button("Save Template", lambda: print("Template saved!"))
        return panel

    def notification_panel(self, message: str = "", title: str = "Notification"):
        panel = UniversalPanel(350, 180, title, self.sound_manager)
        panel.add_label(message)
        panel.add_separator()
        panel.add_button("OK", lambda: print("Notification closed!"))
        return panel

    def class_selection_panel(self, classes=None):
        if classes is None:
            classes = ["Warrior", "Mage", "Rogue", "Cleric"]
        panel = UniversalPanel(400, 350, "Class Selection", sound_manager=self.sound_manager)
        panel.add_label("Choose Your Class:")
        for c in classes:
            panel.add_button(c, lambda c=c: print(f"Selected: {c}"))
        return panel

    def upgrade_panel(self, upgrades=None):
        if upgrades is None:
            upgrades = ["Health +10", "Mana +5", "Attack +2", "Defense +3"]
        panel = UniversalPanel(400, 350, "Upgrade", sound_manager=self.sound_manager)
        panel.add_label("Available Upgrades:")
        for up in upgrades:
            panel.add_checkbox(up, False)
        panel.add_separator()
        panel.add_button("Apply Upgrades", lambda: print("Upgrades applied!"))
        return panel

    def shop_panel(self, items=None):
        if items is None:
            items = [
                ("Potion", 10), ("Elixir", 25), ("Sword", 100), ("Shield", 80)
            ]
        panel = UniversalPanel(400, 400, "Shop", sound_manager=self.sound_manager)
        panel.add_label("Shop Items:")
        for name, price in items:
            panel.add_button(f"Buy {name} - {price}G", lambda n=name, p=price: print(f"Bought {n} for {p}G"))
        panel.add_separator()
        panel.add_button("Exit Shop", lambda: print("Shop closed!"))
        return panel
    
    def pause_menu_panel(self):
        """Create a pause menu panel with standard game pause options."""
        panel = UniversalPanel(350, 450, "Game Paused", sound_manager=self.sound_manager)
        
        # Game status info
        panel.add_label("Game is paused")
        panel.add_separator()
        
        # Main menu buttons
        panel.add_button("Resume Game", lambda: print("[Pause Menu] Resuming game..."))
        panel.add_button("Save Game", lambda: print("[Pause Menu] Saving game..."))
        panel.add_button("Load Game", lambda: print("[Pause Menu] Loading game..."))
        panel.add_separator()
        
        # Settings and options
        panel.add_button("Settings", lambda: print("[Pause Menu] Opening settings..."))
        panel.add_button("Controls", lambda: print("[Pause Menu] Opening controls..."))
        panel.add_separator()
        
        # Quick settings
        panel.add_label("Quick Settings")
        panel.add_checkbox("Mute Audio", False, id="mute_audio")
        panel.add_slider("Master Volume", 75, 0, 100, id="master_vol")
        panel.add_separator()
        
        # Exit options
        panel.add_button("Main Menu", lambda: print("[Pause Menu] Returning to main menu..."))
        panel.add_button("Quit Game", lambda: print("[Pause Menu] Quitting game..."))
        
        return panel

    def level_editor_panel(self):
        pass

    def world_map_editor_panel(self):
        pass

    def mini_map_panel(self):
        pass
