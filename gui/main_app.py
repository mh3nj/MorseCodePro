"""
Morse Code Professional Suite - Complete Main Application
Includes: Translation, Word Breakdown, Learning, History, Audio, Microphone, Metronome, Favorites
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pathlib import Path
import sys
import os

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.morse_engine import MorseEngine
from models.history_db import HistoryDB

# Import GUI components
from gui.word_breakdown import WordBreakdownPanel
from gui.teaching_panel import TeachingPanel
from gui.history_panel import HistoryPanel
from gui.microphone_panel import MicrophonePanel
from gui.favorites_panel import FavoritesPanel
from gui.export_dialog import ExportDialog
from config.settings_manager import SettingsManager

class MorseCodeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🎯 Morse Code Professional Suite v2.0")
        self.geometry("1400x800")
        
        # Set minimum window size
        self.minsize(1200, 700)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize engines
        self.morse_engine = MorseEngine()
        self.current_language = "english"
        
        # Initialize settings
        try:
            self.settings = SettingsManager()
            self.current_language = self.settings.get('last_language', 'english')
        except:
            self.settings = None
        
        # Initialize history database
        try:
            self.history_db = HistoryDB()
        except Exception as e:
            print(f"History DB error: {e}")
            self.history_db = None
        
        # Try to initialize audio
        self.audio_player = None
        try:
            from core.audio_player_fixed import AudioPlayer
            self.audio_player = AudioPlayer()
        except ImportError:
            pass
        
        # Setup UI
        self.setup_ui()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Save current text/morse for favorites
        self.current_text = ""
        self.current_morse = ""
        
    def setup_ui(self):
        # Main container with padding
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        # ========== TITLE BAR ==========
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            title_frame,
            text="📡 MORSE CODE PROFESSIONAL SUITE",
            font=("Arial", 32, "bold"),
            text_color="#00d9ff"
        )
        title.grid(row=0, column=0, pady=10)
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Convert | Learn | Practice | Master | Transcribe",
            font=("Arial", 14),
            text_color="#888888"
        )
        subtitle.grid(row=1, column=0)
        
        # ========== TOP BAR (Controls) ==========
        top_bar = ctk.CTkFrame(main_frame, fg_color="transparent", height=50)
        top_bar.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        top_bar.grid_columnconfigure(0, weight=1)
        
        # Left side - Language selector
        lang_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        lang_frame.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(lang_frame, text="🌐 Language:", font=("Arial", 14)).pack(side="left", padx=5)
        
        self.lang_var = ctk.StringVar(value=self.current_language)
        self.lang_menu = ctk.CTkOptionMenu(
            lang_frame,
            values=["english", "persian", "german", "turkish", "spanish", "french"],
            variable=self.lang_var,
            command=self.change_language,
            width=150,
            height=35,
            font=("Arial", 13)
        )
        self.lang_menu.pack(side="left", padx=10)
        
        # Center - Stats
        stats_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        stats_frame.grid(row=0, column=0, columnspan=3)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="📊 Ready",
            font=("Arial", 12),
            text_color="#888888"
        )
        self.stats_label.pack()
        
        # Right side - Theme toggle and shortcuts
        controls_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        controls_frame.grid(row=0, column=2, sticky="e")
        
        self.theme_btn = ctk.CTkButton(
            controls_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            width=120,
            height=35,
            font=("Arial", 12)
        )
        self.theme_btn.pack(side="left", padx=5)
        
        shortcuts_btn = ctk.CTkButton(
            controls_frame,
            text="⌨️ Shortcuts",
            command=self.show_shortcuts,
            width=100,
            height=35,
            font=("Arial", 12),
            fg_color="#2b5b84"
        )
        shortcuts_btn.pack(side="left", padx=5)
        
        # ========== MAIN CONTENT (Two Columns) ==========
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # ========== LEFT PANEL - INPUT ==========
        left_panel = ctk.CTkFrame(content, corner_radius=15, border_width=1, border_color="#333333")
        left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Left panel header
        left_header = ctk.CTkFrame(left_panel, fg_color="transparent", height=40)
        left_header.pack(fill="x", padx=15, pady=(10, 0))
        
        ctk.CTkLabel(left_header, text="📝 INPUT", font=("Arial", 18, "bold")).pack(side="left")
        
        # Quick example button
        example_btn = ctk.CTkButton(
            left_header,
            text="Example",
            command=self.load_example,
            width=80,
            height=28,
            font=("Arial", 11),
            fg_color="#2b5b84"
        )
        example_btn.pack(side="right")
        
        # Tab view for input types
        self.input_tabview = ctk.CTkTabview(left_panel, height=400)
        self.input_tabview.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Text to Morse tab
        text_tab = self.input_tabview.add("✏️ Text → Morse")
        self.text_input = ctk.CTkTextbox(
            text_tab,
            font=("Arial", 14),
            wrap="word",
            border_width=1,
            border_color="#444444"
        )
        self.text_input.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_input.insert("1.0", "Type or paste your text here...")
        self.text_input.bind("<FocusIn>", lambda e: self.clear_placeholder(self.text_input, "Type or paste your text here..."))
        
        # Morse to Text tab
        morse_tab = self.input_tabview.add("🔊 Morse → Text")
        self.morse_input = ctk.CTkTextbox(
            morse_tab,
            font=("Courier", 14),
            wrap="word",
            border_width=1,
            border_color="#444444"
        )
        self.morse_input.pack(fill="both", expand=True, padx=10, pady=10)
        self.morse_input.insert("1.0", "Enter Morse code (use . for dit, - for dah, space between letters, / between words)...")
        self.morse_input.bind("<FocusIn>", lambda e: self.clear_placeholder(self.morse_input, "Enter Morse code..."))
        
        # Convert button
        self.convert_btn = ctk.CTkButton(
            left_panel,
            text="🔄 CONVERT →",
            command=self.convert,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="#00d9ff",
            hover_color="#0088aa",
            text_color="black",
            corner_radius=10
        )
        self.convert_btn.pack(pady=(0, 15), padx=15, fill="x")
        
        # ========== RIGHT PANEL - OUTPUT (with Tabs) ==========
        right_panel = ctk.CTkFrame(content, corner_radius=15, border_width=1, border_color="#333333")
        right_panel.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        # Tabview for output sections
        self.output_tabview = ctk.CTkTabview(right_panel)
        self.output_tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Translation Output
        output_tab = self.output_tabview.add("📤 Translation")
        
        # Output text area
        self.output_text = ctk.CTkTextbox(
            output_tab,
            font=("Arial", 14),
            wrap="word",
            border_width=1,
            border_color="#444444"
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Output control buttons
        output_btn_frame = ctk.CTkFrame(output_tab, fg_color="transparent")
        output_btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.speak_btn = ctk.CTkButton(
            output_btn_frame,
            text="🔊 Speak Output",
            command=self.speak_output,
            width=120,
            height=35
        )
        self.speak_btn.pack(side="left", padx=5)
        
        self.play_btn = ctk.CTkButton(
            output_btn_frame,
            text="🎵 Play Morse",
            command=self.play_morse,
            width=120,
            height=35
        )
        self.play_btn.pack(side="left", padx=5)
        
        self.copy_btn = ctk.CTkButton(
            output_btn_frame,
            text="📋 Copy",
            command=self.copy_output,
            width=100,
            height=35,
            fg_color="#2b5b84"
        )
        self.copy_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(
            output_btn_frame,
            text="💾 Export",
            command=self.export_output,
            width=100,
            height=35,
            fg_color="#2b5b84"
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.clear_btn = ctk.CTkButton(
            output_btn_frame,
            text="🗑 Clear All",
            command=self.clear_all,
            width=100,
            height=35,
            fg_color="#aa3333",
            hover_color="#ff4444"
        )
        self.clear_btn.pack(side="right", padx=5)
        
        # Speed control frame
        if self.audio_player:
            speed_frame = ctk.CTkFrame(output_tab, fg_color="transparent")
            speed_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            ctk.CTkLabel(speed_frame, text="⚡ Playback Speed:", font=("Arial", 12)).pack(side="left", padx=5)
            
            self.speed_var = ctk.DoubleVar(value=1.0)
            self.speed_slider = ctk.CTkSlider(
                speed_frame,
                from_=0.5,
                to=3.0,
                variable=self.speed_var,
                command=self.update_speed,
                width=200,
                height=20
            )
            self.speed_slider.pack(side="left", padx=10)
            
            self.speed_label = ctk.CTkLabel(speed_frame, text="1.0x", font=("Arial", 12, "bold"), text_color="#00d9ff")
            self.speed_label.pack(side="left", padx=5)
            
            # Speed preset buttons
            ctk.CTkButton(speed_frame, text="0.5x", command=lambda: self.set_speed(0.5), width=40, height=25, font=("Arial", 10)).pack(side="left", padx=2)
            ctk.CTkButton(speed_frame, text="1.0x", command=lambda: self.set_speed(1.0), width=40, height=25, font=("Arial", 10)).pack(side="left", padx=2)
            ctk.CTkButton(speed_frame, text="2.0x", command=lambda: self.set_speed(2.0), width=40, height=25, font=("Arial", 10)).pack(side="left", padx=2)
        
        # Tab 2: Word Breakdown
        breakdown_tab = self.output_tabview.add("🔍 Word Breakdown")
        self.word_breakdown = WordBreakdownPanel(breakdown_tab, self.morse_engine)
        self.word_breakdown.pack(fill="both", expand=True)
        
        # Tab 3: Learning Section
        learning_tab = self.output_tabview.add("📚 Learn Morse")
        self.teaching = TeachingPanel(learning_tab, self.morse_engine)
        self.teaching.pack(fill="both", expand=True)
        
        # Tab 4: History
        history_tab = self.output_tabview.add("📜 History")
        self.history_panel = HistoryPanel(history_tab)
        self.history_panel.pack(fill="both", expand=True)
        
        # Tab 5: Microphone
        mic_tab = self.output_tabview.add("🎤 Microphone")
        self.mic_panel = MicrophonePanel(mic_tab, self.insert_mic_text)
        self.mic_panel.pack(fill="both", expand=True)
        
        # Tab 6: Favorites
        favorites_tab = self.output_tabview.add("⭐ Favorites")
        self.favorites_panel = FavoritesPanel(favorites_tab, self.load_favorite)
        self.favorites_panel.pack(fill="both", expand=True)
        
        # ========== STATUS BAR ==========
        status_bar = ctk.CTkFrame(main_frame, height=35, corner_radius=10)
        status_bar.grid(row=3, column=0, pady=(15, 0), sticky="ew")
        status_bar.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_bar,
            text="✅ Ready | Language: English | Press Ctrl+H for shortcuts",
            font=("Arial", 11),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=15)
        
        # Progress indicator
        self.progress_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=("Arial", 11),
            text_color="#00d9ff"
        )
        self.progress_label.pack(side="right", padx=15)
        
        # Initial update
        self.update_stats()
    
    def clear_placeholder(self, widget, placeholder_text):
        """Clear placeholder text on focus"""
        if widget.get("1.0", "end-1c") == placeholder_text:
            widget.delete("1.0", "end")
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind("<Control-Return>", lambda e: self.convert())
        self.bind("<Control-s>", lambda e: self.export_output())
        self.bind("<Control-c>", lambda e: self.copy_output())
        self.bind("<Control-l>", lambda e: self.clear_all())
        self.bind("<Control-h>", lambda e: self.show_shortcuts())
        self.bind("<Control-plus>", lambda e: self.set_speed(self.speed_var.get() + 0.1) if hasattr(self, 'speed_var') else None)
        self.bind("<Control-minus>", lambda e: self.set_speed(self.speed_var.get() - 0.1) if hasattr(self, 'speed_var') else None)
        self.bind("<F1>", lambda e: self.show_help())
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_text = """
        ⌨️ Keyboard Shortcuts:
        
        Ctrl + Enter     → Convert
        Ctrl + S         → Export Output
        Ctrl + C         → Copy Output
        Ctrl + L         → Clear All
        Ctrl + H         → Show Shortcuts
        Ctrl + +         → Increase Speed
        Ctrl + -         → Decrease Speed
        F1               → Help
        
        🎯 Tip: Use the Microphone tab to detect Morse from your mic!
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        📡 Morse Code Professional Suite v2.0
        
        How to Use:
        
        1. TEXT → MORSE: Type text in left panel, click Convert
        2. MORSE → TEXT: Enter Morse code (., -, space, /), click Convert
        3. 🎤 MICROPHONE: Go to Microphone tab, click Start Listening, make beeps!
        4. 🔊 SPEAK: Listen to translation
        5. 🎵 PLAY: Hear Morse code audio
        6. ⚡ SPEED: Adjust playback speed
        7. 📚 LEARN: Practice with alphabet and words
        8. 🔍 BREAKDOWN: See letter-by-letter analysis
        9. ⭐ FAVORITES: Save important translations
        
        Morse Code Format:
        • . = dit (short beep)
        • - = dah (long beep)
        • Space = between letters
        • / = between words
        
        Supported Languages:
        English, Persian, German, Turkish, Spanish, French
        """
        messagebox.showinfo("Help & Tutorial", help_text)
    
    def load_example(self):
        """Load example text"""
        example = "HELLO WORLD"
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", example)
        self.status_label.configure(text="📝 Example loaded. Click Convert!")
    
    def change_language(self, choice):
        """Change translation language"""
        self.current_language = choice
        self.status_label.configure(text=f"✅ Ready | Language: {choice.capitalize()}")
        if self.settings:
            self.settings.set('last_language', choice)
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        try:
            if self.history_db:
                history = self.history_db.get_all(100)
                count = len(history)
                self.stats_label.configure(text=f"📊 {count} translations in history")
            else:
                self.stats_label.configure(text="📊 Ready")
        except:
            self.stats_label.configure(text="📊 Ready")
    
    def insert_mic_text(self, text):
        """Insert text from microphone"""
        if text and text != " ":
            current = self.text_input.get("1.0", "end-1c")
            if current == "Type or paste your text here...":
                current = ""
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", current + text)
            self.convert()
    
    def load_favorite(self, text, morse):
        """Load a favorite translation"""
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", text)
        self.morse_input.delete("1.0", "end")
        self.morse_input.insert("1.0", morse)
        self.convert()
    
    def convert(self):
        """Convert between text and Morse"""
        # Get input content
        text_content = self.text_input.get("1.0", "end-1c").strip()
        morse_content = self.morse_input.get("1.0", "end-1c").strip()
        
        # Check if it's placeholder text
        if text_content == "Type or paste your text here...":
            text_content = ""
        if morse_content == "Enter Morse code (use . for dit, - for dah, space between letters, / between words)...":
            morse_content = ""
        
        if text_content and text_content != "":
            # Text to Morse
            self.progress_label.configure(text="🔄 Converting...")
            self.update()
            
            try:
                morse = self.morse_engine.text_to_morse(text_content, self.current_language)
                self.morse_input.delete("1.0", "end")
                self.morse_input.insert("1.0", morse)
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", f"📝 Input Text:\n{text_content}\n\n{'='*50}\n\n🔊 Morse Code:\n{morse}")
                self.status_label.configure(text=f"✅ Converted {len(text_content)} characters to Morse")
                
                # Save for favorites
                self.current_text = text_content
                self.current_morse = morse
                
                # Update favorites panel
                if hasattr(self, 'favorites_panel'):
                    self.favorites_panel.set_current(text_content, morse)
                
                # Add to history
                if self.history_db:
                    self.history_db.add(text_content[:100], morse[:100], "text_to_morse", self.current_language)
                    if hasattr(self, 'history_panel'):
                        self.history_panel.refresh()
                
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed: {e}")
            finally:
                self.progress_label.configure(text="")
            
        elif morse_content and morse_content != "":
            # Morse to Text
            self.progress_label.configure(text="🔄 Converting...")
            self.update()
            
            try:
                text = self.morse_engine.morse_to_text(morse_content, self.current_language)
                self.text_input.delete("1.0", "end")
                self.text_input.insert("1.0", text)
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", f"🔊 Morse Code:\n{morse_content}\n\n{'='*50}\n\n📝 Decoded Text:\n{text}")
                self.status_label.configure(text=f"✅ Converted from Morse to text")
                
                # Save for favorites
                self.current_text = text
                self.current_morse = morse_content
                
                # Update favorites panel
                if hasattr(self, 'favorites_panel'):
                    self.favorites_panel.set_current(text, morse_content)
                
                # Add to history
                if self.history_db:
                    self.history_db.add(morse_content[:100], text[:100], "morse_to_text", self.current_language)
                    if hasattr(self, 'history_panel'):
                        self.history_panel.refresh()
                
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed: {e}")
            finally:
                self.progress_label.configure(text="")
        else:
            messagebox.showwarning("No Input", "Please enter text or Morse code to convert")
        
        self.update_stats()
    
    def speak_output(self):
        """Speak the translated text using TTS"""
        output = self.output_text.get("1.0", "end-1c").strip()
        if not output:
            messagebox.showwarning("No Output", "Please convert something first")
            return
        
        # Extract text from output
        if "Decoded Text:" in output:
            text = output.split("Decoded Text:")[-1].strip()
        elif "Input Text:" in output:
            text = output.split("Input Text:")[-1].split("🔊")[0].strip()
        else:
            text = output
        
        if not text:
            messagebox.showwarning("No Text", "No text to speak")
            return
        
        self.progress_label.configure(text="🔊 Speaking...")
        
        def _speak():
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(text[:500])  # Limit length
                engine.runAndWait()
                self.after(0, lambda: self.progress_label.configure(text=""))
                self.after(0, lambda: self.status_label.configure(text="🔊 Speaking completed"))
            except Exception as e:
                self.after(0, lambda: messagebox.showinfo("TTS Info", f"Text to speak:\n\n{text[:200]}"))
                self.after(0, lambda: self.progress_label.configure(text=""))
        
        threading.Thread(target=_speak, daemon=True).start()
    
    def play_morse(self):
        """Play the Morse code audio"""
        morse = self.morse_input.get("1.0", "end-1c").strip()
        
        # Check for placeholder
        if morse == "Enter Morse code (use . for dit, - for dah, space between letters, / between words)...":
            morse = ""
        
        if not morse:
            messagebox.showwarning("No Morse", "No Morse code to play. Convert text to Morse first.")
            return
        
        if self.audio_player:
            self.progress_label.configure(text="🎵 Playing Morse code...")
            self.audio_player.play_morse(morse)
            self.status_label.configure(text=f"🎵 Playing...")
            self.after(3000, lambda: self.progress_label.configure(text=""))
        else:
            messagebox.showinfo("Play Morse", f"Morse Code:\n{morse[:200]}\n\n(Simple audio playback will use beeps)")
            # Fallback beep
            try:
                import winsound
                winsound.Beep(800, 100)
            except:
                pass
    
    def update_speed(self, value):
        """Update playback speed from slider"""
        if self.audio_player:
            speed = float(value)
            self.audio_player.set_speed(speed)
            self.speed_label.configure(text=f"{speed:.1f}x")
    
    def set_speed(self, speed):
        """Set specific playback speed"""
        if self.audio_player and hasattr(self, 'speed_var'):
            speed = max(0.5, min(3.0, speed))
            self.speed_var.set(speed)
            self.update_speed(speed)
    
    def copy_output(self):
        """Copy output to clipboard"""
        output = self.output_text.get("1.0", "end-1c").strip()
        if output:
            self.clipboard_clear()
            self.clipboard_append(output)
            self.status_label.configure(text="📋 Copied to clipboard!")
        else:
            messagebox.showwarning("No Output", "Nothing to copy")
    
    def export_output(self):
        """Export output with dialog"""
        output = self.output_text.get("1.0", "end-1c").strip()
        morse = self.morse_input.get("1.0", "end-1c").strip()
        
        if not output:
            messagebox.showwarning("No Output", "Nothing to export")
            return
        
        try:
            ExportDialog(self, output, morse)
        except Exception as e:
            # Fallback simple save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                self.status_label.configure(text=f"💾 Saved to {Path(file_path).name}")
    
    def clear_all(self):
        """Clear all inputs and outputs"""
        self.text_input.delete("1.0", "end")
        self.morse_input.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.status_label.configure(text="🗑 Cleared all fields")
        self.progress_label.configure(text="")
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="☀️ Light Mode")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌙 Dark Mode")
    
    def on_closing(self):
        """Clean up on close"""
        # Stop microphone if listening
        if hasattr(self, 'mic_panel') and self.mic_panel:
            if self.mic_panel.is_listening:
                self.mic_panel.stop_listening()
        
        # Stop audio player
        if hasattr(self, 'audio_player') and self.audio_player:
            if hasattr(self.audio_player, 'stop'):
                self.audio_player.stop()
        
        # Close database
        if hasattr(self, 'history_db') and self.history_db:
            if hasattr(self.history_db, 'close'):
                self.history_db.close()
        
        self.destroy()


if __name__ == "__main__":
    app = MorseCodeApp()
    app.mainloop()
