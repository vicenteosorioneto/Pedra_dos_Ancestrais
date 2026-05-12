from __future__ import annotations

import math
from array import array

import pygame

from shared.enums import GameEvent

MUSIC_VOLUME = 0.35
SFX_VOLUME = 0.75


def set_music_volume(value):
    global MUSIC_VOLUME
    MUSIC_VOLUME = max(0.0, min(1.0, float(value)))


def set_sfx_volume(value):
    global SFX_VOLUME
    SFX_VOLUME = max(0.0, min(1.0, float(value)))


def get_music_volume():
    return MUSIC_VOLUME


def get_sfx_volume():
    return SFX_VOLUME


class AudioManager:
    def __init__(self, bus=None):
        self.enabled = pygame.mixer.get_init() is not None
        self._ambient_channel = None
        self._current_mood = None
        self._sounds = {}
        if not self.enabled:
            return

        self._sounds = {
            "village": self._tone_theme((196, 247, 294), (294, 330, 247, 220, 196), 9.6, volume=0.11),
            "forest": self._tone_theme((147, 196, 220), (220, 247, 196, 165, 147), 10.8, volume=0.10),
            "trail": self._tone_theme((98, 147, 196), (196, 220, 247, 196, 147, 123), 12.0, volume=0.11),
            "cave": self._tone_theme((82, 123, 165), (165, 147, 123, 110, 98), 12.4, volume=0.11),
            "ending": self._tone_theme((147, 196, 247), (247, 294, 330, 294, 247), 11.2, volume=0.09),
            "pause": self._tone_theme((110, 165, 220), (220, 165, 147, 165), 8.0, volume=0.07),
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
        self._sounds[name].set_volume(SFX_VOLUME)
        self._sounds[name].play()

    def update_for_scene(self, scene):
        if not self.enabled or scene is None:
            return
        mood = "pause" if getattr(scene, "_paused", False) else self._mood_for_scene(scene)
        if mood == self._current_mood:
            if self._ambient_channel:
                self._ambient_channel.set_volume(MUSIC_VOLUME)
            return
        self._current_mood = mood
        snd = self._sounds.get(mood)
        if snd and self._ambient_channel:
            self._ambient_channel.play(snd, loops=-1, fade_ms=350)
        if self._ambient_channel:
            self._ambient_channel.set_volume(MUSIC_VOLUME)

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
            fade = min(1.0, i / max(1, rate // 8), (total - i) / max(1, rate // 8))
            env = fade * (0.72 + 0.18 * math.sin(t * math.pi * 2 / seconds))
            sample = 0.0
            for freq in freqs:
                sample += math.sin(2 * math.pi * freq * t)
                sample += 0.35 * math.sin(2 * math.pi * freq * 2 * t)
            sample /= max(1, len(freqs) * 1.35)
            samples.append(int(sample * env * volume * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _tone_theme(self, chord_freqs, melody_freqs, seconds, volume=0.2):
        rate = 22050
        samples = array("h")
        total = int(rate * seconds)
        beat_len = max(1, total // max(1, len(melody_freqs) * 2))
        phase = 0.0
        for i in range(total):
            t = i / rate
            fade = min(1.0, i / max(1, rate // 3), (total - i) / max(1, rate // 2))
            slow = 0.78 + 0.16 * math.sin(t * math.pi * 2 / max(1.0, seconds * 0.5))
            sample = 0.0
            for n, freq in enumerate(chord_freqs):
                wobble = 1.0 + math.sin(t * 0.45 + n) * 0.004
                sample += math.sin(2 * math.pi * freq * wobble * t) * 0.42
                sample += math.sin(2 * math.pi * freq * 2.0 * t) * 0.10

            melody = melody_freqs[(i // beat_len) % len(melody_freqs)]
            phase += 2 * math.pi * melody / rate
            pluck_t = (i % beat_len) / beat_len
            pluck_env = max(0.0, 1.0 - pluck_t) ** 2
            sample += math.sin(phase) * 0.34 * pluck_env

            breath = 0.03 * math.sin(2 * math.pi * 32 * t) * math.sin(t * 0.9)
            sample = (sample + breath) / 1.75
            samples.append(int(sample * fade * slow * volume * 32767))
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
