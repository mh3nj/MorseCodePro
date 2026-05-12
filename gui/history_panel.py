"""
History Panel - Thread-safe version
"""

import customtkinter as ctk
from tkinter import messagebox
import threading

class HistoryPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10)
        
        # Initialize DB in main thread
        try:
            from models.history_db import HistoryDB
            self.db = HistoryDB()
        except Exception as e:
            print(f"History DB init error: {e}")
            self.db = None
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup UI"""
        # Title
        title = ctk.CTkLabel(self, text="📜 Translation History", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Stats frame
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.count_label = ctk.CTkLabel(stats_frame, text="Total: 0 translations", font=("Arial", 12))
        self.count_label.pack(side="left")
        
        # History display
        self.history_text = ctk.CTkTextbox(self, height=300, font=("Arial", 11), wrap="word")
        self.history_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.refresh_btn = ctk.CTkButton(
            btn_frame, 
            text="🔄 Refresh", 
            command=self.refresh, 
            width=100
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text="🗑 Clear All", 
            command=self.clear_history, 
            width=100,
            fg_color="#aa3333"
        )
        self.clear_btn.pack(side="left", padx=5)
    
    def refresh(self):
        """Refresh history display (runs in main thread)"""
        self.history_text.delete("1.0", "end")
        
        if not self.db:
            self.history_text.insert("end", "⚠️ History database not available")
            self.count_label.configure(text="Total: 0 translations")
            return
        
        try:
            # Run DB query in thread, then update UI in main thread
            def fetch_history():
                return self.db.get_all(50)
            
            def update_display(history):
                if not history:
                    self.history_text.insert("end", "📭 No history yet.\n\nConvert something to see it here!")
                    self.count_label.configure(text="Total: 0 translations")
                else:
                    self.count_label.configure(text=f"Total: {len(history)} translations")
                    
                    for item in history:
                        self.history_text.insert("end", f"📅 {item['timestamp'][:19]}\n")
                        self.history_text.insert("end", f"   Type: {item['input_type']} | Lang: {item['language']}\n")
                        self.history_text.insert("end", f"   Input: {item['input_text'][:80]}\n")
                        self.history_text.insert("end", f"   Output: {item['output_text'][:80]}\n")
                        self.history_text.insert("end", "-"*60 + "\n\n")
            
            # Run in thread to not block UI
            import threading
            def worker():
                history = fetch_history()
                self.after(0, lambda: update_display(history))
            
            threading.Thread(target=worker, daemon=True).start()
            
        except Exception as e:
            self.history_text.insert("end", f"Error loading history: {e}")
    
    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Confirm", "⚠️ Delete ALL translation history?\n\nThis cannot be undone!"):
            if self.db:
                self.db.clear()
                self.refresh()
                messagebox.showinfo("Cleared", "History has been cleared")
