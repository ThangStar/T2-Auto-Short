"""
Text layer model for video editor
"""
from typing import Dict, Any
import tkinter as tk
from tkinter import font
from .base_layer import BaseLayer


class TextLayer(BaseLayer):
    """Text layer for displaying text in video"""
    
    def __init__(self, layer_id: str, text: str = "Sample Text", start_time: float = 0.0, end_time: float = 5.0):
        super().__init__(layer_id, start_time, end_time)
        self.text = text
        self.font_family = "Arial"
        self.font_size = 24
        self.font_color = "#FFFFFF"
        self.bg_color = "#000000"
        self.bg_opacity = 0.0
        self.border_color = "#000000"
        self.border_width = 0
        self.alignment = "center"  # left, center, right
        self.bold = False
        self.italic = False
        self.underline = False
        
    def get_properties(self) -> Dict[str, Any]:
        """Get all text properties"""
        return {
            "text": self.text,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_color": self.font_color,
            "bg_color": self.bg_color,
            "bg_opacity": self.bg_opacity,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "alignment": self.alignment,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "opacity": self.opacity,
            "visible": self.visible
        }
    
    def set_property(self, property_name: str, value: Any) -> bool:
        """Set a text property"""
        if hasattr(self, property_name):
            setattr(self, property_name, value)
            return True
        return False
    
    def render_preview(self, canvas: tk.Canvas, current_time: float) -> None:
        """Render text on preview canvas"""
        if not self.is_visible_at_time(current_time):
            return
            
        # Calculate opacity
        alpha = int(self.opacity * 255)
        
        # Create font
        font_weight = "bold" if self.bold else "normal"
        font_slant = "italic" if self.italic else "roman"
        font_underline = self.underline
        
        font_obj = font.Font(family=self.font_family, size=self.font_size, 
                           weight=font_weight, slant=font_slant, underline=font_underline)
        
        # Draw background if needed
        if self.bg_opacity > 0:
            bg_color = self._hex_to_rgb(self.bg_color)
            canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                fill=self.bg_color, outline="", stipple="gray50"
            )
        
        # Draw border if needed
        if self.border_width > 0:
            canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                outline=self.border_color, width=self.border_width
            )
        
        # Draw text
        text_color = self.font_color
        text_item = canvas.create_text(
            self.x + self.width // 2, self.y + self.height // 2,
            text=self.text, fill=text_color, font=font_obj,
            anchor="center", width=self.width
        )
    
    def export_data(self) -> Dict[str, Any]:
        """Export text layer data for video rendering"""
        return {
            "type": "text",
            "layer_id": self.layer_id,
            "text": self.text,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_color": self.font_color,
            "bg_color": self.bg_color,
            "bg_opacity": self.bg_opacity,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "alignment": self.alignment,
            "bold": self.bold,
            "italic": self.italic,
            "underline": self.underline,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "opacity": self.opacity,
            "visible": self.visible
        }
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
