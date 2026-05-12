"""
Live Microphone Morse Code Detector - FIXED for Razer Seiren Mini
"""

import threading
import queue
import time
import numpy as np

# Try multiple audio backends
AUDIO_BACKEND = None
DEVICE_ID = None

# Try sounddevice first
try:
    import sounddevice as sd
    AUDIO_BACKEND = 'sounddevice'
    
    # Find Razer Seiren Mini
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if 'Razer Seiren' in device['name'] or 'Seiren Mini' in device['name']:
            DEVICE_ID = i
            print(f"✓ Found Razer Seiren Mini at device {i}")
            break
    
    if DEVICE_ID is None:
        # Fallback to first input device
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                DEVICE_ID = i
                print(f"✓ Using default input device {i}: {device['name']}")
                break
                
except ImportError:
    pass

# Try pyaudio as fallback
if AUDIO_BACKEND is None:
    try:
        import pyaudio
        AUDIO_BACKEND = 'pyaudio'
        print("✓ Using pyaudio for microphone")
    except ImportError:
        pass

if AUDIO_BACKEND is None:
    print("⚠️ No audio backend available. Install: pip install sounddevice")

class MicrophoneListener:
    def __init__(self):
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.morse_buffer = []
        self.current_letter = []
        self.silence_threshold = 300  # Lower threshold for Razer mic
        self.min_dit_duration = 0.06  # 60ms - faster detection
        self.max_dah_duration = 0.35  # 350ms
        self.sample_rate = 44100  # Higher quality for Razer
        self.chunk_size = 2048
        self.last_sound_time = 0
        self.silence_start = 0
        self.current_amplitude = 0
        self.last_detected_text = ""
        
        # Callbacks
        self.on_morse_detected = None
        self.on_text_detected = None
        self.on_amplitude_update = None
        
        # Audio stream
        self.stream = None
        
        # Morse code mapping for common letters (for real-time)
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
        
    def start_listening(self, morse_engine, language="english"):
        """Start listening to microphone"""
        if AUDIO_BACKEND is None:
            print("No audio backend available")
            return False
        
        self.is_listening = True
        self.morse_engine = morse_engine
        self.current_language = language
        self.morse_buffer = []
        self.current_letter = []
        self.last_detected_text = ""
        
        try:
            if AUDIO_BACKEND == 'sounddevice':
                self._start_sounddevice()
            elif AUDIO_BACKEND == 'pyaudio':
                self._start_pyaudio()
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self.process_audio, daemon=True)
            self.processing_thread.start()
            
            print(f"✓ Microphone listening started on device {DEVICE_ID}")
            return True
            
        except Exception as e:
            print(f"Failed to start microphone: {e}")
            self.is_listening = False
            return False
    
    def _start_sounddevice(self):
        """Start sounddevice stream with Razer mic"""
        try:
            self.stream = sd.InputStream(
                callback=self.audio_callback_sd,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=DEVICE_ID  # Force use Razer mic
            )
            self.stream.start()
            print(f"✓ Sounddevice stream started on device {DEVICE_ID}")
        except Exception as e:
            print(f"Error starting stream: {e}")
            # Fallback to default device
            self.stream = sd.InputStream(
                callback=self.audio_callback_sd,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size
            )
            self.stream.start()
    
    def _start_pyaudio(self):
        """Start pyaudio stream"""
        self.p = pyaudio.PyAudio()
        
        # Find Razer Seiren Mini in pyaudio
        device_index = None
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if 'Razer' in info['name'] or 'Seiren' in info['name']:
                if info['maxInputChannels'] > 0:
                    device_index = i
                    print(f"✓ Found Razer mic in pyaudio: {info['name']}")
                    break
        
        if device_index is None:
            # Use default input device
            device_index = self.p.get_default_input_device_info()['index']
        
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.audio_callback_pa
        )
        self.stream.start_stream()
    
    def audio_callback_sd(self, indata, frames, time_info, status):
        """Callback for sounddevice"""
        if status:
            # Don't print status to avoid clutter
            pass
        if self.is_listening:
            # Convert to amplitude (absolute mean)
            amplitude = int(np.abs(indata).mean() * 10000)
            self.audio_queue.put(('data', indata.copy(), amplitude))
    
    def audio_callback_pa(self, in_data, frame_count, time_info, status):
        """Callback for pyaudio"""
        if self.is_listening:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            amplitude = int(np.abs(audio_data).mean())
            self.audio_queue.put(('data', audio_data, amplitude))
        return (in_data, pyaudio.paContinue)
    
    def stop_listening(self):
        """Stop listening to microphone"""
        self.is_listening = False
        
        if self.stream:
            if AUDIO_BACKEND == 'sounddevice':
                self.stream.stop()
                self.stream.close()
            elif AUDIO_BACKEND == 'pyaudio':
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
        
        self.stream = None
        print("✓ Microphone stopped")
    
    def process_audio(self):
        """Process audio chunks and detect Morse"""
        last_amplitude_time = time.time()
        
        while self.is_listening:
            try:
                item = self.audio_queue.get(timeout=0.05)
                if item[0] == 'data':
                    _, audio_chunk, amplitude = item
                    self.detect_morse(amplitude, audio_chunk)
                    last_amplitude_time = time.time()
            except queue.Empty:
                # Check for timeout silence (end of word)
                if time.time() - last_amplitude_time > 0.8:
                    if self.current_letter:
                        self.complete_letter()
                    if self.morse_buffer:
                        self.complete_word()
                continue
    
    def detect_morse(self, amplitude, audio_chunk):
        """Detect Morse code from amplitude"""
        self.current_amplitude = amplitude
        
        # Update amplitude callback for visualization
        if self.on_amplitude_update:
            self.on_amplitude_update(amplitude)
        
        # Check if sound is detected (adjust threshold based on your mic)
        if amplitude > self.silence_threshold:
            # Sound detected
            if self.last_sound_time == 0:
                # Start of a new sound
                self.last_sound_time = time.time()
                self.silence_start = 0
        else:
            # Silence detected
            if self.last_sound_time > 0:
                # Sound just ended - measure duration
                sound_duration = time.time() - self.last_sound_time
                self.identify_morse_symbol(sound_duration)
                self.last_sound_time = 0
                self.silence_start = time.time()
            elif self.silence_start > 0:
                # Check for end of letter (medium pause)
                silence_duration = time.time() - self.silence_start
                if silence_duration > 0.25 and self.current_letter:  # 250ms pause = letter space
                    self.complete_letter()
                    self.silence_start = time.time()
    
    def identify_morse_symbol(self, duration):
        """Identify if sound is dit or dah"""
        if duration < self.min_dit_duration:
            return  # Too short, ignore noise
        
        if duration < self.max_dah_duration:
            # Dit (short beep)
            symbol = '.'
        else:
            # Dah (long beep)
            symbol = '-'
        
        self.current_letter.append(symbol)
        
        if self.on_morse_detected:
            self.on_morse_detected(symbol)
    
    def complete_letter(self):
        """Complete current letter and add to buffer"""
        if self.current_letter:
            morse_letter = ''.join(self.current_letter)
            self.morse_buffer.append(morse_letter)
            
            # Try to translate immediately
            if morse_letter in self.morse_map:
                letter = self.morse_map[morse_letter]
                if self.on_text_detected:
                    self.on_text_detected(letter)
                print(f"✓ Detected: {letter} ({morse_letter})")
            
            self.current_letter = []
    
    def complete_word(self):
        """Complete current word and translate full"""
        if self.morse_buffer:
            # Translate full word
            morse_string = ' '.join(self.morse_buffer)
            try:
                text = self.morse_engine.morse_to_text(morse_string, self.current_language)
                if text and text != self.last_detected_text:
                    self.last_detected_text = text
                    if self.on_text_detected:
                        self.on_text_detected(' ' + text + ' ')
                    print(f"✓ Word detected: {text}")
            except Exception as e:
                print(f"Translation error: {e}")
            
            # Clear buffer for next word
            self.morse_buffer = []
    
    def set_sensitivity(self, threshold):
        """Adjust microphone sensitivity (50 to 2000)"""
        # Convert from 0-1 range to actual threshold
        self.silence_threshold = int(50 + (threshold * 1950))
        print(f"✓ Sensitivity set to {self.silence_threshold}")
    
    def get_status(self):
        """Get current listening status"""
        return {
            'listening': self.is_listening,
            'backend': AUDIO_BACKEND,
            'device_id': DEVICE_ID,
            'buffer_length': len(self.morse_buffer),
            'current_letter': ''.join(self.current_letter) if self.current_letter else '',
            'amplitude': self.current_amplitude,
            'threshold': self.silence_threshold
        }
