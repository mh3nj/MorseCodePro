import customtkinter as ctk
from tkinter import Text, END, WORD
from core.morse_engine import MorseEngine

class WordSelector(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.morse_engine = MorseEngine()
        self.current_translation = ""
        self.word_breakdown_text = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup clickable word selector UI"""
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="📝 Click Any Word to See Breakdown",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Translated text display with clickable words
        self.text_display = Text(
            self,
            height=10,
            wrap=WORD,
            font=("Arial", 14),
            bg="#2b2b2b",
            fg="#ffffff",
            relief="flat",
            padx=10,
            pady=10
        )
        self.text_display.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bind click event
        self.text_display.tag_config("word", foreground="#00d9ff", underline=True)
        self.text_display.bind("<Button-1>", self.on_word_click)
        self.text_display.bind("<ButtonRelease-1>", self.on_word_release)
        
        # Breakdown display frame
        self.breakdown_frame = ctk.CTkFrame(self)
        self.breakdown_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Breakdown label
        self.breakdown_title = ctk.CTkLabel(
            self.breakdown_frame,
            text="🔍 Character Breakdown",
            font=("Arial", 14, "bold")
        )
        self.breakdown_title.pack(pady=5)
        
        # Breakdown text area
        self.word_breakdown_text = Text(
            self.breakdown_frame,
            height=8,
            font=("Courier", 12),
            bg="#1e1e1e",
            fg="#00ff00",
            relief="flat",
            padx=10,
            pady=10
        )
        self.word_breakdown_text.pack(fill="both", expand=True)
        
        # Audio preview button
        self.preview_button = ctk.CTkButton(
            self.breakdown_frame,
            text="🔊 Play This Morse",
            command=self.preview_selected_morse,
            state="disabled"
        )
        self.preview_button.pack(pady=5)
    
    def update_translated_text(self, text: str):
        """Update the translated text with clickable words"""
        self.current_translation = text
        
        # Clear and insert with word tags
        self.text_display.delete(1.0, END)
        
        words = text.split()
        for i, word in enumerate(words):
            start_pos = self.text_display.index(END)
            self.text_display.insert(END, word)
            end_pos = self.text_display.index(END)
            
            # Add tag for this word
            self.text_display.tag_add(f"word_{i}", start_pos, end_pos)
            self.text_display.tag_config(f"word_{i}", foreground="#00d9ff", underline=True)
            
            # Store word data
            self.text_display.tag_bind(f"word_{i}", "<Enter>", 
                                       lambda e, w=word: self.on_word_hover(w))
            
            # Add space after word
            self.text_display.insert(END, " ")
    
    def on_word_hover(self, word: str):
        """Handle word hover"""
        self.text_display.config(cursor="hand2")
    
    def on_word_click(self, event):
        """Handle word click start"""
        self.clicked_word = self.get_word_at_position(event.x, event.y)
    
    def on_word_release(self, event):
        """Handle word click release"""
        word = self.get_word_at_position(event.x, event.y)
        if word and word == getattr(self, 'clicked_word', None):
            self.show_word_breakdown(word)
    
    def get_word_at_position(self, x, y):
        """Get word at click position"""
        try:
            index = self.text_display.index(f"@{x},{y}")
            # Get the word at this index
            line = int(index.split('.')[0])
            col = int(index.split('.')[1])
            
            # Get the entire line
            line_text = self.text_display.get(f"{line}.0", f"{line}.end")
            
            # Find word boundaries
            start = col
            while start > 0 and line_text[start-1].isalnum():
                start -= 1
            
            end = col
            while end < len(line_text) and line_text[end].isalnum():
                end += 1
            
            if start < end:
                return line_text[start:end]
        except:
            pass
        return None
    
    def show_word_breakdown(self, word: str):
        """Show letter-by-letter breakdown of selected word"""
        breakdown = self.morse_engine.breakdown_word(word)
        
        self.word_breakdown_text.delete(1.0, END)
        
        # Display breakdown
        self.word_breakdown_text.insert(END, f"📖 Word: {word}\n")
        self.word_breakdown_text.insert(END, "="*40 + "\n\n")
        
        for item in breakdown:
            self.word_breakdown_text.insert(END, f"Letter: {item['letter']}\n")
            self.word_breakdown_text.insert(END, f"Morse:  {item['morse']}\n")
            self.word_breakdown_text.insert(END, f"Pattern: ")
            
            # Visual pattern representation
            pattern_str = ""
            for p in item['audio_pattern']:
                if p == 1:
                    pattern_str += "• "
                elif p == 3:
                    pattern_str += "— "
                elif p == 2:
                    pattern_str += "  "
            self.word_breakdown_text.insert(END, pattern_str + "\n\n")
        
        self.last_selected_word = word
        self.preview_button.configure(state="normal")
    
    def preview_selected_morse(self):
        """Preview the Morse audio for selected word"""
        if hasattr(self, 'last_selected_word'):
            morse = self.morse_engine.text_to_morse(self.last_selected_word)
            # This would connect to audio_player
            print(f"Playing: {morse}")  # Placeholder
            # self.audio_player.play(morse)
    
    def pack_in_tab(self, parent):
        """Pack this widget into a tab"""
        self.pack(fill="both", expand=True, padx=10, pady=10)
