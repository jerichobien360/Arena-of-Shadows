import math, pygame, os
import numpy as np
from settings import *


class SoundManager:
    """
    An enhanced sound manager that automatically integrates with UI elements
    and provides easy-to-use sound effects for game events.
    """
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}  # Data Handler for Music, SFX
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.ui_sounds_enabled = True
        self.music_paused = False  # Track music pause state
        self.load_sounds()
        
        # UI Sound mapping - automatically triggered by UI interactions
        self.ui_sound_map = {
            'button_click': 'ui_click',
            'button_hover': 'ui_hover',
            'slider_drag': 'ui_slider',
            'checkbox_toggle': 'ui_toggle',
            'dropdown_open': 'ui_dropdown',
            'input_focus': 'ui_focus',
            'panel_open': 'ui_panel',
            'error': 'ui_error',
            'success': 'ui_success'
        }
        
    def load_sounds(self):
        """Load sound effects from WAV files with comprehensive fallbacks"""
        try:
            self.load_sound_files()
        except Exception as e:
            print(f"Sound initialization failed: {e}")
            self.generate_fallback_sounds()
    
    def load_sound_files(self):
        """Load WAV sound files from assets directory"""
        
        # Create assets/sounds directory if it doesn't exist
        sound_dir = 'assets/sounds'
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir, exist_ok=True)
            print(f"Created directory: {sound_dir}")
        
        # Load each sound file
        for sound_name, filepath in SOUND_FILES.items():
            if os.path.exists(filepath):
                try:
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[sound_name] = sound
                    print(f"Loaded sound: {filepath}")
                except pygame.error as e:
                    print(f"Failed to load {filepath}: {e}")
                    self.generate_fallback_sound(sound_name)
            else:
                self.generate_fallback_sound(sound_name)
    
    def generate_fallback_sound(self, sound_name):
        """Generate a single fallback sound if WAV file is missing"""
        print(f"Generating fallback sound for: {sound_name}")
        
        # Define fallback sound parameters
        sound_params = {
            # Game sounds
            'attack': (1000, 0.1, 'burst'),
            'enemy_hit': (600, 0.2, 'fade'),
            'enemy_death': (400, 0.4, 'descend'),
            'player_damage': (300, 0.3, 'pain'),
            'level_up': (800, 0.6, 'ascend'),
            'wave_complete': (1200, 0.8, 'victory'),
            
            # UI sounds
            'ui_click': (800, 0.05, 'click'),
            'ui_hover': (600, 0.03, 'soft'),
            'ui_slider': (400, 0.08, 'slide'),
            'ui_toggle': (700, 0.06, 'toggle'),
            'ui_dropdown': (500, 0.1, 'dropdown'),
            'ui_focus': (900, 0.04, 'focus'),
            'ui_panel': (1100, 0.15, 'panel'),
            'ui_error': (200, 0.4, 'error'),
            'ui_success': (1000, 0.3, 'success'),
            
            # Ambient/feedback sounds
            'notification': (800, 0.5, 'notification'),
            'coin_collect': (1200, 0.2, 'coin'),
            'item_pickup': (900, 0.15, 'pickup'),
            'magic_cast': (600, 0.8, 'magic')
        }
        
        if sound_name in sound_params:
            base_freq, duration, style = sound_params[sound_name]
            self.create_tone(sound_name, base_freq, duration, style)
    
    def generate_fallback_sounds(self):
        """Generate all procedural sound effects as fallback"""
        print("Generating fallback procedural sounds...")
        
        # Generate all defined sounds
        sound_params = {
            # Game sounds
            'attack': (1000, 0.1, 'burst'),
            'enemy_hit': (600, 0.2, 'fade'),
            'enemy_death': (400, 0.4, 'descend'),
            'player_damage': (300, 0.3, 'pain'),
            'level_up': (800, 0.6, 'ascend'),
            'wave_complete': (1200, 0.8, 'victory'),
            
            # UI sounds
            'ui_click': (800, 0.05, 'click'),
            'ui_hover': (600, 0.03, 'soft'),
            'ui_slider': (400, 0.08, 'slide'),
            'ui_toggle': (700, 0.06, 'toggle'),
            'ui_dropdown': (500, 0.1, 'dropdown'),
            'ui_focus': (900, 0.04, 'focus'),
            'ui_panel': (1100, 0.15, 'panel'),
            'ui_error': (200, 0.4, 'error'),
            'ui_success': (1000, 0.3, 'success'),
            
            # Ambient/feedback sounds
            'notification': (800, 0.5, 'notification'),
            'coin_collect': (1200, 0.2, 'coin'),
            'item_pickup': (900, 0.15, 'pickup'),
            'magic_cast': (600, 0.8, 'magic')
        }
        
        for sound_name, (base_freq, duration, style) in sound_params.items():
            self.create_tone(sound_name, base_freq, duration, style)
    
    def create_tone(self, name, base_freq, duration, style='fade'):
        """Create different types of tones based on style (fallback method)"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        
        for i in range(frames):
            t = i / sample_rate
            progress = i / frames
            
            if style == 'burst':
                freq = base_freq
                amplitude = 4096 * (1 - progress) * math.exp(-progress * 5)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'fade':
                freq = base_freq
                amplitude = 4096 * (1 - progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'descend':
                freq = base_freq * (1 - progress * 0.7)
                amplitude = 4096 * (1 - progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'ascend':
                freq = base_freq * (1 + progress)
                amplitude = 4096 * math.sin(math.pi * progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'pain':
                # Harsh, distorted sound for damage
                freq1, freq2, freq3 = base_freq, base_freq * 0.7, base_freq * 1.3
                wave1 = math.sin(2 * math.pi * freq1 * t)
                wave2 = math.sin(2 * math.pi * freq2 * t) * 0.6
                wave3 = math.sin(2 * math.pi * freq3 * t) * 0.4
                noise = math.sin(2 * math.pi * freq1 * t * 7) * 0.2
                amplitude = 3072 * (wave1 + wave2 + wave3 + noise) * (1 - progress) * math.sin(progress * math.pi * 3)
                wave = amplitude
            
            elif style == 'victory':
                freq1, freq2 = base_freq, base_freq * 1.25
                amplitude = 2048 * (math.sin(2 * math.pi * freq1 * t) + 
                                  math.sin(2 * math.pi * freq2 * t)) * (1 - progress)
                wave = amplitude
            
            # UI-specific styles
            elif style == 'click':
                freq = base_freq * (1 + progress * 0.5)
                amplitude = 3000 * math.exp(-progress * 8)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'soft':
                freq = base_freq
                amplitude = 1500 * math.exp(-progress * 10)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'slide':
                freq = base_freq * (1 + progress * 0.3)
                amplitude = 2000 * (1 - progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'toggle':
                freq = base_freq * (1 if progress < 0.5 else 1.5)
                amplitude = 2500 * (1 - progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'dropdown':
                freq = base_freq * (1 - progress * 0.3)
                amplitude = 2000 * math.exp(-progress * 3)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'focus':
                freq = base_freq
                amplitude = 1800 * math.sin(math.pi * progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'panel':
                freq1, freq2 = base_freq, base_freq * 0.75
                amplitude = 1500 * math.exp(-progress * 2)
                wave = amplitude * (math.sin(2 * math.pi * freq1 * t) + 
                                  math.sin(2 * math.pi * freq2 * t) * 0.7)
            
            elif style == 'error':
                freq = base_freq * (1 + math.sin(progress * math.pi * 4) * 0.5)
                amplitude = 3500 * (1 - progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'success':
                freq1, freq2, freq3 = base_freq, base_freq * 1.25, base_freq * 1.5
                amplitude = 2000 * math.sin(math.pi * progress)
                wave = amplitude * (math.sin(2 * math.pi * freq1 * t) + 
                                  math.sin(2 * math.pi * freq2 * t) * 0.6 +
                                  math.sin(2 * math.pi * freq3 * t) * 0.4)
            
            # Ambient/feedback styles
            elif style == 'notification':
                freq1, freq2 = base_freq, base_freq * 1.33
                amplitude = 2500 * math.sin(math.pi * progress) * (1 - progress * 0.3)
                wave = amplitude * (math.sin(2 * math.pi * freq1 * t) + 
                                  math.sin(2 * math.pi * freq2 * t) * 0.8)
            
            elif style == 'coin':
                freq = base_freq * (1 + progress * 2)
                amplitude = 3000 * math.exp(-progress * 4)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'pickup':
                freq = base_freq * (1 + progress * 0.8)
                amplitude = 2500 * (1 - progress) * math.sin(math.pi * progress * 2)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            elif style == 'magic':
                freq1 = base_freq * (1 + math.sin(progress * math.pi * 6) * 0.3)
                freq2 = base_freq * 1.5 * (1 + math.cos(progress * math.pi * 4) * 0.2)
                amplitude = 2200 * (1 - progress) * math.sin(math.pi * progress)
                wave = amplitude * (math.sin(2 * math.pi * freq1 * t) + 
                                  math.sin(2 * math.pi * freq2 * t) * 0.7)
            
            else:
                freq = base_freq
                amplitude = 4096 * (1 - progress)
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            
            # Clamp wave values to prevent audio artifacts
            wave = max(-32767, min(32767, wave))
            arr.append([int(wave), int(wave)])
        
        sound = pygame.sndarray.make_sound(np.array(arr, dtype=np.int16))
        sound.set_volume(self.sfx_volume)
        self.sounds[name] = sound
    
    # Core sound playing methods
    def play_sound(self, name):
        """Play a sound effect"""
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except pygame.error as e:
                print(f"Error playing sound {name}: {e}")
    
    def play_ui_sound(self, ui_action):
        """Play a UI sound based on action type"""
        if not self.ui_sounds_enabled:
            return
            
        if ui_action in self.ui_sound_map:
            sound_name = self.ui_sound_map[ui_action]
            self.play_sound(sound_name)
    
    # Game event sound methods
    def play_attack_sound(self):
        """Play attack sound"""
        self.play_sound('attack')
    
    def play_enemy_hit_sound(self):
        """Play enemy hit sound"""
        self.play_sound('enemy_hit')
    
    def play_enemy_death_sound(self):
        """Play enemy death sound"""
        self.play_sound('enemy_death')
    
    def play_player_damage_sound(self):
        """Play player damage sound"""
        self.play_sound('player_damage')
    
    def play_level_up_sound(self):
        """Play level up sound"""
        self.play_sound('level_up')
    
    def play_wave_complete_sound(self):
        """Play wave complete sound"""
        self.play_sound('wave_complete')
    
    # Feedback and ambient sound methods
    def play_notification_sound(self):
        """Play notification sound"""
        self.play_sound('notification')
    
    def play_coin_collect_sound(self):
        """Play coin collection sound"""
        self.play_sound('coin_collect')
    
    def play_item_pickup_sound(self):
        """Play item pickup sound"""
        self.play_sound('item_pickup')
    
    def play_magic_cast_sound(self):
        """Play magic casting sound"""
        self.play_sound('magic_cast')
    
    # Music methods
    def load_background_music(self, filepath):
        """Load background music from file"""
        try:
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                return True
            else:
                print(f"Background music file not found: {filepath}")
        except Exception as e:
            print(f"Failed to load background music {filepath}: {e}")
        return False
    
    def play_background_music(self, loop=True):
        """Play background music"""
        try:
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self.music_paused = False
        except pygame.error as e:
            print(f"Error playing background music: {e}")
    
    def stop_background_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
            self.music_paused = False
        except pygame.error as e:
            print(f"Error stopping background music: {e}")
    
    def pause_background_music(self):
        """Pause background music"""
        try:
            pygame.mixer.music.pause()
            self.music_paused = True
        except pygame.error as e:
            print(f"Error pausing background music: {e}")
    
    def resume_background_music(self):
        """Resume paused background music"""
        try:
            pygame.mixer.music.unpause()
            self.music_paused = False
        except pygame.error as e:
            print(f"Error resuming background music: {e}")
    
    # Volume control methods
    def set_master_volume(self, volume):
        """Set master volume for all SFX (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            try:
                sound.set_volume(self.sfx_volume)
            except pygame.error as e:
                print(f"Error setting sound volume: {e}")
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except pygame.error as e:
            print(f"Error setting music volume: {e}")
    
    def toggle_ui_sounds(self, enabled=None):
        """Toggle UI sounds on/off"""
        if enabled is None:
            self.ui_sounds_enabled = not self.ui_sounds_enabled
        else:
            self.ui_sounds_enabled = enabled
        return self.ui_sounds_enabled
    
    # Utility methods
    def is_sound_loaded(self, sound_name):
        """Check if a specific sound is loaded"""
        return sound_name in self.sounds
    
    def get_loaded_sounds(self):
        """Get list of all loaded sound names"""
        return list(self.sounds.keys())
    
    def reload_sounds(self):
        """Reload all sounds (useful for hot-swapping audio files)"""
        self.sounds.clear()
        self.load_sounds()
