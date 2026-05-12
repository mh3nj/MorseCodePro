import customtkinter as ctk
from config.settings import THEMES, APP_NAME
from gui.translation_panel import TranslationPanel
from gui.audio_controls import AudioControls
from gui.waveform_viewer import WaveformViewer
from gui.word_selector import WordSelector
from gui.teaching_tab import TeachingTab
from gui.history_panel import HistoryPanel

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(APP_NAME)
        self.geometry("1400x800")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Current theme
        self.current_theme = "dark"
        
        # Initialize components
        self.setup_ui()
        self.apply_theme()
        
        # Keyboard shortcuts
        self.bind_shortcuts()
    
    def setup_ui(self):
        """Create glassmorphism UI"""
        
        # Main container with transparency
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=20
        )
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Left panel (60% width)
        self.left_panel = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            bg_color="transparent"
        )
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right panel (40% width)
        self.right_panel = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            bg_color="transparent"
        )
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=6)
        self.main_frame.grid_columnconfigure(1, weight=4)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize panels
        self.translation_panel = TranslationPanel(self.left_panel)
        self.audio_controls = AudioControls(self.left_panel)
        self.waveform_viewer = WaveformViewer(self.left_panel)
        self.word_selector = WordSelector(self.right_panel)
        self.teaching_tab = TeachingTab(self.right_panel)
        self.history_panel = HistoryPanel(self.right_panel)
        
        # Tab view for right panel
        self.tabview = ctk.CTkTabview(self.right_panel)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("Word Breakdown")
        self.tabview.add("Teaching")
        self.tabview.add("History")
        
        self.word_selector.pack_in_tab(self.tabview.tab("Word Breakdown"))
        self.teaching_tab.pack_in_tab(self.tabview.tab("Teaching"))
        self.history_panel.pack_in_tab(self.tabview.tab("History"))
    
    def apply_theme(self):
        """Apply glassmorphism theme"""
        theme = THEMES[self.current_theme]
        
        # Set appearance
        ctk.set_appearance_mode("dark" if self.current_theme == "dark" else "light")
        ctk.set_default_color_theme("blue")
        
        # Apply glassmorphism effect
        self.configure(bg=theme["bg"])
        for frame in [self.left_panel, self.right_panel]:
            frame.configure(fg_color=theme["glass"])
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind("<Control-plus>", lambda e: self.audio_controls.speed_up())
        self.bind("<Control-minus>", lambda e: self.audio_controls.slow_down())
        self.bind("<space>", lambda e: self.audio_controls.toggle_pause())
        self.bind("<Control-n>", lambda e: self.translation_panel.new_translation())
        self.bind("<Control-s>", lambda e: self.translation_panel.save_translation())
    
    def toggle_theme(self):
        """Switch between dark and light themes"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
