"""
Metronome for Morse Code Practice
Helps maintain consistent timing
"""

import threading
import time
import winsound
import math

class Metronome:
    def __init__(self):
        self.is_running = False
        self.bpm = 60  # Beats per minute (standard Morse speed)
        self.tick_sound = 800  # Hz
        self.accent_sound = 1200  # Hz
        self.current_thread = None
        self.callback = None
        
    def start(self, bpm=60, callback=None):
        """Start metronome"""
        self.bpm = bpm
        self.callback = callback
        self.is_running = True
        
        def _run():
            interval = 60.0 / self.bpm
            beat_count = 0
            
            while self.is_running:
                start_time = time.time()
                
                # Accent every 4th beat (for timing)
                if beat_count % 4 == 0:
                    winsound.Beep(self.accent_sound, 50)
                else:
                    winsound.Beep(self.tick_sound, 50)
                
                if self.callback:
                    self.callback(beat_count % 4 == 0)
                
                beat_count += 1
                
                # Precise timing
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)
        
        self.current_thread = threading.Thread(target=_run, daemon=True)
        self.current_thread.start()
    
    def stop(self):
        """Stop metronome"""
        self.is_running = False
        if self.current_thread:
            self.current_thread.join(timeout=0.5)
    
    def set_bpm(self, bpm):
        """Change tempo"""
        self.bpm = max(30, min(200, bpm))
    
    def get_morse_timing(self, wpm=20):
        """
        Get timing based on WPM (words per minute)
        Standard: 1 word = 50 dit lengths
        """
        dit_duration = 1.2 / wpm  # seconds
        dah_duration = dit_duration * 3
        space_duration = dit_duration
        word_space = dit_duration * 7
        
        return {
            'dit': dit_duration,
            'dah': dah_duration,
            'space': space_duration,
            'word_space': word_space,
            'wpm': wpm
        }
