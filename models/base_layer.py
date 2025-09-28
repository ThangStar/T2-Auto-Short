"""
Base layer class for all video elements
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import tkinter as tk


class BaseLayer(ABC):
    """Base class for all video layers (text, image, box)"""
    
    def __init__(self, layer_id: str, start_time: float = 0.0, end_time: float = 5.0):
        self.layer_id = layer_id
        self.start_time = start_time
        self.end_time = end_time
        self.x = 100
        self.y = 100
        self.width = 200
        self.height = 100
        self.visible = True
        self.opacity = 1.0
        self.z_index = 0
        
    @abstractmethod
    def get_properties(self) -> Dict[str, Any]:
        """Get all properties of this layer for editing"""
        pass
    
    @abstractmethod
    def set_property(self, property_name: str, value: Any) -> bool:
        """Set a property value"""
        pass
    
    @abstractmethod
    def render_preview(self, canvas: tk.Canvas, current_time: float) -> None:
        """Render this layer on the preview canvas"""
        pass
    
    @abstractmethod
    def export_data(self) -> Dict[str, Any]:
        """Export layer data for video rendering"""
        pass
    
    def is_visible_at_time(self, time: float) -> bool:
        """Check if layer is visible at given time"""
        return self.visible and self.start_time <= time <= self.end_time
    
    def get_duration(self) -> float:
        """Get layer duration"""
        return self.end_time - self.start_time
    
    def set_timing(self, start_time: float, end_time: float):
        """Set layer timing"""
        self.start_time = start_time
        self.end_time = end_time
    
    def set_position(self, x: float, y: float):
        """Set layer position"""
        self.x = x
        self.y = y
    
    def set_size(self, width: float, height: float):
        """Set layer size"""
        self.width = width
        self.height = height
