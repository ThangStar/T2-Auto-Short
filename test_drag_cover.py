"""
Test script for drag & drop and cover fit mode
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer


def test_drag_and_cover():
    """Test drag & drop and cover fit mode"""
    print("Testing drag & drop and cover fit mode...")
    
    # Create test window
    root = tk.Tk()
    root.title("Drag & Drop + Cover Fit Mode Test")
    root.geometry("1000x700")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create preview canvas
    from ui.preview_canvas import PreviewCanvas
    canvas = PreviewCanvas(main_frame, TimelineManager())
    canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create timeline manager
    timeline = TimelineManager()
    canvas.set_timeline_manager(timeline)
    
    # Control frame
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=10)
    
    def add_text_layer():
        """Add text layer"""
        layer = timeline.create_text_layer("Drag Me!", 0.0, 10.0)
        layer.set_position(100, 100)
        layer.set_size(200, 80)
        layer.font_size = 24
        layer.font_color = "#000000"
        layer.bg_color = "#FFFF00"
        layer.bg_opacity = 0.8
        canvas.refresh()
        print(f"Added text layer: {layer.layer_id}")
    
    def add_box_layer():
        """Add box layer"""
        layer = timeline.create_box_layer(0.0, 10.0)
        layer.set_position(300, 150)
        layer.set_size(150, 100)
        layer.fill_color = "#FF0000"
        layer.fill_opacity = 0.6
        layer.border_color = "#000000"
        layer.border_width = 2
        canvas.refresh()
        print(f"Added box layer: {layer.layer_id}")
    
    def add_image_layer():
        """Add image layer with cover fit mode"""
        image_paths = filedialog.askopenfilenames(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")]
        )
        
        if image_paths:
            layer = timeline.create_image_layer(image_paths[0])
            layer.set_position(200, 300)
            layer.set_size(200, 150)
            layer.fit_mode = "cover"  # Set cover mode
            
            # Load image
            if layer.load_image(image_paths[0]):
                print(f"✅ Added image layer with cover mode: {layer.layer_id}")
            else:
                print(f"❌ Failed to load image: {image_paths[0]}")
            
            canvas.refresh()
        else:
            print("No image selected")
    
    def test_cover_modes():
        """Test different cover modes"""
        image_paths = filedialog.askopenfilenames(
            title="Select Image File for Cover Test",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")]
        )
        
        if image_paths:
            modes = ["stretch", "fit", "fill", "cover", "original"]
            for i, mode in enumerate(modes):
                layer = timeline.create_image_layer(image_paths[0])
                layer.set_position(50 + i * 120, 50)
                layer.set_size(100, 80)
                layer.fit_mode = mode
                
                if layer.load_image(image_paths[0]):
                    print(f"✅ Added image with {mode} mode: {layer.layer_id}")
                else:
                    print(f"❌ Failed to load image for {mode} mode")
            
            canvas.refresh()
        else:
            print("No image selected for cover test")
    
    def clear_all():
        """Clear all layers"""
        timeline.layers.clear()
        canvas.refresh()
        print("Cleared all layers")
    
    def show_info():
        """Show layer information"""
        layers = timeline.get_all_layers()
        print(f"Total layers: {len(layers)}")
        for layer in layers:
            print(f"  - {layer.__class__.__name__}: {layer.layer_id} at ({layer.x}, {layer.y})")
            if isinstance(layer, ImageLayer):
                print(f"    Fit mode: {layer.fit_mode}")
    
    # Buttons
    ttk.Button(control_frame, text="Add Text", command=add_text_layer).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Add Box", command=add_box_layer).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Add Image (Cover)", command=add_image_layer).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Test Cover Modes", command=test_cover_modes).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Show Info", command=show_info).pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(
        main_frame,
        text="Instructions: Click and drag text/box layers to move them. Images use cover fit mode by default.",
        font=("Arial", 10)
    )
    instructions.pack(pady=10)
    
    print("Drag & Drop + Cover Fit Mode Test")
    print("=================================")
    print("✅ Light gray background")
    print("✅ Drag & drop for text and box layers")
    print("✅ Cover fit mode for images")
    print("✅ Selection borders")
    print("✅ Hover effects")
    
    return root


def main():
    """Main test function"""
    try:
        root = test_drag_and_cover()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in drag & cover test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
