import threading
import time
import numpy as np

try:
    import simpleaudio as sa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Simpleaudio not available - using beep fallback")

class AudioPlayer:
    def __init__(self):
        self.is_playing = False
        self.speed = 1.0
        self.frequency = 800
        
        if not AUDIO_AVAILABLE:
            print("Using fallback audio (winsound)")
    
    def play_morse(self, morse_code: str):
        def _play():
            self.is_playing = True
            
            dit_ms = max(50, int(100 / self.speed))
            dah_ms = dit_ms * 3
            space_ms = dit_ms
            word_space_ms = dit_ms * 7
            
            for symbol in morse_code:
                if not self.is_playing:
                    break
                    
                if symbol == '.':
                    self._beep(dit_ms)
                    time.sleep(dit_ms / 1000)
                elif symbol == '-':
                    self._beep(dah_ms)
                    time.sleep(dit_ms / 1000)
                elif symbol == ' ':
                    time.sleep(space_ms / 1000)
                elif symbol == '/':
                    time.sleep(word_space_ms / 1000)
            
            self.is_playing = False
        
        threading.Thread(target=_play, daemon=True).start()
    
    def _beep(self, duration_ms: int):
        try:
            import winsound
            winsound.Beep(self.frequency, duration_ms)
        except:
            print("\a", end='', flush=True)
    
    def stop(self):
        self.is_playing = False
    
    def set_speed(self, speed: float):
        self.speed = max(0.5, min(3.0, speed))
