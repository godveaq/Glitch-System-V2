#!/usr/bin/env python3
# Test script to run Glitcher without login for testing purposes

import tkinter as tk
from glitcher_gui import GlitcherGUI

def main():
    root = tk.Tk()
    
    # Configure styles
    style = tk.ttk.Style()
    style.configure('Danger.TButton', foreground='red')
    
    app = GlitcherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()