"""
Test script for exact size match between canvas preview and video export
"""
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from core.video_renderer import VideoRenderer
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer


def test_exact_size_match():
    """Test exact size match between canvas and video export"""
    print("Testing exact size match between canvas and video export...")
    
    # Create test window
    root = tk.Tk()
    root.title("Exact Size Match Test")
    root.geometry("1000x800")
    
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
    
    def add_test_content():
        """Add test content with known positions"""
        # Clear existing layers
        timeline.layers.clear()
        
        # Add content at specific positions to test exact matching
        # Top-left corner
        text1 = timeline.create_text_layer("TOP-LEFT", 0.0, 5.0)
        text1.set_position(10, 10)
        text1.set_size(100, 50)
        text1.font_size = 16
        text1.font_color = "#FFFFFF"
        text1.bg_color = "#FF0000"
        text1.bg_opacity = 0.8
        
        # Top-right corner
        text2 = timeline.create_text_layer("TOP-RIGHT", 0.0, 5.0)
        text2.set_position(610, 10)  # 720-100-10 = 610
        text2.set_size(100, 50)
        text2.font_size = 16
        text2.font_color = "#FFFFFF"
        text2.bg_color = "#00FF00"
        text2.bg_opacity = 0.8
        
        # Bottom-left corner
        text3 = timeline.create_text_layer("BOTTOM-LEFT", 0.0, 5.0)
        text3.set_position(10, 1220)  # 1280-50-10 = 1220
        text3.set_size(100, 50)
        text3.font_size = 16
        text3.font_color = "#FFFFFF"
        text3.bg_color = "#0000FF"
        text3.bg_opacity = 0.8
        
        # Bottom-right corner
        text4 = timeline.create_text_layer("BOTTOM-RIGHT", 0.0, 5.0)
        text4.set_position(610, 1220)  # 720-100-10 = 610, 1280-50-10 = 1220
        text4.set_size(100, 50)
        text4.font_size = 16
        text4.font_color = "#FFFFFF"
        text4.bg_color = "#FFFF00"
        text4.bg_opacity = 0.8
        
        # Center
        box = timeline.create_box_layer(2.0, 7.0)
        box.set_position(310, 615)  # (720-100)/2 = 310, (1280-50)/2 = 615
        box.set_size(100, 50)
        box.fill_color = "#FF00FF"
        box.fill_opacity = 0.6
        box.border_color = "#FFFFFF"
        box.border_width = 2
        
        print("Added test content at exact positions:")
        print(f"  - Top-left: (10, 10)")
        print(f"  - Top-right: (610, 10)")
        print(f"  - Bottom-left: (10, 1220)")
        print(f"  - Bottom-right: (610, 1220)")
        print(f"  - Center: (310, 615)")
        print(f"  - Total layers: {len(timeline.layers)}")
    
    def add_test_image():
        """Add test image at specific position"""
        image_paths = filedialog.askopenfilenames(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")]
        )
        
        if image_paths:
            layer = timeline.create_image_layer(image_paths[0])
            layer.set_position(360, 640)  # Center of 720x1280
            layer.set_size(200, 150)
            layer.fit_mode = "cover"
            
            # Load image
            if layer.load_image(image_paths[0]):
                print(f"✅ Added image layer at center: ({layer.x}, {layer.y})")
                print(f"   Size: {layer.width}x{layer.height}")
                print(f"   Fit mode: {layer.fit_mode}")
            else:
                print(f"❌ Failed to load image: {image_paths[0]}")
        else:
            print("No image selected")
    
    def export_test_video():
        """Export test video to verify exact size match"""
        if not timeline.layers:
            messagebox.showwarning("Warning", "No layers to export. Add test content first.")
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
        print(f"Canvas size: 720x1280")
        print(f"Export size: 720x1280")
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
                    messagebox.showinfo("Success", f"Test video exported successfully!\n{output_path}\n\nCanvas and video should be identical in size and content positioning.")
                    print("✅ Test video export completed successfully")
                    print("✅ Canvas size: 720x1280")
                    print("✅ Export size: 720x1280")
                    print("✅ Content should be positioned identically")
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
        print(f"Canvas size: 720x1280")
        print(f"Total layers: {len(layers)}")
        for i, layer in enumerate(layers):
            print(f"  {i+1}. {layer.__class__.__name__}:")
            print(f"     Position: ({layer.x}, {layer.y})")
            print(f"     Size: {layer.width}x{layer.height}")
            print(f"     Duration: {layer.start_time}s - {layer.end_time}s")
            if isinstance(layer, ImageLayer):
                print(f"     Image: {layer.image_path}")
                print(f"     Fit mode: {layer.fit_mode}")
            elif isinstance(layer, TextLayer):
                print(f"     Text: {layer.text}")
            print()
    
    def clear_all():
        """Clear all layers"""
        timeline.layers.clear()
        print("Cleared all layers")
    
    # Buttons
    ttk.Button(control_frame, text="Add Test Content", command=add_test_content).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Add Image", command=add_test_image).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Export Test Video", command=export_test_video).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Show Layer Info", command=show_layer_info).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(
        main_frame,
        text="Instructions: 1) Add test content 2) Export video 3) Compare canvas preview with exported video - they should be identical",
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
    
    print("Exact Size Match Test")
    print("====================")
    print("✅ Canvas size: 720x1280")
    print("✅ Export size: 720x1280")
    print("✅ Test content at exact positions")
    print("✅ Compare preview with exported video")
    print("✅ They should be identical in size and positioning")
    
    return root


def main():
    """Main test function"""
    try:
        root = test_exact_size_match()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in exact size match test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
