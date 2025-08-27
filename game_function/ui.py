import pygame
from settings import *


# --- Input Helpers (in a stateless, module-level) ---
def activate_input(panel, element, mouse_pos):
    # Deactivate all other inputs
    for e in panel.elements:
        if e.type == ElementType.INPUT and e != element:
            e.active = False
    element.active = True
    element.cursor_timer = 0

    # Calculate cursor position from mouse click
    if element.value:
        text_x = element.rect.x + 5
        click_x = mouse_pos[0] - text_x
        for i in range(len(element.value) + 1):
            text_width = panel.font.render(element.value[:i], True, panel.COLORS['text']).get_width()
            if click_x <= text_width:
                element.cursor_pos = i
                break
        else:
            element.cursor_pos = len(element.value)
    else:
        element.cursor_pos = 0
    element.selection_start = element.selection_end = element.cursor_pos

def handle_input_key(panel, element, event):
    # Keys: Ctrl, Shift, Cursors
    ctrl_held = pygame.K_LCTRL in panel.keys_held or pygame.K_RCTRL in panel.keys_held
    shift_held = pygame.K_LSHIFT in panel.keys_held or pygame.K_RSHIFT in panel.keys_held
    cursor_moved = False

    # Other Keys
    if event.key == pygame.K_BACKSPACE:
        if ctrl_held:
            if element.selection_start != element.selection_end:
                start, end = min(element.selection_start, element.selection_end), max(element.selection_start, element.selection_end)
                element.value = element.value[:start] + element.value[end:]
                element.cursor_pos = start
                element.selection_start = element.selection_end = start
                cursor_moved = True
            elif element.cursor_pos > 0:
                pos = element.cursor_pos - 1
                while pos > 0 and element.value[pos] in ' \t\n':
                    pos -= 1
                while pos > 0 and element.value[pos - 1] not in ' \t\n':
                    pos -= 1
                element.value = element.value[:pos] + element.value[element.cursor_pos:]
                element.cursor_pos = pos
                element.selection_start = element.selection_end = pos
                cursor_moved = True
        elif element.selection_start != element.selection_end:
            start, end = min(element.selection_start, element.selection_end), max(element.selection_start, element.selection_end)
            element.value = element.value[:start] + element.value[end:]
            element.cursor_pos = start
            element.selection_start = element.selection_end = start
            cursor_moved = True
        elif element.cursor_pos > 0:
            element.value = element.value[:element.cursor_pos-1] + element.value[element.cursor_pos:]
            element.cursor_pos -= 1
            element.selection_start = element.selection_end = element.cursor_pos
            cursor_moved = True
    elif event.key == pygame.K_DELETE:
        if element.selection_start != element.selection_end:
            start, end = min(element.selection_start, element.selection_end), max(element.selection_start, element.selection_end)
            element.value = element.value[:start] + element.value[end:]
            element.cursor_pos = start
            element.selection_start = element.selection_end = start
            cursor_moved = True
        elif element.cursor_pos < len(element.value):
            element.value = element.value[:element.cursor_pos] + element.value[element.cursor_pos+1:]
            cursor_moved = True
    elif event.key == pygame.K_LEFT:
        if ctrl_held:
            pos = element.cursor_pos - 1
            while pos > 0 and element.value[pos] in ' \t\n':
                pos -= 1
            while pos > 0 and element.value[pos - 1] not in ' \t\n':
                pos -= 1
            element.cursor_pos = pos
        else:
            element.cursor_pos = max(0, element.cursor_pos - 1)
        if not shift_held:
            element.selection_start = element.selection_end = element.cursor_pos
        else:
            element.selection_end = element.cursor_pos
        cursor_moved = True
    elif event.key == pygame.K_RIGHT:
        if ctrl_held:
            pos = element.cursor_pos
            while pos < len(element.value) and element.value[pos] in ' \t\n':
                pos += 1
            while pos < len(element.value) and element.value[pos] not in ' \t\n':
                pos += 1
            element.cursor_pos = pos
        else:
            element.cursor_pos = min(len(element.value), element.cursor_pos + 1)
        if not shift_held:
            element.selection_start = element.selection_end = element.cursor_pos
        else:
            element.selection_end = element.cursor_pos
        cursor_moved = True
    elif event.key == pygame.K_HOME:
        element.cursor_pos = 0
        if not shift_held:
            element.selection_start = element.selection_end = 0
        else:
            element.selection_end = 0
        cursor_moved = True
    elif event.key == pygame.K_END:
        element.cursor_pos = len(element.value)
        if not shift_held:
            element.selection_start = element.selection_end = len(element.value)
        else:
            element.selection_end = len(element.value)
        cursor_moved = True
    elif event.key == pygame.K_RETURN:
        element.active = False
        if element.callback:
            element.callback(element.value)
    elif ctrl_held and event.key == pygame.K_a:
        element.selection_start = 0
        element.selection_end = len(element.value)
        element.cursor_pos = len(element.value)
        cursor_moved = True
    elif event.unicode and event.unicode.isprintable():
        if element.selection_start != element.selection_end:
            start, end = min(element.selection_start, element.selection_end), max(element.selection_start, element.selection_end)
            element.value = element.value[:start] + event.unicode + element.value[end:]
            element.cursor_pos = start + 1
            element.selection_start = element.selection_end = element.cursor_pos
        else:
            element.value = element.value[:element.cursor_pos] + event.unicode + element.value[element.cursor_pos:]
            element.cursor_pos += 1
            element.selection_start = element.selection_end = element.cursor_pos
        cursor_moved = True
    if cursor_moved:
        element.cursor_timer = 0
    return True


# --- Drawing helpers (in a stateless, module-level) ---
def draw_button(surface, font, el, colors, button_pressed=None, button_hovered=None):
    color = colors['button']
    if el == button_pressed:
        color = colors['button_active']
    elif el == button_hovered:
        color = colors['button_hover']
    draw_rect_with_border(surface, el.rect, color, colors['text'])
    text = render_text(font, el.text, colors['text'])
    center_text(surface, text, el.rect)

def draw_label(surface, font, el, colors):
    text = render_text(font, el.text, colors['text'])
    surface.blit(text, (el.rect.x + 5, el.rect.centery - text.get_height()//2))

def draw_input(surface, font, el, colors):
    color = colors['input_active'] if el.active else colors['input']
    draw_rect_with_border(surface, el.rect, color, colors['text'] if el.active else colors['button'])
    text_x = el.rect.x + 8
    text_y = el.rect.centery
    # Draw selection highlight
    if el.active and el.selection_start != el.selection_end:
        start_pos = min(el.selection_start, el.selection_end)
        end_pos = max(el.selection_start, el.selection_end)
        if el.value:
            start_x = text_x + font.render(el.value[:start_pos], True, colors['text']).get_width()
            end_x = text_x + font.render(el.value[:end_pos], True, colors['text']).get_width()
            selection_rect = pygame.Rect(start_x, el.rect.y + 3, end_x - start_x, el.rect.height - 6)
            pygame.draw.rect(surface, colors['selection'], selection_rect)
    # Draw text
    if el.value:
        text = render_text(font, el.value, colors['text'])
        surface.blit(text, (text_x, text_y - text.get_height()//2))
    elif el.placeholder and not el.active:
        placeholder_text = render_text(font, el.placeholder, colors['placeholder'])
        surface.blit(placeholder_text, (text_x, text_y - placeholder_text.get_height()//2))
    # Draw cursor
    if el.active and not el.selecting and el.selection_start == el.selection_end:
        cursor_x = text_x
        if el.value and el.cursor_pos > 0:
            cursor_x += font.render(el.value[:el.cursor_pos], True, colors['text']).get_width()
        if el.cursor_timer < 30 or (el.cursor_timer // 30) % 2 == 0:
            pygame.draw.line(surface, colors['text'], (cursor_x, el.rect.y + 5), (cursor_x, el.rect.bottom - 5), 2)

def draw_slider(surface, font, el, colors):
    label = render_text(font, f"{el.text}: {int(el.value)}", colors['text'])
    surface.blit(label, (el.rect.x + 10, el.rect.y - 25))
    track_rect = pygame.Rect(el.rect.x + 10, el.rect.centery - 2, el.rect.width - 20, 4)
    pygame.draw.rect(surface, colors['input'], track_rect)
    ratio = (el.value - el.min_val) / (el.max_val - el.min_val) if el.max_val != el.min_val else 0
    handle_x = el.rect.x + 10 + int(ratio * (el.rect.width - 20)) - 8
    handle_rect = pygame.Rect(handle_x, el.rect.centery - 8, 16, 16)
    pygame.draw.rect(surface, colors['slider'], handle_rect)
    pygame.draw.rect(surface, colors['text'], handle_rect, 2)

def draw_checkbox(surface, font, el, colors):
    cb_rect = pygame.Rect(el.rect.x, el.rect.centery - 9, 18, 18)
    pygame.draw.rect(surface, colors['input'], cb_rect)
    pygame.draw.rect(surface, colors['text'], cb_rect, 2)
    if el.checked:
        points = [(el.rect.x + 3, cb_rect.centery), (el.rect.x + 7, cb_rect.centery + 4), (el.rect.x + 15, cb_rect.centery - 4)]
        pygame.draw.lines(surface, colors['checkbox'], False, points, 2)
    text = render_text(font, el.text, colors['text'])
    surface.blit(text, (el.rect.x + 26, el.rect.centery - text.get_height()//2))

def draw_dropdown(surface, font, el, colors, dropdown_hovered_option=None):
    pygame.draw.rect(surface, colors['input'], el.rect)
    pygame.draw.rect(surface, colors['text'], el.rect, 2)
    selected_text = el.options[el.selected_option] if el.options and 0 <= el.selected_option < len(el.options) else el.text
    text = render_text(font, selected_text, colors['text'])
    surface.blit(text, (el.rect.x + 8, el.rect.centery - text.get_height()//2))
    arrow_x, arrow_y = el.rect.right - 20, el.rect.centery
    if el.dropdown_open:
        arrow_points = [(arrow_x, arrow_y + 3), (arrow_x - 6, arrow_y - 3), (arrow_x + 6, arrow_y - 3)]
    else:
        arrow_points = [(arrow_x - 6, arrow_y - 3), (arrow_x + 6, arrow_y - 3), (arrow_x, arrow_y + 3)]
    pygame.draw.polygon(surface, colors['text'], arrow_points)
    if el.dropdown_open and el.options:
        dropdown_height = len(el.options) * 28
        dropdown_rect = pygame.Rect(el.rect.x, el.rect.bottom, el.rect.width, dropdown_height)
        pygame.draw.rect(surface, colors['input'], dropdown_rect)
        pygame.draw.rect(surface, colors['text'], dropdown_rect, 2)
        for i, option in enumerate(el.options):
            option_y = el.rect.bottom + i * 28
            option_rect = pygame.Rect(el.rect.x + 2, option_y + 1, el.rect.width - 4, 26)
            highlight = False
            if dropdown_hovered_option is not None:
                hovered_el, hovered_idx = dropdown_hovered_option
                if hovered_el == el and hovered_idx == i:
                    highlight = True
            if highlight:
                pygame.draw.rect(surface, colors['button_hover'], option_rect)
            elif i == el.selected_option:
                pygame.draw.rect(surface, colors['button_active'], option_rect)
            option_text = render_text(font, option, colors['text'])
            text_y = option_y + 14 - option_text.get_height()//2
            surface.blit(option_text, (el.rect.x + 8, text_y))
            if i < len(el.options) - 1:
                line_y = option_y + 28
                pygame.draw.line(surface, colors['separator'], (el.rect.x + 5, line_y), (el.rect.right - 5, line_y))

def draw_separator(surface, el, colors):
    pygame.draw.rect(surface, colors['separator'], el.rect)


# --- Module-level helpers ---
def draw_rect_with_border(surface, rect, color, border_color, border_width=2):
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, border_color, rect, border_width)

def render_text(font, text, color):
    return font.render(text, True, color)

def center_text(surface, text_surf, rect):
    surface.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))

def get_cursor_from_mouse(font, text, rect, mouse_pos, color):
    text_x = rect.x + 5
    click_x = mouse_pos[0] - text_x
    if not text:
        return 0
    for i in range(len(text) + 1):
        text_width = font.render(text[:i], True, color).get_width()
        if click_x <= text_width:
            return i
    return len(text)

def clamp(val, minv, maxv):
    return max(minv, min(maxv, val))

def update_slider_value(element, mouse_pos):
    relative_x = mouse_pos[0] - element.rect.x - 10
    slider_width = element.rect.width - 20
    ratio = clamp(relative_x / slider_width, 0, 1)
    element.value = element.min_val + (element.max_val - element.min_val) * ratio
    if element.callback:
        element.callback(element.value)

def handle_element_click(panel, element, mouse_pos):
    if element.type == ElementType.BUTTON:
        if element.callback:
            element.callback()
    elif element.type == ElementType.INPUT:
        activate_input(panel, element, mouse_pos)
    elif element.type == ElementType.CHECKBOX:
        element.checked = not element.checked
        if element.callback:
            element.callback(element.checked)
    elif element.type == ElementType.DROPDOWN:
        element.dropdown_open = not element.dropdown_open
    elif element.type == ElementType.SLIDER:
        update_slider_value(element, mouse_pos)
        element.dragging = True
    return True


# -- Mouse Cursor --
def set_cursor_pointer():
    try:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    except Exception:
        pass
