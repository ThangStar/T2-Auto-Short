"""
Test script for image size consistency between preview and export
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from core.video_renderer import VideoRenderer
from models.image_layer import ImageLayer


def test_image_size_consistency():
    """Test image size consistency between preview and export"""
    print("Testing image size consistency...")
    
    # Create test window
    root = tk.Tk()
    root.title("Image Size Consistency Test")
    root.geometry("800x600")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create timeline manager
    timeline = TimelineManager()
    
    # Create video renderer
    renderer = VideoRenderer()
    
    # Control frame
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=10)
    
    def add_test_image():
        """Add test image with different fit modes"""
        image_paths = filedialog.askopenfilenames(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")]
        )
        
        if image_paths:
            # Clear existing layers
            timeline.layers.clear()
            
            # Test different fit modes
            fit_modes = ["stretch", "fit", "fill", "cover", "original"]
            positions = [(50, 50), (200, 50), (50, 200), (200, 200), (50, 350)]
            
            for i, (fit_mode, (x, y)) in enumerate(zip(fit_modes, positions)):
                layer = timeline.create_image_layer(image_paths[0])
                layer.set_position(x, y)
                layer.set_size(120, 120)  # Fixed size for comparison
                layer.fit_mode = fit_mode
                
                # Load image
                if layer.load_image(image_paths[0]):
                    print(f"✅ Added image with {fit_mode} mode at ({x}, {y})")
                    print(f"   Layer size: {layer.width}x{layer.height}")
                    if layer.scaled_image:
                        print(f"   Scaled size: {layer.scaled_image.width}x{layer.scaled_image.height}")
                else:
                    print(f"❌ Failed to load image for {fit_mode} mode")
            
            print(f"Total layers: {len(timeline.layers)}")
        else:
            print("No image selected")
    
    def export_test_video():
        """Export test video to compare with preview"""
        if not timeline.layers:
            messagebox.showwarning("Warning", "No layers to export. Add test image first.")
            return
        
        # Get output path
        output_path = filedialog.asksaveasfilename(
            title="Save Test Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
        
        # Get timeline data
        timeline_data = {
            "layers": [layer.export_data() for layer in timeline.layers],
            "total_duration": 5.0
        }
        
        print("Exporting test video...")
        print(f"Output path: {output_path}")
        print(f"Layers: {len(timeline_data['layers'])}")
        
        # Show progress dialog
        progress_window = tk.Toplevel(root)
        progress_window.title("Exporting Test Video...")
        progress_window.geometry("400x150")
        progress_window.transient(root)
        progress_window.grab_set()
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.ProgressBar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=20, padx=20, fill=tk.X)
        
        status_label = ttk.Label(progress_window, text="Preparing...")
        status_label.pack(pady=10)
        
        def progress_callback(progress, status):
            progress_var.set(progress)
            status_label.config(text=status)
            progress_window.update()
        
        def export_thread():
            try:
                success = renderer.render_video(
                    timeline_data=timeline_data,
                    output_path=output_path,
                    video_width=720,
                    video_height=1280,
                    fps=30,
                    quality="high",
                    background_video=None,
                    background_music=None,
                    progress_callback=progress_callback
                )
                
                progress_window.after(0, lambda: progress_window.destroy())
                
                if success:
                    messagebox.showinfo("Success", f"Test video exported successfully!\n{output_path}\n\nCompare with preview to check size consistency.")
                    print("✅ Test video export completed successfully")
                else:
                    messagebox.showerror("Error", "Test video export failed. Check console for details.")
                    print("❌ Test video export failed")
                    
            except Exception as e:
                progress_window.after(0, lambda: progress_window.destroy())
                messagebox.showerror("Error", f"Export error: {str(e)}")
                print(f"❌ Export error: {e}")
                import traceback
                traceback.print_exc()
        
        # Start export in thread
        import threading
        thread = threading.Thread(target=export_thread)
        thread.daemon = True
        thread.start()
    
    def show_layer_info():
        """Show detailed layer information"""
        layers = timeline.get_all_layers()
        print(f"Layer Information:")
        print(f"Total layers: {len(layers)}")
        for i, layer in enumerate(layers):
            if isinstance(layer, ImageLayer):
                print(f"  {i+1}. {layer.fit_mode.upper()} mode:")
                print(f"     Layer bounds: ({layer.x}, {layer.y}) {layer.width}x{layer.height}")
                print(f"     Image path: {layer.image_path}")
                if layer.original_image:
                    print(f"     Original size: {layer.original_image.width}x{layer.original_image.height}")
                if layer.scaled_image:
                    print(f"     Scaled size: {layer.scaled_image.width}x{layer.scaled_image.height}")
                print()
    
    def clear_all():
        """Clear all layers"""
        timeline.layers.clear()
        print("Cleared all layers")
    
    # Buttons
    ttk.Button(control_frame, text="Add Test Image", command=add_test_image).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Export Test Video", command=export_test_video).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Show Layer Info", command=show_layer_info).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(
        main_frame,
        text="Instructions: 1) Add test image 2) Check layer info 3) Export video 4) Compare sizes",
        font=("Arial", 10)
    )
    instructions.pack(pady=10)
    
    # Console output area
    console_frame = ttk.LabelFrame(main_frame, text="Console Output")
    console_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    console_text = tk.Text(console_frame, height=15, wrap=tk.WORD)
    scrollbar = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=console_text.yview)
    console_text.configure(yscrollcommand=scrollbar.set)
    
    console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Redirect print to console
    class ConsoleRedirect:
        def __init__(self, text_widget):
            self.text_widget = text_widget
        
        def write(self, text):
            self.text_widget.insert(tk.END, text)
            self.text_widget.see(tk.END)
            self.text_widget.update()
        
        def flush(self):
            pass
    
    # Redirect stdout to console
    import sys
    original_stdout = sys.stdout
    sys.stdout = ConsoleRedirect(console_text)
    
    def on_closing():
        sys.stdout = original_stdout
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("Image Size Consistency Test")
    print("==========================")
    print("✅ Test all fit modes: stretch, fit, fill, cover, original")
    print("✅ Compare preview vs export sizes")
    print("✅ Fixed layer size: 120x120")
    print("✅ Export resolution: 720x1280 (9:16)")
    
    return root


def main():
    """Main test function"""
    try:
        root = test_image_size_consistency()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in image size consistency test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
