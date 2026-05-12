"""
User Settings Manager - Save/Load preferences
"""

import json
from pathlib import Path

class SettingsManager:
    def __init__(self):
        self.settings_file = Path(__file__).parent / "user_settings.json"
        self.default_settings = {
            'theme': 'dark',
            'language': 'english',
            'audio_speed': 1.0,
            'auto_backup': True,
            'mic_sensitivity': 50,
            'tts_rate': 150,
            'tts_volume': 0.8,
            'recent_files': [],
            'favorite_translations': [],
            'last_language': 'english',
            'show_waveform': True,
            'confidence_threshold': 60
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new settings added)
                    merged = self.default_settings.copy()
                    merged.update(loaded)
                    return merged
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()
    
    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()
    
    def add_recent_file(self, filepath):
        """Add file to recent files list"""
        recent = self.settings.get('recent_files', [])
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        self.settings['recent_files'] = recent[:10]  # Keep last 10
        self.save_settings()
    
    def add_favorite(self, text, morse):
        """Add translation to favorites"""
        favorites = self.settings.get('favorite_translations', [])
        favorite = {'text': text, 'morse': morse, 'date': str(Path(__file__).stat().st_mtime)}
        
        # Remove if exists
        favorites = [f for f in favorites if f['text'] != text]
        favorites.insert(0, favorite)
        
        self.settings['favorite_translations'] = favorites[:20]  # Keep last 20
        self.save_settings()
