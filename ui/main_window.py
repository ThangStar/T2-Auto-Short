"""
Main window for video editor
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
from .preview_canvas import PreviewCanvas
from .property_panel import PropertyPanel
from core.timeline_manager import TimelineManager
from core.asset_loader import AssetLoader
from core.video_renderer import VideoRenderer


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Editor")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize core components
        self.timeline_manager = TimelineManager()
        self.asset_loader = AssetLoader()
        self.video_renderer = VideoRenderer()
        
        # UI components
        self.preview_canvas: Optional[PreviewCanvas] = None
        self.property_panel: Optional[PropertyPanel] = None
        self.timeline_frame: Optional[tk.Frame] = None
        
        # Current state
        self.current_time = 0.0
        self.is_playing = False
        self.play_timer = None
        
        self._create_ui()
        self._setup_bindings()
        
    def _create_ui(self):
        """Create the main UI"""
        # Create main menu
        self._create_menu()
        
        # Create main layout
        self._create_main_layout()
        
        # Create toolbar
        self._create_toolbar()
        
        # Create preview area
        self._create_preview_area()
        
        # Create property panel
        self._create_property_panel()
        
        # Create timeline
        self._create_timeline()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self._new_project)
        file_menu.add_command(label="Open Project", command=self._open_project)
        file_menu.add_command(label="Save Project", command=self._save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Import Images", command=self._import_images)
        file_menu.add_command(label="Import Video", command=self._import_video)
        file_menu.add_separator()
        file_menu.add_command(label="Export Video", command=self._export_video)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self._undo)
        edit_menu.add_command(label="Redo", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Selected", command=self._delete_selected)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self._zoom_in)
        view_menu.add_command(label="Zoom Out", command=self._zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self._reset_zoom)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create main layout with paned windows"""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel (preview + timeline)
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=3)
        
        # Right panel (properties)
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=1)
        
        self.left_panel = left_panel
        self.right_panel = right_panel
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = ttk.Frame(self.left_panel)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Playback controls
        ttk.Button(toolbar, text="⏮", command=self._seek_start).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⏯", command=self._toggle_play).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⏭", command=self._seek_end).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Layer controls
        ttk.Button(toolbar, text="Add Text", command=self._add_text_layer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Image", command=self._add_image_layer).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Box", command=self._add_box_layer).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Time display
        self.time_label = ttk.Label(toolbar, text="00:00.0")
        self.time_label.pack(side=tk.RIGHT, padx=10)
    
    def _create_preview_area(self):
        """Create preview area with exact export resolution"""
        preview_frame = ttk.LabelFrame(self.left_panel, text="Preview (720x1280 - Exact Export Size)")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)  # Only fill horizontally
        
        # Create container frame for canvas
        canvas_container = ttk.Frame(preview_frame)
        canvas_container.pack(padx=5, pady=5)
        
        # Create preview canvas with exact export size
        self.preview_canvas = PreviewCanvas(
            canvas_container, 
            timeline_manager=self.timeline_manager,
            on_layer_select=self._on_layer_select
        )
        self.preview_canvas.pack()
        
        # Canvas is already set to 720x1280 in __init__
    
    def _create_property_panel(self):
        """Create property panel"""
        self.property_panel = PropertyPanel(
            self.right_panel,
            on_property_change=self._on_property_change
        )
        self.property_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set preview canvas reference for property panel
        self.property_panel.preview_canvas = self.preview_canvas
    
    def _create_timeline(self):
        """Create timeline"""
        timeline_frame = ttk.LabelFrame(self.left_panel, text="Timeline")
        timeline_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Timeline controls
        controls_frame = ttk.Frame(timeline_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Time slider
        self.time_slider = ttk.Scale(
            controls_frame, 
            from_=0, 
            to=10, 
            orient=tk.HORIZONTAL,
            command=self._on_time_change
        )
        self.time_slider.pack(fill=tk.X, padx=5)
        
        # Layer list
        self.layer_listbox = tk.Listbox(timeline_frame, height=6)
        self.layer_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.layer_listbox.bind('<<ListboxSelect>>', self._on_layer_list_select)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def _setup_bindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self._new_project())
        self.root.bind('<Control-o>', lambda e: self._open_project())
        self.root.bind('<Control-s>', lambda e: self._save_project())
        self.root.bind('<Delete>', lambda e: self._delete_selected())
        self.root.bind('<space>', lambda e: self._toggle_play())
    
    # Event handlers
    def _on_layer_select(self, layer):
        """Handle layer selection"""
        self.timeline_manager.select_layer(layer.layer_id if layer else None)
        self.property_panel.set_selected_layer(layer)
        self._update_layer_list()
    
    def _on_property_change(self, property_name, value):
        """Handle property changes"""
        selected_layer = self.timeline_manager.get_selected_layer()
        if selected_layer:
            selected_layer.set_property(property_name, value)
            self.preview_canvas.refresh()
    
    def _on_time_change(self, value):
        """Handle time slider change"""
        self.current_time = float(value)
        self.timeline_manager.set_current_time(self.current_time)
        self.preview_canvas.set_current_time(self.current_time)
        self._update_time_display()
    
    def _on_layer_list_select(self, event):
        """Handle layer list selection"""
        selection = self.layer_listbox.curselection()
        if selection:
            layer_index = selection[0]
            layers = self.timeline_manager.get_all_layers()
            if 0 <= layer_index < len(layers):
                layer = layers[layer_index]
                self._on_layer_select(layer)
    
    # Menu actions
    def _new_project(self):
        """Create new project"""
        if messagebox.askyesno("New Project", "Create a new project? Unsaved changes will be lost."):
            self.timeline_manager = TimelineManager()
            self.preview_canvas.set_timeline_manager(self.timeline_manager)
            self.property_panel.set_selected_layer(None)
            self._update_layer_list()
            self._update_time_display()
    
    def _open_project(self):
        """Open existing project"""
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            # Implementation for loading project
            pass
    
    def _save_project(self):
        """Save current project"""
        file_path = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            # Implementation for saving project
            pass
    
    def _import_images(self):
        """Import image files"""
        image_paths = self.asset_loader.select_image_files(self.root)
        if image_paths:
            # Create slideshow from images
            slideshow_data = self.asset_loader.create_slideshow_from_images(image_paths, 2.0)
            for slide in slideshow_data:
                layer = self.timeline_manager.create_image_layer(
                    slide["image_path"], 
                    slide["start_time"], 
                    slide["end_time"]
                )
            self._update_layer_list()
    
    def _import_video(self):
        """Import video file"""
        video_path = self.asset_loader.select_video_file(self.root)
        if video_path:
            # Implementation for video import
            pass
    
    def _export_video(self):
        """Export video"""
        output_path = filedialog.asksaveasfilename(
            title="Export Video",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if output_path:
            timeline_data = self.timeline_manager.export_timeline_data()
            
            # Ask for background video and music
            background_video = None
            background_music = None
            
            # Optional: Ask for background video
            if messagebox.askyesno("Background Video", "Do you want to use a background video?"):
                background_video = self.asset_loader.select_video_file(self.root)
            
            # Optional: Ask for background music
            if messagebox.askyesno("Background Music", "Do you want to add background music?"):
                music_files = filedialog.askopenfilenames(
                    title="Select Background Music",
                    filetypes=[("Audio files", "*.mp3 *.wav *.aac *.m4a"), ("All files", "*.*")]
                )
                if music_files:
                    background_music = music_files[0]
            
            self.video_renderer.render_video(
                timeline_data, 
                output_path,
                background_video=background_video,
                background_music=background_music,
                progress_callback=self._on_render_progress
            )
    
    def _undo(self):
        """Undo last action"""
        # Implementation for undo
        pass
    
    def _redo(self):
        """Redo last action"""
        # Implementation for redo
        pass
    
    def _delete_selected(self):
        """Delete selected layer"""
        selected_layer = self.timeline_manager.get_selected_layer()
        if selected_layer:
            self.timeline_manager.remove_layer(selected_layer.layer_id)
            self.property_panel.set_selected_layer(None)
            self._update_layer_list()
            self.preview_canvas.refresh()
    
    def _zoom_in(self):
        """Zoom in preview"""
        self.preview_canvas.zoom_in()
    
    def _zoom_out(self):
        """Zoom out preview"""
        self.preview_canvas.zoom_out()
    
    def _reset_zoom(self):
        """Reset zoom level"""
        self.preview_canvas.reset_zoom()
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Video Editor v1.0\nA simple video editing application")
    
    # Playback controls
    def _toggle_play(self):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self._start_playback()
        else:
            self._stop_playback()
    
    def _start_playback(self):
        """Start playback"""
        if not self.is_playing:
            return
        
        # Update time
        self.current_time += 0.1  # 10 FPS for preview
        if self.current_time >= self.timeline_manager.get_total_duration():
            self.current_time = 0.0
        
        self.timeline_manager.set_current_time(self.current_time)
        self.preview_canvas.set_current_time(self.current_time)
        self.time_slider.set(self.current_time)
        self._update_time_display()
        
        # Schedule next frame
        self.play_timer = self.root.after(100, self._start_playback)
    
    def _stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        if self.play_timer:
            self.root.after_cancel(self.play_timer)
            self.play_timer = None
    
    def _seek_start(self):
        """Seek to start"""
        self.current_time = 0.0
        self._update_time()
    
    def _seek_end(self):
        """Seek to end"""
        self.current_time = self.timeline_manager.get_total_duration()
        self._update_time()
    
    def _update_time(self):
        """Update time display and canvas"""
        self.timeline_manager.set_current_time(self.current_time)
        self.preview_canvas.set_current_time(self.current_time)
        self.time_slider.set(self.current_time)
        self._update_time_display()
    
    def _update_time_display(self):
        """Update time display"""
        minutes = int(self.current_time // 60)
        seconds = self.current_time % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:04.1f}")
    
    def _update_layer_list(self):
        """Update layer list display"""
        self.layer_listbox.delete(0, tk.END)
        layers = self.timeline_manager.get_all_layers()
        for layer in layers:
            layer_type = layer.__class__.__name__.replace("Layer", "")
            self.layer_listbox.insert(tk.END, f"{layer_type}: {layer.layer_id}")
    
    def _add_text_layer(self):
        """Add text layer"""
        layer = self.timeline_manager.create_text_layer()
        self._update_layer_list()
        self._on_layer_select(layer)
    
    def _add_image_layer(self):
        """Add image layer"""
        image_paths = self.asset_loader.select_image_files(self.root)
        if image_paths:
            layer = self.timeline_manager.create_image_layer(image_paths[0])
            
            # Load the image
            if layer.load_image(image_paths[0]):
                print(f"Successfully loaded image: {image_paths[0]}")
            else:
                print(f"Failed to load image: {image_paths[0]}")
            
            self._update_layer_list()
            self._on_layer_select(layer)
            self.preview_canvas.refresh()
    
    def _add_box_layer(self):
        """Add box layer"""
        layer = self.timeline_manager.create_box_layer()
        self._update_layer_list()
        self._on_layer_select(layer)
    
    def _on_render_progress(self, progress, status):
        """Handle render progress"""
        self.progress_bar['value'] = progress * 100
        self.status_label.config(text=status)
        self.root.update_idletasks()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
