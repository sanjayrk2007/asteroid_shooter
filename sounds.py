import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.volume = 0.5
        self.load_sounds()

    def load_sounds(self):
        """Load all game sounds from assets/sounds directory"""
        base_path = os.path.join("assets", "sounds")
        sound_files = {
            "shoot": "shoot.wav",
            "explosion": "explosion.wav",
            "hit": "hit.wav",
            "thrust": "thrust.wav",
            "game_over": "game_over.wav"
        }
        
        # Create directory if it doesn't exist
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            print(f"Created sounds directory: {base_path}")
            print("Please add sound files (.wav format) to this directory")
        
        for key, filename in sound_files.items():
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(path)
                    self.sounds[key].set_volume(self.volume)
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"Sound file missing: {path}")

    def play(self, sound_key):
        """Play a sound by its key"""
        sound = self.sounds.get(sound_key)
        if sound:
            sound.play()

    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def stop_all(self):
        """Stop all currently playing sounds"""
        pygame.mixer.stop()
