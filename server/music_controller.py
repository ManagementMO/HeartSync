"""
Reactive Music System for HeartSync.

Uses 3 pre-prepared audio stems that crossfade based on sync score:
- Layer A: Warm, harmonious ambient (plays at high sync)
- Layer B: Neutral melodic pad (always plays softly)
- Layer C: Dissonant/tense texture (plays at low sync)

Audio files should be:
- WAV or OGG format
- Same length and BPM (loop seamlessly)
- Placed in audio/ directory
"""

import pygame
import threading
import time

class MusicController:
    """Crossfades music layers based on sync score."""

    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(4)

        self.channels = {
            "harmony": pygame.mixer.Channel(0),
            "neutral": pygame.mixer.Channel(1),
            "tension": pygame.mixer.Channel(2),
            "narration": pygame.mixer.Channel(3),  # Reserved for ElevenLabs
        }

        self.sounds = {}
        self.loaded = False
        self.current_sync = 0.0

    def load_stems(self, harmony_path, neutral_path, tension_path):
        """Load the three music stems."""
        try:
            self.sounds["harmony"] = pygame.mixer.Sound(harmony_path)
            self.sounds["neutral"] = pygame.mixer.Sound(neutral_path)
            self.sounds["tension"] = pygame.mixer.Sound(tension_path)
            self.loaded = True
        except Exception as e:
            print(f"Music load error: {e}")
            self.loaded = False

    def start(self):
        """Start playing all layers (volumes will be controlled by update)."""
        if not self.loaded:
            return
        for name, channel in self.channels.items():
            if name in self.sounds:
                channel.play(self.sounds[name], loops=-1)  # Loop forever
        # Start with neutral mix
        self.update_sync(0.5)

    def stop(self):
        """Stop all music."""
        for channel in self.channels.values():
            channel.stop()

    def update_sync(self, sync_score):
        """
        Adjust layer volumes based on sync score.

        sync = 0.0 (disconnected):
            harmony=0.0, neutral=0.3, tension=0.7
        sync = 0.5 (connecting):
            harmony=0.4, neutral=0.5, tension=0.2
        sync = 1.0 (deeply connected):
            harmony=0.8, neutral=0.3, tension=0.0
        """
        if not self.loaded:
            return

        self.current_sync = sync_score
        s = sync_score

        harmony_vol = min(1.0, s * 1.0)           # 0->0, 0.5->0.5, 1.0->1.0
        neutral_vol = 0.3 + 0.2 * (1 - abs(s - 0.5) * 2)  # Peak at 0.5
        tension_vol = max(0.0, 0.7 - s * 1.0)     # 0.7->0, tapers off

        self.channels["harmony"].set_volume(harmony_vol)
        self.channels["neutral"].set_volume(neutral_vol)
        self.channels["tension"].set_volume(tension_vol)
