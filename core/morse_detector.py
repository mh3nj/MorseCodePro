"""
Morse Code Detector - With Frequency Filtering (Ignores Speech)
"""

import threading
import queue
import time
import numpy as np

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

class MorseDetector:
    def __init__(self, device_id=None):
        self.is_listening = False
        self.audio_queue = queue.Queue()
        
        # Find working device
        self.device_id = device_id
        if AUDIO_AVAILABLE and self.device_id is None:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0 and 'Razer' in device['name']:
                    self.device_id = i
                    break
        
        # Detection parameters
        self.threshold = 500
        self.min_dit_duration = 0.08
        self.max_dit_duration = 0.25
        self.min_dah_duration = 0.26
        self.max_dah_duration = 0.60
        self.word_pause = 0.8
        self.letter_pause = 0.3
        
        # Frequency filtering (800-1200 Hz for Morse beeps)
        self.min_freq = 700
        self.max_freq = 1300
        self.sample_rate = 44100
        
        # State
        self.sound_start = 0
        self.silence_start = 0
        self.current_letter = []
        self.current_word = []
        
        # Callbacks
        self.on_morse_symbol = None
        self.on_letter = None
        self.on_word = None
        self.on_amplitude = None
        
        self.morse_map = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9'
        }
    
    def start_listening(self):
        """Start listening"""
        if not AUDIO_AVAILABLE:
            return False
        
        try:
            self.is_listening = True
            self.stream = sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=2048,
                device=self.device_id
            )
            self.stream.start()
            
            self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
            self.processing_thread.start()
            
            print(f"✅ Listening on device {self.device_id}")
            return True
        except Exception as e:
            print(f"Failed: {e}")
            self.is_listening = False
            return False
    
    def stop_listening(self):
        """Stop"""
        self.is_listening = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
    
    def audio_callback(self, indata, frames, time_info, status):
        """Audio callback with frequency analysis"""
        if self.is_listening:
            # Get amplitude
            amplitude = int(np.abs(indata).mean() * 10000)
            
            # Check if this sounds like a Morse beep (pure tone)
            is_pure_tone = self.is_morse_tone(indata.flatten())
            
            self.audio_queue.put(('data', amplitude, is_pure_tone))
    
    def is_morse_tone(self, audio_data):
        """Check if audio contains a pure tone in Morse frequency range"""
        # Simple frequency detection using FFT
        fft = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1/self.sample_rate)
        magnitudes = np.abs(fft)
        
        # Find dominant frequency (ignore DC)
        if len(magnitudes) > 10:
            dominant_idx = np.argmax(magnitudes[10:]) + 10
            dominant_freq = freqs[dominant_idx]
            
            # Check if in Morse range
            return self.min_freq <= dominant_freq <= self.max_freq
        
        return False
    
    def process_audio(self):
        """Process audio"""
        is_sound = False
        
        while self.is_listening:
            try:
                item = self.audio_queue.get(timeout=0.05)
                if item[0] == 'data':
                    _, amplitude, is_tone = item
                    
                    # Update meter
                    if self.on_amplitude:
                        self.on_amplitude(amplitude)
                    
                    # ONLY detect if it's a pure tone (Morse beep)
                    if is_tone and amplitude > self.threshold:
                        if not is_sound:
                            is_sound = True
                            self.sound_start = time.time()
                    else:
                        if is_sound:
                            is_sound = False
                            duration = time.time() - self.sound_start
                            self.process_beep(duration)
                            self.silence_start = time.time()
                        elif self.silence_start > 0:
                            silence = time.time() - self.silence_start
                            self.process_pause(silence)
                            
            except queue.Empty:
                pass
    
    def process_beep(self, duration):
        """Process beep"""
        if self.min_dit_duration <= duration <= self.max_dit_duration:
            symbol = '.'
        elif self.min_dah_duration <= duration <= self.max_dah_duration:
            symbol = '-'
        else:
            return
        
        self.current_letter.append(symbol)
        
        if self.on_morse_symbol:
            self.on_morse_symbol(symbol)
        
        print(f"✓ Beep: {symbol} ({duration:.2f}s)")
    
    def process_pause(self, duration):
        """Process pause"""
        if not self.current_letter and not self.current_word:
            return
        
        if duration > self.word_pause:
            if self.current_letter:
                self.complete_letter()
            if self.current_word:
                self.complete_word()
            self.silence_start = 0
        elif duration > self.letter_pause:
            if self.current_letter:
                self.complete_letter()
    
    def complete_letter(self):
        """Complete letter"""
        if self.current_letter:
            morse = ''.join(self.current_letter)
            letter = self.morse_map.get(morse, '?')
            self.current_word.append(letter)
            
            if self.on_letter:
                self.on_letter(letter, morse)
            
            print(f"  → Letter: {letter} = {morse}")
            self.current_letter = []
    
    def complete_word(self):
        """Complete word"""
        if self.current_word:
            word = ''.join(self.current_word)
            
            if self.on_word:
                self.on_word(word)
            
            print(f"  📝 Word: {word}")
            self.current_word = []
    
    def set_sensitivity(self, percent):
        """Set sensitivity"""
        self.threshold = int(100 + (percent / 100) * 1900)
