"""Fallback audio processor using winsound (Windows only)"""

import winsound
import threading
import time
import numpy as np

class SimpleAudioProcessor:
    """Simplified audio processor for Windows using built-in winsound"""
    
    def __init__(self):
        self.is_playing = False
        self.frequency = 800  # Hz
    
    def play_morse(self, morse_code: str, speed: float = 1.0):
        """Play Morse code using winsound (simpler but works everywhere)"""
        def _play():
            self.is_playing = True
            
            # Timing in milliseconds
            dit_duration = int(100 / speed)
            dah_duration = int(300 / speed)
            letter_space = int(300 / speed)
            word_space = int(700 / speed)
            
            for symbol in morse_code:
                if not self.is_playing:
                    break
                    
                if symbol == '.':
                    winsound.Beep(self.frequency, dit_duration)
                    time.sleep(dit_duration / 1000)
                elif symbol == '-':
                    winsound.Beep(self.frequency, dah_duration)
                    time.sleep(dit_duration / 1000)
                elif symbol == ' ':
                    time.sleep(letter_space / 1000)
                elif symbol == '/':
                    time.sleep(word_space / 1000)
            
            self.is_playing = False
        
        threading.Thread(target=_play, daemon=True).start()
    
    def stop(self):
        """Stop playback"""
        self.is_playing = False