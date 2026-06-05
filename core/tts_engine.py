import pyttsx3
import threading
from typing import Dict

class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.is_speaking = False
        self.current_language = "en"
        
        # Language codes mapping
        self.languages = {
            "english": "en",
            "persian": "fa",  # Requires separate voice pack
            "german": "de",
            "turkish": "tr"
        }
        
        self.available_voices = self._get_available_voices()
    
    def _get_available_voices(self) -> Dict:
        """Get available TTS voices"""
        voices = {}
        for voice in self.engine.getProperty('voices'):
            voices[voice.id] = voice.name
        return voices
    
    def set_language(self, language: str):
        """Set TTS language"""
        lang_code = self.languages.get(language.lower(), "en")
        
        # Try to find matching voice
        for voice_id, voice_name in self.available_voices.items():
            if lang_code in voice_name.lower() or lang_code in voice_id:
                self.engine.setProperty('voice', voice_id)
                self.current_language = lang_code
                return True
        
        # Fallback to default
        print(f"Warning: No voice found for {language}, using default")
        return False
    
    def speak(self, text: str, callback=None):
        """Speak text asynchronously"""
        def _speak():
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
            if callback:
                callback()
        
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop speaking"""
        self.engine.stop()
        self.is_speaking = False
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
    
    def get_available_languages(self) -> list:
        """Get list of languages with installed voices"""
        installed = []
        for lang, code in self.languages.items():
            for voice_id, voice_name in self.available_voices.items():
                if code in voice_name.lower() or code in voice_id:
                    installed.append(lang)
                    break
        return installed