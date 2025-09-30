"""
Main window for video editor
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
from .preview_canvas import PreviewCanvas
from .property_panel import PropertyPanel
from .layer_panel import LayerPanel
from core.timeline_manager import TimelineManager
from core.asset_loader import AssetLoader
from core.video_renderer import VideoRenderer
from core.video_renderer import VideoRenderer


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Video Editor")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        self.root.state("zoomed")
        
        # Configure modern Bootstrap-like styling
        self._configure_styles()
        
        # Initialize core components
        self.timeline_manager = TimelineManager()
        self.asset_loader = AssetLoader()
        self.video_renderer = VideoRenderer()
        
        # UI components
        self.preview_canvas: Optional[PreviewCanvas] = None
        self.property_panel: Optional[PropertyPanel] = None
        self.layer_panel: Optional[LayerPanel] = None
        self.timeline_frame: Optional[tk.Frame] = None
        
        # Current state
        self.current_time = 0.0
        self.is_playing = False
        self.play_timer = None
        self.background_music_path: Optional[str] = None
        self.background_music_volume: float = 1.0
        self.voice_path: Optional[str] = None
        self.voice_volume: float = 1.0
        
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
        
        # Bootstrap color scheme
        style.configure('TButton',
                       background='#6c757d',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       focuscolor='none',
                       padding=(12, 8),
                       font=('Inter', 9))
        
        style.map('TButton',
                 background=[('active', '#5a6268'),
                           ('pressed', '#545b62'),
                           ('disabled', '#6c757d')])
        
        # Bootstrap Primary buttons
        style.configure('Primary.TButton',
                       background='#007bff',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Inter', 9, 'bold'),
                       padding=(12, 8))
        
        style.map('Primary.TButton',
                 background=[('active', '#0056b3'),
                           ('pressed', '#004085'),
                           ('disabled', '#6c757d')])
        
        # Bootstrap Secondary buttons
        style.configure('Secondary.TButton',
                       background='#6c757d',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Inter', 9),
                       padding=(12, 8))
        
        style.map('Secondary.TButton',
                 background=[('active', '#5a6268'),
                           ('pressed', '#545b62'),
                           ('disabled', '#adb5bd')])
        
        # Bootstrap Success buttons
        style.configure('Success.TButton',
                       background='#28a745',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Inter', 9),
                       padding=(12, 8))
        
        style.map('Success.TButton',
                 background=[('active', '#218838'),
                           ('pressed', '#1e7e34'),
                           ('disabled', '#6c757d')])
        
        # Bootstrap Danger buttons
        style.configure('Danger.TButton',
                       background='#dc3545',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Inter', 9),
                       padding=(12, 8))
        
        style.map('Danger.TButton',
                 background=[('active', '#c82333'),
                           ('pressed', '#bd2130'),
                           ('disabled', '#6c757d')])
        
        # Bootstrap Info buttons
        style.configure('Info.TButton',
                       background='#17a2b8',
                       foreground='white',
                       borderwidth=1,
                       relief='solid',
                       font=('Inter', 9),
                       padding=(12, 8))
        
        style.map('Info.TButton',
                 background=[('active', '#138496'),
                           ('pressed', '#117a8b'),
                           ('disabled', '#6c757d')])
        
        # Bootstrap labels
        style.configure('TLabel',
                       background='#ffffff',
                       foreground='#212529',
                       font=('Inter', 10))
        
        # Bootstrap header labels
        style.configure('Header.TLabel',
                       background='#ffffff',
                       foreground='#007bff',
                       font=('Inter', 12, 'bold'))
        
        # Configure frames with consistent colors
        style.configure('TFrame',
                       background='#ffffff',
                       relief='flat')
        
        # Bootstrap card-style frames
        style.configure('Card.TFrame',
                       background='#ffffff',
                       relief='solid',
                       borderwidth=1)
        
        # Bootstrap LabelFrame styling
        style.configure('TLabelframe',
                       background='#ffffff',
                       foreground='#212529',
                       font=('Inter', 11, 'bold'),
                       borderwidth=1,
                       relief='solid')
        
        style.configure('TLabelframe.Label',
                       background='#ffffff',
                       foreground='#007bff',
                       font=('Inter', 11, 'bold'))
        
        # Bootstrap progress bar
        style.configure('TProgressbar',
                       background='#007bff',
                       troughcolor='#e9ecef',
                       borderwidth=0,
                       lightcolor='#007bff',
                       darkcolor='#007bff')
        
        # Bootstrap scale/slider
        style.configure('TScale',
                       background='#ffffff',
                       troughcolor='#e9ecef',
                       sliderlength=20,
                       sliderrelief='flat')
        
        # Bootstrap combobox
        style.configure('TCombobox',
                       fieldbackground='#ffffff',
                       background='#ffffff',
                       foreground='#212529',
                       font=('Inter', 10),
                       borderwidth=1,
                       relief='solid')
        
        # Bootstrap spinbox
        style.configure('TSpinbox',
                       fieldbackground='#ffffff',
                       background='#ffffff',
                       foreground='#212529',
                       font=('Inter', 10),
                       borderwidth=1,
                       relief='solid')
        
        # Bootstrap listbox
        style.configure('TListbox',
                       background='#ffffff',
                       foreground='#212529',
                       font=('Inter', 10),
                       selectbackground='#007bff',
                       selectforeground='white',
                       borderwidth=1,
                       relief='solid')
        
        # Bootstrap separators
        style.configure('TSeparator',
                       background='#dee2e6')
        
        # Bootstrap root background
        self.root.configure(bg='#f8f9fa')
        
        # Store style reference for potential fallback
        self.style = style

    def _select_background_music(self):
        """Select or clear background music for the export"""
        answer = messagebox.askyesno("Background Music", "Would you like to select a background music file?")
        if not answer:
            if self.background_music_path:
                if messagebox.askyesno("Background Music", "Clear the current background music?"):
                    self.background_music_path = None
            return
        file_path = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.m4a"), ("All Files", "*.*")]
        )
        if file_path:
            self.background_music_path = file_path

    def _open_music_config(self):
        """Open a dialog to choose music file and volume."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Music Settings")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill=tk.BOTH, expand=True)

        # File row
        ttk.Label(frm, text="File:").grid(row=0, column=0, sticky="w")
        file_var = tk.StringVar(value=self.background_music_path or "")
        file_entry = ttk.Entry(frm, textvariable=file_var, width=42)
        file_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        def on_browse():
            path = filedialog.askopenfilename(
                title="Select Background Music",
                filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.m4a"), ("All Files", "*.*")]
            )
            if path:
                file_var.set(path)
        ttk.Button(frm, text="Browse", command=on_browse).grid(row=0, column=2, sticky="w")

        # Volume row
        ttk.Label(frm, text="Volume:").grid(row=1, column=0, sticky="w", pady=(12, 0))
        vol_var = tk.DoubleVar(value=self.background_music_volume)
        vol_scale = ttk.Scale(frm, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=vol_var)
        vol_scale.grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=(12, 0))
        vol_val_lbl = ttk.Label(frm, text=f"{self.background_music_volume:.2f}")
        vol_val_lbl.grid(row=1, column=2, sticky="w", pady=(12, 0))
        def on_vol_change(*_):
            try:
                vol_val_lbl.config(text=f"{float(vol_var.get()):.2f}")
            except Exception:
                pass
        vol_var.trace_add('write', on_vol_change)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=3, sticky="e", pady=(16, 0))
        def on_ok():
            self.background_music_path = file_var.get().strip() or None
            self.background_music_volume = max(0.0, min(1.0, float(vol_var.get())))
            dlg.destroy()
        ttk.Button(btns, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=(8,0))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT)

        frm.columnconfigure(1, weight=1)

    def _open_voice_config(self):
        """Open a dialog to choose voice file and volume."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Voice Settings")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill=tk.BOTH, expand=True)

        # File row
        ttk.Label(frm, text="File:").grid(row=0, column=0, sticky="w")
        file_var = tk.StringVar(value=self.voice_path or "")
        file_entry = ttk.Entry(frm, textvariable=file_var, width=42)
        file_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        def on_browse():
            path = filedialog.askopenfilename(
                title="Select Voice Audio",
                filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.m4a"), ("All Files", "*.*")]
            )
            if path:
                file_var.set(path)
        ttk.Button(frm, text="Browse", command=on_browse).grid(row=0, column=2, sticky="w")

        # Volume row
        ttk.Label(frm, text="Volume:").grid(row=1, column=0, sticky="w", pady=(12, 0))
        vol_var = tk.DoubleVar(value=self.voice_volume)
        vol_scale = ttk.Scale(frm, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=vol_var)
        vol_scale.grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=(12, 0))
        vol_val_lbl = ttk.Label(frm, text=f"{self.voice_volume:.2f}")
        vol_val_lbl.grid(row=1, column=2, sticky="w", pady=(12, 0))
        def on_vol_change(*_):
            try:
                vol_val_lbl.config(text=f"{float(vol_var.get()):.2f}")
            except Exception:
                pass
        vol_var.trace_add('write', on_vol_change)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=3, sticky="e", pady=(16, 0))
        def on_ok():
            self.voice_path = file_var.get().strip() or None
            self.voice_volume = max(0.0, min(1.0, float(vol_var.get())))
            dlg.destroy()
        ttk.Button(btns, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=(8,0))
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side=tk.RIGHT)

        frm.columnconfigure(1, weight=1)
    
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
        # Main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Top toolbar area
        toolbar_frame = ttk.Frame(main_container, style='Card.TFrame')
        toolbar_frame.pack(fill=tk.X, pady=(0, 8))
        self.toolbar_container = toolbar_frame
        
        # Create horizontal paned window for main content
        main_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Preview
        left_panel = ttk.Frame(main_paned, style='Card.TFrame')
        main_paned.add(left_panel, weight=4)
        
        # Center: Timeline and layers
        center_panel = ttk.Frame(main_paned, style='Card.TFrame')
        main_paned.add(center_panel, weight=3)
        
        # Right side: Properties
        right_panel = ttk.Frame(main_paned, style='Card.TFrame')
        main_paned.add(right_panel, weight=2)
        
        self.left_panel = left_panel
        self.center_panel = center_panel
        self.right_panel = right_panel
    
    def _create_toolbar(self):
        """Create toolbar"""
        parent = getattr(self, "toolbar_container", self.left_panel)
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=16, pady=12)
        
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
        self._create_styled_button(toolbar, text="Music", command=self._open_music_config, style_name='Info.TButton').pack(side=tk.LEFT, padx=4)
        self._create_styled_button(toolbar, text="Voice", command=self._open_voice_config, style_name='Info.TButton').pack(side=tk.LEFT, padx=4)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        # Bootstrap time display
        self.time_label = ttk.Label(toolbar, text="00:00.0", font=('Inter', 11, 'bold'))
        self.time_label.pack(side=tk.RIGHT, padx=20)
    
    def _create_preview_area(self):
        """Create preview area with exact export resolution"""
        parent = self.left_panel
        
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=16, pady=(16, 8))
        ttk.Label(header_frame, text="📹 Preview", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Label(header_frame, text="720×1280", style='TLabel').pack(side=tk.RIGHT)
        
        # Preview frame
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        
        # Create container frame for canvas
        canvas_container = ttk.Frame(preview_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Create preview canvas with exact export size
        self.preview_canvas = PreviewCanvas(
            canvas_container, 
            timeline_manager=self.timeline_manager,
            on_layer_select=self._on_layer_select
        )
        # Add vertical scrollbar for preview
        vscroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        self.preview_canvas.configure(yscrollcommand=vscroll.set)
        # Layout: canvas left, scrollbar right
        self.preview_canvas.pack(side=tk.LEFT)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas is already set to 720x1280 in __init__
    
    def _create_property_panel(self):
        """Create property panel"""
        parent = self.right_panel
        
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=16, pady=(16, 8))
        ttk.Label(header_frame, text="⚙️ Properties", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Property panel frame
        panel_frame = ttk.Frame(parent)
        panel_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        
        self.property_panel = PropertyPanel(
            panel_frame,
            on_property_change=self._on_property_change
        )
        self.property_panel.pack(fill=tk.BOTH, expand=True)
        
        # Set preview canvas reference for property panel
        self.property_panel.preview_canvas = self.preview_canvas
        
        # Set preview canvas reference for layer panel (will be set in _create_timeline if layer_panel exists)
        pass
    
    def _create_timeline(self):
        """Create timeline"""
        parent = self.center_panel
        
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=16, pady=(16, 8))
        ttk.Label(header_frame, text="🎬 Timeline & Layers", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Timeline frame
        timeline_frame = ttk.Frame(parent)
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        
        # Timeline controls with better spacing
        controls_frame = ttk.Frame(timeline_frame)
        controls_frame.pack(fill=tk.X, padx=12, pady=12)
        
        # Time slider
        self.time_slider = ttk.Scale(
            controls_frame, 
            from_=0, 
            to=10, 
            orient=tk.HORIZONTAL,
            command=self._on_time_change
        )
        self.time_slider.pack(fill=tk.X, padx=8)
        
        # Modern layer panel
        self.layer_panel = LayerPanel(
            timeline_frame,
            timeline_manager=self.timeline_manager,
            on_layer_select=self._on_layer_select
        )
        self.layer_panel.pack(fill=tk.BOTH, expand=True)
        
        # Set preview canvas reference if it exists
        if hasattr(self, 'preview_canvas') and self.preview_canvas is not None:
            self.layer_panel.preview_canvas = self.preview_canvas
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root, style='Card.TFrame')
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=(0, 8))
        
        self.status_label = ttk.Label(self.status_bar, text="✅ Ready", font=('Inter', 10))
        self.status_label.pack(side=tk.LEFT, padx=16, pady=8)
        
        self.progress_bar = ttk.Progressbar(self.status_bar, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=16, pady=8)
    
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
        """Handle layer list selection - now handled by layer panel"""
        pass
    
    # Menu actions
    def _new_project(self):
        """Create new project"""
        if messagebox.askyesno("New Project", "Create new project? Unsaved changes will be lost."):
            self.timeline_manager = TimelineManager()
            self.preview_canvas.set_timeline_manager(self.timeline_manager)
            self.property_panel.set_selected_layer(None)
            if hasattr(self, 'layer_panel') and self.layer_panel is not None:
                self.layer_panel.set_timeline_manager(self.timeline_manager)
            self._update_layer_list()
            self._update_time_display()
    
    def _open_project(self):
        """Open existing project"""
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                import json
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Load timeline
                ok = self.timeline_manager.import_timeline_data(data.get("timeline", data))
                if not ok:
                    messagebox.showerror("Open Project", "Failed to load project timeline data.")
                    return
                # Apply audio settings if present
                self.background_music_path = data.get("background_music")
                self.background_music_volume = data.get("background_music_volume", 1.0)
                self.voice_path = data.get("voice_path")
                self.voice_volume = data.get("voice_volume", 1.0)
                # Rewire UI to new timeline
                self.preview_canvas.set_timeline_manager(self.timeline_manager)
                self.property_panel.set_selected_layer(None)
                if hasattr(self, 'layer_panel') and self.layer_panel is not None:
                    self.layer_panel.set_timeline_manager(self.timeline_manager)
                # Update time slider and display
                self.time_slider.configure(to=self.timeline_manager.get_total_duration())
                self.time_slider.set(self.timeline_manager.get_current_time())
                self._update_layer_list()
                self.preview_canvas.refresh()
                self._update_time_display()
                self.status_label.config(text=f"Loaded: {file_path}")
            except Exception as e:
                messagebox.showerror("Open Project", f"Error loading project: {e}")
    
    def _save_project(self):
        """Save current project"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Project",
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            if file_path:
                import json
                timeline_data = self.timeline_manager.export_timeline_data()
                project = {
                    "timeline": timeline_data,
                    "background_music": self.background_music_path,
                    "background_music_volume": self.background_music_volume,
                    "voice_path": self.voice_path,
                    "voice_volume": self.voice_volume,
                    "app": {
                        "name": "Video Editor",
                        "version": "1.0.0"
                    }
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(project, f, ensure_ascii=False, indent=2)
                
                # Safely update status label
                try:
                    if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                        self.status_label.config(text=f"Saved: {file_path}")
                except (tk.TclError, AttributeError):
                    pass  # Ignore widget errors
                    
                messagebox.showinfo("Save Project", f"Project saved successfully to:\n{file_path}")
                
        except Exception as e:
            print(f"Error saving project: {e}")
            messagebox.showerror("Save Project", f"Error saving project: {str(e)}")
    
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
            # Export settings dialog (encoder, quality)
            settings = self._ask_export_settings()
            if not settings:
                return
            preferred_encoder = settings.get("encoder", "auto")
            quality = settings.get("quality", "high")
            timeline_data = self.timeline_manager.export_timeline_data()
            
            # No background video - use solid color background
            background_video = None
            
            background_music = self.background_music_path
            if background_music is None:
                if messagebox.askyesno("Background Music", "Would you like to add background music?"):
                    music_files = filedialog.askopenfilenames(
                        title="Select Background Music",
                        filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.m4a"), ("All Files", "*.*")]
                    )
                    if music_files:
                        background_music = music_files[0]
                        self.background_music_path = background_music
            # Show modal progress dialog before starting render
            self._show_render_progress_dialog()

            self.video_renderer.render_video(
                timeline_data, 
                output_path,
                quality=quality,
                background_video=background_video,
                background_music=background_music,
                music_volume=self.background_music_volume,
                voice_path=self.voice_path,
                voice_volume=self.voice_volume,
                preferred_encoder=preferred_encoder,
                progress_callback=self._on_render_progress
            )

    def _ask_export_settings(self):
        """Modal dialog to choose export encoder and quality."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Export Settings")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        frm = ttk.Frame(dlg, padding=16)
        frm.pack(fill=tk.BOTH, expand=True)

        # Encoder selection
        ttk.Label(frm, text="Encoder:").grid(row=0, column=0, sticky="w")
        enc_var = tk.StringVar(value="auto")
        enc_combo = ttk.Combobox(frm, state="readonly", textvariable=enc_var,
                                 values=["auto", "nvidia (NVENC)", "amd (AMF)", "cpu (x264)"])
        enc_combo.grid(row=0, column=1, sticky="ew", padx=(12, 0))
        enc_combo.current(0)

        # Quality selection
        ttk.Label(frm, text="Quality:").grid(row=1, column=0, sticky="w", pady=(12, 0))
        qual_var = tk.StringVar(value="high")
        qual_combo = ttk.Combobox(frm, state="readonly", textvariable=qual_var,
                                  values=["high", "medium", "low"])
        qual_combo.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(12, 0))
        qual_combo.current(0)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(16, 0))
        result = {"encoder": "auto", "quality": "high"}
        def on_ok():
            sel = enc_var.get().lower()
            if sel.startswith("nvidia"):
                enc = "nvidia"
            elif sel.startswith("amd"):
                enc = "amd"
            elif sel.startswith("cpu"):
                enc = "cpu"
            else:
                enc = "auto"
            result.update({"encoder": enc, "quality": qual_var.get()})
            dlg.destroy()
        def on_cancel():
            result.clear()
            dlg.destroy()
        ttk.Button(btns, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=(8,0))
        ttk.Button(btns, text="Cancel", command=on_cancel).pack(side=tk.RIGHT)

        frm.columnconfigure(1, weight=1)

        # Center and wait
        dlg.update_idletasks()
        px = self.root.winfo_rootx(); py = self.root.winfo_rooty()
        pw = self.root.winfo_width(); ph = self.root.winfo_height()
        ww = dlg.winfo_width(); wh = dlg.winfo_height()
        x = px + (pw - ww) // 2; y = py + (ph - wh) // 2
        dlg.geometry(f"+{x}+{y}")
        self.root.wait_window(dlg)

        return result if result else None

    def _show_render_progress_dialog(self):
        """Create and show a modal progress dialog for rendering."""
        # If already showing, reuse
        if hasattr(self, "progress_window") and self.progress_window and tk.Toplevel.winfo_exists(self.progress_window):
            return
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Exporting Video")
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        self.progress_window.resizable(False, False)
        self.progress_window.protocol("WM_DELETE_WINDOW", self._on_cancel_render)

        container = ttk.Frame(self.progress_window, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        title_lbl = ttk.Label(container, text="Exporting...", font=("Segoe UI", 12, "bold"))
        title_lbl.pack(anchor=tk.W)

        self.status_label = ttk.Label(container, text="Initializing render...", foreground="#495057")
        self.status_label.pack(fill=tk.X, pady=(8, 6))

        self.progress_bar = ttk.Progressbar(container, orient=tk.HORIZONTAL, length=360, mode='determinate', maximum=100)
        self.progress_bar.pack(fill=tk.X)

        btn_row = ttk.Frame(container)
        btn_row.pack(fill=tk.X, pady=(12, 0))
        self.cancel_btn = ttk.Button(btn_row, text="Cancel", command=self._on_cancel_render)
        self.cancel_btn.pack(side=tk.RIGHT)

        # Center dialog relative to parent
        self.progress_window.update_idletasks()
        px = self.root.winfo_rootx()
        py = self.root.winfo_rooty()
        pw = self.root.winfo_width()
        ph = self.root.winfo_height()
        ww = self.progress_window.winfo_width()
        wh = self.progress_window.winfo_height()
        x = px + (pw - ww) // 2
        y = py + (ph - wh) // 2
        self.progress_window.geometry(f"+{x}+{y}")

    def _on_cancel_render(self):
        """Handle cancel action from progress dialog."""
        try:
            if hasattr(self, "video_renderer") and self.video_renderer and self.video_renderer.is_rendering:
                self.video_renderer.cancel_render()
        except Exception:
            pass
        # Disable button to prevent repeat
        if hasattr(self, "cancel_btn") and self.cancel_btn:
            self.cancel_btn.state(["disabled"]) 
        # Update status
        if hasattr(self, "status_label") and self.status_label:
            self.status_label.config(text="Cancelling...")
    
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
        if hasattr(self, 'layer_panel') and self.layer_panel is not None:
            self.layer_panel.refresh_layers()
    
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
        # Ensure dialog exists
        if not hasattr(self, "progress_window") or not tk.Toplevel.winfo_exists(self.progress_window):
            self._show_render_progress_dialog()
        # Update UI
        if hasattr(self, "progress_bar") and self.progress_bar:
            self.progress_bar['value'] = max(0, min(100, progress * 100))
        if hasattr(self, "status_label") and self.status_label:
            self.status_label.config(text=status)
        self.root.update_idletasks()

        # Close on completion or failure
        status_lower = (status or "").lower()
        if progress >= 1.0 or "complete" in status_lower or "failed" in status_lower or "error" in status_lower or not getattr(self.video_renderer, "is_rendering", False):
            try:
                if hasattr(self, "progress_window") and tk.Toplevel.winfo_exists(self.progress_window):
                    self.progress_window.grab_release()
                    self.progress_window.destroy()
            except Exception:
                pass
            # Notify user
            if "complete" in status_lower or progress >= 1.0:
                messagebox.showinfo("Export", "Video export completed successfully.")
            elif "failed" in status_lower or "error" in status_lower:
                messagebox.showerror("Export", f"Video export failed: {status}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
