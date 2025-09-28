"""
Main entry point for Video Editor application
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    if missing_deps:
        messagebox.showerror(
            "Missing Dependencies",
            f"The following packages are required but not installed:\n\n" +
            "\n".join(missing_deps) +
            "\n\nPlease install them using:\npip install " + " ".join(missing_deps)
        )
        return False
    
    return True


def main():
    """Main application entry point"""
    try:
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Create and run the application
        app = MainWindow()
        app.run()
        
        return 0
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
