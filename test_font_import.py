import pygame
import os

def test_custom_font_loaded():
    pygame.init()
    screen = pygame.display.set_mode((400, 100))
    font_path = "segoeui.ttf"
    font_loaded = False
    font = None
    if os.path.exists(font_path):
        try:
            font = pygame.font.Font(font_path, 32)
            font_loaded = True
        except Exception as e:
            print(f"Font load error: {e}")
    else:
        print("Custom font file not found.")
    
    screen.fill((30, 30, 30))
    if font_loaded:
        text = font.render("Custom font loaded!", True, (0, 255, 0))
    else:
        text = pygame.font.SysFont(None, 32).render("Custom font NOT loaded!", True, (255, 0, 0))
    screen.blit(text, (20, 30))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    return font_loaded

if __name__ == "__main__":
    result = test_custom_font_loaded()
    print("Custom font loaded:" if result else "Custom font NOT loaded!")
