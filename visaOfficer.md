# Morse Code Pro — software development timeline

**applicant:** Mohsen Jafari
**project title:** Morse Code Pro v2.0
**development period:** May 10, 2026 to May 15, 2026
**total development time:** approximately 42 hours across 6 days
**total lines of code:** 8,500+ (Python)

---

## purpose of this document

this document provides a detailed, day-by-day account of the development of Morse Code Pro, a professional desktop application for morse code translation, audio playback, live microphone detection, and learning. it is intended to demonstrate the scope, complexity, and timeline of the project as evidence of independent software development work.

---

## project overview

Morse Code Pro is a fully offline desktop application built with Python. it allows users to convert text to morse code and back across six languages (English, Persian/Farsi, German, Turkish, Spanish, and French), listen to audio playback of morse code, practice through interactive learning exercises, and detect live morse code signals through a microphone with real-time transcription.

the project was developed entirely independently by Mohsen Jafari during a period of internet restrictions in Iran, using locally available tools and documentation.

**technology stack:** Python 3.11, customtkinter, sounddevice, numpy, scipy, sqlite3, pyttsx3, simpleaudio, pydub, matplotlib

---

## day-by-day development log

### day 1 — May 10, 2026 (foundation)
**total time: approximately 6 hours**

the first day was focused entirely on architecture and the core translation engine. no UI work was done yet — this day established the data structures and logic that every other feature would depend on.

**morning session (3 hours)**

work began with planning the overall project structure. the decision was made to use JSON-based mapping files for each language rather than hardcoding character maps, which would allow easy extension to new languages later. a Python virtual environment was configured and the repository was initialized.

the core morse engine was written from scratch. it handles bidirectional conversion: text to morse (splitting input into characters, looking up each in the language map, joining with spaces) and morse to text (splitting on spaces and slashes, doing a reverse lookup). edge cases such as unknown characters, word boundaries, and multi-word inputs were handled.

**afternoon session (3 hours)**

the multi-language architecture was finalized. individual JSON mapping files were created for English (A-Z, 0-9), Persian (Farsi) with 32 letters and custom Unicode mappings, German with extended Latin characters (Ä, Ö, Ü, ß), and Turkish with its specific diacritics (Ç, Ğ, İ, Ş). each file follows the same key-value structure so the engine can load any of them identically.

the engine was tested manually against known morse sequences to verify accuracy before any UI work began.

**milestone reached:** core translation engine complete and tested

---

### day 2 — May 11, 2026 (user interface)
**total time: approximately 8 hours**

the second day was dedicated to building the graphical interface. the UI framework chosen was customtkinter, which provides modern-looking widgets on top of tkinter with support for dark and light themes.

**morning session (4 hours)**

the main window layout was designed using a two-column structure: an input panel on the left and an output panel on the right. each panel uses a tab view so the user can switch between text-to-morse input and morse-to-text input without losing context. the glassmorphism visual style was implemented using semi-transparent frames, rounded corners, and a consistent accent color system.

a placeholder text system was added to both input areas so users see guidance before they start typing.

**afternoon session (4 hours)**

the translation panel was connected to the core engine. the convert button triggers the appropriate conversion direction depending on which input has content. a status bar was added at the bottom to show progress and confirmation messages.

the dark and light theme toggle was implemented using customtkinter's appearance mode system. audio control buttons (play morse, stop, speak output) were added with a speed slider from 0.5x to 3x. a keyboard shortcut system was bound at the window level (Ctrl+Enter to convert, Ctrl+S to export, Ctrl+L to clear, F1 for help, and others).

a bug was found and fixed during this session: the placeholder text was not clearing when the user clicked into the input field. this was resolved by binding a FocusIn event to delete the placeholder on first focus.

**milestone reached:** graphical interface functional with full translation workflow

---

### day 3 — May 12, 2026 (audio and teaching)
**total time: approximately 8 hours**

**morning session (4 hours)**

the audio playback engine was written. it generates pure 800Hz sine wave tones using numpy, with timing derived from the selected words-per-minute speed. a dit (short beep) is one unit, a dah (long beep) is three units, letter spacing is three units of silence, and word spacing is seven units. the engine was designed with a backend priority chain: simpleaudio is tried first for best quality, then sounddevice for numpy-based playback, then winsound as a Windows fallback. playback runs in a background thread so the interface stays responsive.

text-to-speech output was integrated using pyttsx3, which runs entirely offline. it reads back the decoded text in a background thread to avoid blocking the UI.

the word breakdown feature was written. it takes any word, splits it letter by letter, and returns each character paired with its morse representation. this is used in the breakdown tab for visual study.

**afternoon session (4 hours)**

the teaching section was built as a standalone panel. alphabet mode randomly selects a letter or number, displays its morse code, and asks the user to type the character. advanced mode uses a built-in dictionary of 200+ common words grouped by length (easy: 3-4 letters, medium: 5-7, hard: 8+). both modes give immediate visual and audio feedback and award 10 points per correct answer.

the SQLite history database was integrated. every conversion is stored with a timestamp, input text, output text, conversion direction, and language. the database uses thread-local connections to avoid threading errors. the history panel displays the last 50 entries and can clear the database on user confirmation.

export functionality was added for TXT, JSON, and CSV formats. each format includes the translated content and optional metadata.

**milestone reached:** audio playback, TTS, learning module, and history database complete

---

### day 4 — May 13, 2026 (microphone detection)
**total time: approximately 10 hours**

this was the most technically demanding day of the project. real-time audio signal processing requires careful handling of threading, timing, and signal analysis.

**morning session (4 hours)**

microphone input was set up using sounddevice's InputStream with a callback-based architecture. audio chunks arrive as float32 numpy arrays at 44,100 Hz sample rate. each chunk's RMS amplitude is calculated to measure volume level.

the volume meter was built using a canvas widget that updates in real time. a red threshold line shows the detection cutoff. initial implementation used a fixed amplitude threshold, but it quickly became clear this would not work reliably across different microphones and environments.

the basic dit and dah detection logic was written: measure how long a sound lasts, classify it as a dit if short or a dah if long, accumulate symbols until a silence indicates the end of a letter, and emit the decoded letter.

**afternoon session (4 hours)**

FFT-based frequency analysis was added to filter out speech and background noise. only sounds whose dominant frequency falls between 700 and 1300 Hz (the range of standard morse beeps) are counted as valid signals. this prevents the app from interpreting conversation or ambient noise as morse code.

the pause detection logic was refined. a pause of 0.3 seconds or more signals the end of a letter. a pause of 0.8 seconds or more signals the end of a word. the decoded letters are assembled into words and words into sentences in real time.

a sensitivity slider was added to the microphone panel. it maps a 0-to-100 percent value to a detection threshold range so users can tune the app to their specific microphone without understanding the underlying signal values.

**evening session (2 hours)**

a keyboard mode was added as an alternative to microphone input. the user presses and holds the spacebar: a short press produces a dit and a long press produces a dah. this is useful for practice without a microphone. a device selection dropdown was added so users with multiple microphones can choose which one the app listens to.

**milestone reached:** live microphone detection working with frequency filtering and device selection

---

### day 5 — May 14, 2026 (advanced features)
**total time: approximately 8 hours**

**morning session (3 hours)**

a metronome was added for timing practice. it generates click sounds at a user-selected BPM using the same audio backend as the morse player. every fourth beat is accented (louder and higher pitch) to mark the start of a measure.

an audio exporter was written that takes a morse string and generates a real WAV or MP3 audio file. WAV export uses numpy and soundfile directly. MP3 export requires pydub and ffmpeg but degrades gracefully with a clear message if those are not installed.

a waveform visualizer was added using matplotlib embedded in a tkinter canvas, showing the audio signal shape for educational purposes.

**afternoon session (3 hours)**

a favorites panel was added. the user can save any translation (text and morse together) with the current timestamp. favorites persist between sessions in a JSON file. up to 20 favorites can be stored (configurable). a single click loads a favorite back into the main translation fields.

a custom morse map editor was added. users can define their own character-to-morse mappings for characters not in the standard sets. these are stored in a separate JSON file and merged with the active language map at load time.

audio file import was implemented. WAV, FLAC, and OGG files can be loaded using soundfile. MP3, OPUS, and M4A files use pydub. the imported audio is processed through the same detection pipeline as live microphone input to extract the morse content.

drag and drop support was added for the file import panel using tkinterdnd2.

**evening session (2 hours)**

the backup manager was written. it runs on a background timer every hour and creates a compressed ZIP archive of the database, custom maps, and settings file. the last 10 backups are kept automatically. manual backup and restore buttons were added to the settings area.

user preferences (last language used, theme choice, sensitivity level) are saved to a JSON settings file on close and restored on next launch.

**milestone reached:** all advanced features complete including metronome, favorites, audio import, custom maps, and backup system

---

### day 6 — May 15, 2026 (polish and release)
**total time: approximately 4 hours**

**morning session (2 hours)**

final keyboard shortcuts were bound and tested. a help dialog was written explaining all features and controls with formatting instructions. the status bar was improved to show more contextual information (character count, word count, current language, history count).

edge case handling was reviewed across all panels: empty inputs, very long strings, unknown characters in non-English text, failed audio device initialization, and corrupted database entries. appropriate error messages and fallbacks were added throughout.

**afternoon session (2 hours)**

the application was tested end-to-end on Windows. a full README.md was written covering installation, features, keyboard shortcuts, troubleshooting, and the morse code reference table. this development timeline document was written.

**milestone reached:** project complete and documented

---

## summary of features delivered

| category | features |
|----------|----------|
| translation | bidirectional text and morse conversion in 6 languages |
| audio playback | 800Hz sine wave, 0.5x to 3x speed, cross-platform backend |
| text-to-speech | offline TTS via pyttsx3 |
| microphone detection | real-time, FFT frequency filtering, adaptive threshold, device selection |
| learning | alphabet mode, advanced word mode, scoring system |
| word breakdown | letter-by-letter visual analysis |
| history | sqlite database, search, CSV and JSON export |
| export | TXT, JSON, CSV, WAV, MP3 |
| import | TXT, JSON, WAV, MP3, OPUS audio files |
| metronome | adjustable BPM with accent on beat 1 |
| favorites | persistent saved translations with one-click restore |
| custom maps | user-defined character mappings for any language |
| backup | hourly auto-backup, manual backup and restore |
| UI | glassmorphism dark and light theme, keyboard shortcuts, drag and drop |

---

## technical statistics

| metric | value |
|--------|-------|
| total development days | 6 |
| total estimated hours | approximately 42 |
| total lines of Python code | 8,500+ |
| total Python source files | 22 |
| language mapping files (JSON) | 6 |
| keyboard shortcuts | 10+ |
| export formats supported | 5 |
| import formats supported | 5 |
| integrated feature tabs | 6 |

---

## challenges encountered and how they were solved

**microphone detecting background noise as morse signals**
the initial amplitude-only approach had no way to distinguish morse beeps from speech or ambient sound. FFT analysis was added to check that the dominant frequency of any detected sound falls within the 700-1300 Hz range typical of morse beeps. this eliminated almost all false positives from voice and environmental noise.

**threshold not working across different microphones**
a fixed threshold value that worked well on one microphone was either too sensitive or not sensitive enough on others. an auto-calibration routine was added that measures the background noise level for 1.5 seconds on startup and sets the threshold as a multiple of the measured noise floor. users can further adjust it with a sensitivity slider.

**sqlite threading errors**
Python's sqlite3 module does not allow the same connection object to be used from multiple threads. this was solved by using thread-local storage so each thread creates and uses its own connection to the same database file.

**audio playback blocking the user interface**
early versions ran audio playback on the main thread, which froze the UI for the duration of the beeps. all audio operations were moved to background daemon threads. UI updates from those threads are scheduled back to the main thread using tkinter's `after()` mechanism.

**Persian and Farsi character encoding**
Python's standard string handling works correctly with Unicode, but the morse mapping files needed to be saved with explicit UTF-8 encoding and loaded with the same. all file operations were updated to specify `encoding='utf-8'` explicitly.

---

## author

**Mohsen Jafari**
independent software developer, logo designer, and land surveyor

this project was developed entirely independently during internet restrictions in Iran. all documentation, research, and testing was done with locally available resources.

- GitHub: [github.com/mh3nj](https://github.com/mh3nj)
- LinkedIn: [linkedin.com/in/mh3nj](https://linkedin.com/in/mh3nj)
- logo design: [Parsegan.com](https://parsegan.com)
- surveying portfolio: [Dahgan.com](https://dahgan.com)
