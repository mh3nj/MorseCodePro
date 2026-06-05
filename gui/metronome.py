import threading
import time
import simpleaudio as sa
import numpy as np
from config.settings import SAMPLE_RATE

class Metronome:
    def __init__(self):
        self.is_running = False
        self.bpm = 60  # Beats per minute
        self.beat_sound = self._generate_click()
        self.current_thread = None
    
    def _generate_click(self) -> np.ndarray:
        """Generate metronome click sound"""
        duration = 0.05  # 50ms click
        samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples)
        
        # Sharp click with decay
        click = np.exp(-t * 100) * np.sin(2 * np.pi * 1000 * t)
        click = (click * 32767).astype(np.int16)
        
        return click
    
    def start(self, bpm: int = None, callback=None):
        """Start metronome"""
        if bpm:
            self.bpm = bpm
        
        self.is_running = True
        
        def _run():
            interval = 60.0 / self.bpm
            
            while self.is_running:
                start_time = time.time()
                
                # Play click
                play_obj = sa.play_buffer(self.beat_sound, 1, 2, SAMPLE_RATE)
                
                if callback:
                    callback()
                
                # Wait for next beat
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
    
    def set_bpm(self, bpm: int):
        """Change tempo"""
        self.bpm = max(30, min(240, bpm))