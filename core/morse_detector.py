"""
Morse Code Detector - Rewritten for accuracy
Fixes:
 - Adaptive calibration replaces fixed threshold
 - Proper FFT pure-tone check (float32 audio, correct freq bins)
 - State machine with debounce so gaps never double-fire
 - Adaptive dit/dah boundary derived from measured beep durations
"""

import threading
import queue
import time
import numpy as np

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


class MorseDetector:
    # ── public tunables ──────────────────────────────────────────────
    SAMPLE_RATE   = 44100
    CHUNK         = 2048          # ~46 ms per chunk
    FREQ_LO       = 500           # Hz  - accept Morse beeps in this band
    FREQ_HI       = 1400
    CALIBRATE_SEC = 1.5           # seconds of silence used for auto-threshold
    NOISE_FACTOR  = 6.0           # threshold = noise_rms * NOISE_FACTOR
    MIN_THRESHOLD = 80            # absolute minimum (avoids over-sensitive)

    # timing (seconds) – updated adaptively after each beep
    MIN_BEEP      = 0.04          # anything shorter → noise, ignore
    MAX_BEEP      = 1.2           # anything longer  → still a dah
    LETTER_GAP    = 0.28          # silence ≥ this  → end of letter
    WORD_GAP      = 0.70          # silence ≥ this  → end of word
    DIT_DAH_RATIO = 2.0           # boundary between dit and dah

    def __init__(self, device_id=None):
        self.device_id   = device_id
        self.is_listening = False
        self._q          = queue.Queue(maxsize=200)

        # detection state
        self._in_beep       = False
        self._beep_start    = 0.0
        self._silence_start = 0.0
        self._cur_letter    = []   # list of '.' / '-'
        self._cur_word      = []   # list of decoded letters

        # adaptive timing
        self._recent_dits   = []   # ring buffer of recent dit durations
        self._dit_ref       = 0.12 # initial guess – updated on the fly

        # threshold (updated by calibrate / set_sensitivity)
        self.threshold = 400
        self._sensitivity_pct = 50

        # callbacks
        self.on_morse_symbol = None   # fn(symbol: str)
        self.on_letter       = None   # fn(letter: str, morse: str)
        self.on_word         = None   # fn(word: str)
        self.on_amplitude    = None   # fn(amplitude: int)

        self._morse_map = {
            '.-':'A',  '-...':'B', '-.-.':'C', '-..':'D',  '.':'E',
            '..-.':'F','.--.':'P', '--.-':'Q', '.-.':'R',  '...':'S',
            '-':'T',   '..-':'U',  '...-':'V', '.--':'W',  '-..-':'X',
            '-.--':'Y','--..':'Z', '--.':'G',  '....':'H', '..':'I',
            '.---':'J', '-.-':'K', '.-..':'L', '--':'M',   '-.':'N',
            '---':'O',
            '-----':'0','.----':'1','..---':'2','...--':'3','....-':'4',
            '.....':'5','-....':'6','--...':'7','---..':'8','----.':'9',
        }

        # find a usable input device if not given
        if AUDIO_AVAILABLE and self.device_id is None:
            self._pick_device()

    # ── device selection ─────────────────────────────────────────────
    def _pick_device(self):
        try:
            devices = sd.query_devices()
            # prefer Razer if present
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0 and 'razer' in d['name'].lower():
                    self.device_id = i
                    return
            # else first input device
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0:
                    self.device_id = i
                    return
        except Exception:
            pass

    # ── public API ───────────────────────────────────────────────────
    def start_listening(self):
        if not AUDIO_AVAILABLE:
            print("sounddevice not installed – cannot listen")
            return False
        try:
            self.is_listening = True
            self._in_beep       = False
            self._silence_start = time.time()
            self._cur_letter    = []
            self._cur_word      = []

            self._stream = sd.InputStream(
                callback=self._audio_cb,
                channels=1,
                samplerate=self.SAMPLE_RATE,
                blocksize=self.CHUNK,
                device=self.device_id,
                dtype='float32',
            )
            self._stream.start()

            # auto-calibrate from background noise
            threading.Thread(target=self._calibrate, daemon=True).start()
            # main FSM loop
            threading.Thread(target=self._fsm_loop, daemon=True).start()

            print(f"✓ MorseDetector listening on device {self.device_id}")
            return True
        except Exception as e:
            print(f"✗ MorseDetector start error: {e}")
            self.is_listening = False
            return False

    def stop_listening(self):
        self.is_listening = False
        if hasattr(self, '_stream'):
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
        print("✓ MorseDetector stopped")

    def set_sensitivity(self, percent: float):
        """0 = most sensitive (low threshold), 100 = least sensitive."""
        self._sensitivity_pct = float(percent)
        # map 0-100 → threshold multiplier 2x – 12x of noise floor
        factor = 2.0 + (percent / 100.0) * 10.0
        # if we have a measured noise floor use it, else use fixed mapping
        noise = getattr(self, '_noise_rms', None)
        if noise and noise > 0:
            self.threshold = max(self.MIN_THRESHOLD, int(noise * factor))
        else:
            self.threshold = max(self.MIN_THRESHOLD, int(100 + percent * 19))
        print(f"✓ threshold = {self.threshold}  (sensitivity {percent:.0f}%)")

    # ── internal audio callback (runs in sounddevice thread) ─────────
    def _audio_cb(self, indata, frames, time_info, status):
        if not self.is_listening:
            return
        chunk = indata[:, 0]                       # mono, float32  -1..+1
        rms   = float(np.sqrt(np.mean(chunk ** 2)) * 32768)   # scale to int16 range
        tone  = self._is_pure_tone(chunk)
        try:
            self._q.put_nowait((rms, tone, time.time()))
        except queue.Full:
            pass

    def _is_pure_tone(self, chunk: np.ndarray) -> bool:
        """True if the dominant frequency is in the Morse beep band."""
        n   = len(chunk)
        fft = np.abs(np.fft.rfft(chunk * np.hanning(n)))
        freqs = np.fft.rfftfreq(n, 1.0 / self.SAMPLE_RATE)

        # ignore DC (bin 0) and very low freqs
        lo_bin = max(1, int(self.FREQ_LO * n / self.SAMPLE_RATE))
        hi_bin = min(len(fft) - 1, int(self.FREQ_HI * n / self.SAMPLE_RATE))
        if hi_bin <= lo_bin:
            return False

        band_power  = np.sum(fft[lo_bin:hi_bin + 1] ** 2)
        total_power = np.sum(fft[1:] ** 2)           # exclude DC
        if total_power < 1e-10:
            return False

        ratio = band_power / total_power
        # pure tone → almost all energy in one band; speech → spread across many
        return ratio > 0.30

    # ── auto-calibration ─────────────────────────────────────────────
    def _calibrate(self):
        """Measure ambient noise for CALIBRATE_SEC seconds, set threshold."""
        samples = []
        deadline = time.time() + self.CALIBRATE_SEC
        while time.time() < deadline and self.is_listening:
            try:
                rms, _, _ = self._q.get(timeout=0.1)
                samples.append(rms)
            except queue.Empty:
                pass
        if samples:
            noise = float(np.percentile(samples, 85))   # 85th-pct as noise floor
            self._noise_rms = noise
            factor = 2.0 + (self._sensitivity_pct / 100.0) * 10.0
            self.threshold = max(self.MIN_THRESHOLD, int(noise * factor))
            print(f"✓ Auto-calibrated: noise={noise:.1f}, threshold={self.threshold}")

    # ── finite-state machine loop ─────────────────────────────────────
    def _fsm_loop(self):
        """
        Reads (rms, is_tone, ts) tuples.
        State: _in_beep  True = beep ongoing, False = silence
        """
        while self.is_listening:
            try:
                rms, is_tone, ts = self._q.get(timeout=0.06)
            except queue.Empty:
                # nothing came in – check for letter / word timeout
                if not self._in_beep:
                    self._check_gaps(time.time())
                continue

            active = is_tone and (rms > self.threshold)

            if self.on_amplitude:
                try:
                    self.on_amplitude(int(rms))
                except Exception:
                    pass

            if active and not self._in_beep:
                # ── rising edge: silence → beep ───────────────────
                self._in_beep    = True
                self._beep_start = ts
                self._silence_start = 0.0

            elif not active and self._in_beep:
                # ── falling edge: beep → silence ──────────────────
                self._in_beep       = False
                duration            = ts - self._beep_start
                self._silence_start = ts
                self._process_beep(duration)

            elif not active and not self._in_beep:
                # ongoing silence – check gap timeouts
                self._check_gaps(ts)

    def _process_beep(self, duration: float):
        if duration < self.MIN_BEEP:
            return   # noise / click – ignore
        if duration > self.MAX_BEEP:
            duration = self.MAX_BEEP

        # adaptive dit/dah boundary
        boundary = self._dit_ref * self.DIT_DAH_RATIO

        if duration <= boundary:
            symbol = '.'
            # update running average of dit duration
            self._recent_dits.append(duration)
            if len(self._recent_dits) > 8:
                self._recent_dits.pop(0)
            self._dit_ref = float(np.mean(self._recent_dits))
        else:
            symbol = '-'

        self._cur_letter.append(symbol)

        if self.on_morse_symbol:
            try:
                self.on_morse_symbol(symbol)
            except Exception:
                pass

        print(f"  ·  {symbol}  ({duration*1000:.0f} ms)  ref={self._dit_ref*1000:.0f} ms")

    def _check_gaps(self, now: float):
        if self._silence_start <= 0:
            return
        silence = now - self._silence_start

        # letter gap
        if silence >= self.LETTER_GAP and self._cur_letter:
            self._complete_letter()
            self._silence_start = now   # reset so we don't fire again

        # word gap (only after letter was just completed)
        if silence >= self.WORD_GAP and self._cur_word:
            self._complete_word()
            self._silence_start = now

    def _complete_letter(self):
        if not self._cur_letter:
            return
        morse  = ''.join(self._cur_letter)
        letter = self._morse_map.get(morse, '?')
        self._cur_word.append(letter)
        self._cur_letter = []

        if self.on_letter:
            try:
                self.on_letter(letter, morse)
            except Exception:
                pass
        print(f"  → letter: {letter} ({morse})")

    def _complete_word(self):
        if not self._cur_word:
            return
        word = ''.join(self._cur_word)
        self._cur_word = []

        if self.on_word:
            try:
                self.on_word(word)
            except Exception:
                pass
        print(f"  ⬛ word: {word}")
