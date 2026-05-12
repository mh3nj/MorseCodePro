import customtkinter as ctk
import random
from tkinter import messagebox

class TeachingPanel(ctk.CTkFrame):
    def __init__(self, parent, morse_engine):
        super().__init__(parent, corner_radius=10)
        self.morse_engine = morse_engine
        self.current_mode = "alphabet"
        self.score = 0
        self.current_question = None
        self.questions_answered = 0
        
        # Title
        title = ctk.CTkLabel(self, text="📚 Learn Morse Code", font=("Arial", 18, "bold"))
        title.pack(pady=10)
        
        # Mode selector
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(pady=10)
        
        self.alphabet_btn = ctk.CTkButton(
            mode_frame, text="🔤 Alphabet Mode", 
            command=lambda: self.set_mode("alphabet"), 
            width=140, height=35,
            fg_color="#00d9ff" if self.current_mode == "alphabet" else "#2b5b84"
        )
        self.alphabet_btn.pack(side="left", padx=5)
        
        self.advanced_btn = ctk.CTkButton(
            mode_frame, text="🚀 Advanced Mode", 
            command=lambda: self.set_mode("advanced"), 
            width=140, height=35,
            fg_color="#2b5b84"
        )
        self.advanced_btn.pack(side="left", padx=5)
        
        # Question area
        self.question_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2, border_color="#00d9ff")
        self.question_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.question_label = ctk.CTkLabel(
            self.question_frame, 
            text="What is this Morse code?", 
            font=("Arial", 16, "bold")
        )
        self.question_label.pack(pady=20)
        
        self.morse_display = ctk.CTkLabel(
            self.question_frame, 
            text="", 
            font=("Courier", 28, "bold"), 
            text_color="#00d9ff"
        )
        self.morse_display.pack(pady=15)
        
        # Answer input
        self.answer_entry = ctk.CTkEntry(
            self.question_frame, 
            placeholder_text="Type your answer here...", 
            width=350, 
            height=45,
            font=("Arial", 14)
        )
        self.answer_entry.pack(pady=15)
        self.answer_entry.bind('<Return>', lambda e: self.check_answer())
        
        # Submit button
        self.submit_btn = ctk.CTkButton(
            self.question_frame, 
            text="✓ Check Answer", 
            command=self.check_answer,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#00d9ff",
            text_color="black"
        )
        self.submit_btn.pack(pady=10)
        
        # Score display
        self.score_label = ctk.CTkLabel(
            self, 
            text="⭐ Score: 0 | Questions: 0", 
            font=("Arial", 14, "bold"),
            text_color="#ffd700"
        )
        self.score_label.pack(pady=5)
        
        # Next button
        self.next_btn = ctk.CTkButton(
            self, 
            text="Next Question →", 
            command=self.new_question, 
            state="disabled",
            height=40,
            font=("Arial", 14)
        )
        self.next_btn.pack(pady=10)
        
        # Start first question
        self.new_question()
    
    def set_mode(self, mode):
        self.current_mode = mode
        self.score = 0
        self.questions_answered = 0
        self.score_label.configure(text=f"⭐ Score: 0 | Questions: 0")
        
        # Update button colors
        if mode == "alphabet":
            self.alphabet_btn.configure(fg_color="#00d9ff")
            self.advanced_btn.configure(fg_color="#2b5b84")
        else:
            self.alphabet_btn.configure(fg_color="#2b5b84")
            self.advanced_btn.configure(fg_color="#00d9ff")
        
        self.new_question()
    
    def new_question(self):
        self.submit_btn.configure(state="normal")
        self.next_btn.configure(state="disabled")
        self.answer_entry.delete(0, "end")
        self.answer_entry.configure(placeholder_text="Type your answer here...")
        
        if self.current_mode == "alphabet":
            # Alphabet mode - simple letters and numbers
            chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            self.current_question = random.choice(chars)
            morse = self.morse_engine.text_to_morse(self.current_question)
            self.morse_display.configure(text=morse)
            self.question_label.configure(text="🔤 What letter or number is this?")
        else:
            # Advanced mode - common words and phrases
            words = ["HELLO", "WORLD", "SOS", "OK", "YES", "NO", "HELP", "STOP", 
                    "GOOD", "BAD", "DAY", "NIGHT", "MORSE", "CODE", "LEARN"]
            self.current_question = random.choice(words)
            morse = self.morse_engine.text_to_morse(self.current_question)
            self.morse_display.configure(text=morse)
            self.question_label.configure(text="🚀 What word or phrase is this?")
    
    def check_answer(self):
        answer = self.answer_entry.get().strip().upper()
        if not answer:
            messagebox.showwarning("Empty", "Please type your answer")
            return
        
        if answer == self.current_question:
            self.score += 10
            self.questions_answered += 1
            self.score_label.configure(text=f"⭐ Score: {self.score} | Questions: {self.questions_answered}")
            messagebox.showinfo("Correct! 🎉", f"✓ Excellent!\n\n{self.current_question} = {self.morse_display.cget('text')}")
            self.submit_btn.configure(state="disabled")
            self.next_btn.configure(state="normal")
        else:
            messagebox.showerror("Wrong! ❌", f"✗ Incorrect.\n\nAnswer: {self.current_question}\nMorse: {self.morse_display.cget('text')}\n\nKeep practicing!")
