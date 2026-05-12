"""Simple microphone test UI"""
import tkinter as tk
from tkinter import ttk

class MicTestApp:
    def __init__(self, root):
        self.root = root
        root.title("Microphone Test")
        root.geometry("500x400")
        
        # Status
        self.status_label = tk.Label(root, text="Testing microphone...", font=("Arial", 14))
        self.status_label.pack(pady=20)
        
        # Amplitude meter
        self.meter_canvas = tk.Canvas(root, width=400, height=50, bg='black')
        self.meter_canvas.pack(pady=10)
        self.meter_bar = self.meter_canvas.create_rectangle(0, 0, 0, 50, fill='#00ff00')
        
        # Detected text
        self.text_display = tk.Text(root, height=10, width=50, font=("Courier", 12))
        self.text_display.pack(pady=10)
        
        # Buttons
        self.start_btn = tk.Button(root, text="Start Listening", command=self.start, bg='green', fg='white')
        self.start_btn.pack(side='left', padx=20)
        
        self.stop_btn = tk.Button(root, text="Stop", command=self.stop, bg='red', fg='white', state='disabled')
        self.stop_btn.pack(side='right', padx=20)
        
        self.listener = None
        
    def start(self):
        try:
            from core.microphone_listener import MicrophoneListener
            self.listener = MicrophoneListener()
            
            # Set callbacks
            self.listener.on_text_detected = self.on_text
            self.listener.on_amplitude_update = self.on_amplitude
            
            if self.listener.start_listening(None):
                self.start_btn.config(state='disabled')
                self.stop_btn.config(state='normal')
                self.status_label.config(text="🔴 Listening... Speak Morse code!", fg='red')
            else:
                self.status_label.config(text="❌ Failed to start microphone", fg='red')
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg='red')
    
    def on_text(self, text):
        self.text_display.insert(tk.END, text)
        self.text_display.see(tk.END)
    
    def on_amplitude(self, amp):
        # Update meter bar
        width = min(400, int(amp / 2000 * 400))
        self.meter_canvas.coords(self.meter_bar, 0, 0, width, 50)
        
        # Change color based on amplitude
        if amp > 1000:
            color = '#ff0000'
        elif amp > 500:
            color = '#ffff00'
        else:
            color = '#00ff00'
        self.meter_canvas.itemconfig(self.meter_bar, fill=color)
    
    def stop(self):
        if self.listener:
            self.listener.stop_listening()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="⏹️ Stopped", fg='black')

if __name__ == "__main__":
    root = tk.Tk()
    app = MicTestApp(root)
    root.mainloop()
