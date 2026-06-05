"""Find working microphone device"""
import sounddevice as sd

print("Available Input Devices:\n")
devices = sd.query_devices()

for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"[{i}] {device['name']}")
        print(f"    Channels: {device['max_input_channels']}")
        print(f"    Default SR: {device['default_samplerate']}")
        print()

# Test each Razer device
razers = [4, 15, 29, 42]
print("\n" + "="*50)
print("Testing Razer devices...")
print("Speak into your microphone now!\n")

import numpy as np

for dev in razers:
    print(f"Testing device {dev}...")
    try:
        recording = sd.rec(int(2 * 44100), samplerate=44100, channels=1, device=dev)
        sd.wait()
        max_amp = np.abs(recording).max()
        print(f"  Device {dev}: Max amplitude = {max_amp:.0f}")
        if max_amp > 100:
            print(f"  ✅ Device {dev} WORKS! Use this one.")
        else:
            print(f"  ❌ Device {dev} - No sound detected")
    except Exception as e:
        print(f"  ❌ Device {dev} - Error: {e}")
    print()