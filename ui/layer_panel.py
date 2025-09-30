"""
Modern layer panel with drag & drop support and icons
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List
from models.base_layer import BaseLayer
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer


class LayerItem(ttk.Frame):
    """Individual layer item with icon, name, and controls"""
    
    def __init__(self, parent, layer: BaseLayer, on_select: Optional[Callable] = None, 
                 on_toggle_visibility: Optional[Callable] = None, on_delete: Optional[Callable] = None):
        super().__init__(parent, style='LayerItem.TFrame')
        self.layer = layer
        self.on_select = on_select
        self.on_toggle_visibility = on_toggle_visibility
        self.on_delete = on_delete
        self.is_selected = False
        self.drag_start_y = 0
        
        self._create_widgets()
        self._setup_bindings()
    
    def _create_widgets(self):
        """Create layer item widgets"""
        # Main container with padding
        self.configure(padding=8)
        
        # Icon based on layer type
        icon_text = self._get_layer_icon()
        self.icon_label = ttk.Label(self, text=icon_text, font=('Segoe UI Emoji', 14))
        self.icon_label.grid(row=0, column=0, padx=(0, 8), sticky='w')
        
        # Layer info frame
        info_frame = ttk.Frame(self)
        info_frame.grid(row=0, column=1, sticky='ew', padx=(0, 8))
        info_frame.columnconfigure(0, weight=1)
        
        # Layer name
        layer_name = self._get_layer_name()
        self.name_label = ttk.Label(info_frame, text=layer_name, font=('Inter', 10, 'bold'))
        self.name_label.grid(row=0, column=0, sticky='w')
        
        # Layer details
        details = self._get_layer_details()
        self.details_label = ttk.Label(info_frame, text=details, font=('Inter', 8), 
                                     foreground='#6c757d')
        self.details_label.grid(row=1, column=0, sticky='w')
        
        # Controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=2, sticky='e')
        
        # Visibility toggle
        vis_text = "👁" if self.layer.visible else "🚫"
        self.visibility_btn = ttk.Button(controls_frame, text=vis_text, width=3,
                                       command=self._toggle_visibility)
        self.visibility_btn.grid(row=0, column=0, padx=2)
        
        # Delete button
        self.delete_btn = ttk.Button(controls_frame, text="🗑", width=3,
                                   command=self._delete_layer, style='Danger.TButton')
        self.delete_btn.grid(row=0, column=1, padx=2)
        
        # Configure grid weights
        self.columnconfigure(1, weight=1)
    
    def _get_layer_icon(self) -> str:
        """Get icon for layer type"""
        if isinstance(self.layer, TextLayer):
            return "📝"
        elif isinstance(self.layer, ImageLayer):
            return "🖼️"
        elif isinstance(self.layer, BoxLayer):
            return "⬜"
        else:
            return "📄"
    
    def _get_layer_name(self) -> str:
        """Get display name for layer"""
        if isinstance(self.layer, TextLayer):
            return f"Text: {self.layer.text[:20]}..."
        elif isinstance(self.layer, ImageLayer):
            import os
            if self.layer.image_path:
                return f"Image: {os.path.basename(self.layer.image_path)[:20]}..."
            return "Image Layer"
        elif isinstance(self.layer, BoxLayer):
            return "Box Layer"
        else:
            return f"Layer {self.layer.layer_id}"
    
    def _get_layer_details(self) -> str:
        """Get layer details text"""
        duration = self.layer.get_duration()
        return f"{self.layer.start_time:.1f}s - {self.layer.end_time:.1f}s ({duration:.1f}s)"
    
    def _setup_bindings(self):
        """Setup mouse bindings for drag & drop"""
        widgets = [self, self.icon_label, self.name_label, self.details_label]
        for widget in widgets:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<B1-Motion>", self._on_drag)
            widget.bind("<ButtonRelease-1>", self._on_release)
            widget.bind("<Double-Button-1>", self._on_double_click)
    
    def _on_click(self, event):
        """Handle click - select layer and start drag"""
        self.drag_start_y = event.y_root
        if self.on_select:
            self.on_select(self.layer)
    
    def _on_drag(self, event):
        """Handle drag motion"""
        # Visual feedback for dragging could be added here
        pass
    
    def _on_release(self, event):
        """Handle drag release"""
        # Drag & drop reordering logic will be handled by parent
        pass
    
    def _on_double_click(self, event):
        """Handle double click - could open properties"""
        pass
    
    def _toggle_visibility(self):
        """Toggle layer visibility"""
        self.layer.visible = not self.layer.visible
        vis_text = "👁" if self.layer.visible else "🚫"
        self.visibility_btn.config(text=vis_text)
        if self.on_toggle_visibility:
            self.on_toggle_visibility(self.layer)
    
    def _delete_layer(self):
        """Delete this layer"""
        if self.on_delete:
            self.on_delete(self.layer)
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        if selected:
            self.configure(style='LayerItemSelected.TFrame')
        else:
            self.configure(style='LayerItem.TFrame')
    
    def update_layer_info(self):
        """Update layer information display"""
        self.name_label.config(text=self._get_layer_name())
        self.details_label.config(text=self._get_layer_details())
        vis_text = "👁" if self.layer.visible else "🚫"
        self.visibility_btn.config(text=vis_text)


class LayerPanel(ttk.Frame):
    """Modern layer panel with drag & drop reordering"""
    
    def __init__(self, parent, timeline_manager=None, on_layer_select: Optional[Callable] = None):
        super().__init__(parent)
        self.timeline_manager = timeline_manager
        self.on_layer_select = on_layer_select
        self.layer_items: List[LayerItem] = []
        self.selected_layer = None
        
        self._configure_styles()
        self._create_widgets()
    
    def _configure_styles(self):
        """Configure custom styles for layer items"""
        style = ttk.Style()
        
        # Normal layer item
        style.configure('LayerItem.TFrame',
                       background='#ffffff',
                       relief='solid',
                       borderwidth=1)
        
        # Selected layer item
        style.configure('LayerItemSelected.TFrame',
                       background='#e3f2fd',
                       relief='solid',
                       borderwidth=2)
    
    def _create_widgets(self):
        """Create panel widgets"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=12, pady=(12, 8))
        
        ttk.Label(header_frame, text="🎬 Layers", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Add layer buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="📝", width=3, command=self._add_text_layer,
                  style='Success.TButton').pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="🖼️", width=3, command=self._add_image_layer,
                  style='Success.TButton').pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="⬜", width=3, command=self._add_box_layer,
                  style='Success.TButton').pack(side=tk.LEFT, padx=1)
        
        # Scrollable layer list
        self._create_scrollable_list()
    
    def _create_scrollable_list(self):
        """Create scrollable layer list"""
        # Canvas and scrollbar for custom scrolling
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        self.canvas = tk.Canvas(canvas_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def set_timeline_manager(self, timeline_manager):
        """Set timeline manager"""
        self.timeline_manager = timeline_manager
        self.refresh_layers()
    
    def refresh_layers(self):
        """Refresh layer list display"""
        # Clear existing layer items
        for item in self.layer_items:
            item.destroy()
        self.layer_items.clear()
        
        if not self.timeline_manager:
            return
        
        # Get layers sorted by z_index (bottom to top)
        layers = sorted(self.timeline_manager.get_all_layers(), 
                       key=lambda l: l.z_index, reverse=True)  # Top layers first in UI
        
        # Create layer items
        for i, layer in enumerate(layers):
            item = LayerItem(
                self.scrollable_frame,
                layer,
                on_select=self._on_layer_select,
                on_toggle_visibility=self._on_layer_visibility_toggle,
                on_delete=self._on_layer_delete
            )
            item.pack(fill=tk.X, padx=4, pady=2)
            self.layer_items.append(item)
        
        # Update canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_layer_select(self, layer):
        """Handle layer selection"""
        self.selected_layer = layer
        
        # Update selection visual state
        for item in self.layer_items:
            item.set_selected(item.layer == layer)
        
        if self.on_layer_select:
            self.on_layer_select(layer)
    
    def _on_layer_visibility_toggle(self, layer):
        """Handle layer visibility toggle"""
        # Trigger refresh in main window
        if hasattr(self, 'preview_canvas'):
            self.preview_canvas.refresh()
    
    def _on_layer_delete(self, layer):
        """Handle layer deletion"""
        if self.timeline_manager:
            self.timeline_manager.remove_layer(layer.layer_id)
            self.refresh_layers()
            if hasattr(self, 'preview_canvas'):
                self.preview_canvas.refresh()
    
    def _add_text_layer(self):
        """Add new text layer"""
        if self.timeline_manager:
            layer = self.timeline_manager.create_text_layer("New Text")
            self.refresh_layers()
            self._on_layer_select(layer)
    
    def _add_image_layer(self):
        """Add new image layer"""
        from tkinter import filedialog
        image_paths = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), 
                      ("All Files", "*.*")]
        )
        if image_paths and self.timeline_manager:
            created = self.timeline_manager.add_sequential_images(list(image_paths), duration_per_image=3.0)
            self.refresh_layers()
            if created:
                self._on_layer_select(created[0])
    
    def _add_box_layer(self):
        """Add new box layer"""
        if self.timeline_manager:
            layer = self.timeline_manager.create_box_layer()
            self.refresh_layers()
            self._on_layer_select(layer)
