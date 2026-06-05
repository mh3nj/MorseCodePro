"""
Advanced Features Panel - Microphone, File Import, Visualization
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path

class AdvancedFeaturesPanel(ctk.CTkFrame):
    def __init__(self, parent, morse_engine, audio_player, on_text_detected=None):
        super().__init__(parent, corner_radius=15, border_width=1, border_color="#333333")
        
        self.morse_engine = morse_engine
        self.audio_player = audio_player
        self.on_text_detected = on_text_detected
        
        # Initialize components
        self.detector = None
        self.audio_processor = None
        self.is_listening = False
        self.detector_mode = "spacebar"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup advanced features UI"""
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="🎙️ ADVANCED FEATURES", 
            font=("Arial", 18, "bold"),
            text_color="#00d9ff"
        )
        title.pack(pady=10)
        
        # ===== MICROPHONE SECTION =====
        mic_frame = ctk.CTkFrame(self, corner_radius=10)
        mic_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(mic_frame, text="🎤 Live Microphone", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Mode selection
        mode_frame = ctk.CTkFrame(mic_frame, fg_color="transparent")
        mode_frame.pack(pady=5)
        
        ctk.CTkLabel(mode_frame, text="Mode:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.mode_var = ctk.StringVar(value="⌨️ Keyboard Mode")
        mode_options = ctk.CTkOptionMenu(
            mode_frame,
            values=["⌨️ Keyboard Mode", "🎤 Mic Mode"],
            variable=self.mode_var,
            command=self.change_mode,
            width=150
        )
        mode_options.pack(side="left", padx=5)
        
        # Help text
        self.mode_help = ctk.CTkLabel(
            mic_frame,
            text="💡 Keyboard Mode: Press SPACEBAR (short=. , long=-)",
            font=("Arial", 10),
            text_color="#888888"
        )
        self.mode_help.pack(pady=5)
        
        # Mic button
        self.mic_btn = ctk.CTkButton(
            mic_frame,
            text="🎙️ Start Listening",
            command=self.toggle_microphone,
            width=200,
            height=40,
            fg_color="#00d9ff",
            text_color="black",
            font=("Arial", 13, "bold")
        )
        self.mic_btn.pack(pady=10)
        
        # Status
        self.mic_status = ctk.CTkLabel(mic_frame, text="⚪ Not listening", font=("Arial", 11), text_color="#888888")
        self.mic_status.pack(pady=5)
        
        # Test area
        test_frame = ctk.CTkFrame(mic_frame, fg_color="transparent")
        test_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(test_frame, text="Test Morse:", font=("Arial", 11)).pack()
        
        test_buttons = ctk.CTkFrame(test_frame, fg_color="transparent")
        test_buttons.pack(pady=5)
        
        ctk.CTkButton(test_buttons, text="S (...)", command=lambda: self.send_test_morse("..."), width=60).pack(side="left", padx=2)
        ctk.CTkButton(test_buttons, text="O (---)", command=lambda: self.send_test_morse("---"), width=60).pack(side="left", padx=2)
        ctk.CTkButton(test_buttons, text="SOS", command=lambda: self.send_test_morse("... --- ..."), width=60).pack(side="left", padx=2)
        
        # ===== AUDIO FILE IMPORT =====
        file_frame = ctk.CTkFrame(self, corner_radius=10)
        file_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(file_frame, text="📁 Import Audio File", font=("Arial", 16, "bold")).pack(pady=5)
        
        self.file_btn = ctk.CTkButton(
            file_frame,
            text="📂 Choose Audio File",
            command=self.import_audio_file,
            width=200,
            height=40,
            fg_color="#2b5b84"
        )
        self.file_btn.pack(pady=5)
        
        self.file_status = ctk.CTkLabel(file_frame, text="No file loaded", font=("Arial", 10), text_color="#888888")
        self.file_status.pack()
    
    def change_mode(self, choice):
        """Change detection mode"""
        if "Keyboard" in choice:
            self.detector_mode = "spacebar"
            self.mode_help.configure(text="💡 Press SPACEBAR: quick tap = . (dit), hold = - (dah)")
        else:
            self.detector_mode = "mic"
            self.mode_help.configure(text="💡 Speak into mic: short beep = ., long beep = -")
        
        if self.is_listening:
            self.stop_listening()
            self.start_listening()
    
    def start_listening(self):
        """Start listening"""
        if self.detector_mode == "spacebar":
            try:
                import keyboard
                self.keyboard_active = True
                keyboard.on_press_key('space', self.on_key_press)
                keyboard.on_release_key('space', self.on_key_release)
                
                self.is_listening = True
                self.mic_btn.configure(text="🛑 Stop Listening", fg_color="#aa3333")
                self.mic_status.configure(text="🔴 Listening - Press SPACEBAR!", text_color="#ff4444")
                return True
            except ImportError:
                messagebox.showerror("Error", "Install keyboard: pip install keyboard")
                return False
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")
                return False
        else:
            messagebox.showinfo("Info", "Mic mode coming soon. Use Keyboard mode for now.")
            return False
    
    def on_key_press(self, e):
        """Handle spacebar press"""
        self.key_press_time = time.time()
    
    def on_key_release(self, e):
        """Handle spacebar release"""
        duration = time.time() - self.key_press_time
        
        if duration < 0.2:
            symbol = '.'
            letter = 'E'
        else:
            symbol = '-'
            letter = 'T'
        
        self.mic_status.configure(text=f"🔴 {symbol} ({letter})", text_color="#00ff00")
        
        if self.on_text_detected:
            self.on_text_detected(letter)
        
        # Reset status after 1 second
        self.after(1000, lambda: self.mic_status.configure(
            text="🔴 Listening - Press SPACEBAR!", text_color="#ff4444"
        ))
    
    def send_test_morse(self, morse):
        """Send test Morse code"""
        morse_map = {'.': 'E', '-': 'T', '...': 'S', '---': 'O'}
        
        # Simple translation
        if morse == "...":
            text = "S"
        elif morse == "---":
            text = "O"
        elif morse == "... --- ...":
            text = "SOS"
        else:
            text = morse_map.get(morse, "?")
        
        if self.on_text_detected:
            self.on_text_detected(text)
        
        self.mic_status.configure(text=f"📢 Test: {morse} = {text}", text_color="#00d9ff")
        self.after(2000, lambda: self.mic_status.configure(
            text="🔴 Listening" if self.is_listening else "⚪ Not listening", 
            text_color="#ff4444" if self.is_listening else "#888888"
        ))
    
    def stop_listening(self):
        """Stop listening"""
        if self.detector_mode == "spacebar":
            try:
                import keyboard
                keyboard.unhook_all()
            except:
                pass
        
        self.is_listening = False
        self.mic_btn.configure(text="🎙️ Start Listening", fg_color="#00d9ff")
        self.mic_status.configure(text="⚪ Not listening", text_color="#888888")
    
    def toggle_microphone(self):
        """Toggle listening"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def import_audio_file(self):
        """Import audio file"""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.wav *.mp3 *.opus"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_status.configure(text=f"Loaded: {Path(file_path).name}")
            messagebox.showinfo("File Loaded", f"Loaded: {Path(file_path).name}\n\nProcessing audio files coming soon!")

# Need time module
import time