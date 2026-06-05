"""
Advanced Morse Code Detector with Push-to-Talk and Voice Filtering
"""

import threading
import queue
import time
import numpy as np

try:
    import sounddevice as sd
    AUDIO_BACKEND = 'sounddevice'
except ImportError:
    AUDIO_BACKEND = None

class MorseDetectorV2:
    def __init__(self):
        self.is_listening = False
        self.is_recording = False  # Push-to-talk state
        self.audio_queue = queue.Queue()
        
        # Detection parameters (optimized for Morse beeps)
        self.beep_detection_mode = True  # True = only detect beeps, False = voice speech
        self.min_frequency = 600  # Morse beeps are typically 600-1000 Hz
        self.max_frequency = 1200
        self.silence_threshold = 800  # Higher threshold for beep detection
        self.min_beep_duration = 0.04  # 40ms minimum beep
        self.max_beep_duration = 0.5   # 500ms maximum beep
        self.sample_rate = 44100
        self.chunk_size = 2048
        
        # State tracking
        self.current_morse = []
        self.current_letter = []
        self.last_beep_time = 0
        self.silence_start = 0
        self.current_amplitude = 0
        
        # Callbacks
        self.on_morse_symbol = None  # Called for each . or -
        self.on_letter = None        # Called when a letter is completed
        self.on_word = None          # Called when a word is completed
        self.on_amplitude = None
        
        # Morse mapping for real-time translation
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
        
        # Morse audio generator (for testing)
        self.morse_audio = None
        
        # Find Razer mic
        self.device_id = None
        if AUDIO_BACKEND:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if 'Razer' in device['name'] or 'Seiren' in device['name']:
                    if device['max_input_channels'] > 0:
                        self.device_id = i
                        print(f"✓ Using Razer mic at device {i}")
                        break
    
    def start_listening(self, mode='beep'):
        """
        Start listening with specified mode:
        - 'beep': Only detects intentional Morse beeps (use with tone generator)
        - 'tap': Detects tapping on desk/mic (practice mode)
        - 'spacebar': Spacebar as Morse key (easiest for learning)
        """
        if not AUDIO_BACKEND:
            print("No audio backend available")
            return False
        
        self.is_listening = True
        self.mode = mode
        
        if mode == 'spacebar':
            # Use keyboard instead of mic
            self._start_keyboard_mode()
        else:
            self._start_microphone_mode()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
        self.processing_thread.start()
        
        return True
    
    def _start_microphone_mode(self):
        """Start microphone stream"""
        try:
            self.stream = sd.InputStream(
                callback=self.audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=self.device_id
            )
            self.stream.start()
            print(f"✓ Microphone started in {self.mode} mode")
        except Exception as e:
            print(f"Error starting mic: {e}")
    
    def _start_keyboard_mode(self):
        """Use keyboard spacebar as Morse key"""
        try:
            import keyboard
            self.keyboard_listener = keyboard.threaded.Listener(
                on_press=self.key_pressed,
                on_release=self.key_released
            )
            self.keyboard_listener.start()
            print("✓ Keyboard mode started - Press SPACEBAR for dits/dahs")
            print("  Short press = . (dit) | Long press = - (dah)")
        except ImportError:
            print("Install keyboard module: pip install keyboard")
    
    def key_pressed(self, e):
        """Handle key press for keyboard mode"""
        if e.name == 'space' and not self.is_recording:
            self.is_recording = True
            self.key_press_time = time.time()
    
    def key_released(self, e):
        """Handle key release for keyboard mode"""
        if e.name == 'space' and self.is_recording:
            self.is_recording = False
            duration = time.time() - self.key_press_time
            
            if duration < 0.2:
                self.on_beep_detected('.', 0.1)
            else:
                self.on_beep_detected('-', 0.3)
    
    def audio_callback(self, indata, frames, time_info, status):
        """Audio callback for microphone"""
        if self.is_listening:
            amplitude = int(np.abs(indata).mean() * 10000)
            self.audio_queue.put(('data', indata.copy(), amplitude))
    
    def process_audio(self):
        """Process audio and detect beeps"""
        is_sound = False
        sound_start_time = 0
        
        while self.is_listening:
            try:
                item = self.audio_queue.get(timeout=0.05)
                if item[0] == 'data':
                    _, audio_chunk, amplitude = item
                    self.current_amplitude = amplitude
                    
                    if self.on_amplitude:
                        self.on_amplitude(amplitude)
                    
                    # Detect if this is a intentional beep (high frequency)
                    is_beep = self._is_intentional_beep(audio_chunk, amplitude)
                    
                    if is_beep and not is_sound:
                        # Sound started
                        is_sound = True
                        sound_start_time = time.time()
                    elif not is_beep and is_sound:
                        # Sound ended
                        is_sound = False
                        duration = time.time() - sound_start_time
                        self.on_beep_detected(self._duration_to_symbol(duration), duration)
                        
            except queue.Empty:
                # Check for silence timeout (end of letter/word)
                if not is_sound and self.current_letter and (time.time() - sound_start_time) > 0.3:
                    self.complete_letter()
    
    def _is_intentional_beep(self, audio_chunk, amplitude):
        """Check if sound is an intentional Morse beep"""
        if self.mode == 'tap':
            # Tapping mode - detect impact sounds
            return amplitude > self.silence_threshold * 2
        
        elif self.mode == 'beep':
            # Beep mode - check frequency content
            if amplitude < self.silence_threshold:
                return False
            
            # Analyze frequency spectrum
            fft = np.fft.rfft(audio_chunk.flatten())
            freqs = np.fft.rfftfreq(len(audio_chunk), 1/self.sample_rate)
            magnitudes = np.abs(fft)
            
            # Find dominant frequency
            if len(magnitudes) > 0:
                dominant_freq = freqs[np.argmax(magnitudes[10:]) + 10]
                is_target_freq = self.min_frequency < dominant_freq < self.max_frequency
                return is_target_freq and amplitude > self.silence_threshold
        
        return amplitude > self.silence_threshold
    
    def _duration_to_symbol(self, duration):
        """Convert beep duration to Morse symbol"""
        if duration < self.max_beep_duration * 0.6:
            return '.'
        else:
            return '-'
    
    def on_beep_detected(self, symbol, duration):
        """Handle detected beep"""
        self.current_letter.append(symbol)
        
        if self.on_morse_symbol:
            self.on_morse_symbol(symbol)
        
        print(f"✓ Detected: {symbol} ({duration:.2f}s)")
    
    def complete_letter(self):
        """Complete current letter"""
        if self.current_letter:
            morse = ''.join(self.current_letter)
            self.current_morse.append(morse)
            
            # Translate letter
            if morse in self.morse_map:
                letter = self.morse_map[morse]
                if self.on_letter:
                    self.on_letter(letter, morse)
                print(f"  → Letter: {letter} = {morse}")
            else:
                print(f"  → Unknown: {morse}")
            
            self.current_letter = []
            self.last_letter_time = time.time()
        else:
            # Check for word completion
            if self.current_morse and (time.time() - getattr(self, 'last_letter_time', 0)) > 0.5:
                self.complete_word()
    
    def complete_word(self):
        """Complete current word"""
        if self.current_morse:
            word_morse = ' '.join(self.current_morse)
            word_text = ''.join([self.morse_map.get(m, '?') for m in self.current_morse])
            
            if self.on_word:
                self.on_word(word_text, word_morse)
            
            print(f"  📝 Word: {word_text} = {word_morse}")
            self.current_morse = []
    
    def set_sensitivity(self, value):
        """Set detection sensitivity (0-100)"""
        # Convert 0-100 to 200-2000 threshold
        self.silence_threshold = int(200 + (value / 100) * 1800)
        print(f"✓ Sensitivity: {value}% (threshold: {self.silence_threshold})")
    
    def set_frequency_range(self, min_freq, max_freq):
        """Set frequency range for beep detection"""
        self.min_frequency = min_freq
        self.max_frequency = max_freq
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()