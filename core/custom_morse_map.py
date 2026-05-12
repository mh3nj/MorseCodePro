"""
Custom Morse Code Mapping for any language
"""

import json
from pathlib import Path

class CustomMorseMap:
    def __init__(self):
        self.maps_dir = Path(__file__).parent.parent / "config" / "morse_maps"
        self.maps_dir.mkdir(parents=True, exist_ok=True)
        self.custom_maps_file = self.maps_dir / "custom_maps.json"
        self.load_custom_maps()
    
    def load_custom_maps(self):
        """Load custom maps from file"""
        if self.custom_maps_file.exists():
            with open(self.custom_maps_file, 'r', encoding='utf-8') as f:
                self.maps = json.load(f)
        else:
            self.maps = {}
    
    def save_custom_maps(self):
        """Save custom maps to file"""
        with open(self.custom_maps_file, 'w', encoding='utf-8') as f:
            json.dump(self.maps, f, ensure_ascii=False, indent=2)
    
    def add_mapping(self, language: str, character: str, morse: str):
        """Add custom character mapping"""
        if language not in self.maps:
            self.maps[language] = {}
        
        self.maps[language][character.upper()] = morse
        self.save_custom_maps()
        return True
    
    def remove_mapping(self, language: str, character: str):
        """Remove custom mapping"""
        if language in self.maps and character.upper() in self.maps[language]:
            del self.maps[language][character.upper()]
            self.save_custom_maps()
            return True
        return False
    
    def get_mappings(self, language: str) -> dict:
        """Get all mappings for a language"""
        return self.maps.get(language, {})
    
    def get_all_languages(self) -> list:
        """Get all languages with custom mappings"""
        return list(self.maps.keys())
    
    # Example Persian mappings
    PERSIAN_MORSE = {
        'آ': '.--.-', 'ب': '-...', 'پ': '.--.', 'ت': '-', 'ث': '...-.',
        'ج': '.---', 'چ': '---.', 'ح': '....', 'خ': '-.-.', 'د': '-..',
        'ذ': '--..', 'ر': '.-.', 'ز': '--..', 'ژ': '--.-', 'س': '...',
        'ش': '----', 'ص': '.-...', 'ض': '...-.', 'ط': '..-', 'ظ': '.--.',
        'ع': '.-.-', 'غ': '--.', 'ف': '..-.', 'ق': '--.-', 'ک': '-.-',
        'گ': '--.', 'ل': '.-..', 'م': '--', 'ن': '-.', 'و': '.--',
        'ه': '....', 'ی': '..--'
    }
