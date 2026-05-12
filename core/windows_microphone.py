"""Use Windows built-in speech recognition as fallback"""
import subprocess
import threading
import time

class WindowsMicListener:
    def __init__(self):
        self.is_listening = False
        self.on_text_detected = None
    
    def start_listening(self, morse_engine, language="english"):
        """Start Windows speech recognition"""
        self.is_listening = True
        self.morse_engine = morse_engine
        
        def listen():
            while self.is_listening:
                try:
                    # Use Windows built-in dictation
                    import speech_recognition as sr
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source)
                        audio = r.listen(source, timeout=3)
                        
                    text = r.recognize_google(audio)
                    if self.on_text_detected:
                        self.on_text_detected(text)
                except:
                    pass
                time.sleep(0.1)
        
        threading.Thread(target=listen, daemon=True).start()
        return True
    
    def stop_listening(self):
        self.is_listening = False
