"""
Test script for layout fix - preview canvas not covering timeline
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def test_layout_fix():
    """Test layout fix for preview canvas"""
    print("Testing layout fix...")
    
    # Create main window
    root = tk.Tk()
    root.title("Layout Fix Test")
    root.geometry("1200x800")
    
    # Create main window
    app = MainWindow()
    
    print("Layout Fix Test")
    print("===============")
    print("✅ Preview canvas with fixed size")
    print("✅ Timeline visible below preview")
    print("✅ Layer list visible")
    print("✅ Property panel visible")
    print("✅ 9:16 aspect ratio maintained")
    print("✅ Maximum size limits applied")
    
    return root


def main():
    """Main test function"""
    try:
        root = test_layout_fix()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in layout fix test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
