<div align="center">

<img src="/assets/banner.png" alt="Morse Code Pro's Banner" width="100%" loading="lazy">

# Morse Code Pro

**translate. listen. detect. learn. practice. master.**

a professional desktop toolkit for morse code — built entirely offline, with no telemetry, no internet required, and no compromises on quality.

[![python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![license MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![version 2.0](https://img.shields.io/badge/version-1.5-orange.svg)]()
[![platform windows](https://img.shields.io/badge/platform-windows-lightgrey.svg)]()

</div>

---

<table>
    <tr>
        <td>
            <img alt="main window light theme screenshot of morse code pro python app" width="100%" src="/screenshots/1.png">
        </td>
        <td>
            <img alt="main window dark theme screenshot of morse code pro python app" width="100%" src="/screenshots/2.png">
        </td>
    </tr>
</table>

---

## what is Morse Code Pro?

Morse Code Pro is a complete desktop suite for anyone who works with or wants to learn morse code. whether you are a ham radio operator, a student, a professional in emergency communications, or just curious about telegraphy history, this app brings everything you need into one clean window.

it converts text to morse and morse to text across six languages, plays back audio beeps with adjustable speed, listens to your microphone in real time, and teaches you the alphabet letter by letter with a scoring system. everything runs on your computer with zero data leaving your machine.

---

## six integrated tools

| tab | what it does |
|-----|-------------|
| translation | converts text to morse and morse to text across six languages instantly |
| word breakdown | shows each letter with its morse pattern side by side for study |
| learn morse | alphabet and advanced practice modes with live scoring |
| history | stores every translation in a local sqlite database with search and export |
| microphone | listens to beeps through your mic and transcribes them to text in real time |
| favorites | saves and organizes translations you want to keep |

---

## screenshots


<table>
    <tr>
        <td>
            <img alt="translation window dark theme screenshot of morse code pro python app" width="100%" src="/screenshots/6.png">
        </td>
        <td>
            <img alt="learning window dark theme screenshot of morse code pro python app" width="100%" src="/screenshots/3.png">
        </td>
    </tr>
</table>

---

## getting started

### requirements

- Python 3.11 or newer
- works on Windows (Linux and macOS mostly supported)

# how to Run Morse Code Pro

### option 1: From Source (Python required)

```bash
# Clone the repository
git clone https://github.com/mh3nj/MorseCodePro.git
cd MorseCodePro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the app
python main.py
```

### option 2: Using the Cross-Platform Launcher

```bash
# Windows
launch.bat

# macOS / Linux
chmod +x launch.sh
./launch.sh
```

### option 3: Universal Python Installer

```bash
python install.py
```

---

## First Launch Tips

- **Microphone detection**: Keep quiet for 1-2 seconds after clicking "Start Listening"; the app auto-calibrates to your background noise
- **Audio playback**: Use the speed slider (0.5x to 3x) to adjust playback speed
- **Learning mode**: Start with Alphabet mode before moving to Advanced
- **Dark/Light theme**: Toggle using the button in the top-right corner

---

## System Requirements

- **Python**: 3.11 or newer (for source installation)
- **OS**: Windows 10/11 (fully supported), macOS/Linux (mostly supported)
- **RAM**: 256MB minimum, 512MB recommended
- **Storage**: 150MB for source code + dependencies

---

## Need Help?

- Press `F1` inside the app for help
- Check the [Issues](https://github.com/mh3nj/MorseCodePro/issues) page
- Open a new issue with your error log

---

**That's it! Start your Morse journey today!**

---

## features

### translation engine

converts between text and morse code in six languages: English, Persian (Farsi), German, Turkish, Spanish, and French. each language has its own JSON mapping file so you can extend or customize them freely. the engine correctly handles word spacing, special characters, and multi-word inputs.

### audio playback

plays morse code as clean 800Hz sine wave beeps. speed is adjustable from 0.5x to 3x with a slider. the audio backend automatically picks the best available library on your system (simpleaudio, sounddevice, or winsound) so it works on any machine.

### live microphone detection

listens to your microphone and transcribes beeps into text in real time. on startup it auto-calibrates to your mic's background noise so you do not need to fiddle with settings. a volume meter shows signal level and a live symbol preview displays each dit and dah as you make them. sensitivity is adjustable with a slider for different microphone types.

### learning and practice

alphabet mode shows random letters and asks you to type their morse equivalent. advanced mode uses a dictionary of common words at three difficulty levels. every correct answer adds 10 points. there is also a word breakdown view that shows each character alongside its morse pattern for study, and a metronome for timing practice with adjustable BPM.

### history and backup

every translation is stored automatically in a local sqlite database. you can browse, search, and export the full history as CSV or JSON. an auto-backup system runs hourly and keeps the last 10 compressed backups. manual backup and restore are also available.

### import and export

exports to TXT, JSON, CSV, WAV, and MP3. imports from text files, JSON, and morse audio files (WAV, MP3, OPUS). WAV and MP3 export generates a real audio file of the morse beeps. MP3 requires pydub and ffmpeg installed separately.

---

## keyboard shortcuts

| shortcut | action |
|----------|--------|
| Ctrl + Enter | convert |
| Ctrl + S | export output |
| Ctrl + C | copy output |
| Ctrl + L | clear all fields |
| Ctrl + H | show shortcuts |
| Ctrl + Plus | increase playback speed |
| Ctrl + Minus | decrease playback speed |
| F1 | open help dialog |

---

## morse code reference

| letter | morse | letter | morse | number | morse |
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
| J | .--- | W | .-- | 9 | ----. |
| K | -.- | X | -..- | | |
| L | .-.. | Y | -.-- | | |
| M | -- | Z | --.. | | |

**format rules:** `.` is a dit (short), `-` is a dah (long), a space separates letters, `/` separates words.

---

## project structure

```
MorseCodePro/
├── main.py
├── requirements.txt
├── config/
│   ├── settings.py
│   ├── settings_manager.py
│   └── morse_maps/
│       ├── english.json
│       ├── persian.json
│       ├── german.json
│       ├── turkish.json
│       ├── spanish.json
│       └── french.json
├── core/
│   ├── morse_engine.py
│   ├── morse_detector.py
│   ├── audio_player_fixed.py
│   ├── audio_exporter.py
│   ├── metronome.py
│   └── confidence_scorer.py
├── gui/
│   ├── main_app.py
│   ├── microphone_panel.py
│   ├── teaching_panel.py
│   ├── word_breakdown.py
│   ├── history_panel.py
│   ├── favorites_panel.py
│   └── export_dialog.py
├── models/
│   └── history_db.py
├── utils/
│   ├── backup_manager.py
│   └── file_handler.py
├── assets/
│   └── icons/
└── data/
    ├── history.db
    └── backups/
```

---

## troubleshooting

**microphone not detected**
open a terminal and run `python -c "import sounddevice as sd; print(sd.query_devices())"` to list available devices. on Windows, go to Settings, Privacy, Microphone and make sure app access is enabled. then use the dropdown in the microphone tab to select the correct device.

**no audio playback**
the app tries simpleaudio first, then sounddevice, then winsound. if all three fail, run `pip install simpleaudio sounddevice` and try again.

**import errors on startup**
run `pip install -r requirements.txt` to make sure all dependencies are installed. if pydub or ffmpeg errors appear, those are only needed for MP3 export and can be safely ignored for other features.

**microphone detection inaccurate**
use clean, short beeps at a consistent pitch between 600 and 1400 Hz. the detector auto-calibrates on startup, so keep quiet for the first one to two seconds after pressing start. if it still misses beeps, move the sensitivity slider to the left to make it more sensitive.

---

## known limitations

- microphone detection works best with pure tone beeps and will not transcribe speech
- Persian and Farsi require the included custom mapping files which are already bundled
- MP3 export requires pydub and ffmpeg installed separately
- Linux and macOS are mostly supported but have not been extensively tested

---

## fun facts

- morse code was invented in 1836 by Samuel Morse
- SOS (... --- ...) is not an acronym, it was chosen purely for its simple symmetric pattern
- the fastest morse code speed ever recorded was 75.2 words per minute
- Morse Code Pro can detect morse at up to 40 WPM
- the word "morse" in morse code is: -- --- .-. ... .

---

## author

**Mohsen Jafari**.

built during internet restrictions in Iran. proof that creativity and persistence know no boundaries.

- GitHub: [github.com/mh3nj](https://github.com/mh3nj)
- Xing: [Mohsen Jafari's Xing Profile](https://www.xing.com/profile/Mohsen_Jafari093223/)
- logo design portfolio: [Parsegan.com](https://parsegan.com)
- land survey / portfolio: [Dahgan.com](https://dahgan.com)

---

## license

MIT license. free for personal and commercial use. share, modify, and distribute freely.
