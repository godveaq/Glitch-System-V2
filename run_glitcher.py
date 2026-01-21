# run_glitcher.py
import subprocess
import sys
import os

def main():
    print("Starting Glitcher - Professional Web Security Testing Platform")
    print("Running Python GUI version...")
    print()
    
    # Check if tkinter is available
    try:
        import tkinter as tk
        print("Tkinter is available")
    except ImportError:
        print("Error: Tkinter is not available. Please ensure you have Python with Tkinter support.")
        return
    
    # Run the GUI application
    try:
        # Change to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Import and run the GUI
        from glitcher_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"Error running Glitcher GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()