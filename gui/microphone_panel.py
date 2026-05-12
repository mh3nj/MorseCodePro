"""
Microphone Panel - FIXED with device selection
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import time

class MicrophonePanel(ctk.CTkFrame):
    def __init__(self, parent, on_text_detected):
        super().__init__(parent, corner_radius=15)
        
        self.on_text_detected = on_text_detected
        self.detector = None
        self.is_listening = False
        self.device_id = None
        
        self.setup_ui()
        self.scan_devices()
    
    def scan_devices(self):
        """Scan for available microphones"""
        try:
            import sounddevice as sd
            self.devices = []
            devices = sd.query_devices()
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    self.devices.append((i, device['name']))
                    
            # Update device selector
            if hasattr(self, 'device_menu') and self.devices:
                self.device_menu.configure(values=[f"[{d[0]}] {d[1][:30]}" for d in self.devices])
                # Try to find Razer by default
                for i, (idx, name) in enumerate(self.devices):
                    if 'Razer' in name or 'Seiren' in name:
                        self.device_menu.set(f"[{idx}] {name[:30]}")
                        self.device_id = idx
                        break
                if self.device_id is None and self.devices:
                    self.device_menu.set(f"[{self.devices[0][0]}] {self.devices[0][1][:30]}")
                    self.device_id = self.devices[0][0]
        except:
            self.devices = []
    
    def setup_ui(self):
        """Setup microphone UI"""
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="🎤 Live Morse Code Detector",
            font=("Arial", 18, "bold"),
            text_color="#00d9ff"
        )
        title.pack(pady=10)
        
        # Device selection
        device_frame = ctk.CTkFrame(self, fg_color="transparent")
        device_frame.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(device_frame, text="Microphone:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.device_menu = ctk.CTkOptionMenu(
            device_frame,
            values=["Scanning..."],
            command=self.change_device,
            width=300
        )
        self.device_menu.pack(side="left", padx=5)
        
        ctk.CTkButton(
            device_frame,
            text="🔄",
            command=self.scan_devices,
            width=30
        ).pack(side="left", padx=5)
        
        # Instructions
        instructions = ctk.CTkLabel(
            self,
            text="Make beeping sounds into your microphone:\n• Short beep (0.1-0.25s) = dit (.) → E\n• Long beep (0.26-0.6s) = dah (-) → T\n• Short pause (0.3s) = next letter\n• Long pause (0.8s) = next word",
            font=("Arial", 11),
            text_color="#888888",
            justify="left"
        )
        instructions.pack(pady=10, padx=20)
        
        # Volume meter
        meter_frame = ctk.CTkFrame(self, corner_radius=5)
        meter_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(meter_frame, text="Volume Meter:", font=("Arial", 11)).pack()
        
        # Canvas for meter
        self.meter_canvas = ctk.CTkCanvas(meter_frame, height=40, bg='#1a1a2e', highlightthickness=0)
        self.meter_canvas.pack(fill="x", padx=10, pady=5)
        
        # Create meter rectangle
        self.meter_rect = self.meter_canvas.create_rectangle(0, 0, 0, 40, fill='#00d9ff')
        
        # Add threshold line
        self.meter_canvas.create_line(0, 0, 0, 40, fill='#ff4444', width=2, dash=(5, 5))
        
        # Control buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.listen_btn = ctk.CTkButton(
            btn_frame,
            text="🎙️ Start Listening",
            command=self.toggle_listening,
            width=180,
            height=45,
            fg_color="#00d9ff",
            text_color="black",
            font=("Arial", 14, "bold")
        )
        self.listen_btn.pack(pady=5)
        
        # Sensitivity slider
        sens_frame = ctk.CTkFrame(self, fg_color="transparent")
        sens_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(sens_frame, text="Sensitivity:", font=("Arial", 11)).pack()
        
        self.sensitivity_var = ctk.DoubleVar(value=50)
        self.sensitivity_slider = ctk.CTkSlider(
            sens_frame,
            from_=0,
            to=100,
            variable=self.sensitivity_var,
            command=self.update_sensitivity,
            height=20
        )
        self.sensitivity_slider.pack(fill="x", pady=5)
        
        self.sensitivity_label = ctk.CTkLabel(sens_frame, text="Medium", font=("Arial", 10))
        self.sensitivity_label.pack()
        
        # Status display
        self.status_label = ctk.CTkLabel(
            self,
            text="⚪ Not listening",
            font=("Arial", 12),
            text_color="#888888"
        )
        self.status_label.pack(pady=5)
        
        # Detected text display
        detected_frame = ctk.CTkFrame(self, corner_radius=10)
        detected_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(detected_frame, text="Detected Text:", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.detected_text = ctk.CTkTextbox(detected_frame, height=120, font=("Arial", 14))
        self.detected_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Test buttons
        test_frame = ctk.CTkFrame(self, fg_color="transparent")
        test_frame.pack(pady=10)
        
        ctk.CTkLabel(test_frame, text="Test:", font=("Arial", 11)).pack(side="left", padx=5)
        
        ctk.CTkButton(
            test_frame,
            text="S (...)",
            command=lambda: self.add_test_text("S"),
            width=60
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            test_frame,
            text="O (---)",
            command=lambda: self.add_test_text("O"),
            width=60
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            test_frame,
            text="SOS",
            command=lambda: self.add_test_text("SOS"),
            width=60
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            test_frame,
            text="Clear",
            command=self.clear_text,
            width=60,
            fg_color="#aa3333"
        ).pack(side="left", padx=2)
    
    def change_device(self, choice):
        """Change microphone device"""
        try:
            # Extract device ID from string like "[4] Microphone Name"
            import re
            match = re.search(r'\[(\d+)\]', choice)
            if match:
                self.device_id = int(match.group(1))
                print(f"Selected device: {self.device_id}")
                
                if self.is_listening:
                    self.stop_listening()
                    self.start_listening()
        except:
            pass
    
    def toggle_listening(self):
        """Toggle microphone listening"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start listening with callback"""
        try:
            from core.morse_detector import MorseDetector
            self.detector = MorseDetector(device_id=self.device_id)
            
            # Set callbacks
            self.detector.on_letter = self.on_letter
            self.detector.on_word = self.on_word
            self.detector.on_morse_symbol = self.on_symbol
            self.detector.on_amplitude = self.on_amplitude
            
            if self.detector.start_listening():
                self.is_listening = True
                self.listen_btn.configure(text="🛑 Stop Listening", fg_color="#aa3333")
                self.status_label.configure(text="🔴 Listening... Make beeps!", text_color="#ff4444")
                self.detected_text.delete("1.0", "end")
                self.detected_text.insert("1.0", "Listening... Speak or make beeps into your mic!\n\n")
            else:
                messagebox.showerror("Error", "Failed to start microphone.\nCheck device selection.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start: {e}")
    
    def stop_listening(self):
        """Stop listening"""
        if self.detector:
            self.detector.stop_listening()
        
        self.is_listening = False
        self.listen_btn.configure(text="🎙️ Start Listening", fg_color="#00d9ff")
        self.status_label.configure(text="⚪ Not listening", text_color="#888888")
        
        # Reset meter
        self.meter_canvas.coords(self.meter_rect, 0, 0, 0, 40)
    
    def on_letter(self, letter, morse):
        """Handle detected letter"""
        self.detected_text.insert("end", letter)
        self.detected_text.see("end")
        self.status_label.configure(text=f"🔴 Detected: {letter} ({morse})", text_color="#00ff00")
        
        if self.on_text_detected:
            self.on_text_detected(letter)
        
        self.after(1000, lambda: self.status_label.configure(
            text="🔴 Listening...", text_color="#ff4444"
        ))
    
    def on_word(self, word):
        """Handle detected word"""
        self.detected_text.insert("end", " ")
        self.status_label.configure(text=f"🔴 Word: {word}", text_color="#00d9ff")
        
        if self.on_text_detected:
            self.on_text_detected(" ")
    
    def on_symbol(self, symbol):
        """Handle detected Morse symbol"""
        self.status_label.configure(text=f"🔴 {symbol}", text_color="#ffff00")
        self.after(200, lambda: self.status_label.configure(
            text="🔴 Listening...", text_color="#ff4444"
        ))
    
    def on_amplitude(self, amplitude):
        """Update volume meter - THIS SHOULD MOVE THE BAR"""
        # Map amplitude (0-3000) to width (0-500)
        max_width = 500
        width = min(max_width, int(amplitude / 3000 * max_width))
        
        # Update the rectangle
        self.meter_canvas.coords(self.meter_rect, 0, 0, width, 40)
        
        # Change color based on amplitude
        if amplitude > self.detector.threshold:
            color = '#ff4444'  # Red when detecting
        elif amplitude > self.detector.threshold / 2:
            color = '#ffff00'  # Yellow for medium
        else:
            color = '#00d9ff'  # Blue for quiet
        
        self.meter_canvas.itemconfig(self.meter_rect, fill=color)
        
        # Update threshold line position
        threshold_x = int(self.detector.threshold / 3000 * max_width)
        self.meter_canvas.delete("threshold")
        self.meter_canvas.create_line(threshold_x, 0, threshold_x, 40, fill='#ff4444', width=2, dash=(5, 5), tags="threshold")
    
    def update_sensitivity(self, value):
        """Update sensitivity"""
        percent = int(value)
        if percent < 30:
            label = "Very Low (quiet sounds)"
        elif percent < 50:
            label = "Low"
        elif percent < 70:
            label = "Medium"
        elif percent < 90:
            label = "High"
        else:
            label = "Very High (all sounds)"
        
        self.sensitivity_label.configure(text=label)
        
        if self.detector and self.is_listening:
            self.detector.set_sensitivity(percent)
    
    def add_test_text(self, text):
        """Add test text"""
        self.detected_text.insert("end", text)
        self.detected_text.see("end")
        if self.on_text_detected:
            for char in text:
                self.on_text_detected(char)
    
    def clear_text(self):
        """Clear detected text"""
        self.detected_text.delete("1.0", "end")
