"""
Advanced Export Dialog with multiple formats and options
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent, content, morse_code=None):
        super().__init__(parent)
        
        self.title("Export Translation")
        self.geometry("500x500")
        self.parent = parent
        self.content = content
        self.morse_code = morse_code
        
        self.result = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup export dialog UI"""
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="Export Options",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=20)
        
        # Format selection
        format_frame = ctk.CTkFrame(self)
        format_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(format_frame, text="Format:", font=("Arial", 14)).pack(pady=5)
        
        self.format_var = ctk.StringVar(value="TXT")
        formats = ["TXT", "JSON", "CSV", "WAV", "MP3"]
        self.format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=formats,
            variable=self.format_var,
            command=self.on_format_change
        )
        self.format_menu.pack(pady=5)
        
        # Options frame (changes based on format)
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_options()
        
        # Include metadata checkbox
        self.metadata_var = ctk.BooleanVar(value=True)
        metadata_check = ctk.CTkCheckBox(
            self,
            text="Include metadata (timestamp, language, etc.)",
            variable=self.metadata_var
        )
        metadata_check.pack(pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        export_btn = ctk.CTkButton(
            btn_frame,
            text="Export",
            command=self.export,
            width=120,
            fg_color="#00d9ff",
            text_color="black"
        )
        export_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=120
        )
        cancel_btn.pack(side="left", padx=10)
    
    def on_format_change(self, choice):
        """Update options based on selected format"""
        self.update_options()
    
    def update_options(self):
        """Update options frame content"""
        # Clear existing
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        format_type = self.format_var.get()
        
        if format_type in ["WAV", "MP3"]:
            # Audio options
            ctk.CTkLabel(self.options_frame, text="WPM (Speed):", font=("Arial", 12)).pack()
            self.wpm_var = ctk.IntVar(value=20)
            wpm_slider = ctk.CTkSlider(
                self.options_frame,
                from_=5,
                to=50,
                variable=self.wpm_var
            )
            wpm_slider.pack(pady=5)
            ctk.CTkLabel(self.options_frame, textvariable=self.wpm_var).pack()
        
        elif format_type == "CSV":
            # CSV options
            self.include_header = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self.options_frame,
                text="Include header row",
                variable=self.include_header
            ).pack()
    
    def export(self):
        """Perform export based on selected options"""
        format_type = self.format_var.get()
        
        file_ext = {
            "TXT": ".txt",
            "JSON": ".json", 
            "CSV": ".csv",
            "WAV": ".wav",
            "MP3": ".mp3"
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=file_ext[format_type],
            filetypes=[(f"{format_type} files", f"*{file_ext[format_type]}")]
        )
        
        if not file_path:
            return
        
        try:
            if format_type == "TXT":
                self.export_txt(file_path)
            elif format_type == "JSON":
                self.export_json(file_path)
            elif format_type == "CSV":
                self.export_csv(file_path)
            elif format_type in ["WAV", "MP3"]:
                self.export_audio(file_path, format_type.lower())
            
            messagebox.showinfo("Success", f"Exported to {file_path}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_txt(self, filepath):
        """Export as text file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.content)
    
    def export_json(self, filepath):
        """Export as JSON"""
        import json
        from datetime import datetime
        
        data = {
            'content': self.content,
            'export_date': datetime.now().isoformat(),
            'format': 'JSON'
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def export_csv(self, filepath):
        """Export as CSV"""
        import csv
        
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if self.include_header.get():
                writer.writerow(['Content', 'Type', 'Date'])
            writer.writerow([self.content, 'Translation', ''])
    
    def export_audio(self, filepath, format_type):
        """Export as audio file"""
        if not self.morse_code:
            messagebox.showerror("Error", "No Morse code to export")
            return
        
        try:
            from core.audio_exporter import AudioExporter
            exporter = AudioExporter()
            wpm = getattr(self, 'wpm_var', ctk.IntVar(value=20)).get()
            
            if format_type == 'wav':
                exporter.export_as_wav(self.morse_code, Path(filepath), wpm)
            else:
                exporter.export_as_mp3(self.morse_code, Path(filepath), wpm)
        except ImportError:
            messagebox.showerror("Error", "Audio export requires soundfile or pydub")
