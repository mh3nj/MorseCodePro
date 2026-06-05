"""Simple Morse practice with keyboard"""
import winsound
import keyboard
import time

print("🎹 MORSE PRACTICE - Press keys:")
print("  '.' (period) = dit (short beep)")
print("  '-' (minus) = dah (long beep)")
print("  Space = next letter")
print("  Enter = translate word")
print("  ESC = quit\n")

current_letter = []
current_word = []

morse_map = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z'
}

def play_beep(duration):
    winsound.Beep(800, int(duration * 1000))

def translate():
    if current_letter:
        morse = ''.join(current_letter)
        letter = morse_map.get(morse, '?')
        current_word.append(letter)
        print(f"  → {letter} (morse: {morse})")
        current_letter.clear()

def show_word():
    if current_word:
        word = ''.join(current_word)
        print(f"\n📝 WORD: {word}\n")
        current_word.clear()

print("Try sending 'SOS':")
print("  Press . three times (dit dit dit)")
print("  Press Space")
print("  Press - three times (dah dah dah)")
print("  Press Space")
print("  Press . three times (dit dit dit)")
print("  Press Enter\n")

while True:
    event = keyboard.read_event()
    
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == '.':
            current_letter.append('.')
            play_beep(0.15)
            print(".", end='', flush=True)
        elif event.name == '-':
            current_letter.append('-')
            play_beep(0.45)
            print("-", end='', flush=True)
        elif event.name == 'space':
            translate()
            print(" ", end='', flush=True)
        elif event.name == 'enter':
            show_word()
        elif event.name == 'esc':
            break