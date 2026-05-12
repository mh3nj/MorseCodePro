#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from gui.main_app import MorseCodeApp
        import customtkinter as ctk
        
        print("="*60)
        print("🎯 MORSE CODE PROFESSIONAL SUITE v2.0")
        print("="*60)
        print("Starting application...")
        
        app = MorseCodeApp()
        app.mainloop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
