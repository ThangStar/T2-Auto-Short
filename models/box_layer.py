"""
Box layer model for video editor
"""
from typing import Dict, Any
import tkinter as tk
from .base_layer import BaseLayer


class BoxLayer(BaseLayer):
    """Box layer for displaying rectangular shapes in video"""
    
    def __init__(self, layer_id: str, start_time: float = 0.0, end_time: float = 5.0):
        super().__init__(layer_id, start_time, end_time)
        self.fill_color = "#FF0000"
        self.fill_opacity = 0.5
        self.border_color = "#000000"
        self.border_width = 2
        self.border_style = "solid"  # solid, dashed, dotted
        self.corner_radius = 0  # For rounded rectangles
        self.gradient = False
        self.gradient_color = "#00FF00"
        self.gradient_direction = "horizontal"  # horizontal, vertical, diagonal
        
    def get_properties(self) -> Dict[str, Any]:
        """Get all box properties"""
        return {
            "fill_color": self.fill_color,
            "fill_opacity": self.fill_opacity,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "border_style": self.border_style,
            "corner_radius": self.corner_radius,
            "gradient": self.gradient,
            "gradient_color": self.gradient_color,
            "gradient_direction": self.gradient_direction,
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
        """Set a box property"""
        if hasattr(self, property_name):
            setattr(self, property_name, value)
            return True
        return False
    
    def render_preview(self, canvas: tk.Canvas, current_time: float) -> None:
        """Render box on preview canvas"""
        if not self.is_visible_at_time(current_time):
            return
        
        # Calculate final opacity
        final_opacity = self.opacity * self.fill_opacity
        
        # Draw fill
        if self.fill_opacity > 0:
            if self.corner_radius > 0:
                # Rounded rectangle
                self._draw_rounded_rectangle(
                    canvas, self.x, self.y, self.x + self.width, self.y + self.height,
                    self.corner_radius, self.fill_color, final_opacity
                )
            else:
                # Regular rectangle
                fill_item = canvas.create_rectangle(
                    self.x, self.y, self.x + self.width, self.y + self.height,
                    fill=self.fill_color, outline="", stipple="gray50"
                )
        
        # Draw gradient if enabled
        if self.gradient and self.fill_opacity > 0:
            self._draw_gradient(canvas)
        
        # Draw border
        if self.border_width > 0:
            dash_pattern = None
            if self.border_style == "dashed":
                dash_pattern = (5, 5)
            elif self.border_style == "dotted":
                dash_pattern = (2, 2)
            
            border_item = canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                outline=self.border_color, width=self.border_width,
                dash=dash_pattern
            )
    
    def _draw_rounded_rectangle(self, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, radius: int, color: str, opacity: float):
        """Draw a rounded rectangle"""
        # For simplicity, we'll use a regular rectangle
        # In a real implementation, you'd use PIL or other graphics library
        rounded_item = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
    
    def _draw_gradient(self, canvas: tk.Canvas):
        """Draw gradient fill"""
        # Simple gradient implementation
        steps = 20
        color1 = self._hex_to_rgb(self.fill_color)
        color2 = self._hex_to_rgb(self.gradient_color)
        
        for i in range(steps):
            ratio = i / (steps - 1)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            if self.gradient_direction == "horizontal":
                x1 = self.x + (self.width * ratio)
                x2 = self.x + (self.width * (ratio + 1/steps))
                canvas.create_rectangle(x1, self.y, x2, self.y + self.height, fill=color, outline="")
            else:  # vertical
                y1 = self.y + (self.height * ratio)
                y2 = self.y + (self.height * (ratio + 1/steps))
                canvas.create_rectangle(self.x, y1, self.x + self.width, y2, fill=color, outline="")
    
    def export_data(self) -> Dict[str, Any]:
        """Export box layer data for video rendering"""
        return {
            "type": "box",
            "layer_id": self.layer_id,
            "fill_color": self.fill_color,
            "fill_opacity": self.fill_opacity,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "border_style": self.border_style,
            "corner_radius": self.corner_radius,
            "gradient": self.gradient,
            "gradient_color": self.gradient_color,
            "gradient_direction": self.gradient_direction,
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
