"""
Word Breakdown Panel - Simplified
"""

import customtkinter as ctk
from tkinter import messagebox

class WordBreakdownPanel(ctk.CTkFrame):
    def __init__(self, parent, morse_engine):
        super().__init__(parent, corner_radius=10)
        self.morse_engine = morse_engine
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        # Title
        title = ctk.CTkLabel(self, text="🔍 Word Breakdown", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Word input
        self.word_entry = ctk.CTkEntry(self, placeholder_text="Enter any word...", width=300, height=40)
        self.word_entry.pack(pady=10)
        self.word_entry.bind('<Return>', lambda e: self.breakdown())
        
        # Analyze button
        self.analyze_btn = ctk.CTkButton(self, text="🔎 Analyze Word", command=self.breakdown, height=35)
        self.analyze_btn.pack(pady=5)
        
        # Results area
        self.result_text = ctk.CTkTextbox(self, height=250, font=("Courier", 13), wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def breakdown(self):
        """Analyze word"""
        word = self.word_entry.get().strip()
        if not word:
            messagebox.showwarning("Empty", "Please enter a word to analyze")
            return
        
        try:
            breakdown = self.morse_engine.breakdown_word(word)
            
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", f"📖 WORD: {word.upper()}\n")
            self.result_text.insert("end", "="*50 + "\n\n")
            
            for i, item in enumerate(breakdown, 1):
                self.result_text.insert("end", f"{i}. Letter: {item['letter']}\n")
                self.result_text.insert("end", f"   Morse:  {item['morse']}\n")
                
                # Visual representation
                visual = ""
                for c in item['morse']:
                    if c == '.':
                        visual += "• "
                    elif c == '-':
                        visual += "— "
                self.result_text.insert("end", f"   Visual: {visual}\n\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze: {e}")
