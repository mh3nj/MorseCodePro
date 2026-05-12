"""
Favorites/Bookmarks Panel - Save and load favorite translations
"""

import customtkinter as ctk
from tkinter import messagebox

class FavoritesPanel(ctk.CTkFrame):
    def __init__(self, parent, on_load_callback):
        super().__init__(parent, corner_radius=10)
        
        self.on_load_callback = on_load_callback
        self.favorites = []
        
        self.setup_ui()
        self.load_favorites()
    
    def setup_ui(self):
        """Setup favorites UI"""
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="⭐ Favorites & Bookmarks",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # Listbox for favorites
        self.favorites_listbox = ctk.CTkTextbox(self, height=200, font=("Arial", 11))
        self.favorites_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="⭐ Save Current",
            command=self.save_current,
            width=100
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.load_btn = ctk.CTkButton(
            btn_frame,
            text="📖 Load Selected",
            command=self.load_selected,
            width=100
        )
        self.load_btn.pack(side="left", padx=5)
        
        self.remove_btn = ctk.CTkButton(
            btn_frame,
            text="🗑 Remove",
            command=self.remove_selected,
            width=100,
            fg_color="#aa3333"
        )
        self.remove_btn.pack(side="left", padx=5)
    
    def load_favorites(self):
        """Load favorites from settings"""
        try:
            from config.settings_manager import SettingsManager
            settings = SettingsManager()
            self.favorites = settings.get('favorite_translations', [])
            self.refresh_display()
        except:
            pass
    
    def save_favorites(self):
        """Save favorites to settings"""
        try:
            from config.settings_manager import SettingsManager
            settings = SettingsManager()
            settings.settings['favorite_translations'] = self.favorites
            settings.save_settings()
        except:
            pass
    
    def refresh_display(self):
        """Refresh favorites display"""
        self.favorites_listbox.delete("1.0", "end")
        
        if not self.favorites:
            self.favorites_listbox.insert("end", "No favorites yet.\n\nClick 'Save Current' to add translations!")
        else:
            for i, fav in enumerate(self.favorites, 1):
                self.favorites_listbox.insert("end", f"{i}. {fav['text'][:50]}\n")
                self.favorites_listbox.insert("end", f"   {fav['morse'][:50]}\n\n")
    
    def save_current(self):
        """Save current translation to favorites"""
        if hasattr(self, 'current_text') and self.current_text:
            self.favorites.insert(0, {
                'text': self.current_text,
                'morse': self.current_morse
            })
            self.save_favorites()
            self.refresh_display()
            messagebox.showinfo("Saved", "Added to favorites!")
    
    def load_selected(self):
        """Load selected favorite"""
        try:
            index = int(self.favorites_listbox.index("insert").split('.')[0]) - 1
            if 0 <= index < len(self.favorites):
                favorite = self.favorites[index]
                if self.on_load_callback:
                    self.on_load_callback(favorite['text'], favorite['morse'])
        except:
            pass
    
    def remove_selected(self):
        """Remove selected favorite"""
        try:
            index = int(self.favorites_listbox.index("insert").split('.')[0]) - 1
            if 0 <= index < len(self.favorites):
                removed = self.favorites.pop(index)
                self.save_favorites()
                self.refresh_display()
                messagebox.showinfo("Removed", "Favorite removed")
        except:
            pass
    
    def set_current(self, text, morse):
        """Set current translation for saving"""
        self.current_text = text
        self.current_morse = morse
