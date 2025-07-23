import pygame
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import *
from systems.manager.ui_manager import *


# DEBUGGING PURPOSES
# '''
def main():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Universal Panel System Demo - Pythonic")
    clock = pygame.time.Clock()
    
    # Add the upgrade panel and shop panel to the existing panels
    panels = [
        PanelTemplates.game_settings_panel(), 
        PanelTemplates.quest_panel(),
        PanelTemplates.upgrade_panel(),
        PanelTemplates.shop_panel()
    ]
    current_panel_idx = 0
    target_panel_pos = (400, 100)
    current_panel_pos = [400, 100]
    panel_transition_speed = 0.15
    
    button_font = pygame.font.Font(None, 24)
    switch_button = pygame.Rect(50, 50, 200, 40)
    
    # Updated instructions to reflect the new panels
    instructions = [
        "Click 'Switch Panel' to cycle between Settings, Quest, Upgrade, and Shop panels",
        "Use mouse wheel to scroll in panels",
        "Click elements to interact with them",
        "Check upgrades and click 'Apply Upgrades' or buy items from the shop"
    ]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and switch_button.collidepoint(event.pos):
                current_panel_idx = (current_panel_idx + 1) % len(panels)
                # Animate panel sliding in from the right
                current_panel_pos[0] = 1200  # Start from off-screen right
            
            panels[current_panel_idx].handle_event(event, tuple(current_panel_pos))
        
        screen.fill((20, 20, 20))
        
        # Animate panel position
        current_panel_pos[0] += (target_panel_pos[0] - current_panel_pos[0]) * panel_transition_speed
        current_panel_pos[1] += (target_panel_pos[1] - current_panel_pos[1]) * panel_transition_speed
        
        # Draw Switch button
        pygame.draw.rect(screen, (80, 80, 80), switch_button)
        pygame.draw.rect(screen, (255, 255, 255), switch_button, 2)
        text = button_font.render("Switch Panel", True, (255, 255, 255))
        screen.blit(text, (switch_button.centerx - text.get_width()//2, switch_button.centery - text.get_height()//2))
        
        # Display current panel name
        panel_names = ["Game Settings", "Quest Creator", "Upgrade Panel", "Shop"]
        current_panel_text = button_font.render(f"Current: {panel_names[current_panel_idx]}", True, (200, 200, 200))
        screen.blit(current_panel_text, (50, 100))
        
        panels[current_panel_idx].draw(screen, tuple(current_panel_pos))
        
        # Draw instructions
        for i, instruction in enumerate(instructions):
            text = button_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 650 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

# '''
