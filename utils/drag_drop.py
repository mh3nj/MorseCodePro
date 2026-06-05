from tkinterdnd2 import TkinterDnD  # Requires pip install tkinterdnd2
import customtkinter as ctk
from pathlib import Path

class DragDropHandler:
    def __init__(self, widget, callback):
        self.widget = widget
        self.callback = callback
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Register drop target
        self.widget.drop_target_register('*')
        self.widget.dnd_bind('<<Drop>>', self.on_drop)
        
        # Change cursor on drag enter
        self.widget.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.widget.dnd_bind('<<DragLeave>>', self.on_drag_leave)
    
    def on_drop(self, event):
        """Handle file drop"""
        files = event.data.split()
        for file_path in files:
            # Remove curly braces if present (Windows)
            file_path = file_path.strip('{}')
            path = Path(file_path)
            
            if path.exists():
                self.callback(path)
    
    def on_drag_enter(self, event):
        """Handle drag enter - visual feedback"""
        if hasattr(self.widget, 'configure'):
            self.widget.configure(
                fg_color="#2b5b84",
                border_width=2,
                border_color="#00d9ff"
            )
    
    def on_drag_leave(self, event):
        """Handle drag leave - restore appearance"""
        if hasattr(self.widget, 'configure'):
            self.widget.configure(
                fg_color="transparent",
                border_width=0
            )