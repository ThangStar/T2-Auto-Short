"""
Test script specifically for image display in canvas
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from models.image_layer import ImageLayer


def test_image_display():
    """Test image display functionality"""
    print("Testing image display in canvas...")
    
    # Create test window
    root = tk.Tk()
    root.title("Image Display Test")
    root.geometry("800x600")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create canvas
    canvas = tk.Canvas(main_frame, bg="lightgray", width=640, height=360)
    canvas.pack(pady=20)
    
    # Create timeline manager
    timeline = TimelineManager()
    
    # Control frame
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=10)
    
    def select_and_add_image():
        """Select image and add to canvas"""
        image_paths = filedialog.askopenfilenames(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")]
        )
        
        if image_paths:
            image_path = image_paths[0]
            print(f"Selected image: {image_path}")
            
            # Create image layer
            layer = timeline.create_image_layer(image_path)
            layer.set_position(100, 100)
            layer.set_size(200, 150)
            
            # Load image
            if layer.load_image(image_path):
                print(f"✅ Successfully loaded image: {image_path}")
                print(f"Original image size: {layer.original_image.size if layer.original_image else 'None'}")
                print(f"Scaled image size: {layer.scaled_image.size if layer.scaled_image else 'None'}")
            else:
                print(f"❌ Failed to load image: {image_path}")
            
            # Render on canvas
            canvas.delete("all")
            layer.render_preview(canvas, 0.0)
            
            # Add selection border
            canvas.create_rectangle(
                layer.x - 3, layer.y - 3, layer.x + layer.width + 3, layer.y + layer.height + 3,
                outline="blue", width=2, dash=(5, 5)
            )
            
            print(f"Layer properties:")
            print(f"  - Position: ({layer.x}, {layer.y})")
            print(f"  - Size: {layer.width}x{layer.height}")
            print(f"  - Image path: {layer.image_path}")
            print(f"  - Fit mode: {layer.fit_mode}")
        else:
            print("No image selected")
    
    def test_with_sample_image():
        """Test with a sample image if available"""
        # Look for common image files in current directory
        sample_images = ["test.jpg", "test.png", "sample.jpg", "sample.png"]
        
        for img_name in sample_images:
            if os.path.exists(img_name):
                print(f"Found sample image: {img_name}")
                
                # Create image layer
                layer = timeline.create_image_layer(img_name)
                layer.set_position(50, 50)
                layer.set_size(300, 200)
                
                # Load image
                if layer.load_image(img_name):
                    print(f"✅ Successfully loaded sample image: {img_name}")
                    
                    # Render on canvas
                    canvas.delete("all")
                    layer.render_preview(canvas, 0.0)
                    
                    # Add selection border
                    canvas.create_rectangle(
                        layer.x - 3, layer.y - 3, layer.x + layer.width + 3, layer.y + layer.height + 3,
                        outline="blue", width=2, dash=(5, 5)
                    )
                    
                    return True
                else:
                    print(f"❌ Failed to load sample image: {img_name}")
        
        print("No sample images found in current directory")
        return False
    
    def clear_canvas():
        """Clear canvas"""
        canvas.delete("all")
        timeline.layers.clear()
        print("Canvas cleared")
    
    def show_debug_info():
        """Show debug information"""
        layers = timeline.get_all_layers()
        print(f"Total layers: {len(layers)}")
        for layer in layers:
            if isinstance(layer, ImageLayer):
                print(f"Image layer {layer.layer_id}:")
                print(f"  - Path: {layer.image_path}")
                print(f"  - Original image: {layer.original_image is not None}")
                print(f"  - Scaled image: {layer.scaled_image is not None}")
                print(f"  - Position: ({layer.x}, {layer.y})")
                print(f"  - Size: {layer.width}x{layer.height}")
    
    # Buttons
    ttk.Button(control_frame, text="Select Image", command=select_and_add_image).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Test Sample", command=test_with_sample_image).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Clear", command=clear_canvas).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Debug Info", command=show_debug_info).pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(
        main_frame,
        text="Click 'Select Image' to choose an image file, or 'Test Sample' to use a sample image if available.",
        font=("Arial", 10)
    )
    instructions.pack(pady=10)
    
    print("Image Display Test")
    print("==================")
    print("✅ Light gray background")
    print("✅ Image loading and display")
    print("✅ Debug information")
    print("✅ Selection border")
    
    return root


def main():
    """Main test function"""
    try:
        root = test_image_display()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in image display test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
