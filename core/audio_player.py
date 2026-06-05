import threading
import time
import numpy as np
import simpleaudio as sa
from config.settings import SAMPLE_RATE, FREQUENCY, DIT_DURATION

class AudioPlayer:
    def __init__(self):
        self.current_playback = None
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.speed = 1.0  # 1.0 = normal speed
        self.dit_duration = DIT_DURATION
    
    def morse_to_audio(self, morse_code: str) -> np.ndarray:
        """Convert Morse code to audio waveform"""
        samples = []
        
        for char in morse_code:
            if char == '.':
                samples.extend(self._generate_tone(self._adjusted_duration(1)))
                samples.extend(self._generate_silence(self._adjusted_duration(1)))
            elif char == '-':
                samples.extend(self._generate_tone(self._adjusted_duration(3)))
                samples.extend(self._generate_silence(self._adjusted_duration(1)))
            elif char == ' ':
                samples.extend(self._generate_silence(self._adjusted_duration(3)))
            elif char == '/':  # Word space
                samples.extend(self._generate_silence(self._adjusted_duration(7)))
        
        return np.array(samples)
    
    def _adjusted_duration(self, units: int) -> float:
        """Adjust duration based on speed"""
        return (self.dit_duration * units) / 1000 / self.speed
    
    def _generate_tone(self, duration: float) -> np.ndarray:
        """Generate sine wave tone"""
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        wave = 0.5 * np.sin(2 * np.pi * FREQUENCY * t)
        return (wave * 32767).astype(np.int16)
    
    def _generate_silence(self, duration: float) -> np.ndarray:
        """Generate silence"""
        samples = int(SAMPLE_RATE * duration)
        return np.zeros(samples, dtype=np.int16)
    
    def play(self, morse_code: str, callback=None):
        """Play Morse code audio"""
        def _play():
            audio_data = self.morse_to_audio(morse_code)
            self.current_playback = sa.play_buffer(
                audio_data, 1, 2, SAMPLE_RATE
            )
            self.current_playback.wait_done()
            self.is_playing = False
            if callback:
                callback()
        
        self.is_playing = True
        self.thread = threading.Thread(target=_play)
        self.thread.start()
    
    def pause(self):
        """Pause playback"""
        if self.current_playback and self.is_playing:
            self.is_paused = True
            # Note: simpleaudio doesn't support pause natively
            # We'll implement with position tracking in full version
    
    def resume(self):
        """Resume playback"""
        self.is_paused = False
        # Position-based resume
    
    def stop(self):
        """Stop playback"""
        if self.current_playback:
            self.current_playback.stop()
            self.is_playing = False
    
    def set_speed(self, speed: float):
        """Change playback speed (0.5x to 3.0x)"""
        self.speed = max(0.5, min(3.0, speed))