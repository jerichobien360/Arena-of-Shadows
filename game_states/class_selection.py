from settings import *
from entities.character_classes import CHARACTER_CLASSES
from game_states.gameplay import *
import pygame

class ClassSelectionState:
    """State for selecting character class at game start"""
    def __init__(self, font, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        self.selected_class = 'warrior'
        self.class_list = list(CHARACTER_CLASSES.keys())
        self.selected_index = 0
        
        # UI properties
        self.title_font = pygame.font.Font(None, 48)
        self.desc_font = pygame.font.Font(None, 24)
        
        # Animation
        self.selection_timer = 0
        self.preview_rotation = 0
    
    def enter(self):
        """Initialize class selection"""
        self.sound_manager.play_sound('menu_select')
    
    def update(self, dt):
        """Update class selection state"""
        self.selection_timer += dt
        self.preview_rotation += dt * 50  # Rotate preview
        
        keys = pygame.key.get_pressed()
        
        # Navigate classes
        if self._is_key_just_pressed(pygame.K_LEFT) or self._is_key_just_pressed(pygame.K_a):
            self.selected_index = (self.selected_index - 1) % len(self.class_list)
            self.selected_class = self.class_list[self.selected_index]
            self.sound_manager.play_sound('menu_move')
        
        elif self._is_key_just_pressed(pygame.K_RIGHT) or self._is_key_just_pressed(pygame.K_d):
            self.selected_index = (self.selected_index + 1) % len(self.class_list)
            self.selected_class = self.class_list[self.selected_index]
            self.sound_manager.play_sound('menu_move')
        
        # Confirm selection
        if self._is_key_just_pressed(pygame.K_RETURN) or self._is_key_just_pressed(pygame.K_SPACE):
            self.sound_manager.play_sound('menu_confirm')
            return "gameplay"
        
        # Go back to menu
        if self._is_key_just_pressed(pygame.K_ESCAPE):
            return "menu"
        
        return None
    
    def render(self, screen):
        """Render class selection screen"""
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Title
        title = self.title_font.render("Choose Your Class", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Class selection area
        self._render_class_selection(screen)
        
        # Instructions
        instructions = [
            "Use A/D or Arrow Keys to navigate",
            "Press ENTER or SPACE to select",
            "Press ESC to go back"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 25))
            screen.blit(text, text_rect)
    
    def _render_class_selection(self, screen):
        """Render the class selection interface"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Render all classes
        for i, class_name in enumerate(self.class_list):
            char_class = CHARACTER_CLASSES[class_name]
            offset_x = (i - self.selected_index) * 300
            
            # Calculate position and scale based on selection
            class_x = center_x + offset_x
            class_y = center_y - 50
            
            is_selected = (i == self.selected_index)
            scale = 1.5 if is_selected else 1.0
            alpha = 255 if is_selected else 128
            
            # Only render if on screen
            if -100 < class_x < SCREEN_WIDTH + 100:
                self._render_class_preview(screen, char_class, class_x, class_y, scale, alpha, is_selected)
    
    def _render_class_preview(self, screen, char_class, x, y, scale, alpha, is_selected):
        """Render preview of a character class"""
        # Create surface for alpha blending
        preview_surface = pygame.Surface((200, 300), pygame.SRCALPHA)
        
        # Class visual representation
        radius = int(30 * scale)
        pygame.draw.circle(preview_surface, char_class.color, (100, 100), radius)
        
        # Add selection glow
        if is_selected:
            glow_intensity = int(50 + 50 * abs(math.sin(self.selection_timer * 3)))
            glow_color = (*char_class.secondary_color, glow_intensity)
            pygame.draw.circle(preview_surface, glow_color, (100, 100), radius + 10, 3)
        
        # Class name
        name_text = self.font.render(char_class.name, True, WHITE)
        name_rect = name_text.get_rect(center=(100, 150))
        preview_surface.blit(name_text, name_rect)
        
        # Class stats preview
        if is_selected:
            self._render_class_stats(preview_surface, char_class, 100, 180)
        
        # Apply alpha and blit to main screen
        preview_surface.set_alpha(alpha)
        screen.blit(preview_surface, (x - 100, y - 100))
    
    def _render_class_stats(self, surface, char_class, center_x, start_y):
        """Render class statistics"""
        stats = [
            f"HP: {int(100 * char_class.hp_modifier)}",
            f"ATK: {int(25 * char_class.attack_modifier)}",
            f"SPD: {int(200 * char_class.speed_modifier)}",
            f"DEF: {int(10 * char_class.defense_modifier)}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.desc_font.render(stat, True, GRAY)
            stat_rect = stat_text.get_rect(center=(center_x, start_y + i * 20))
            surface.blit(stat_text, stat_rect)
    
    def _is_key_just_pressed(self, key):
        """Simple key press detection (you might want to use InputHandler)"""
        # This is a simplified version - in a real game you'd use proper input handling
        return pygame.key.get_pressed()[key]
    
    def get_selected_class(self):
        """Get the currently selected class"""
        return self.selected_class

# Enhanced GameplayState integration
class EnhancedGameplayState(GameplayState):
    """Enhanced gameplay state with better class integration"""
    
    def __init__(self, font, sound_manager, selected_class='warrior'):
        super().__init__(font, sound_manager)
        self.selected_class = selected_class
        self.class_ui_timer = 0
        
        # Class-specific UI elements
        self.show_class_abilities = False
        self.ability_cooldown_display = {}
    
    def _initialize_entities(self):
        """Initialize game entities with selected class"""
        # Set world bounds for player
        world_bounds = (0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        
        self.player = Player(
            self.sound_manager, 
            self.camera, 
            character_class=self.selected_class,
            start_x=WORLD_WIDTH // 2,
            start_y=WORLD_HEIGHT // 2
        )
        
        # Set world boundaries
        self.player.set_world_bounds(world_bounds)
        
        self.enemies = []
        self.wave_manager.start_wave(1)
    
    def _handle_input(self):
        """Enhanced input handling with class abilities"""
        keys = pygame.key.get_pressed()
        
        # Base input handling
        next_state = super()._handle_input()
        if next_state:
            return next_state
        
        # Class-specific ability inputs
        self._handle_class_abilities(keys)
        
        # Toggle class ability display
        if self.input_handler.is_key_just_pressed(pygame.K_TAB):
            self.show_class_abilities = not self.show_class_abilities
        
        return None
    
    def _handle_class_abilities(self, keys):
        """Handle class-specific ability inputs"""
        class_name = self.player.character_class.name.lower()
        
        if class_name == 'warrior':
            self._handle_warrior_abilities(keys)
        elif class_name == 'mage':
            self._handle_mage_abilities(keys)
        elif class_name == 'fireshooter':
            self._handle_fireshooter_abilities(keys)
    
    def _handle_warrior_abilities(self, keys):
        """Handle Warrior-specific abilities"""
        warrior = self.player.character_class
        
        # Charge ability (Q key)
        if keys[pygame.K_q] and warrior.charge_cooldown <= 0:
            self._activate_warrior_charge()
        
        # Shield bash (E key)
        if keys[pygame.K_e] and warrior.shield_bash_cooldown <= 0:
            self._activate_shield_bash()
    
    def _handle_mage_abilities(self, keys):
        """Handle Mage-specific abilities"""
        mage = self.player.character_class
        
        # Fireball spell (Q key)
        if keys[pygame.K_q] and mage.spell_cooldown <= 0 and mage.mana >= 30:
            self._cast_fireball()
        
        # Mana shield (E key)
        if keys[pygame.K_e] and mage.mana >= 20:
            self._activate_mana_shield()
    
    def _handle_fireshooter_abilities(self, keys):
        """Handle Fireshooter-specific abilities"""
        fireshooter = self.player.character_class
        
        # Rapid fire mode (Q key)
        if keys[pygame.K_q] and not fireshooter.rapid_fire_mode:
            self._activate_rapid_fire()
        
        # Explosive shot (E key)
        if keys[pygame.K_e] and fireshooter.explosion_cooldown <= 0:
            self._fire_explosive_shot()
    
    def _activate_warrior_charge(self):
        """Activate warrior charge ability"""
        # Implementation for charge ability
        warrior = self.player.character_class
        warrior.charge_cooldown = 5.0  # 5 second cooldown
        self.sound_manager.play_sound('warrior_charge')
        
        # Add charge effect (speed boost, damage immunity, etc.)
        # This would need more implementation
    
    def _activate_shield_bash(self):
        """Activate shield bash ability"""
        warrior = self.player.character_class
        warrior.shield_bash_cooldown = 3.0
        self.sound_manager.play_sound('shield_bash')
        
        # Stun nearby enemies
        for enemy in self.enemies:
            distance = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if distance <= 100:  # Shield bash range
                enemy.stunned = True
                enemy.stun_timer = 2.0
    
    def _cast_fireball(self):
        """Cast mage fireball spell"""
        mage = self.player.character_class
        mage.spell_cooldown = 2.0
        mage.mana -= 30
        self.sound_manager.play_sound('fireball')
        
        # Create area of effect damage
        # Implementation would create explosion at target location
    
    def _activate_mana_shield(self):
        """Activate mage mana shield"""
        mage = self.player.character_class
        mage.mana -= 20
        # Add temporary damage reduction
        # This would need more implementation
    
    def _activate_rapid_fire(self):
        """Activate fireshooter rapid fire mode"""
        fireshooter = self.player.character_class
        fireshooter.rapid_fire_mode = True
        fireshooter.rapid_fire_timer = 5.0
        self.sound_manager.play_sound('rapid_fire_activate')
    
    def _fire_explosive_shot(self):
        """Fire explosive shot"""
        fireshooter = self.player.character_class
        fireshooter.explosion_cooldown = 4.0
        self.sound_manager.play_sound('explosion')
        
        # Create explosive projectile
        # Implementation would create area damage on impact
    
    def _render_ui(self):
        """Enhanced UI rendering with class-specific elements"""
        super()._render_ui()
        
        # Render class-specific UI
        if self.show_class_abilities:
            self._render_class_abilities_ui()
    
    def _render_class_abilities_ui(self):
        """Render class abilities UI"""
        # This would show ability cooldowns, mana for mage, etc.
        pass
    
    def _get_ui_elements(self):
        """Enhanced UI elements including class info"""
        base_elements = super()._get_ui_elements()
        
        # Add class-specific UI elements
        class_name = self.player.character_class.name
        base_elements.insert(1, f"Class: {class_name}")
        
        # Add class-specific stats
        if class_name.lower() == 'mage':
            mage = self.player.character_class
            base_elements.append(f"Mana: {int(mage.mana)}/{mage.max_mana}")
        
        return base_elements

# Usage in main.py integration
def integrate_class_system_in_main():
    """
    Example of how to integrate this into your main game loop:
    
    # In your main.py or game manager:
    
    # Add class selection state
    class_selection = ClassSelectionState(font, sound_manager)
    game_state_manager.add_state("class_selection", class_selection)
    
    # Modified gameplay state creation
    def create_gameplay_state(selected_class):
        return EnhancedGameplayState(font, sound_manager, selected_class)
    
    # In your state transitions:
    if current_state == "menu" and player_starts_game:
        game_state_manager.change_state("class_selection")
    
    elif current_state == "class_selection" and class_selected:
        selected_class = class_selection.get_selected_class()
        gameplay_state = create_gameplay_state(selected_class)
        game_state_manager.add_state("gameplay", gameplay_state)
        game_state_manager.change_state("gameplay")
    """
    pass
