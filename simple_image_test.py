"""
Simple test for image display in Tkinter Canvas
"""
import tkinter as tk
from PIL import Image, ImageTk
import os


def test_simple_image():
    """Test simple image display"""
    root = tk.Tk()
    root.title("Simple Image Test")
    root.geometry("600x400")
    
    # Create canvas
    canvas = tk.Canvas(root, bg="lightgray", width=500, height=300)
    canvas.pack(pady=20)
    
    def load_and_display_image():
        """Load and display image"""
        from tkinter import filedialog
        
        # Open file dialog
        image_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")]
        )
        
        if image_path:
            print(f"Selected image: {image_path}")
            
            try:
                # Load image with PIL
                pil_image = Image.open(image_path)
                print(f"PIL image loaded: {pil_image.size}")
                
                # Resize if too large
                if pil_image.width > 400 or pil_image.height > 300:
                    pil_image.thumbnail((400, 300), Image.Resampling.LANCZOS)
                    print(f"Resized to: {pil_image.size}")
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)
                print(f"PhotoImage created: {photo.width()}x{photo.height()}")
                
                # Clear canvas and display image
                canvas.delete("all")
                canvas.create_image(250, 150, image=photo, anchor="center")
                
                # Keep reference to prevent garbage collection
                canvas.image = photo
                
                print("✅ Image displayed successfully!")
                
            except Exception as e:
                print(f"❌ Error loading image: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No image selected")
    
    def create_test_image():
        """Create a simple test image"""
        try:
            # Create a simple colored rectangle
            test_image = Image.new('RGB', (200, 150), color='red')
            
            # Add some text (simplified)
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(test_image)
            
            # Try to use default font
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.text((50, 50), "TEST IMAGE", fill='white', font=font)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(test_image)
            print(f"Test image created: {photo.width()}x{photo.height()}")
            
            # Display on canvas
            canvas.delete("all")
            canvas.create_image(250, 150, image=photo, anchor="center")
            
            # Keep reference
            canvas.image = photo
            
            print("✅ Test image displayed successfully!")
            
        except Exception as e:
            print(f"❌ Error creating test image: {e}")
            import traceback
            traceback.print_exc()
    
    # Control frame
    control_frame = tk.Frame(root)
    control_frame.pack(pady=10)
    
    tk.Button(control_frame, text="Load Image", command=load_and_display_image).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Create Test Image", command=create_test_image).pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Click 'Load Image' to select an image file, or 'Create Test Image' to generate a test image.",
        font=("Arial", 10)
    )
    instructions.pack(pady=10)
    
    print("Simple Image Test")
    print("=================")
    print("✅ Basic Tkinter Canvas")
    print("✅ PIL Image loading")
    print("✅ PhotoImage conversion")
    print("✅ Image display")
    
    return root


def main():
    """Main test function"""
    try:
        root = test_simple_image()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in simple image test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
