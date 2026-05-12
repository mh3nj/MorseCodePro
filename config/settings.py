import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
MAPS_DIR = BASE_DIR / "config" / "morse_maps"

# Create directories
for dir_path in [DATA_DIR, BACKUP_DIR, MAPS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# App settings
APP_NAME = "Morse Code Professional Suite"
VERSION = "2.0.0"
DEFAULT_LANGUAGE = "english"

# Morse timing (milliseconds)
DIT_DURATION = 100  # Base unit
DAH_DURATION = 300
WORD_SPACING = 700
LETTER_SPACING = 300

# Audio settings
SAMPLE_RATE = 44100
FREQUENCY = 800  # Hz for Morse tones
MIC_BUFFER_SIZE = 1024
SILENCE_THRESHOLD = 500  # Amplitude threshold

# Theme colors (glassmorphism)
THEMES = {
    "dark": {
        "bg": "#1a1a2e",
        "glass": "rgba(255,255,255,0.1)",
        "text": "#ffffff",
        "accent": "#00d9ff"
    },
    "light": {
        "bg": "#f0f0f0",
        "glass": "rgba(255,255,255,0.7)",
        "text": "#000000",
        "accent": "#0066cc"
    }
}
