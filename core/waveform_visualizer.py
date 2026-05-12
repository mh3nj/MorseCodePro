"""
Create waveform visualizations of Morse code audio
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io

class WaveformVisualizer:
    def __init__(self):
        self.figure = None
        self.canvas = None
        
    def create_waveform_plot(self, audio_data, sample_rate=44100):
        """Create waveform plot from audio data"""
        fig = Figure(figsize=(10, 4), dpi=100, facecolor='#1a1a2e')
        ax = fig.add_subplot(111)
        
        # Generate time axis
        duration = len(audio_data) / sample_rate
        time = np.linspace(0, duration, len(audio_data))
        
        # Plot waveform
        ax.plot(time, audio_data, color='#00d9ff', linewidth=1, alpha=0.8)
        ax.fill_between(time, audio_data, 0, alpha=0.3, color='#00d9ff')
        
        # Style
        ax.set_facecolor('#0d0d1a')
        ax.set_xlabel('Time (seconds)', color='white', fontsize=10)
        ax.set_ylabel('Amplitude', color='white', fontsize=10)
        ax.set_title('Morse Code Waveform', color='#00d9ff', fontsize=12, fontweight='bold')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.2, color='white')
        
        fig.tight_layout()
        return fig
    
    def create_spectrogram(self, audio_data, sample_rate=44100):
        """Create spectrogram for frequency analysis"""
        fig = Figure(figsize=(10, 4), dpi=100, facecolor='#1a1a2e')
        ax = fig.add_subplot(111)
        
        # Compute spectrogram
        Pxx, freqs, bins, im = ax.specgram(
            audio_data, 
            Fs=sample_rate,
            NFFT=1024,
            noverlap=512,
            cmap='plasma'
        )
        
        # Style
        ax.set_facecolor('#0d0d1a')
        ax.set_xlabel('Time (seconds)', color='white', fontsize=10)
        ax.set_ylabel('Frequency (Hz)', color='white', fontsize=10)
        ax.set_title('Morse Code Spectrogram', color='#00d9ff', fontsize=12, fontweight='bold')
        ax.tick_params(colors='white')
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Intensity (dB)', color='white')
        cbar.ax.yaxis.set_tick_params(colors='white')
        
        fig.tight_layout()
        return fig
    
    def create_morse_pattern_visual(self, morse_code):
        """Create visual pattern of Morse code (dit/dah visualization)"""
        fig = Figure(figsize=(12, 2), dpi=100, facecolor='#1a1a2e')
        ax = fig.add_subplot(111)
        
        # Parse Morse code
        x_pos = 0
        patterns = []
        
        for char in morse_code:
            if char == '.':
                patterns.append(('dit', x_pos, 1))
                x_pos += 1.5
            elif char == '-':
                patterns.append(('dah', x_pos, 3))
                x_pos += 3.5
            elif char == ' ':
                x_pos += 1
            elif char == '/':
                x_pos += 3
        
        # Draw patterns
        for pattern_type, x, width in patterns:
            if pattern_type == 'dit':
                color = '#00d9ff'
                height = 0.6
                rect = plt.Rectangle((x, 0.2), width, height, facecolor=color, alpha=0.8)
                ax.add_patch(rect)
            else:
                color = '#ff6b6b'
                height = 0.6
                rect = plt.Rectangle((x, 0.2), width, height, facecolor=color, alpha=0.8)
                ax.add_patch(rect)
        
        # Style
        ax.set_xlim(0, x_pos)
        ax.set_ylim(0, 1)
        ax.set_facecolor('#0d0d1a')
        ax.set_title('Morse Code Pattern (• = dit, — = dah)', color='#00d9ff', fontsize=10)
        ax.axis('off')
        
        fig.tight_layout()
        return fig
    
    def plot_to_image(self, fig):
        """Convert matplotlib figure to image bytes for display"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        return buf
