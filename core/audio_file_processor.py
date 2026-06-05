"""
Process audio files (MP3, WAV, OPUS) and extract Morse code
"""

import numpy as np
from pathlib import Path

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class AudioFileProcessor:
    def __init__(self):
        self.sample_rate = 44100
        self.silence_threshold = 0.01
        
    def load_audio(self, file_path):
        """Load audio file (supports MP3, WAV, OGG, OPUS, M4A)"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = file_path.suffix.lower()
        
        # Try soundfile first (supports WAV, FLAC, OGG)
        if SOUNDFILE_AVAILABLE and ext in ['.wav', '.flac', '.ogg']:
            audio, sr = sf.read(file_path)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)  # Convert to mono
            return audio, sr
        
        # Try pydub for MP3, M4A, OPUS
        elif PYDUB_AVAILABLE and ext in ['.mp3', '.m4a', '.opus', '.mp4']:
            audio_segment = AudioSegment.from_file(str(file_path))
            audio = np.array(audio_segment.get_array_of_samples())
            sr = audio_segment.frame_rate
            
            # Convert to mono if stereo
            if audio_segment.channels == 2:
                audio = audio.reshape(-1, 2).mean(axis=1)
            
            # Normalize
            audio = audio / np.max(np.abs(audio))
            return audio, sr
        
        else:
            raise ValueError(f"Unsupported file format: {ext}. Install soundfile or pydub.")
    
    def extract_morse_from_audio(self, audio, sample_rate, morse_engine, language="english"):
        """Extract Morse code from audio data"""
        # Resample if needed
        if sample_rate != self.sample_rate:
            from scipy import signal
            audio = signal.resample(audio, int(len(audio) * self.sample_rate / sample_rate))
        
        # Detect tone/silence
        energy = np.abs(audio)
        threshold = np.mean(energy) * 2
        
        # Find tone segments
        is_tone = energy > threshold
        
        # Detect state changes
        changes = np.diff(is_tone.astype(int))
        tone_starts = np.where(changes == 1)[0]
        tone_ends = np.where(changes == -1)[0]
        
        # Calculate durations
        morse_symbols = []
        
        for start, end in zip(tone_starts[:len(tone_ends)], tone_ends):
            duration = (end - start) / self.sample_rate
            
            if duration < 0.03:  # Ignore very short noises
                continue
            elif duration < 0.15:  # Dit
                morse_symbols.append('.')
            else:  # Dah
                morse_symbols.append('-')
            
            # Check silence after tone
            if end < len(is_tone) - 1:
                next_tone = np.where(is_tone[end:])[0]
                if len(next_tone) > 0:
                    silence_duration = next_tone[0] / self.sample_rate
                    if silence_duration > 0.3:  # Word space
                        morse_symbols.append('/')
                    elif silence_duration > 0.1:  # Letter space
                        morse_symbols.append(' ')
        
        # Convert to string
        morse_string = ''.join(morse_symbols)
        
        # Translate to text
        text = morse_engine.morse_to_text(morse_string, language)
        
        return {
            'morse': morse_string,
            'text': text,
            'symbol_count': len(morse_symbols),
            'duration_seconds': len(audio) / self.sample_rate
        }
    
    def get_supported_formats(self):
        """Return list of supported audio formats"""
        formats = []
        if SOUNDFILE_AVAILABLE:
            formats.extend(['.wav', '.flac', '.ogg'])
        if PYDUB_AVAILABLE:
            formats.extend(['.mp3', '.m4a', '.opus', '.mp4'])
        return formats