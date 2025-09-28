"""
Test script for image loading and display
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from models.image_layer import ImageLayer


def test_image_loading():
    """Test image loading functionality"""
    print("Testing image loading...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Image Test")
    root.geometry("800x600")
    
    # Create canvas
    canvas = tk.Canvas(root, bg="black", width=640, height=360)
    canvas.pack(pady=20)
    
    # Create timeline manager
    timeline = TimelineManager()
    
    # Test image layer creation
    print("Creating image layer...")
    
    # Try to create image layer with a test image path
    test_image_path = "test_image.jpg"  # You can replace this with an actual image path
    
    # Check if test image exists
    if not os.path.exists(test_image_path):
        print(f"Test image not found: {test_image_path}")
        print("Please place a test image named 'test_image.jpg' in the project directory")
        return False
    
    # Create image layer
    layer = timeline.create_image_layer(test_image_path)
    print(f"Created layer: {layer.layer_id}")
    print(f"Image path: {layer.image_path}")
    print(f"Original image loaded: {layer.original_image is not None}")
    print(f"Scaled image loaded: {layer.scaled_image is not None}")
    
    # Test rendering
    print("Testing canvas rendering...")
    try:
        layer.render_preview(canvas, 0.0)
        print("✅ Image rendered successfully on canvas")
    except Exception as e:
        print(f"❌ Error rendering image: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Add some controls
    frame = ttk.Frame(root)
    frame.pack(pady=10)
    
    def refresh_canvas():
        canvas.delete("all")
        layer.render_preview(canvas, 0.0)
    
    ttk.Button(frame, text="Refresh", command=refresh_canvas).pack(side=tk.LEFT, padx=5)
    
    def test_properties():
        print(f"Layer properties:")
        print(f"  - Position: ({layer.x}, {layer.y})")
        print(f"  - Size: {layer.width}x{layer.height}")
        print(f"  - Fit mode: {layer.fit_mode}")
        print(f"  - Rotation: {layer.rotation}")
        print(f"  - Visible: {layer.visible}")
    
    ttk.Button(frame, text="Show Properties", command=test_properties).pack(side=tk.LEFT, padx=5)
    
    print("✅ Image test completed successfully!")
    print("Close the window to exit.")
    
    root.mainloop()
    return True


def main():
    """Main test function"""
    print("Image Loading Test")
    print("==================")
    
    try:
        success = test_image_loading()
        if success:
            print("\n✅ All image tests passed!")
        else:
            print("\n❌ Image tests failed!")
            return 1
    except Exception as e:
        print(f"Error in image test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
