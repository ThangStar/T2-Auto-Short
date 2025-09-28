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
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Configure modern Bootstrap-like styling
        self._configure_styles()
        
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
    
    def _configure_styles(self):
        """Configure modern Bootstrap-like styling"""
        style = ttk.Style()
        
        # Try to use a theme that supports custom colors
        try:
            style.theme_use('clam')  # Use clam theme which supports custom colors better
        except:
            pass  # Fall back to default theme if clam is not available
        
        # Configure modern color scheme inspired by Bootstrap
        style.configure('TButton',
                       background='#007bff',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       focuscolor='none',
                       padding=(12, 8),
                       font=('Segoe UI', 9))
        
        style.map('TButton',
                 background=[('active', '#0056b3'),
                           ('pressed', '#004085'),
                           ('disabled', '#6c757d')])
        
        # Configure primary buttons (blue)
        style.configure('Primary.TButton',
                       background='#007bff',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9, 'bold'),
                       padding=(12, 8))
        
        style.map('Primary.TButton',
                 background=[('active', '#0056b3'),
                           ('pressed', '#004085'),
                           ('disabled', '#6c757d')])
        
        # Configure secondary buttons (gray)
        style.configure('Secondary.TButton',
                       background='#6c757d',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        style.map('Secondary.TButton',
                 background=[('active', '#5a6268'),
                           ('pressed', '#545b62'),
                           ('disabled', '#adb5bd')])
        
        # Configure success buttons (green)
        style.configure('Success.TButton',
                       background='#28a745',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        style.map('Success.TButton',
                 background=[('active', '#218838'),
                           ('pressed', '#1e7e34'),
                           ('disabled', '#6c757d')])
        
        # Configure danger buttons (red)
        style.configure('Danger.TButton',
                       background='#dc3545',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        style.map('Danger.TButton',
                 background=[('active', '#c82333'),
                           ('pressed', '#bd2130'),
                           ('disabled', '#6c757d')])
        
        # Configure info buttons (cyan)
        style.configure('Info.TButton',
                       background='#17a2b8',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9),
                       padding=(12, 8))
        
        style.map('Info.TButton',
                 background=[('active', '#138496'),
                           ('pressed', '#117a8b'),
                           ('disabled', '#6c757d')])
        
        # Configure labels
        style.configure('TLabel',
                       background='white',
                       foreground='#212529',
                       font=('Segoe UI', 9))
        
        # Configure frames
        style.configure('TFrame',
                       background='white')
        
        # Configure LabelFrame with modern styling
        style.configure('TLabelframe',
                       background='white',
                       foreground='#495057',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=1,
                       relief='solid')
        
        style.configure('TLabelframe.Label',
                       background='white',
                       foreground='#495057',
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure progress bar
        style.configure('TProgressbar',
                       background='#007bff',
                       troughcolor='#e9ecef',
                       borderwidth=0,
                       lightcolor='#007bff',
                       darkcolor='#007bff')
        
        # Configure scale/slider
        style.configure('TScale',
                       background='white',
                       troughcolor='#e9ecef',
                       sliderlength=20,
                       sliderrelief='flat')
        
        # Configure combobox
        style.configure('TCombobox',
                       fieldbackground='white',
                       background='white',
                       foreground='#495057',
                       font=('Segoe UI', 9),
                       borderwidth=1,
                       relief='solid')
        
        # Configure spinbox
        style.configure('TSpinbox',
                       fieldbackground='white',
                       background='white',
                       foreground='#495057',
                       font=('Segoe UI', 9),
                       borderwidth=1,
                       relief='solid')
        
        # Configure listbox
        style.configure('TListbox',
                       background='white',
                       foreground='#495057',
                       font=('Segoe UI', 9),
                       selectbackground='#007bff',
                       selectforeground='white',
                       borderwidth=1,
                       relief='solid')
        
        # Configure separators
        style.configure('TSeparator',
                       background='#dee2e6')
        
        # Set root background to light gray
        self.root.configure(bg='#f8f9fa')
        
        # Store style reference for potential fallback
        self.style = style
    
    def _create_styled_button(self, parent, text, command, style_name='TButton', **kwargs):
        """Create a styled button with fallback support"""
        try:
            # Try ttk button first
            button = ttk.Button(parent, text=text, command=command, style=style_name, **kwargs)
            return button
        except:
            # Fallback to regular tkinter button with manual styling
            button = tk.Button(parent, text=text, command=command, **kwargs)
            
            # Apply Bootstrap-like colors based on style
            if 'Primary' in style_name:
                button.configure(bg='#007bff', fg='white', font=('Segoe UI', 9, 'bold'))
            elif 'Secondary' in style_name:
                button.configure(bg='#6c757d', fg='white', font=('Segoe UI', 9))
            elif 'Success' in style_name:
                button.configure(bg='#28a745', fg='white', font=('Segoe UI', 9))
            elif 'Danger' in style_name:
                button.configure(bg='#dc3545', fg='white', font=('Segoe UI', 9))
            elif 'Info' in style_name:
                button.configure(bg='#17a2b8', fg='white', font=('Segoe UI', 9))
            else:
                button.configure(bg='#007bff', fg='white', font=('Segoe UI', 9))
            
            # Add hover effects
            def on_enter(event):
                if 'Primary' in style_name:
                    button.configure(bg='#0056b3')
                elif 'Secondary' in style_name:
                    button.configure(bg='#5a6268')
                elif 'Success' in style_name:
                    button.configure(bg='#218838')
                elif 'Danger' in style_name:
                    button.configure(bg='#c82333')
                elif 'Info' in style_name:
                    button.configure(bg='#138496')
                else:
                    button.configure(bg='#0056b3')
            
            def on_leave(event):
                if 'Primary' in style_name:
                    button.configure(bg='#007bff')
                elif 'Secondary' in style_name:
                    button.configure(bg='#6c757d')
                elif 'Success' in style_name:
                    button.configure(bg='#28a745')
                elif 'Danger' in style_name:
                    button.configure(bg='#dc3545')
                elif 'Info' in style_name:
                    button.configure(bg='#17a2b8')
                else:
                    button.configure(bg='#007bff')
            
            button.bind('<Enter>', on_enter)
            button.bind('<Leave>', on_leave)
            
            return button
        
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
        # Create main paned window with better spacing
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel (preview + timeline)
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=3)
        
        # Right panel (properties)
        right_panel = ttk.Frame(main_paned)
        main_paned.add(right_panel, weight=1)
        
        self.left_panel = left_panel
        self.right_panel = right_panel
        
        # Top area in left panel for toolbar with better spacing
        self.toolbar_container = ttk.Frame(self.left_panel)
        self.toolbar_container.pack(fill=tk.X, padx=15, pady=(15, 10))

        # Create inner split on the left: preview (left) and timeline/layers (right)
        self.left_inner = ttk.PanedWindow(self.left_panel, orient=tk.HORIZONTAL)
        self.left_inner.pack(fill=tk.BOTH, expand=True, padx=15)
        
        self.preview_side = ttk.Frame(self.left_inner)
        self.timeline_side = ttk.Frame(self.left_inner, width=340)
        
        self.left_inner.add(self.preview_side, weight=3)
        self.left_inner.add(self.timeline_side, weight=2)
    
    def _create_toolbar(self):
        """Create toolbar"""
        parent = getattr(self, "toolbar_container", self.left_panel)
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=15, pady=15)
        
        # Playback controls with modern styling
        self._create_styled_button(toolbar, text="⏮", command=self._seek_start, style_name='Secondary.TButton').pack(side=tk.LEFT, padx=4)
        self._create_styled_button(toolbar, text="⏯", command=self._toggle_play, style_name='Primary.TButton').pack(side=tk.LEFT, padx=4)
        self._create_styled_button(toolbar, text="⏭", command=self._seek_end, style_name='Secondary.TButton').pack(side=tk.LEFT, padx=4)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Layer controls with modern styling
        self._create_styled_button(toolbar, text="Add Text", command=self._add_text_layer, style_name='Success.TButton').pack(side=tk.LEFT, padx=4)
        self._create_styled_button(toolbar, text="Add Image", command=self._add_image_layer, style_name='Success.TButton').pack(side=tk.LEFT, padx=4)
        self._create_styled_button(toolbar, text="Add Box", command=self._add_box_layer, style_name='Success.TButton').pack(side=tk.LEFT, padx=4)
        self._create_styled_button(toolbar, text="Effects", command=self._configure_image_transitions, style_name='Info.TButton').pack(side=tk.LEFT, padx=12)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Time display with modern styling
        self.time_label = ttk.Label(toolbar, text="00:00.0", font=('Segoe UI', 11, 'bold'), foreground='#495057')
        self.time_label.pack(side=tk.RIGHT, padx=20)
    
    def _create_preview_area(self):
        """Create preview area with exact export resolution"""
        parent = getattr(self, "preview_side", self.left_panel)
        preview_frame = ttk.LabelFrame(parent, text="Preview (720x1280 - Exact Export Size)")
        # Keep preview anchored to top-left without consuming vertical space
        preview_frame.pack(anchor=tk.NW, padx=15, pady=15)
        
        # Create container frame for canvas with better padding
        canvas_container = ttk.Frame(preview_frame)
        canvas_container.pack(padx=15, pady=15)
        
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
        self.property_panel.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Set preview canvas reference for property panel
        self.property_panel.preview_canvas = self.preview_canvas
    
    def _create_timeline(self):
        """Create timeline"""
        parent = getattr(self, "timeline_side", self.left_panel)
        timeline_frame = ttk.LabelFrame(parent, text="Timeline")
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Timeline controls with better spacing
        controls_frame = ttk.Frame(timeline_frame)
        controls_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Time slider
        self.time_slider = ttk.Scale(
            controls_frame, 
            from_=0, 
            to=10, 
            orient=tk.HORIZONTAL,
            command=self._on_time_change
        )
        self.time_slider.pack(fill=tk.X, padx=15)
        
        # Layer list with modern styling
        self.layer_listbox = tk.Listbox(timeline_frame, font=('Segoe UI', 9))
        self.layer_listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.layer_listbox.bind('<<ListboxSelect>>', self._on_layer_list_select)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready", font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=20, pady=8)
    
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
            # Propagate to group if this is an image in a sequential group
            group_id = getattr(selected_layer, "group_id", None)
            if group_id:
                self.timeline_manager.apply_property_to_group(group_id, property_name, value, include_selected_id=selected_layer.layer_id)
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
        if messagebox.askyesno("New Project", "Create new project? Unsaved changes will be lost."):
            self.timeline_manager = TimelineManager()
            self.preview_canvas.set_timeline_manager(self.timeline_manager)
            self.property_panel.set_selected_layer(None)
            self._update_layer_list()
            self._update_time_display()
    
    def _open_project(self):
        """Open existing project"""
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            # Implementation for loading project
            pass
    
    def _save_project(self):
        """Save current project"""
        file_path = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            # Implementation for saving project
            pass
    
    def _import_images(self):
        """Import image files"""
        image_paths = self.asset_loader.select_image_files(self.root)
        if image_paths:
            self.timeline_manager.add_sequential_images(image_paths, duration_per_image=3.0)
            # Update time slider max to new duration
            self.time_slider.configure(to=self.timeline_manager.get_total_duration())
            self._update_layer_list()
            self.preview_canvas.refresh()
    
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
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if output_path:
            timeline_data = self.timeline_manager.export_timeline_data()
            
            # Ask for background video and music
            background_video = None
            background_music = None
            
            # Optional: Ask for background video
            if messagebox.askyesno("Background Video", "Would you like to use a background video?"):
                background_video = self.asset_loader.select_video_file(self.root)
            
            # Optional: Ask for background music
            if messagebox.askyesno("Background Music", "Would you like to add background music?"):
                music_files = filedialog.askopenfilenames(
                    title="Select Background Music",
                    filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.m4a"), ("All Files", "*.*")]
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
        messagebox.showinfo("About", "Video Editor v1.0\nSimple video editing application")

    def _configure_image_transitions(self):
        """Open dialog to select image transition effects"""
        dlg = tk.Toplevel(self.root)
        dlg.title("Transition Effects")
        dlg.resizable(False, False)
        dlg.configure(bg='#f8f9fa')
        dlg.geometry('400x250')
        
        # Center the dialog
        dlg.transient(self.root)
        dlg.grab_set()
        
        frm = ttk.Frame(dlg)
        frm.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Effect Type:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=(0, 8))
        trans_var = tk.StringVar(value=self.timeline_manager.image_transition.get("type", "none"))
        options = [
            ("None", "none"),
            ("Crossfade", "crossfade"),
            ("Fade to Black", "fadeblack"),
            ("Wipe Left", "wipeleft"),
            ("Wipe Right", "wiperight"),
            ("Zoom In", "zoomin"),
            ("Zoom Out", "zoomout"),
            ("Rotate", "rotate"),
            ("Flip", "flip"),
        ]
        combo = ttk.Combobox(frm, state="readonly", values=[o[0] for o in options])
        # map label to value
        label_to_value = {o[0]: o[1] for o in options}
        value_to_label = {o[1]: o[0] for o in options}
        combo.set(value_to_label.get(trans_var.get(), "None"))
        combo.grid(row=0, column=1, padx=15, pady=8, sticky="ew")

        ttk.Label(frm, text="Duration (seconds):", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky="w", pady=(15, 8))
        dur_var = tk.DoubleVar(value=float(self.timeline_manager.image_transition.get("duration", 0.5)))
        dur_entry = ttk.Spinbox(frm, from_=0.0, to=3.0, increment=0.1, textvariable=dur_var, width=10)
        dur_entry.grid(row=1, column=1, sticky="w", padx=15, pady=8)

        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=2, pady=(25, 0))
        
        def on_ok():
            sel_label = combo.get()
            sel_value = label_to_value.get(sel_label, "none")
            self.timeline_manager.image_transition = {
                "type": sel_value,
                "duration": max(0.0, float(dur_var.get()))
            }
            dlg.destroy()
        
        self._create_styled_button(btns, text="OK", command=on_ok, style_name='Primary.TButton').pack(side=tk.LEFT, padx=10)
        self._create_styled_button(btns, text="Cancel", command=dlg.destroy, style_name='Secondary.TButton').pack(side=tk.LEFT, padx=10)
    
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
            created = self.timeline_manager.add_sequential_images(image_paths, duration_per_image=3.0)
            if created:
                # Preload first image for instant feedback
                first = created[0]
                first.load_image(image_paths[0])
                # Ensure cover default if that's your desired default elsewhere
                # first.fit_mode = "cover"  # Uncomment if you want cover by button add
                # if hasattr(first, "_update_scaled_image"): first._update_scaled_image()
                self._on_layer_select(first)
            # Update time slider max to new duration
            self.time_slider.configure(to=self.timeline_manager.get_total_duration())
            self._update_layer_list()
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
