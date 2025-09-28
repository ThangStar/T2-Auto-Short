"""
Timeline manager for handling video layers and timing
"""
from typing import List, Dict, Any, Optional
import uuid
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
        # Global transition settings for image sequences
        self.image_transition: Dict[str, Any] = {"type": "none", "duration": 0.5}
        
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

    def add_sequential_images(self, image_paths: List[str], duration_per_image: float = 3.0,
                               x: Optional[float] = None, y: Optional[float] = None,
                               width: Optional[float] = None, height: Optional[float] = None) -> List[ImageLayer]:
        """Create image layers that appear one after another with fixed duration.

        All created image layers share the same position/size if provided.
        The timeline total_duration is extended to fit the last image.
        Existing text layers are extended to the new end (keep their start_time).
        """
        created_layers: List[ImageLayer] = []
        current_start = 0.0

        # If there are existing non-text layers with timings, start after the latest end
        if self.layers:
            latest_end = 0.0
            for layer in self.layers:
                if not isinstance(layer, TextLayer):
                    latest_end = max(latest_end, layer.end_time)
            current_start = latest_end

        group_id = f"imggrp_{uuid.uuid4().hex[:8]}"

        # Defaults when not provided
        if x is None:
            x = 0.0
        if y is None:
            y = 120.0
        if width is None:
            width = 720.0
        if height is None:
            height = 1050.0

        for idx, path in enumerate(image_paths):
            start_time = current_start + idx * duration_per_image
            end_time = start_time + duration_per_image
            layer = self.create_image_layer(path, start_time, end_time)
            # Mark group id for synchronized edits later
            setattr(layer, "group_id", group_id)
            if x is not None and y is not None:
                layer.set_position(x, y)
            if width is not None and height is not None:
                layer.set_size(width, height)
            created_layers.append(layer)

        # Inherit position/size and display options from the first image for the rest
        if len(created_layers) > 1:
            base = created_layers[0]
            for layer in created_layers[1:]:
                layer.set_position(base.x, base.y)
                layer.set_size(base.width, base.height)
                # Copy display-related attributes when available
                try:
                    layer.fit_mode = getattr(base, "fit_mode", layer.__dict__.get("fit_mode", "cover"))
                    layer.rotation = getattr(base, "rotation", 0.0)
                    layer.flip_horizontal = getattr(base, "flip_horizontal", False)
                    layer.flip_vertical = getattr(base, "flip_vertical", False)
                    # Recompute scaled image to reflect new fit/size before first render
                    if hasattr(layer, "_update_scaled_image"):
                        layer._update_scaled_image()
                except Exception:
                    pass

        # Extend total duration to the end of the last created image
        if created_layers:
            new_total = max(self.total_duration, created_layers[-1].end_time)
            self.set_total_duration(new_total)

            # Extend all text layers to the end of the video
            for layer in self.layers:
                if isinstance(layer, TextLayer):
                    layer.end_time = self.total_duration

        return created_layers

    def apply_property_to_group(self, group_id: str, property_name: str, value: Any,
                                include_selected_id: Optional[str] = None):
        """Apply a property to all image layers in the same group.

        Only applies to safe-to-sync properties like position, size, and display options.
        """
        sync_props = {"x", "y", "width", "height", "fit_mode", "rotation", "flip_horizontal", "flip_vertical"}
        if property_name not in sync_props:
            return
        for layer in self.layers:
            if isinstance(layer, ImageLayer) and getattr(layer, "group_id", None) == group_id:
                if include_selected_id and layer.layer_id == include_selected_id:
                    continue
                if hasattr(layer, property_name):
                    setattr(layer, property_name, value)
                    # Trigger scaled image recompute if size/fit changed
                    try:
                        if property_name in ["width", "height", "fit_mode"] and hasattr(layer, "_update_scaled_image"):
                            layer._update_scaled_image()
                    except Exception:
                        pass
    
    def export_timeline_data(self) -> Dict[str, Any]:
        """Export timeline data for saving/loading"""
        return {
            "total_duration": self.total_duration,
            "fps": self.fps,
            "current_time": self.current_time,
            "image_transition": self.image_transition,
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
