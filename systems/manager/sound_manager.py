import math, pygame, os
import numpy as np
from settings import *

class SoundManager:
    def __init__(self):
        self.sounds = {} # Data Handler for Music, SFX
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.load_sounds()
    
    def load_sounds(self):
        """Load sound effects from WAV files"""
        try:
            self.load_sound_files()
        except Exception as e:
            print(f"Sound initialization failed: {e}")
            # Fallback to procedural sounds if WAV files fail to load
            self.generate_fallback_sounds()
    
    def load_sound_files(self):
        """Load WAV sound files from assets directory"""
        sound_files = {
            'attack': 'assets/sounds/attack.wav',
            'enemy_hit': 'assets/sounds/enemy_hit.wav',
            'enemy_death': 'assets/sounds/enemy_death.wav',
            'player_damage': 'assets/sounds/player_damage.wav',  # NEW: Player damage sound
            'level_up': 'assets/sounds/level_up.wav',
            'wave_complete': 'assets/sounds/wave_complete.wav'
        }
        
        # Create assets/sounds directory if it doesn't exist
        sound_dir = 'assets/sounds'
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir, exist_ok=True)
            print(f"Created directory: {sound_dir}")
            print("Please place your WAV files in the assets/sounds/ directory:")
            for sound_name, filepath in sound_files.items():
                print(f"  - {filepath}")
        
        # Load each sound file
        for sound_name, filepath in sound_files.items():
            if os.path.exists(filepath):
                try:
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.sfx_volume)
                    self.sounds[sound_name] = sound
                    print(f"Loaded sound: {filepath}")
                except pygame.error as e:
                    print(f"Failed to load {filepath}: {e}")
                    # Generate fallback for this specific sound
                    self.generate_fallback_sound(sound_name)
            else:
                print(f"Sound file not found: {filepath}")
                # Generate fallback for this specific sound
                self.generate_fallback_sound(sound_name)
    
    def generate_fallback_sound(self, sound_name):
        """Generate a single fallback sound if WAV file is missing"""
        print(f"Generating fallback sound for: {sound_name}")
        
        # Define fallback sound parameters
        sound_params = {
            'attack': (1000, 0.1, 'burst'),
            'enemy_hit': (600, 0.2, 'fade'),
            'enemy_death': (400, 0.4, 'descend'),
            'player_damage': (300, 0.3, 'pain'),  # NEW: Player damage sound parameters
            'level_up': (800, 0.6, 'ascend'),
            'wave_complete': (1200, 0.8, 'victory')
        }
        
        if sound_name in sound_params:
            base_freq, duration, style = sound_params[sound_name]
            self.create_tone(sound_name, base_freq, duration, style)
    
    def generate_fallback_sounds(self):
        """Generate all procedural sound effects as fallback"""
        print("Generating fallback procedural sounds...")
        # Attack sound - sharp burst
        self.create_tone('attack', 1000, 0.1, 'burst')
        # Enemy hit - mid tone
        self.create_tone('enemy_hit', 600, 0.2, 'fade')
        # Enemy death - descending tone
        self.create_tone('enemy_death', 400, 0.4, 'descend')
        # Player damage - pain sound
        self.create_tone('player_damage', 300, 0.3, 'pain')  # NEW: Player damage fallback
        # Level up - ascending chord
        self.create_tone('level_up', 800, 0.6, 'ascend')
        # Wave complete - victory chord
        self.create_tone('wave_complete', 1200, 0.8, 'victory')
    
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
            elif style == 'fade':
                freq = base_freq
                amplitude = 4096 * (1 - progress)
            elif style == 'descend':
                freq = base_freq * (1 - progress * 0.7)
                amplitude = 4096 * (1 - progress)
            elif style == 'ascend':
                freq = base_freq * (1 + progress)
                amplitude = 4096 * math.sin(math.pi * progress)
            elif style == 'pain':  # NEW: Pain sound style for player damage
                # Create a harsh, distorted sound with multiple frequencies
                freq1 = base_freq
                freq2 = base_freq * 0.7
                freq3 = base_freq * 1.3
                wave1 = math.sin(2 * math.pi * freq1 * t)
                wave2 = math.sin(2 * math.pi * freq2 * t) * 0.6
                wave3 = math.sin(2 * math.pi * freq3 * t) * 0.4
                # Add some noise for harsh effect
                noise = (math.sin(2 * math.pi * freq1 * t * 7) * 0.2)
                amplitude = 3072 * (wave1 + wave2 + wave3 + noise) * (1 - progress) * math.sin(progress * math.pi * 3)
            elif style == 'victory':
                freq1 = base_freq
                freq2 = base_freq * 1.25
                amplitude = 2048 * (math.sin(2 * math.pi * freq1 * t) + 
                                  math.sin(2 * math.pi * freq2 * t)) * (1 - progress)
            else:
                freq = base_freq
                amplitude = 4096 * (1 - progress)
            
            if style not in ['victory', 'pain']:
                wave = amplitude * math.sin(2 * math.pi * freq * t)
            else:
                wave = amplitude
            
            arr.append([int(wave), int(wave)])
        
        sound = pygame.sndarray.make_sound(np.array(arr, dtype=np.int16))
        sound.set_volume(self.sfx_volume)

        # Adding/Updating on the Sound Data Handler
        self.sounds[name] = sound
    
    def play_sound(self, name):
        """Play a sound effect"""
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass
    
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
        except:
            pass
    
    def stop_background_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
        except:
            pass
