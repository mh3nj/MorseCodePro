import json
from pathlib import Path

class MorseEngine:
    def __init__(self):
        self.maps = {}
        self.current_map = "english"
        self.load_maps()
    
    def load_maps(self):
        maps_dir = Path(__file__).parent.parent / "config" / "morse_maps"
        for map_file in maps_dir.glob("*.json"):
            lang = map_file.stem
            with open(map_file, 'r', encoding='utf-8') as f:
                self.maps[lang] = json.load(f)
    
    def text_to_morse(self, text: str, language: str = None) -> str:
        lang = language or self.current_map
        char_map = self.maps.get(lang, self.maps["english"])
        
        result = []
        for char in text.upper():
            if char in char_map:
                result.append(char_map[char])
            else:
                result.append("?")
        return ' '.join(result)
    
    def morse_to_text(self, morse: str, language: str = None) -> str:
        lang = language or self.current_map
        char_map = self.maps.get(lang, self.maps["english"])
        
        # Build reverse map
        reverse_map = {v: k for k, v in char_map.items()}
        
        # Handle word separators (/)
        words = morse.split('/')
        result = []
        
        for word in words:
            letters = word.strip().split()
            decoded = ''.join(reverse_map.get(letter, '?') for letter in letters)
            result.append(decoded)
        
        return ' '.join(result)
    
    def breakdown_word(self, word: str, language: str = None) -> list:
        lang = language or self.current_map
        char_map = self.maps.get(lang, self.maps["english"])
        
        breakdown = []
        for char in word.upper():
            if char in char_map:
                breakdown.append({
                    "letter": char,
                    "morse": char_map[char]
                })
        return breakdown
