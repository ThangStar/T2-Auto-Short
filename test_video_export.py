"""
Test script for video export with images
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


def test_video_export():
    """Test video export with images"""
    print("Testing video export with images...")
    
    # Create test window
    root = tk.Tk()
    root.title("Video Export Test")
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
    
    def add_test_layers():
        """Add test layers for export"""
        # Clear existing layers
        timeline.layers.clear()
        
        # Add text layer
        text_layer = timeline.create_text_layer("Hello World!", 0.0, 5.0)
        text_layer.set_position(50, 50)
        text_layer.set_size(200, 80)
        text_layer.font_size = 24
        text_layer.font_color = "#FFFFFF"
        text_layer.bg_color = "#FF0000"
        text_layer.bg_opacity = 0.8
        
        # Add box layer
        box_layer = timeline.create_box_layer(2.0, 7.0)
        box_layer.set_position(300, 100)
        box_layer.set_size(150, 100)
        box_layer.fill_color = "#00FF00"
        box_layer.fill_opacity = 0.6
        box_layer.border_color = "#000000"
        box_layer.border_width = 2
        
        print("Added test layers")
        print(f"Total layers: {len(timeline.layers)}")
    
    def add_image_layer():
        """Add image layer"""
        image_paths = filedialog.askopenfilenames(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("All files", "*.*")]
        )
        
        if image_paths:
            layer = timeline.create_image_layer(image_paths[0])
            layer.set_position(100, 200)
            layer.set_size(200, 150)
            layer.fit_mode = "cover"
            
            # Load image
            if layer.load_image(image_paths[0]):
                print(f"✅ Added image layer: {layer.layer_id}")
                print(f"Image path: {layer.image_path}")
                print(f"Fit mode: {layer.fit_mode}")
            else:
                print(f"❌ Failed to load image: {image_paths[0]}")
        else:
            print("No image selected")
    
    def export_video():
        """Export video with current layers"""
        if not timeline.layers:
            messagebox.showwarning("Warning", "No layers to export. Add some layers first.")
            return
        
        # Get output path
        output_path = filedialog.asksaveasfilename(
            title="Save Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
        
        # Get timeline data
        timeline_data = {
            "layers": [layer.export_data() for layer in timeline.layers],
            "total_duration": 10.0
        }
        
        print("Exporting video...")
        print(f"Output path: {output_path}")
        print(f"Layers: {len(timeline_data['layers'])}")
        
        # Show progress dialog
        progress_window = tk.Toplevel(root)
        progress_window.title("Exporting Video...")
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
                    messagebox.showinfo("Success", f"Video exported successfully!\n{output_path}")
                    print("✅ Video export completed successfully")
                else:
                    messagebox.showerror("Error", "Video export failed. Check console for details.")
                    print("❌ Video export failed")
                    
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
    
    def show_timeline_info():
        """Show timeline information"""
        layers = timeline.get_all_layers()
        print(f"Timeline Info:")
        print(f"Total layers: {len(layers)}")
        for i, layer in enumerate(layers):
            print(f"  {i+1}. {layer.__class__.__name__}: {layer.layer_id}")
            print(f"     Position: ({layer.x}, {layer.y})")
            print(f"     Size: {layer.width}x{layer.height}")
            print(f"     Duration: {layer.start_time}s - {layer.end_time}s")
            if isinstance(layer, ImageLayer):
                print(f"     Image: {layer.image_path}")
                print(f"     Fit mode: {layer.fit_mode}")
            elif isinstance(layer, TextLayer):
                print(f"     Text: {layer.text}")
            print()
    
    # Buttons
    ttk.Button(control_frame, text="Add Test Layers", command=add_test_layers).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Add Image", command=add_image_layer).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Export Video", command=export_video).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Show Info", command=show_timeline_info).pack(side=tk.LEFT, padx=5)
    
    # Instructions
    instructions = ttk.Label(
        main_frame,
        text="Instructions: 1) Add test layers 2) Add image 3) Export video. Check console for FFmpeg command.",
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
    
    print("Video Export Test")
    print("================")
    print("✅ FFmpeg overlay filter for images")
    print("✅ ASS subtitles for text and boxes")
    print("✅ Progress tracking")
    print("✅ Console output")
    
    return root


def main():
    """Main test function"""
    try:
        root = test_video_export()
        root.mainloop()
        return 0
    except Exception as e:
        print(f"Error in video export test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
