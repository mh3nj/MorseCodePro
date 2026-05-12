import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from config.settings import THEMES

class WaveformViewer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.figure = plt.Figure(figsize=(8, 2), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1a1a2e')
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 100)
        self.ax.axis('off')
        
        self.current_waveform = None
        
    def update_waveform(self, audio_data: np.ndarray):
        """Update waveform display"""
        self.ax.clear()
        
        # Normalize audio data
        if len(audio_data) > 0:
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            
            # Plot waveform
            time = np.linspace(0, len(audio_data) / 44100, len(audio_data))
            self.ax.plot(time[:10000], audio_data[:10000], 
                        color='#00d9ff', linewidth=1)
            
            # Add dit/dah markers
            self._add_morse_markers(audio_data)
        
        self.ax.set_facecolor('#1a1a2e')
        self.ax.axis('off')
        self.canvas.draw()
    
    def _add_morse_markers(self, audio_data: np.ndarray):
        """Add markers for detected Morse symbols"""
        # Detect peaks
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(np.abs(audio_data), height=0.5)
        
        # Mark peaks
        if len(peaks) > 0:
            self.ax.scatter(peaks[:100] / 44100, 
                          audio_data[peaks[:100]], 
                          color='red', s=10, alpha=0.5)
    
    def clear(self):
        """Clear waveform display"""
        self.ax.clear()
        self.ax.axis('off')
        self.canvas.draw()
    
    def show_spectrogram(self, audio_data: np.ndarray):
        """Show spectrogram instead of waveform"""
        self.ax.clear()
        
        from scipy import signal
        f, t, Sxx = signal.spectrogram(audio_data, fs=44100)
        
        self.ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), 
                          cmap='plasma', shading='auto')
        self.ax.set_ylabel('Frequency [Hz]')
        self.ax.set_xlabel('Time [sec]')
        self.ax.set_title('Morse Code Spectrogram')
        
        self.canvas.draw()
