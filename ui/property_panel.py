"""
Property panel for editing layer properties
"""
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from typing import Optional, Callable, Dict, Any
from models.base_layer import BaseLayer
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer


class PropertyPanel(ttk.Frame):
    """Property panel for editing layer properties"""
    
    def __init__(self, parent, on_property_change: Optional[Callable] = None):
        super().__init__(parent)
        
        self.on_property_change = on_property_change
        self.selected_layer: Optional[BaseLayer] = None
        self.property_widgets: Dict[str, tk.Widget] = {}
        
        self._create_ui()
    
    def _create_ui(self):
        """Create property panel UI"""
        # Create scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Show empty state initially
        self._show_empty_state()
    
    def set_selected_layer(self, layer: Optional[BaseLayer]):
        """Set selected layer and update panel"""
        self.selected_layer = layer
        self._clear_properties()
        
        if layer:
            self._show_layer_properties(layer)
        else:
            self._show_empty_state()
    
    def _clear_properties(self):
        """Clear all property widgets"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.property_widgets.clear()
    
    def _show_empty_state(self):
        """Show empty state when no layer is selected"""
        label = ttk.Label(self.scrollable_frame, text="No layer selected", font=("Segoe UI", 12))
        label.pack(pady=20)
    
    def _show_layer_properties(self, layer: BaseLayer):
        """Show properties for selected layer"""
        if isinstance(layer, TextLayer):
            self._show_text_properties(layer)
        elif isinstance(layer, ImageLayer):
            self._show_image_properties(layer)
        elif isinstance(layer, BoxLayer):
            self._show_box_properties(layer)
        else:
            self._show_generic_properties(layer)
    
    def _show_text_properties(self, layer: TextLayer):
        """Show text layer properties"""
        # Layer info
        self._add_section("Layer Info")
        self._add_label("Type", "Text Layer")
        self._add_label("ID", layer.layer_id)
        
        # Text content
        self._add_section("Text Content")
        self._add_text_entry("text", "Text", layer.text)
        
        # Font properties
        self._add_section("Font Properties")
        self._add_font_family_combo("font_family", "Font Family", layer.font_family)
        self._add_spinbox("font_size", "Font Size", layer.font_size, 8, 72)
        self._add_color_button("font_color", "Font Color", layer.font_color)
        self._add_checkbox("bold", "Bold", layer.bold)
        self._add_checkbox("italic", "Italic", layer.italic)
        self._add_checkbox("underline", "Underline", layer.underline)
        
        # Background
        self._add_section("Background")
        self._add_color_button("bg_color", "Background Color", layer.bg_color)
        self._add_scale("bg_opacity", "Background Opacity", layer.bg_opacity, 0.0, 1.0)
        
        # Border
        self._add_section("Border")
        self._add_color_button("border_color", "Border Color", layer.border_color)
        self._add_spinbox("border_width", "Border Width", layer.border_width, 0, 10)
        
        # Position and size
        self._add_section("Position & Size")
        self._add_spinbox("x", "X Position", int(layer.x), 0, 2000)
        self._add_spinbox("y", "Y Position", int(layer.y), 0, 2000)
        self._add_spinbox("width", "Width", int(layer.width), 10, 2000)
        self._add_spinbox("height", "Height", int(layer.height), 10, 2000)
        
        # Timing
        self._add_section("Timing")
        self._add_spinbox("start_time", "Start Time", layer.start_time, 0.0, 100.0, 0.1)
        self._add_spinbox("end_time", "End Time", layer.end_time, 0.0, 100.0, 0.1)
        
        # Visibility
        self._add_section("Visibility")
        self._add_scale("opacity", "Opacity", layer.opacity, 0.0, 1.0)
        self._add_checkbox("visible", "Visible", layer.visible)
    
    def _show_image_properties(self, layer: ImageLayer):
        """Show image layer properties"""
        # Layer info
        self._add_section("Layer Info")
        self._add_label("Type", "Image Layer")
        self._add_label("ID", layer.layer_id)
        
        # Image file
        self._add_section("Image File")
        self._add_file_button("image_path", "Image Path", layer.image_path, [("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        
        # Image properties
        self._add_section("Image Properties")
        self._add_combo("fit_mode", "Fit Mode", layer.fit_mode, ["stretch", "fit", "fill", "cover", "original"])
        self._add_spinbox("rotation", "Rotation", layer.rotation, -360, 360, 1)
        self._add_checkbox("flip_horizontal", "Flip Horizontal", layer.flip_horizontal)
        self._add_checkbox("flip_vertical", "Flip Vertical", layer.flip_vertical)
        
        # Effects
        self._add_section("Effects")
        self._add_scale("brightness", "Brightness", layer.brightness, 0.0, 2.0)
        self._add_scale("contrast", "Contrast", layer.contrast, 0.0, 2.0)
        self._add_scale("saturation", "Saturation", layer.saturation, 0.0, 2.0)
        
        # Position and size
        self._add_section("Position & Size")
        self._add_spinbox("x", "X Position", int(layer.x), 0, 2000)
        self._add_spinbox("y", "Y Position", int(layer.y), 0, 2000)
        self._add_spinbox("width", "Width", int(layer.width), 10, 2000)
        self._add_spinbox("height", "Height", int(layer.height), 10, 2000)
        
        # Timing
        self._add_section("Timing")
        self._add_spinbox("start_time", "Start Time", layer.start_time, 0.0, 100.0, 0.1)
        self._add_spinbox("end_time", "End Time", layer.end_time, 0.0, 100.0, 0.1)
        
        # Visibility
        self._add_section("Visibility")
        self._add_scale("opacity", "Opacity", layer.opacity, 0.0, 1.0)
        self._add_checkbox("visible", "Visible", layer.visible)
    
    def _show_box_properties(self, layer: BoxLayer):
        """Show box layer properties"""
        # Layer info
        self._add_section("Layer Info")
        self._add_label("Type", "Box Layer")
        self._add_label("ID", layer.layer_id)
        
        # Fill properties
        self._add_section("Fill Properties")
        self._add_color_button("fill_color", "Fill Color", layer.fill_color)
        self._add_scale("fill_opacity", "Fill Opacity", layer.fill_opacity, 0.0, 1.0)
        
        # Border properties
        self._add_section("Border Properties")
        self._add_color_button("border_color", "Border Color", layer.border_color)
        self._add_spinbox("border_width", "Border Width", layer.border_width, 0, 20)
        self._add_combo("border_style", "Border Style", layer.border_style, ["solid", "dashed", "dotted"])
        
        # Shape properties
        self._add_section("Shape Properties")
        self._add_spinbox("corner_radius", "Corner Radius", layer.corner_radius, 0, 50)
        
        # Gradient
        self._add_section("Gradient")
        self._add_checkbox("gradient", "Enable Gradient", layer.gradient)
        self._add_color_button("gradient_color", "Gradient Color", layer.gradient_color)
        self._add_combo("gradient_direction", "Gradient Direction", layer.gradient_direction, ["horizontal", "vertical", "diagonal"])
        
        # Position and size
        self._add_section("Position & Size")
        self._add_spinbox("x", "X Position", int(layer.x), 0, 2000)
        self._add_spinbox("y", "Y Position", int(layer.y), 0, 2000)
        self._add_spinbox("width", "Width", int(layer.width), 10, 2000)
        self._add_spinbox("height", "Height", int(layer.height), 10, 2000)
        
        # Timing
        self._add_section("Timing")
        self._add_spinbox("start_time", "Start Time", layer.start_time, 0.0, 100.0, 0.1)
        self._add_spinbox("end_time", "End Time", layer.end_time, 0.0, 100.0, 0.1)
        
        # Visibility
        self._add_section("Visibility")
        self._add_scale("opacity", "Opacity", layer.opacity, 0.0, 1.0)
        self._add_checkbox("visible", "Visible", layer.visible)
    
    def _show_generic_properties(self, layer: BaseLayer):
        """Show generic layer properties"""
        # Layer info
        self._add_section("Layer Info")
        self._add_label("Type", layer.__class__.__name__)
        self._add_label("ID", layer.layer_id)
        
        # Position and size
        self._add_section("Position & Size")
        self._add_spinbox("x", "X Position", int(layer.x), 0, 2000)
        self._add_spinbox("y", "Y Position", int(layer.y), 0, 2000)
        self._add_spinbox("width", "Width", int(layer.width), 10, 2000)
        self._add_spinbox("height", "Height", int(layer.height), 10, 2000)
        
        # Timing
        self._add_section("Timing")
        self._add_spinbox("start_time", "Start Time", layer.start_time, 0.0, 100.0, 0.1)
        self._add_spinbox("end_time", "End Time", layer.end_time, 0.0, 100.0, 0.1)
        
        # Visibility
        self._add_section("Visibility")
        self._add_scale("opacity", "Opacity", layer.opacity, 0.0, 1.0)
        self._add_checkbox("visible", "Visible", layer.visible)
    
    def _add_section(self, title: str):
        """Add a section header"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=(10, 5))
        
        label = ttk.Label(frame, text=title, font=("Segoe UI", 10, "bold"))
        label.pack(anchor="w")
    
    def _add_label(self, name: str, value: str):
        """Add a label widget"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=name + ":", width=15, anchor="w").pack(side="left")
        ttk.Label(frame, text=str(value)).pack(side="left", padx=(5, 0))
    
    def _add_text_entry(self, property_name: str, label: str, value: str):
        """Add a text entry widget"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        entry = ttk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        entry.insert(0, str(value))
        entry.bind("<KeyRelease>", lambda e: self._on_property_change(property_name, entry.get()))
        
        self.property_widgets[property_name] = entry
    
    def _add_spinbox(self, property_name: str, label: str, value: float, from_: float, to: float, increment: float = 1.0):
        """Add a spinbox widget"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        spinbox = ttk.Spinbox(frame, from_=from_, to=to, increment=increment, width=10)
        spinbox.pack(side="left", padx=(5, 0))
        spinbox.set(value)
        spinbox.bind("<KeyRelease>", lambda e: self._on_property_change(property_name, float(spinbox.get())))
        spinbox.bind("<Button-1>", lambda e: self._on_property_change(property_name, float(spinbox.get())))
        
        self.property_widgets[property_name] = spinbox
    
    def _add_scale(self, property_name: str, label: str, value: float, from_: float, to: float):
        """Add a scale widget"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        scale = ttk.Scale(frame, from_=from_, to=to, orient="horizontal")
        scale.pack(side="left", fill="x", expand=True, padx=(5, 0))
        scale.set(value)
        scale.bind("<ButtonRelease-1>", lambda e: self._on_property_change(property_name, scale.get()))
        
        # Value label
        value_label = ttk.Label(frame, text=f"{value:.2f}", width=6)
        value_label.pack(side="left", padx=(5, 0))
        
        def update_value_label(e):
            value_label.config(text=f"{scale.get():.2f}")
            self._on_property_change(property_name, scale.get())
        
        scale.bind("<Motion>", update_value_label)
        
        self.property_widgets[property_name] = scale
    
    def _add_checkbox(self, property_name: str, label: str, value: bool):
        """Add a checkbox widget"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        checkbox = ttk.Checkbutton(frame, command=lambda: self._on_property_change(property_name, checkbox_var.get()))
        checkbox.pack(side="left", padx=(5, 0))
        
        checkbox_var = tk.BooleanVar(value=value)
        checkbox.config(variable=checkbox_var)
        
        self.property_widgets[property_name] = checkbox
    
    def _add_combo(self, property_name: str, label: str, value: str, values: list):
        """Add a combobox widget"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        combo = ttk.Combobox(frame, values=values, state="readonly", width=15)
        combo.pack(side="left", padx=(5, 0))
        combo.set(value)
        combo.bind("<<ComboboxSelected>>", lambda e: self._on_property_change(property_name, combo.get()))
        
        self.property_widgets[property_name] = combo
    
    def _add_color_button(self, property_name: str, label: str, value: str):
        """Add a color chooser button"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        
        color_frame = ttk.Frame(frame)
        color_frame.pack(side="left", padx=(5, 0))
        
        color_button = tk.Button(color_frame, bg=value, width=3, height=1,
                                command=lambda: self._choose_color(property_name, color_button))
        color_button.pack(side="left")
        
        ttk.Label(color_frame, text=value, width=10).pack(side="left", padx=(5, 0))
        
        self.property_widgets[property_name] = color_button
    
    def _add_file_button(self, property_name: str, label: str, value: str, filetypes: list):
        """Add a file selection button"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        
        file_frame = ttk.Frame(frame)
        file_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        entry = ttk.Entry(file_frame)
        entry.pack(side="left", fill="x", expand=True)
        entry.insert(0, value)
        
        button = ttk.Button(file_frame, text="Browse", width=8,
                           command=lambda: self._choose_file(property_name, entry, filetypes))
        button.pack(side="left", padx=(5, 0))
        
        self.property_widgets[property_name] = entry
    
    def _add_font_family_combo(self, property_name: str, label: str, value: str):
        """Add a font family combobox"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label + ":", width=15, anchor="w").pack(side="left")
        combo = ttk.Combobox(frame, values=["Arial", "Times", "Courier", "Helvetica", "Verdana"], 
                           state="readonly", width=15)
        combo.pack(side="left", padx=(5, 0))
        combo.set(value)
        combo.bind("<<ComboboxSelected>>", lambda e: self._on_property_change(property_name, combo.get()))
        
        self.property_widgets[property_name] = combo
    
    def _choose_color(self, property_name: str, button: tk.Button):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(initialcolor=button.cget("bg"))[1]
        if color:
            button.config(bg=color)
            self._on_property_change(property_name, color)
    
    def _choose_file(self, property_name: str, entry: ttk.Entry, filetypes: list):
        """Open file chooser dialog"""
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
            self._on_property_change(property_name, file_path)
            
            # Special handling for image_path changes
            if property_name == "image_path" and self.selected_layer:
                if hasattr(self.selected_layer, 'load_image'):
                    if self.selected_layer.load_image(file_path):
                        print(f"Successfully loaded image: {file_path}")
                    else:
                        print(f"Failed to load image: {file_path}")
                    # Refresh preview canvas if available
                    if hasattr(self, 'preview_canvas'):
                        self.preview_canvas.refresh()
    
    def _on_property_change(self, property_name: str, value):
        """Handle property change"""
        if self.on_property_change:
            self.on_property_change(property_name, value)
