"""
AudioPlayer - cross-platform Morse beep player
Priority: simpleaudio (best) → sounddevice (numpy sine) → winsound → bell
"""

import threading
import time
import numpy as np


def _generate_tone(frequency: int, duration_ms: int, sample_rate: int = 44100) -> np.ndarray:
    """Return int16 mono PCM samples for a sine-wave beep with fade in/out."""
    n = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n, endpoint=False)
    wave = 0.45 * np.sin(2 * np.pi * frequency * t)
    # 5 ms fade in + fade out to avoid clicks
    fade = min(int(sample_rate * 0.005), n // 4)
    if fade > 0:
        wave[:fade]  *= np.linspace(0, 1, fade)
        wave[-fade:] *= np.linspace(1, 0, fade)
    return (wave * 32767).astype(np.int16)


# detect best backend once at import time
_BACKEND = None

try:
    import simpleaudio as _sa
    _BACKEND = 'simpleaudio'
except ImportError:
    pass

if _BACKEND is None:
    try:
        import sounddevice as _sd
        _BACKEND = 'sounddevice'
    except ImportError:
        pass

if _BACKEND is None:
    try:
        import winsound as _ws
        _BACKEND = 'winsound'
    except ImportError:
        pass

if _BACKEND is None:
    _BACKEND = 'bell'

print(f"AudioPlayer backend: {_BACKEND}")


class AudioPlayer:
    def __init__(self):
        self.is_playing = False
        self.speed      = 1.0
        self.frequency  = 800
        self._stop_flag = threading.Event()

    # ── public API ───────────────────────────────────────────────────
    def play_morse(self, morse_code: str):
        """Play a morse string asynchronously. Stops any current playback."""
        self.stop()
        self._stop_flag.clear()
        threading.Thread(target=self._play_loop, args=(morse_code,), daemon=True).start()

    def stop(self):
        self._stop_flag.set()
        self.is_playing = False

    def set_speed(self, speed: float):
        self.speed = max(0.3, min(4.0, float(speed)))

    # ── playback loop ─────────────────────────────────────────────────
    def _play_loop(self, morse_code: str):
        self.is_playing = True
        dit_ms  = max(40, int(120 / self.speed))   # base dit length
        dah_ms  = dit_ms * 3
        gap_ms  = dit_ms                            # inter-symbol gap
        lspc_ms = dit_ms * 3                        # letter space
        wspc_ms = dit_ms * 7                        # word space

        for symbol in morse_code:
            if self._stop_flag.is_set():
                break
            if symbol == '.':
                self._beep(dit_ms)
                self._sleep(gap_ms)
            elif symbol == '-':
                self._beep(dah_ms)
                self._sleep(gap_ms)
            elif symbol == ' ':
                self._sleep(lspc_ms - gap_ms)      # already waited gap_ms
            elif symbol == '/':
                self._sleep(wspc_ms)

        self.is_playing = False

    # ── low-level beep ────────────────────────────────────────────────
    def _beep(self, duration_ms: int):
        if _BACKEND == 'simpleaudio':
            try:
                samples = _generate_tone(self.frequency, duration_ms)
                play_obj = _sa.play_buffer(samples, 1, 2, 44100)
                play_obj.wait_done()
                return
            except Exception:
                pass

        if _BACKEND == 'sounddevice':
            try:
                samples = _generate_tone(self.frequency, duration_ms).astype(np.float32) / 32768.0
                _sd.play(samples, samplerate=44100, blocking=True)
                return
            except Exception:
                pass

        if _BACKEND == 'winsound':
            try:
                _ws.Beep(self.frequency, duration_ms)
                return
            except Exception:
                pass

        # last resort: terminal bell + sleep
        print('\a', end='', flush=True)
        time.sleep(duration_ms / 1000)

    def _sleep(self, ms: int):
        if ms > 0 and not self._stop_flag.is_set():
            time.sleep(ms / 1000)
