"""
Test script for preview canvas with new visual features
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer


def create_test_window():
    """Create test window with preview canvas"""
    root = tk.Tk()
    root.title("Preview Canvas Test - Light Gray Background & Focus Effects")
    root.geometry("1000x700")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create timeline manager
    timeline = TimelineManager()
    timeline.set_total_duration(10.0)
    
    # Create preview canvas
    from ui.preview_canvas import PreviewCanvas
    canvas = PreviewCanvas(main_frame, timeline)
    canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create control panel
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=5)
    
    def add_text_layer():
        layer = timeline.create_text_layer("Sample Text", 0.0, 5.0)
        layer.set_position(100, 100)
        layer.set_size(200, 80)
        layer.font_size = 24
        layer.font_color = "#000000"
        layer.bg_color = "#FFFF00"
        layer.bg_opacity = 0.8
        canvas.refresh()
        print(f"Added text layer: {layer.layer_id}")
    
    def add_box_layer():
        layer = timeline.create_box_layer(0.0, 5.0)
        layer.set_position(300, 150)
        layer.set_size(150, 100)
        layer.fill_color = "#FF0000"
        layer.fill_opacity = 0.6
        layer.border_color = "#000000"
        layer.border_width = 2
        canvas.refresh()
        print(f"Added box layer: {layer.layer_id}")
    
    def add_image_layer():
        layer = timeline.create_image_layer("")
        layer.set_position(200, 300)
        layer.set_size(200, 150)
        canvas.refresh()
        print(f"Added image layer: {layer.layer_id}")
    
    def clear_layers():
        timeline.layers.clear()
        canvas.refresh()
        print("Cleared all layers")
    
    def show_info():
        layers = timeline.get_all_layers()
        print(f"Total layers: {len(layers)}")
        for layer in layers:
            print(f"  - {layer.__class__.__name__}: {layer.layer_id} at ({layer.x}, {layer.y})")
    
    # Control buttons
    ttk.Button(control_frame, text="Add Text", command=add_text_layer).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Add Box", command=add_box_layer).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Add Image", command=add_image_layer).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Clear All", command=clear_layers).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Show Info", command=show_info).pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(
        control_frame, 
        text="Instructions: Click on elements to see dashed blue focus border. Hover for orange outline.",
        font=("Arial", 9)
    )
    instructions.pack(side=tk.RIGHT, padx=10)
    
    print("Preview Canvas Test")
    print("==================")
    print("✅ Light gray background")
    print("✅ Dashed blue focus border when selected")
    print("✅ Orange hover outline")
    print("✅ Resize handles for selected elements")
    print("✅ Drag & drop areas with better colors")
    
    return root


def main():
    """Main test function"""
    try:
        root = create_test_window()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in preview test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
