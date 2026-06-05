import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy import signal
from scipy.fft import fft, fftfreq
import threading
import queue
import time
from pathlib import Path
from typing import Callable, Optional
from config.settings import SAMPLE_RATE, MIC_BUFFER_SIZE, SILENCE_THRESHOLD

class AudioProcessor:
    def __init__(self):
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.morse_buffer = []
        self.current_frequency = 800  # Hz
        self.confidence_threshold = 0.6
        
    def start_mic_listening(self, callback: Callable):
        """Start live microphone listening with spectrogram analysis"""
        self.is_listening = True
        
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")
            if self.is_listening:
                self.audio_queue.put(indata.copy())
        
        def process_audio():
            while self.is_listening:
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                    detected = self.detect_morse_from_audio(audio_chunk)
                    if detected:
                        callback(detected)
                except queue.Empty:
                    continue
        
        self.stream = sd.InputStream(
            callback=audio_callback,
            channels=1,
            samplerate=SAMPLE_RATE,
            blocksize=MIC_BUFFER_SIZE
        )
        self.stream.start()
        
        self.processing_thread = threading.Thread(target=process_audio, daemon=True)
        self.processing_thread.start()
    
    def stop_mic_listening(self):
        """Stop live microphone listening"""
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
    
    def detect_morse_from_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """Detect Morse code from audio chunk using spectrogram"""
        # Convert to mono if needed
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Calculate spectrogram
        f, t, Sxx = signal.spectrogram(
            audio_data.flatten(),
            fs=SAMPLE_RATE,
            nperseg=256,
            noverlap=128
        )
        
        # Find dominant frequency
        frequencies = fftfreq(len(audio_data), 1/SAMPLE_RATE)
        fft_values = np.abs(fft(audio_data.flatten()))
        dominant_freq = frequencies[np.argmax(fft_values[:len(frequencies)//2])]
        
        # Check if dominant frequency is in Morse range (500-1500 Hz)
        if 500 < dominant_freq < 1500:
            self.current_frequency = dominant_freq
            
            # Detect tone energy levels
            energy = np.mean(Sxx, axis=0)
            max_energy = np.max(energy)
            
            # Tone detection with threshold
            is_tone = energy > (max_energy * 0.3)
            
            # Detect dits and dahs based on duration
            tone_durations = self._measure_tone_durations(is_tone, t)
            
            # Convert to Morse symbols
            morse_symbols = self._durations_to_morse(tone_durations)
            
            if morse_symbols:
                return ''.join(morse_symbols)
        
        return None
    
    def _measure_tone_durations(self, is_tone: np.ndarray, time_array: np.ndarray) -> list:
        """Measure durations of tones and silences"""
        durations = []
        current_type = is_tone[0]
        start_time = time_array[0]
        
        for i, is_tone_now in enumerate(is_tone):
            if is_tone_now != current_type:
                duration = time_array[i] - start_time
                durations.append(('tone' if current_type else 'silence', duration))
                current_type = is_tone_now
                start_time = time_array[i]
        
        # Add last segment
        duration = time_array[-1] - start_time
        durations.append(('tone' if current_type else 'silence', duration))
        
        return durations
    
    def _durations_to_morse(self, durations: list) -> list:
        """Convert tone durations to Morse symbols (dit/dah)"""
        morse_symbols = []
        
        # Find median tone duration as reference
        tone_durations = [d for t, d in durations if t == 'tone']
        if not tone_durations:
            return []
        
        median_tone = np.median(tone_durations)
        
        for seg_type, duration in durations:
            if seg_type == 'tone':
                if duration < median_tone * 1.5:
                    morse_symbols.append('.')  # Dit
                else:
                    morse_symbols.append('-')  # Dah
            elif seg_type == 'silence':
                if duration > median_tone * 3:
                    morse_symbols.append(' ')  # Space between words
                elif duration > median_tone * 1.5:
                    morse_symbols.append('/')  # Between letters
                # Short silences are gaps within letters (ignored)
        
        return morse_symbols
    
    def process_audio_file(self, file_path: str, callback: Callable):
        """Process audio file (mp3, wav, opus) and detect Morse"""
        try:
            # Load audio file
            audio_data, sample_rate = sf.read(file_path, always_2d=True)
            
            # Convert to mono if stereo
            if audio_data.shape[1] > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if needed
            if sample_rate != SAMPLE_RATE:
                import scipy.signal as sig
                audio_data = sig.resample(audio_data, int(len(audio_data) * SAMPLE_RATE / sample_rate))
            
            # Process in chunks for long files
            chunk_size = SAMPLE_RATE * 5  # 5-second chunks
            full_morse = []
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                morse = self.detect_morse_from_audio(chunk)
                if morse:
                    full_morse.append(morse)
            
            result = ''.join(full_morse)
            callback(result)
            
        except Exception as e:
            print(f"Error processing audio file: {e}")
            callback("")
    
    def generate_spectrogram_image(self, audio_data: np.ndarray, output_path: str):
        """Generate spectrogram image for visualization"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 4))
        plt.specgram(audio_data, Fs=SAMPLE_RATE, cmap='plasma')
        plt.title('Morse Code Spectrogram')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Frequency (Hz)')
        plt.colorbar(label='Intensity (dB)')
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()