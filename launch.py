"""Launcher that chooses best available modules"""

import sys

def launch_minimal():
    print("Launching minimal version...")
    import minimal_main

def launch_full():
    print("Launching full version...")
    from gui.main_window import MainWindow
    import customtkinter as ctk
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    try:
        import customtkinter
        launch_full()
    except ImportError:
        print("Full version dependencies missing. Launching minimal version...")
        launch_minimal()