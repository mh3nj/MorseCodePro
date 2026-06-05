import json
import csv
from pathlib import Path
import soundfile as sf
import numpy as np
from typing import Dict, Any

class FileHandler:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.export_dir = data_dir / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    def export_as_txt(self, content: str, filename: str) -> Path:
        """Export translation as text file"""
        filepath = self.export_dir / f"{filename}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    
    def export_as_json(self, data: Dict[str, Any], filename: str) -> Path:
        """Export translation history as JSON"""
        filepath = self.export_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath
    
    def export_as_csv(self, history: list, filename: str) -> Path:
        """Export translation history as CSV"""
        filepath = self.export_dir / f"{filename}.csv"
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'input', 'output', 'language'])
            writer.writeheader()
            writer.writerows(history)
        return filepath
    
    def export_as_morse_audio(self, morse_code: str, filename: str, 
                             audio_player) -> Path:
        """Export Morse code as audio file (WAV/MP3)"""
        filepath = self.export_dir / f"{filename}.wav"
        
        # Generate audio data
        audio_data = audio_player.morse_to_audio(morse_code)
        
        # Save as WAV
        sf.write(filepath, audio_data, 44100)
        
        return filepath
    
    def import_file(self, filepath: Path):
        """Import supported file types"""
        ext = filepath.suffix.lower()
        
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        elif ext in ['.wav', '.mp3', '.opus']:
            # Audio file - return path for processing
            return filepath
        
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def get_supported_import_formats(self) -> list:
        """Return list of supported import formats"""
        return ['.txt', '.json', '.wav', '.mp3', '.opus', '.csv']
    
    def get_supported_export_formats(self) -> list:
        """Return list of supported export formats"""
        return ['.txt', '.json', '.csv', '.wav']