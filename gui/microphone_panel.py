"""
Microphone Panel - Rewritten to use fixed MorseDetector
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import re


class MicrophonePanel(ctk.CTkFrame):
    def __init__(self, parent, on_text_detected):
        super().__init__(parent, corner_radius=15)
        self.on_text_detected = on_text_detected
        self.detector   = None
        self.is_listening = False
        self.device_id  = None
        self.devices    = []

        self.setup_ui()
        self.after(200, self.scan_devices)   # defer so window is rendered first

    # ── device scanning ──────────────────────────────────────────────
    def scan_devices(self):
        try:
            import sounddevice as sd
            self.devices = []
            for i, d in enumerate(sd.query_devices()):
                if d['max_input_channels'] > 0:
                    self.devices.append((i, d['name']))

            labels = [f"[{idx}] {name[:35]}" for idx, name in self.devices]
            if not labels:
                labels = ["No input devices found"]

            self.device_menu.configure(values=labels)

            # prefer Razer, else first device
            chosen_idx = None
            for idx, (dev_id, name) in enumerate(self.devices):
                if 'razer' in name.lower() or 'seiren' in name.lower():
                    self.device_menu.set(labels[idx])
                    self.device_id = dev_id
                    chosen_idx = idx
                    break
            if chosen_idx is None and self.devices:
                self.device_menu.set(labels[0])
                self.device_id = self.devices[0][0]

            self.status_label.configure(
                text=f"⚪ Ready  ({len(self.devices)} input device(s) found)",
                text_color="#888888"
            )
        except ImportError:
            self.status_label.configure(
                text="⚠ sounddevice not installed. Run:  pip install sounddevice",
                text_color="#ff8800"
            )
        except Exception as e:
            self.status_label.configure(text=f"⚠ Scan error: {e}", text_color="#ff4444")

    # ── UI ───────────────────────────────────────────────────────────
    def setup_ui(self):
        # Title
        ctk.CTkLabel(
            self, text="🎤 Live Morse Code Detector",
            font=("Arial", 18, "bold"), text_color="#00d9ff"
        ).pack(pady=10)

        # Device row
        device_frame = ctk.CTkFrame(self, fg_color="transparent")
        device_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(device_frame, text="Microphone:", font=("Arial", 12)).pack(side="left", padx=5)
        self.device_menu = ctk.CTkOptionMenu(
            device_frame, values=["Scanning…"],
            command=self.change_device, width=310
        )
        self.device_menu.pack(side="left", padx=5)
        ctk.CTkButton(
            device_frame, text="🔄", command=self.scan_devices, width=32
        ).pack(side="left", padx=4)

        # Instructions
        ctk.CTkLabel(
            self,
            text=(
                "Beep (or whistle) into your microphone:\n"
                "  • Short beep  (< 2× dit)  →  dit  (.)\n"
                "  • Long beep   (≥ 2× dit)  →  dah  (─)\n"
                "  • Pause ~0.3 s  →  end of letter\n"
                "  • Pause ~0.7 s  →  end of word\n\n"
                "Tip: the detector auto-calibrates to your mic on start."
            ),
            font=("Arial", 11), text_color="#888888", justify="left"
        ).pack(pady=8, padx=20, anchor="w")

        # Volume meter
        meter_frame = ctk.CTkFrame(self, corner_radius=5)
        meter_frame.pack(pady=6, padx=20, fill="x")
        ctk.CTkLabel(meter_frame, text="Volume meter:", font=("Arial", 11)).pack(anchor="w", padx=8, pady=(6,0))
        self.meter_canvas = ctk.CTkCanvas(
            meter_frame, height=36, bg="#1a1a2e", highlightthickness=0
        )
        self.meter_canvas.pack(fill="x", padx=10, pady=6)
        self.meter_bar   = self.meter_canvas.create_rectangle(0, 2, 0, 34, fill="#00d9ff")
        self.thresh_line = self.meter_canvas.create_line(0, 0, 0, 36, fill="#ff4444", width=2, dash=(5, 3))

        # Start/stop button
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=8)
        self.listen_btn = ctk.CTkButton(
            btn_frame,
            text="🎙️ Start Listening",
            command=self.toggle_listening,
            width=190, height=44,
            fg_color="#00d9ff", text_color="black",
            font=("Arial", 14, "bold")
        )
        self.listen_btn.pack(pady=4)

        # Sensitivity
        sens_frame = ctk.CTkFrame(self, fg_color="transparent")
        sens_frame.pack(pady=6, padx=20, fill="x")
        ctk.CTkLabel(sens_frame, text="Sensitivity:", font=("Arial", 11)).pack(anchor="w")
        self.sens_var = ctk.DoubleVar(value=50)
        ctk.CTkSlider(
            sens_frame, from_=0, to=100,
            variable=self.sens_var,
            command=self._update_sensitivity
        ).pack(fill="x", pady=4)
        self.sens_label = ctk.CTkLabel(sens_frame, text="Medium", font=("Arial", 10))
        self.sens_label.pack()

        # Status
        self.status_label = ctk.CTkLabel(
            self, text="⚪ Not listening", font=("Arial", 12), text_color="#888888"
        )
        self.status_label.pack(pady=5)

        # Current letter being built
        self.morse_live = ctk.CTkLabel(
            self, text="", font=("Arial", 20, "bold"), text_color="#ffff00"
        )
        self.morse_live.pack(pady=2)

        # Detected text output
        out_frame = ctk.CTkFrame(self, corner_radius=10)
        out_frame.pack(fill="both", expand=True, padx=20, pady=8)
        ctk.CTkLabel(out_frame, text="Detected Text:", font=("Arial", 12, "bold")).pack(pady=5)
        self.detected_text = ctk.CTkTextbox(out_frame, height=110, font=("Arial", 14))
        self.detected_text.pack(fill="both", expand=True, padx=10, pady=8)

        # Test buttons
        test_frame = ctk.CTkFrame(self, fg_color="transparent")
        test_frame.pack(pady=8)
        ctk.CTkLabel(test_frame, text="Inject test:", font=("Arial", 11)).pack(side="left", padx=5)
        for label, text in [("S (...)", "S"), ("O (---)", "O"), ("SOS", "SOS")]:
            ctk.CTkButton(
                test_frame, text=label, width=68,
                command=lambda t=text: self._inject_test(t)
            ).pack(side="left", padx=2)
        ctk.CTkButton(
            test_frame, text="Clear", width=60, fg_color="#aa3333",
            command=lambda: self.detected_text.delete("1.0", "end")
        ).pack(side="left", padx=2)

    # ── device change ────────────────────────────────────────────────
    def change_device(self, choice):
        m = re.search(r'\[(\d+)\]', choice)
        if m:
            self.device_id = int(m.group(1))
            if self.is_listening:
                self.stop_listening()
                self.start_listening()

    # ── listen toggle ────────────────────────────────────────────────
    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        try:
            from core.morse_detector import MorseDetector
        except ImportError as e:
            messagebox.showerror("Import error", str(e))
            return

        self.detector = MorseDetector(device_id=self.device_id)

        self.detector.on_morse_symbol = self._on_symbol
        self.detector.on_letter       = self._on_letter
        self.detector.on_word         = self._on_word
        self.detector.on_amplitude    = self._on_amplitude

        # apply current sensitivity
        self.detector.set_sensitivity(self.sens_var.get())

        if self.detector.start_listening():
            self.is_listening = True
            self.listen_btn.configure(text="🛑 Stop Listening", fg_color="#aa3333")
            self.status_label.configure(
                text="🔴 Calibrating… keep quiet for 1–2 s", text_color="#ffaa00"
            )
            self.detected_text.delete("1.0", "end")
            self.after(1600, lambda: self.status_label.configure(
                text="🔴 Listening – make beeps!", text_color="#ff4444"
            ))
        else:
            messagebox.showerror(
                "Microphone Error",
                "Could not open microphone.\n\n"
                "• Make sure sounddevice is installed:  pip install sounddevice\n"
                "• Check that the selected device is a microphone\n"
                "• Try a different device from the dropdown"
            )

    def stop_listening(self):
        if self.detector:
            self.detector.stop_listening()
            self.detector = None
        self.is_listening = False
        self.listen_btn.configure(text="🎙️ Start Listening", fg_color="#00d9ff")
        self.status_label.configure(text="⚪ Not listening", text_color="#888888")
        self.morse_live.configure(text="")
        self.meter_canvas.coords(self.meter_bar, 0, 2, 0, 34)

    # ── detector callbacks (called from background thread) ───────────
    def _on_symbol(self, symbol):
        def _ui():
            current = self.morse_live.cget("text")
            self.morse_live.configure(text=current + symbol)
        self.after(0, _ui)

    def _on_letter(self, letter, morse):
        def _ui():
            self.morse_live.configure(text="")
            self.detected_text.insert("end", letter)
            self.detected_text.see("end")
            self.status_label.configure(
                text=f"🟢 {letter}  ({morse})", text_color="#00ff88"
            )
            self.after(900, lambda: self.status_label.configure(
                text="🔴 Listening…", text_color="#ff4444"
            ))
            if self.on_text_detected:
                self.on_text_detected(letter)
        self.after(0, _ui)

    def _on_word(self, word):
        def _ui():
            self.detected_text.insert("end", " ")
            self.detected_text.see("end")
            self.status_label.configure(
                text=f"🟢 Word: {word}", text_color="#00d9ff"
            )
            if self.on_text_detected:
                self.on_text_detected(" ")
        self.after(0, _ui)

    def _on_amplitude(self, amplitude):
        def _ui():
            if not self.detector:
                return
            canvas_w = self.meter_canvas.winfo_width() or 400
            max_amp  = max(self.detector.threshold * 4, 1200)
            w = min(canvas_w, int(amplitude / max_amp * canvas_w))

            if amplitude > self.detector.threshold:
                color = "#ff4444"
            elif amplitude > self.detector.threshold * 0.5:
                color = "#ffaa00"
            else:
                color = "#00d9ff"

            self.meter_canvas.coords(self.meter_bar, 0, 2, w, 34)
            self.meter_canvas.itemconfig(self.meter_bar, fill=color)

            # threshold line
            tx = min(canvas_w - 1, int(self.detector.threshold / max_amp * canvas_w))
            self.meter_canvas.coords(self.thresh_line, tx, 0, tx, 36)
        self.after(0, _ui)

    # ── sensitivity ──────────────────────────────────────────────────
    def _update_sensitivity(self, value):
        pct = float(value)
        if pct < 25:
            label = "Very sensitive (quiet mic)"
        elif pct < 50:
            label = "Sensitive"
        elif pct < 75:
            label = "Medium"
        elif pct < 90:
            label = "Low sensitivity"
        else:
            label = "Very low (loud beeps only)"
        self.sens_label.configure(text=label)
        if self.detector and self.is_listening:
            self.detector.set_sensitivity(pct)

    # ── test helpers ─────────────────────────────────────────────────
    def _inject_test(self, text):
        self.detected_text.insert("end", text)
        self.detected_text.see("end")
        if self.on_text_detected:
            for ch in text:
                self.on_text_detected(ch)
