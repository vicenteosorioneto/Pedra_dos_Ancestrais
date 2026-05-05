from __future__ import annotations

import math
from array import array

import pygame

from shared.enums import GameEvent


class AudioManager:
    def __init__(self, bus=None):
        self.enabled = pygame.mixer.get_init() is not None
        self._ambient_channel = None
        self._current_mood = None
        self._sounds = {}
        if not self.enabled:
            return

        self._sounds = {
            "village": self._tone_chord((196, 247), 1.6, volume=0.16),
            "forest": self._tone_chord((165, 220), 1.8, volume=0.13),
            "trail": self._tone_chord((110, 165), 1.9, volume=0.14),
            "cave": self._tone_chord((82, 123), 2.1, volume=0.16),
            "ending": self._tone_chord((147, 196), 2.0, volume=0.12),
            "pickup": self._tone_sweep(520, 880, 0.18, volume=0.35),
            "damage": self._tone_sweep(180, 80, 0.16, volume=0.35),
            "portal": self._tone_sweep(260, 740, 0.45, volume=0.32),
        }
        self._ambient_channel = pygame.mixer.Channel(0)

        if bus:
            bus.subscribe(GameEvent.PLAYER_DAMAGED, lambda **_: self.play("damage"))
            bus.subscribe(GameEvent.ITEM_COLLECTED, lambda **_: self.play("pickup"))
            bus.subscribe(GameEvent.KARMA_CHANGED, lambda **_: None)

    def play(self, name):
        if not self.enabled or name not in self._sounds:
            return
        self._sounds[name].play()

    def update_for_scene(self, scene):
        if not self.enabled or scene is None:
            return
        mood = self._mood_for_scene(scene)
        if mood == self._current_mood:
            return
        self._current_mood = mood
        snd = self._sounds.get(mood)
        if snd and self._ambient_channel:
            self._ambient_channel.play(snd, loops=-1, fade_ms=350)
            self._ambient_channel.set_volume(0.35)

    def _mood_for_scene(self, scene):
        name = scene.__class__.__name__.lower()
        if "forest" in name:
            return "forest"
        if "trail" in name or "ruins" in name:
            return "trail"
        if "cave" in name:
            return "cave"
        if "ending" in name:
            return "ending"
        return "village"

    def _tone_chord(self, freqs, seconds, volume=0.2):
        rate = 22050
        samples = array("h")
        total = int(rate * seconds)
        for i in range(total):
            t = i / rate
            env = 0.65 + 0.35 * math.sin(t * math.pi * 2 / seconds)
            sample = 0.0
            for freq in freqs:
                sample += math.sin(2 * math.pi * freq * t)
            sample /= max(1, len(freqs))
            samples.append(int(sample * env * volume * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _tone_sweep(self, start_freq, end_freq, seconds, volume=0.3):
        rate = 22050
        samples = array("h")
        total = int(rate * seconds)
        phase = 0.0
        for i in range(total):
            t = i / total
            freq = start_freq + (end_freq - start_freq) * t
            phase += 2 * math.pi * freq / rate
            env = max(0.0, 1.0 - t)
            samples.append(int(math.sin(phase) * env * volume * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())
