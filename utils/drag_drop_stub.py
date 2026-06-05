"""Drag and drop stub for when tkinterdnd2 is not available"""

class DragDropHandler:
    def __init__(self, widget, callback):
        self.widget = widget
        self.callback = callback
        print("Drag and drop not available - install tkinterdnd2 for this feature")
    
    def setup_drag_drop(self):
        pass