"""
Timeline manager for handling video layers and timing
"""
from typing import List, Dict, Any, Optional
from models.base_layer import BaseLayer
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer
import json


class TimelineManager:
    """Manages timeline, layers, and timing for video editor"""
    
    def __init__(self):
        self.layers: List[BaseLayer] = []
        self.current_time = 0.0
        self.total_duration = 10.0  # Default 10 seconds
        self.fps = 30
        self.selected_layer: Optional[BaseLayer] = None
        
    def add_layer(self, layer: BaseLayer) -> bool:
        """Add a new layer to timeline"""
        try:
            self.layers.append(layer)
            self._sort_layers_by_z_index()
            return True
        except Exception as e:
            print(f"Error adding layer: {e}")
            return False
    
    def remove_layer(self, layer_id: str) -> bool:
        """Remove layer by ID"""
        try:
            self.layers = [layer for layer in self.layers if layer.layer_id != layer_id]
            if self.selected_layer and self.selected_layer.layer_id == layer_id:
                self.selected_layer = None
            return True
        except Exception as e:
            print(f"Error removing layer: {e}")
            return False
    
    def get_layer(self, layer_id: str) -> Optional[BaseLayer]:
        """Get layer by ID"""
        for layer in self.layers:
            if layer.layer_id == layer_id:
                return layer
        return None
    
    def get_layers_at_time(self, time: float) -> List[BaseLayer]:
        """Get all visible layers at given time"""
        visible_layers = []
        for layer in self.layers:
            if layer.is_visible_at_time(time):
                visible_layers.append(layer)
        return visible_layers
    
    def get_all_layers(self) -> List[BaseLayer]:
        """Get all layers"""
        return self.layers.copy()
    
    def set_current_time(self, time: float):
        """Set current timeline time"""
        self.current_time = max(0, min(time, self.total_duration))
    
    def get_current_time(self) -> float:
        """Get current timeline time"""
        return self.current_time
    
    def set_total_duration(self, duration: float):
        """Set total video duration"""
        self.total_duration = max(1.0, duration)
    
    def get_total_duration(self) -> float:
        """Get total video duration"""
        return self.total_duration
    
    def select_layer(self, layer_id: str) -> bool:
        """Select layer by ID"""
        layer = self.get_layer(layer_id)
        if layer:
            self.selected_layer = layer
            return True
        return False
    
    def get_selected_layer(self) -> Optional[BaseLayer]:
        """Get currently selected layer"""
        return self.selected_layer
    
    def clear_selection(self):
        """Clear layer selection"""
        self.selected_layer = None
    
    def move_layer_up(self, layer_id: str) -> bool:
        """Move layer up in z-order"""
        layer = self.get_layer(layer_id)
        if layer:
            layer.z_index += 1
            self._sort_layers_by_z_index()
            return True
        return False
    
    def move_layer_down(self, layer_id: str) -> bool:
        """Move layer down in z-order"""
        layer = self.get_layer(layer_id)
        if layer:
            layer.z_index -= 1
            self._sort_layers_by_z_index()
            return True
        return False
    
    def _sort_layers_by_z_index(self):
        """Sort layers by z-index"""
        self.layers.sort(key=lambda layer: layer.z_index)
    
    def create_text_layer(self, text: str = "New Text", start_time: float = 0.0, end_time: float = 5.0) -> TextLayer:
        """Create a new text layer"""
        layer_id = f"text_{len(self.layers) + 1}"
        layer = TextLayer(layer_id, text, start_time, end_time)
        layer.z_index = len(self.layers)
        self.add_layer(layer)
        return layer
    
    def create_image_layer(self, image_path: str, start_time: float = 0.0, end_time: float = 5.0) -> ImageLayer:
        """Create a new image layer"""
        layer_id = f"image_{len(self.layers) + 1}"
        layer = ImageLayer(layer_id, image_path, start_time, end_time)
        layer.z_index = len(self.layers)
        self.add_layer(layer)
        return layer
    
    def create_box_layer(self, start_time: float = 0.0, end_time: float = 5.0) -> BoxLayer:
        """Create a new box layer"""
        layer_id = f"box_{len(self.layers) + 1}"
        layer = BoxLayer(layer_id, start_time, end_time)
        layer.z_index = len(self.layers)
        self.add_layer(layer)
        return layer
    
    def export_timeline_data(self) -> Dict[str, Any]:
        """Export timeline data for saving/loading"""
        return {
            "total_duration": self.total_duration,
            "fps": self.fps,
            "current_time": self.current_time,
            "layers": [layer.export_data() for layer in self.layers]
        }
    
    def import_timeline_data(self, data: Dict[str, Any]) -> bool:
        """Import timeline data from saved project"""
        try:
            self.total_duration = data.get("total_duration", 10.0)
            self.fps = data.get("fps", 30)
            self.current_time = data.get("current_time", 0.0)
            
            self.layers.clear()
            for layer_data in data.get("layers", []):
                layer_type = layer_data.get("type")
                if layer_type == "text":
                    layer = TextLayer(layer_data["layer_id"])
                elif layer_type == "image":
                    layer = ImageLayer(layer_data["layer_id"])
                elif layer_type == "box":
                    layer = BoxLayer(layer_data["layer_id"])
                else:
                    continue
                
                # Set properties
                for key, value in layer_data.items():
                    if hasattr(layer, key):
                        setattr(layer, key, value)
                
                self.layers.append(layer)
            
            self._sort_layers_by_z_index()
            return True
        except Exception as e:
            print(f"Error importing timeline data: {e}")
            return False
    
    def get_timeline_summary(self) -> Dict[str, Any]:
        """Get timeline summary for UI display"""
        return {
            "total_layers": len(self.layers),
            "total_duration": self.total_duration,
            "current_time": self.current_time,
            "fps": self.fps,
            "layers": [
                {
                    "id": layer.layer_id,
                    "type": layer.__class__.__name__.replace("Layer", "").lower(),
                    "start_time": layer.start_time,
                    "end_time": layer.end_time,
                    "duration": layer.get_duration(),
                    "z_index": layer.z_index,
                    "visible": layer.visible
                }
                for layer in self.layers
            ]
        }
