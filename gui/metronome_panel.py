"""
Metronome Panel for Practice
"""

import customtkinter as ctk
from tkinter import messagebox
import threading

class MetronomePanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10)
        self.metronome = None
        self.is_running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup metronome UI"""
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="🎵 Metronome & Timing Practice", 
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # BPM Control
        bpm_frame = ctk.CTkFrame(self, fg_color="transparent")
        bpm_frame.pack(pady=10)
        
        ctk.CTkLabel(bpm_frame, text="Speed (BPM):", font=("Arial", 14)).pack(side="left", padx=5)
        
        self.bpm_var = ctk.IntVar(value=60)
        self.bpm_slider = ctk.CTkSlider(
            bpm_frame,
            from_=30,
            to=180,
            variable=self.bpm_var,
            command=self.update_bpm,
            width=200
        )
        self.bpm_slider.pack(side="left", padx=10)
        
        self.bpm_label = ctk.CTkLabel(bpm_frame, text="60 BPM", font=("Arial", 14))
        self.bpm_label.pack(side="left", padx=5)
        
        # WPM Display
        wpm_frame = ctk.CTkFrame(self, fg_color="transparent")
        wpm_frame.pack(pady=5)
        
        ctk.CTkLabel(wpm_frame, text="≈ 15 WPM", font=("Arial", 12), text_color="#888888").pack()
        
        # Control buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Start Metronome",
            command=self.start_metronome,
            width=140,
            fg_color="#00d9ff",
            text_color="black"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Stop",
            command=self.stop_metronome,
            width=100,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        # Timing reference
        ref_frame = ctk.CTkFrame(self, corner_radius=10)
        ref_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ref_frame, text="📖 Timing Reference", font=("Arial", 12, "bold")).pack(pady=5)
        
        timing_text = """
        • Dit (.) = 1 unit
        • Dah (-) = 3 units  
        • Space between letters = 3 units
        • Space between words = 7 units
        
        Practice: Tap to the beat!
        """
        
        self.timing_label = ctk.CTkLabel(
            ref_frame,
            text=timing_text,
            font=("Arial", 10),
            text_color="#888888",
            justify="left"
        )
        self.timing_label.pack(pady=5)
        
        # Beat indicator
        self.beat_indicator = ctk.CTkLabel(
            self,
            text="⚪",
            font=("Arial", 32),
            text_color="#888888"
        )
        self.beat_indicator.pack(pady=10)
    
    def update_bpm(self, value):
        """Update BPM value"""
        bpm = int(value)
        self.bpm_var.set(bpm)
        wpm = int(bpm / 4)  # Approximate conversion
        self.bpm_label.configure(text=f"{bpm} BPM")
        
        if self.metronome and self.is_running:
            self.metronome.set_bpm(bpm)
    
    def on_beat(self, is_accent):
        """Called on each beat"""
        if is_accent:
            self.beat_indicator.configure(text="🔴", text_color="#ff4444")
        else:
            self.beat_indicator.configure(text="🟢", text_color="#00ff00")
        
        self.after(100, lambda: self.beat_indicator.configure(text="⚪", text_color="#888888"))
    
    def start_metronome(self):
        """Start the metronome"""
        try:
            from core.metronome import Metronome
            self.metronome = Metronome()
            self.is_running = True
            
            self.metronome.start(self.bpm_var.get(), self.on_beat)
            
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start metronome: {e}")
    
    def stop_metronome(self):
        """Stop the metronome"""
        if self.metronome:
            self.metronome.stop()
        
        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.beat_indicator.configure(text="⚪", text_color="#888888")