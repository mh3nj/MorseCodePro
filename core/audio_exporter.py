"""
Export Morse code as audio files (WAV, MP3)
"""

import numpy as np
from pathlib import Path

class AudioExporter:
    def __init__(self):
        self.sample_rate = 44100
        self.frequency = 800  # Hz
    
    def morse_to_audio(self, morse_code: str, wpm: int = 20) -> np.ndarray:
        """Convert Morse code to audio waveform"""
        # Calculate timing based on WPM
        dit_duration = 1.2 / wpm  # seconds
        dah_duration = dit_duration * 3
        space_duration = dit_duration
        word_space = dit_duration * 7
        
        samples = []
        
        for symbol in morse_code:
            if symbol == '.':
                samples.extend(self._generate_tone(dit_duration))
                samples.extend(self._generate_silence(space_duration))
            elif symbol == '-':
                samples.extend(self._generate_tone(dah_duration))
                samples.extend(self._generate_silence(space_duration))
            elif symbol == ' ':
                samples.extend(self._generate_silence(space_duration))
            elif symbol == '/':
                samples.extend(self._generate_silence(word_space))
        
        return np.array(samples)
    
    def _generate_tone(self, duration: float) -> np.ndarray:
        """Generate sine wave tone"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = 0.5 * np.sin(2 * np.pi * self.frequency * t)
        return (wave * 32767).astype(np.int16)
    
    def _generate_silence(self, duration: float) -> np.ndarray:
        """Generate silence"""
        return np.zeros(int(self.sample_rate * duration), dtype=np.int16)
    
    def export_as_wav(self, morse_code: str, filepath: Path, wpm: int = 20):
        """Export Morse as WAV file"""
        try:
            import soundfile as sf
            audio_data = self.morse_to_audio(morse_code, wpm)
            sf.write(str(filepath), audio_data, self.sample_rate)
            return True
        except ImportError:
            return False
    
    def export_as_mp3(self, morse_code: str, filepath: Path, wpm: int = 20):
        """Export Morse as MP3 file"""
        try:
            from pydub import AudioSegment
            import io
            
            # Generate WAV first
            audio_data = self.morse_to_audio(morse_code, wpm)
            
            # Convert to MP3 using pydub
            audio_segment = AudioSegment(
                audio_data.tobytes(),
                frame_rate=self.sample_rate,
                sample_width=2,
                channels=1
            )
            audio_segment.export(str(filepath), format="mp3")
            return True
        except ImportError:
            return False