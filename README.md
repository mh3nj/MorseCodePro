# 📡 Morse Code Pro – Complete Morse Communication Toolkit

**Status:** Stable Release v2.0  
**Build Date:** May 12, 2026

A professional desktop application for Morse code enthusiasts, learners, and professionals – translate, transcribe, learn, and practice Morse code with **live microphone detection**, **multi-language support**, **audio processing**, and **beautiful glassmorphism UI** – all offline, privacy-focused, and completely free.

---

## About Morse Code Pro

Morse Code Pro is a complete Morse code command center designed for everyone from beginners learning their first letter to professionals working with Morse communication. Named for its ability to bridge the gap between traditional Morse and modern digital communication.

### What Morse Code Pro Helps You Do

- **Convert** – Text ↔ Morse instantly in 6+ languages
- **Listen** – Audio playback with speed control (0.5x to 3x)
- **Detect** – Live microphone transcription of Morse beeps
- **Learn** – Built-in teaching section with alphabet and advanced words
- **Export** – Save as TXT, JSON, CSV, WAV, or MP3
- **Track** – Full translation history with SQLite database
- **Practice** – Metronome for timing and word breakdown analysis
- **Personalize** – Custom Morse maps for any language

**6 integrated tools** | **Dark/Light theme** | **100% offline** | **Zero telemetry**

---

## The 6 Core Tools

| Tab | Description |
|-----|-------------|
| Translation | Text ↔ Morse conversion with multi-language support (English, Persian, German, Turkish, Spanish, French) |
| Word Breakdown | Letter-by-letter analysis with visual dit/dah patterns |
| Learn Morse | Alphabet mode + Advanced mode with scoring system |
| History | Complete translation history with search and export |
| Microphone | Live Morse detection from mic with real-time transcription |
| Favorites | Save and organize important translations |

---

## Getting Started

### Option 1: From Source (Python 3.11+ required)

```bash
git clone https://github.com/mh3nj/MorseCodePro.git
cd MorseCodePro
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

### Option 2: Standalone Executable

Download from GitHub Releases. No Python installation required. Just unzip and run MorseCodePro.exe.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Enter | Convert |
| Ctrl+S | Export Output |
| Ctrl+C | Copy Output |
| Ctrl+L | Clear All |
| Ctrl+H | Show Shortcuts |
| Ctrl++ | Increase Speed |
| Ctrl+- | Decrease Speed |
| F1 | Help |

---

## Features In Detail

### Translation Engine
- Convert between text and Morse code instantly
- Support for 6+ languages (English, Persian, German, Turkish, Spanish, French)
- Custom Morse maps for any language/character
- Real-time character counting and validation

### Audio Playback
- Play Morse code as audible beeps (800Hz)
- Adjustable speed from 0.5x to 3x
- Pause/Resume functionality
- Visual waveform representation

### Live Microphone Detection
- Real-time Morse code detection from microphone
- Frequency filtering (700-1300Hz pure tones)
- Adjustable sensitivity slider
- Volume meter with visual feedback
- Support for beep mode and keyboard mode

### Learning & Practice
- **Alphabet Mode** – Learn letters and numbers with instant feedback
- **Advanced Mode** – Practice with real words and phrases
- **Scoring System** – Track your progress (10 points per correct answer)
- **Word Breakdown** – See letter-by-letter translation with visual patterns
- **Metronome** – Practice timing with adjustable BPM

### History & Backup
- Automatic history storage in SQLite database
- Search through previous translations
- Export history as CSV or JSON
- Auto-backup system (hourly)
- Manual backup and restore

### Import/Export
- **Import:** Text files, JSON, Morse audio (WAV/MP3/OPUS)
- **Export:** TXT, JSON, CSV, WAV, MP3
- Metadata inclusion (timestamp, language, confidence score)
- Drag & drop file support

### Customization
- Dark/Light theme toggle
- Glassmorphism UI design
- Adjustable playback speed
- Custom Morse character mappings
- Sensitivity adjustment for microphone

---

## Project Structure

```
MorseCodePro/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   ├── settings.py         # App configuration
│   ├── settings_manager.py # User preferences
│   └── morse_maps/         # Language mappings (JSON)
│       ├── english.json
│       ├── persian.json
│       ├── german.json
│       └── turkish.json
├── core/
│   ├── morse_engine.py     # Core conversion logic
│   ├── morse_detector.py   # Microphone detection
│   ├── audio_player.py     # Audio playback
│   ├── audio_exporter.py   # Export as WAV/MP3
│   ├── metronome.py        # Practice metronome
│   └── confidence_scorer.py # Detection accuracy
├── gui/
│   ├── main_app.py         # Main window
│   ├── microphone_panel.py # Mic detection UI
│   ├── teaching_panel.py   # Learning section
│   ├── word_breakdown.py   # Letter analysis
│   ├── history_panel.py    # History viewer
│   ├── favorites_panel.py  # Saved translations
│   └── export_dialog.py    # Export options
├── models/
│   └── history_db.py       # SQLite database
├── utils/
│   ├── backup_manager.py   # Auto backups
│   └── file_handler.py     # Import/Export
├── assets/
│   ├── icons/              # UI icons
│   └── sounds/             # Audio assets
└── data/
    ├── history.db          # SQLite database
    └── backups/            # Backup storage
```

---

## Requirements

- Python 3.11+
- customtkinter (modern UI)
- sounddevice (microphone input)
- numpy, scipy (audio processing)
- pyttsx3 (text-to-speech)
- soundfile, pydub (audio file handling)
- keyboard (optional, for keyboard mode)
- matplotlib (waveform visualization)

---

## Morse Code Reference

| Letter | Morse | Letter | Morse | Number | Morse |
|--------|-------|--------|-------|--------|-------|
| A | .- | N | -. | 0 | ----- |
| B | -... | O | --- | 1 | .---- |
| C | -.-. | P | .--. | 2 | ..--- |
| D | -.. | Q | --.- | 3 | ...-- |
| E | . | R | .-. | 4 | ....- |
| F | ..-. | S | ... | 5 | ..... |
| G | --. | T | - | 6 | -.... |
| H | .... | U | ..- | 7 | --... |
| I | .. | V | ...- | 8 | ---.. |
| J | .--- | W | .-- | 9 | ---- |
| K | -.- | X | -..- | | |
| L | .-.. | Y | -.-- | | |
| M | -- | Z | --.. | | |

**Format Rules:**
- `.` = dit (short beep)
- `-` = dah (long beep)
- Space = between letters
- `/` = between words

---

## Development Timeline

| Phase | Duration | Key Achievements |
|-------|----------|------------------|
| Day 1 (May 10) | ~6 hours | Core engine: Text ↔ Morse, multi-language maps |
| Day 2 (May 11) | ~8 hours | GUI development: Glassmorphism UI, translation panel |
| Day 3 (May 12) | ~10 hours | Audio: Playback, speed control, TTS |
| Day 4 (May 13) | ~8 hours | Microphone detection, frequency filtering |
| Day 5 (May 14) | ~6 hours | Learning module, word breakdown, history |
| Day 6 (May 15) | ~4 hours | Polish: Export, favorites, metronome, documentation |

**Total:** ~42 hours | **Lines of code:** 8,500+ | **Tabs:** 6 integrated tools

---

## Known Limitations

- Microphone detection works best with **pure tone beeps** (700-1300Hz), not speech
- Speech recognition is **not** supported (Morse detection only)
- Persian/Farsi requires custom mappings (included as reference)
- MP3 export requires `pydub` and `ffmpeg` (optional)

---

## Troubleshooting

### Microphone not working
```bash
# Test your microphone
python -c "import sounddevice as sd; print(sd.query_devices())"

# Adjust Windows settings:
# Settings → Privacy → Microphone → Enable access
```

### Audio playback issues
```bash
# Use winsound fallback (built into Windows)
# The app automatically falls back if simpleaudio fails
```

### Import errors
```bash
# Install all dependencies
pip install -r requirements.txt
```

---

## Author

**Mohsen Jafari** - Creator, Developer, Designer

- GitHub: [mh3nj](https://github.com/mh3nj)
- LinkedIn: [mh3nj](https://linkedin.com/in/mh3nj)
- Websites: [Parsegan.com](https://parsegan.com) (logo design), [Dahgan.com](https://dahgan.com) (land surveying/portfolio)

---

## License

MIT License – Free for personal and commercial use. Share, modify, and distribute freely.

---

## Acknowledgments

- **customtkinter** team – Beautiful modern UI
- **sounddevice** – Cross-platform audio capture
- **numpy/scipy** – Signal processing
- **pyttsx3** – Offline text-to-speech
- **The open-source community** – For endless inspiration

---

## Fun Facts

- Morse code was invented in 1836 by Samuel Morse
- SOS (... --- ...) is not an acronym – it was chosen for its simple pattern
- The fastest Morse code speed ever recorded was 75.2 words per minute
- This app can detect Morse at up to 40 WPM
- The word "Morse" in Morse is: -- --- .-. ... .

---

*Created with passion during internet restrictions in Iran – proof that creativity and persistence know no boundaries.*

**Morse Code Pro – Bridging silence and signal, one beep at a time.** 📡

---

## Star History

⭐ If this project helped you learn Morse code or build something cool, give it a star! It helps others discover the project.
