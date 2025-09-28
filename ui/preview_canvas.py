"""
Preview canvas for video editor with drag & drop support
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List
from core.timeline_manager import TimelineManager
from models.base_layer import BaseLayer


class PreviewCanvas(tk.Canvas):
    """Preview canvas with drag & drop support"""
    
    def __init__(self, parent, timeline_manager: TimelineManager, on_layer_select: Optional[Callable] = None):
        # 9:16 aspect ratio for short video - exact same size as export
        self.canvas_width = 720   # Same as video export width
        self.canvas_height = 1280 # Same as video export height
        super().__init__(parent, bg="lightgray", width=self.canvas_width, height=self.canvas_height)
        
        self.timeline_manager = timeline_manager
        self.on_layer_select = on_layer_select
        self.current_time = 0.0
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        
        # Drag & drop state
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.dragging = False
        self.drag_layer = None
        
        # Selection state
        self.selected_layer = None
        self.selection_rect = None
        self.hover_layer = None
        
        self._setup_bindings()
        self._create_drag_drop_areas()
    
    def _setup_bindings(self):
        """Setup mouse and keyboard bindings"""
        # Mouse bindings
        self.bind("<Button-1>", self._on_mouse_click)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.bind("<Double-Button-1>", self._on_double_click)
        self.bind("<Motion>", self._on_mouse_motion)
        self.bind("<Leave>", self._on_mouse_leave)
        
        # Keyboard bindings
        self.bind("<KeyPress>", self._on_key_press)
        self.focus_set()  # Enable keyboard focus
        
        # Mouse wheel for zoom
        self.bind("<MouseWheel>", self._on_mouse_wheel)
        self.bind("<Button-4>", self._on_mouse_wheel)  # Linux
        self.bind("<Button-5>", self._on_mouse_wheel)  # Linux
    
    def _create_drag_drop_areas(self):
        """Create drag & drop areas for adding elements"""
        # Text drop area
        self.create_rectangle(50, 50, 150, 100, fill="lightblue", outline="darkblue", width=2, tags="text_drop")
        self.create_text(100, 75, text="CHỮ", fill="darkblue", font=("Arial", 12, "bold"), tags="text_drop")
        
        # Image drop area
        self.create_rectangle(200, 50, 300, 100, fill="lightgreen", outline="darkgreen", width=2, tags="image_drop")
        self.create_text(250, 75, text="ẢNH", fill="darkgreen", font=("Arial", 12, "bold"), tags="image_drop")
        
        # Box drop area
        self.create_rectangle(350, 50, 450, 100, fill="lightcoral", outline="darkred", width=2, tags="box_drop")
        self.create_text(400, 75, text="HỘP", fill="darkred", font=("Arial", 12, "bold"), tags="box_drop")
    
    def set_timeline_manager(self, timeline_manager: TimelineManager):
        """Set timeline manager"""
        self.timeline_manager = timeline_manager
        self.refresh()
    
    def resize_canvas(self, width: int, height: int):
        """Resize canvas while maintaining exact export resolution"""
        # Always use exact export resolution: 720x1280
        self.canvas_width = 720
        self.canvas_height = 1280
        
        # Update canvas size
        self.config(width=self.canvas_width, height=self.canvas_height)
        
        # Refresh to redraw everything
        self.refresh()
    
    def set_current_time(self, time: float):
        """Set current time and refresh display"""
        self.current_time = time
        self.refresh()
    
    def refresh(self):
        """Refresh the canvas display"""
        self.delete("layer", "selection", "hover")
        self._render_layers()
        self._update_drag_drop_areas()
        self._update_hover_effects()
    
    def _render_layers(self):
        """Render all visible layers"""
        if not self.timeline_manager:
            return
        
        visible_layers = self.timeline_manager.get_layers_at_time(self.current_time)

        # If crossfade is enabled, render overlap of previous/next images
        transition = getattr(self.timeline_manager, 'image_transition', {"type": "none", "duration": 0.0})
        trans_type = transition.get("type", "none")
        trans_dur = float(transition.get("duration", 0.0) or 0.0)

        if trans_type in ("crossfade", "fadeblack", "wipeleft", "wiperight", "zoomin", "zoomout", "rotate", "flip") and trans_dur > 0:
            # Collect image layers sorted by time
            all_layers = sorted(self.timeline_manager.get_all_layers(), key=lambda l: getattr(l, 'start_time', 0.0))
            # Find adjacent image layers around current time
            prev_img = None
            next_img = None
            current_img = None
            for i, l in enumerate(all_layers):
                if hasattr(l, 'image_path'):
                    if getattr(l, 'start_time', 0.0) <= self.current_time <= getattr(l, 'end_time', 0.0):
                        # l is current image
                        current_img = l
                        # Find prev
                        for j in range(i - 1, -1, -1):
                            if hasattr(all_layers[j], 'image_path'):
                                prev_img = all_layers[j]
                                break
                        # Find next
                        for j in range(i + 1, len(all_layers)):
                            if hasattr(all_layers[j], 'image_path'):
                                next_img = all_layers[j]
                                break
                        break

            # Determine if we are in overlap window at end of current image
            # Fade out current and fade in next during [end - trans_dur, end]
            did_crossfade = False
            
            # If there is a current image and we are within crossfade window at its end
            if current_img and hasattr(current_img, 'image_path'):
                fade_out_start = getattr(current_img, 'end_time', 0.0) - trans_dur
                if fade_out_start <= self.current_time <= getattr(current_img, 'end_time', 0.0) and next_img:
                    # Compute opacities
                    t = (self.current_time - fade_out_start) / trans_dur
                    t = max(0.0, min(1.0, t))
                    # current image opacity to end
                    cur_opacity = 1.0 - t
                    # next image opacity from start
                    next_opacity = t
                    # Draw next image underneath first to avoid covering selection lines
                    if hasattr(next_img, 'render_preview_with_opacity'):
                        next_img.render_preview_with_opacity(self, next_opacity)
                    # Draw current on top with reduced opacity
                    if hasattr(current_img, 'render_preview_with_opacity'):
                        current_img.render_preview_with_opacity(self, cur_opacity)
                    did_crossfade = True

            if did_crossfade:
                return
        
        # Default path
        for layer in visible_layers:
            self._render_layer(layer)
        
        # Draw selection if layer is selected
        if self.selected_layer:
            self._draw_selection(self.selected_layer)
    
    def _render_layer(self, layer: BaseLayer):
        """Render a single layer"""
        try:
            # Store original position and size for transition effects
            if hasattr(layer, 'group_id') and hasattr(layer, 'fit_mode'):  # ImageLayer
                if not hasattr(layer, '_original_x'):
                    layer._original_x = layer.x
                if not hasattr(layer, '_original_y'):
                    layer._original_y = layer.y
                if not hasattr(layer, '_original_width'):
                    layer._original_width = layer.width
                if not hasattr(layer, '_original_height'):
                    layer._original_height = layer.height
                
                # Apply transition effects for image layers in preview
                self._apply_image_transition_effects(layer)
            
            # Apply zoom and pan transformations
            x = int((layer.x + self.pan_x) * self.zoom_level)
            y = int((layer.y + self.pan_y) * self.zoom_level)
            width = int(layer.width * self.zoom_level)
            height = int(layer.height * self.zoom_level)
            
            # Get current item count before rendering
            items_before = len(self.find_all())
            
            # Render layer based on type
            layer.render_preview(self, self.current_time)
            
            # Get items created during rendering and add tags
            items_after = self.find_all()
            new_items = items_after[items_before:]
            
            for item in new_items:
                self.addtag_withtag("layer", item)
                self.addtag_withtag(f"layer_{layer.layer_id}", item)
            
        except Exception as e:
            print(f"Error rendering layer {layer.layer_id}: {e}")
            import traceback
            traceback.print_exc()
    
    def _apply_image_transition_effects(self, layer):
        """Apply transition effects to image layer in preview"""
        if not self.timeline_manager:
            return
            
        transition = getattr(self.timeline_manager, 'image_transition', {"type": "none", "duration": 0.0})
        trans_type = transition.get("type", "none")
        trans_dur = float(transition.get("duration", 0.0) or 0.0)
        
        if trans_type == "crossfade" and trans_dur > 0:
            # Calculate fade opacity based on current time
            fade_in_end = layer.start_time + trans_dur
            fade_out_start = layer.end_time - trans_dur
            
            if self.current_time < layer.start_time:
                # Before layer starts
                layer.opacity = 0.0
            elif self.current_time <= fade_in_end:
                # Fade in phase
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = min(1.0, max(0.0, progress))
            elif self.current_time <= fade_out_start:
                # Full visibility phase
                layer.opacity = 1.0
            elif self.current_time <= layer.end_time:
                # Fade out phase
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = min(1.0, max(0.0, progress))
            else:
                # After layer ends
                layer.opacity = 0.0
        elif trans_type == "fadeblack" and trans_dur > 0:
            # Fade to black - different from crossfade
            fade_in_end = layer.start_time + trans_dur
            fade_out_start = layer.end_time - trans_dur
            
            if self.current_time < layer.start_time:
                layer.opacity = 0.0
            elif self.current_time <= fade_in_end:
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = min(1.0, max(0.0, progress))
            elif self.current_time <= fade_out_start:
                layer.opacity = 1.0
            elif self.current_time <= layer.end_time:
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = min(1.0, max(0.0, progress))
            else:
                layer.opacity = 0.0
        elif trans_type == "wipeleft" and trans_dur > 0:
            # Wipe left - slide from right to left
            if self.current_time < layer.start_time:
                layer.opacity = 0.0
                # Move layer off-screen to the right
                layer.x = layer.width
            elif self.current_time <= layer.start_time + trans_dur:
                # Wipe in from right to left
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = 1.0
                # Slide from right to final position
                original_x = getattr(layer, '_original_x', layer.x)
                layer.x = original_x + (1.0 - progress) * layer.width
            elif self.current_time <= layer.end_time - trans_dur:
                layer.opacity = 1.0
                # Restore original position
                if hasattr(layer, '_original_x'):
                    layer.x = layer._original_x
            elif self.current_time <= layer.end_time:
                # Wipe out from left to right
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = 1.0
                # Slide from current position to left
                original_x = getattr(layer, '_original_x', layer.x)
                layer.x = original_x - (1.0 - progress) * layer.width
            else:
                layer.opacity = 0.0
                layer.x = -layer.width
        elif trans_type == "wiperight" and trans_dur > 0:
            # Wipe right - slide from left to right
            if self.current_time < layer.start_time:
                layer.opacity = 0.0
                # Move layer off-screen to the left
                layer.x = -layer.width
            elif self.current_time <= layer.start_time + trans_dur:
                # Wipe in from left to right
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = 1.0
                # Slide from left to final position
                original_x = getattr(layer, '_original_x', layer.x)
                layer.x = original_x - (1.0 - progress) * layer.width
            elif self.current_time <= layer.end_time - trans_dur:
                layer.opacity = 1.0
                # Restore original position
                if hasattr(layer, '_original_x'):
                    layer.x = layer._original_x
            elif self.current_time <= layer.end_time:
                # Wipe out from right to left
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = 1.0
                # Slide from current position to right
                original_x = getattr(layer, '_original_x', layer.x)
                layer.x = original_x + (1.0 - progress) * layer.width
            else:
                layer.opacity = 0.0
                layer.x = layer.width
        elif trans_type == "zoomin" and trans_dur > 0:
            # Zoom in - start small, grow to normal
            if self.current_time < layer.start_time:
                layer.opacity = 0.0
                # Start very small
                layer.width = 1.0
                layer.height = 1.0
            elif self.current_time <= layer.start_time + trans_dur:
                # Zoom in from small to normal
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = 1.0
                # Scale from small to normal
                original_width = getattr(layer, '_original_width', layer.width)
                original_height = getattr(layer, '_original_height', layer.height)
                layer.width = 1.0 + (original_width - 1.0) * progress
                layer.height = 1.0 + (original_height - 1.0) * progress
            elif self.current_time <= layer.end_time - trans_dur:
                layer.opacity = 1.0
                # Restore original size
                if hasattr(layer, '_original_width'):
                    layer.width = layer._original_width
                if hasattr(layer, '_original_height'):
                    layer.height = layer._original_height
            elif self.current_time <= layer.end_time:
                # Zoom out from normal to small
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = 1.0
                # Scale from normal to small
                original_width = getattr(layer, '_original_width', layer.width)
                original_height = getattr(layer, '_original_height', layer.height)
                layer.width = 1.0 + (original_width - 1.0) * progress
                layer.height = 1.0 + (original_height - 1.0) * progress
            else:
                layer.opacity = 0.0
                layer.width = 1.0
                layer.height = 1.0
        elif trans_type == "zoomout" and trans_dur > 0:
            # Zoom out - start normal, shrink to small
            if self.current_time < layer.start_time:
                layer.opacity = 0.0
                # Start very small
                layer.width = 1.0
                layer.height = 1.0
            elif self.current_time <= layer.start_time + trans_dur:
                # Zoom out from normal to small
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = 1.0
                # Scale from normal to small
                original_width = getattr(layer, '_original_width', layer.width)
                original_height = getattr(layer, '_original_height', layer.height)
                layer.width = original_width - (original_width - 1.0) * progress
                layer.height = original_height - (original_height - 1.0) * progress
            elif self.current_time <= layer.end_time - trans_dur:
                layer.opacity = 1.0
                # Restore original size
                if hasattr(layer, '_original_width'):
                    layer.width = layer._original_width
                if hasattr(layer, '_original_height'):
                    layer.height = layer._original_height
            elif self.current_time <= layer.end_time:
                # Zoom in from small to normal
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = 1.0
                # Scale from small to normal
                original_width = getattr(layer, '_original_width', layer.width)
                original_height = getattr(layer, '_original_height', layer.height)
                layer.width = original_width - (original_width - 1.0) * progress
                layer.height = original_height - (original_height - 1.0) * progress
            else:
                layer.opacity = 0.0
                layer.width = 1.0
                layer.height = 1.0
        elif trans_type == "rotate" and trans_dur > 0:
            # Rotate - spin effect
            if self.current_time < layer.start_time:
                layer.opacity = 0.0
                layer.rotation = 0.0
            elif self.current_time <= layer.start_time + trans_dur:
                # Rotate in with spin
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = 1.0
                # Rotate from 0 to 360 degrees
                layer.rotation = 360.0 * progress
            elif self.current_time <= layer.end_time - trans_dur:
                layer.opacity = 1.0
                layer.rotation = 0.0
            elif self.current_time <= layer.end_time:
                # Rotate out with spin
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = 1.0
                # Rotate from 0 to 360 degrees
                layer.rotation = 360.0 * progress
            else:
                layer.opacity = 0.0
                layer.rotation = 0.0
        elif trans_type == "flip" and trans_dur > 0:
            # Flip - horizontal flip effect
            if self.current_time < layer.start_time:
                layer.opacity = 0.0
                layer.flip_horizontal = False
            elif self.current_time <= layer.start_time + trans_dur:
                # Flip in with horizontal flip
                progress = (self.current_time - layer.start_time) / trans_dur
                layer.opacity = 1.0
                # Toggle flip during transition
                layer.flip_horizontal = (int(progress * 10) % 2) == 1
            elif self.current_time <= layer.end_time - trans_dur:
                layer.opacity = 1.0
                layer.flip_horizontal = False
            elif self.current_time <= layer.end_time:
                # Flip out with horizontal flip
                progress = (layer.end_time - self.current_time) / trans_dur
                layer.opacity = 1.0
                # Toggle flip during transition
                layer.flip_horizontal = (int(progress * 10) % 2) == 1
            else:
                layer.opacity = 0.0
                layer.flip_horizontal = False
        else:
            # No transition, use normal opacity
            layer.opacity = 1.0 if layer.visible else 0.0
    
    def _draw_selection(self, layer: BaseLayer):
        """Draw selection rectangle around layer with dashed border"""
        x = int((layer.x + self.pan_x) * self.zoom_level)
        y = int((layer.y + self.pan_y) * self.zoom_level)
        width = int(layer.width * self.zoom_level)
        height = int(layer.height * self.zoom_level)
        
        # Draw dashed selection rectangle
        self.create_rectangle(
            x - 3, y - 3, x + width + 3, y + height + 3,
            outline="blue", width=2, dash=(5, 5), tags="selection"
        )
        
        # Draw inner dashed rectangle for better visibility
        self.create_rectangle(
            x - 1, y - 1, x + width + 1, y + height + 1,
            outline="blue", width=1, dash=(3, 3), tags="selection"
        )
        
        # Draw resize handles
        handle_size = 8
        handles = [
            (x - handle_size//2, y - handle_size//2),  # Top-left
            (x + width//2 - handle_size//2, y - handle_size//2),  # Top-center
            (x + width - handle_size//2, y - handle_size//2),  # Top-right
            (x + width - handle_size//2, y + height//2 - handle_size//2),  # Right-center
            (x + width - handle_size//2, y + height - handle_size//2),  # Bottom-right
            (x + width//2 - handle_size//2, y + height - handle_size//2),  # Bottom-center
            (x - handle_size//2, y + height - handle_size//2),  # Bottom-left
            (x - handle_size//2, y + height//2 - handle_size//2),  # Left-center
        ]
        
        for handle_x, handle_y in handles:
            self.create_rectangle(
                handle_x, handle_y, handle_x + handle_size, handle_y + handle_size,
                fill="blue", outline="white", width=2, tags="selection"
            )
    
    def _update_drag_drop_areas(self):
        """Update drag & drop areas visibility"""
        # Hide drop areas when there are layers
        if self.timeline_manager and len(self.timeline_manager.get_all_layers()) > 0:
            self.itemconfig("text_drop", state="hidden")
            self.itemconfig("image_drop", state="hidden")
            self.itemconfig("box_drop", state="hidden")
        else:
            self.itemconfig("text_drop", state="normal")
            self.itemconfig("image_drop", state="normal")
            self.itemconfig("box_drop", state="normal")
    
    def _on_mouse_click(self, event):
        """Handle mouse click"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        # Check if clicking on a layer
        clicked_items = self.find_closest(event.x, event.y)
        if clicked_items:
            item = clicked_items[0]
            tags = self.gettags(item)
            
            # Check if clicking on a layer
            for tag in tags:
                if tag.startswith("layer_"):
                    layer_id = tag.replace("layer_", "")
                    layer = self.timeline_manager.get_layer(layer_id)
                    if layer:
                        self._select_layer(layer)
                        # Enable dragging for all layer types
                        self.dragging = True
                        self.drag_layer = layer
                        return
            
            # Check if clicking on drop areas
            if "text_drop" in tags:
                self._create_text_layer_at_position(event.x, event.y)
            elif "image_drop" in tags:
                self._create_image_layer_at_position(event.x, event.y)
            elif "box_drop" in tags:
                self._create_box_layer_at_position(event.x, event.y)
        
        # Clear selection if clicking on empty area
        if not clicked_items or not any(tag.startswith("layer_") for tag in self.gettags(clicked_items[0])):
            self._clear_selection()
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.dragging and self.drag_layer:
            # Calculate drag delta
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            # Update layer position
            new_x = self.drag_layer.x + dx / self.zoom_level
            new_y = self.drag_layer.y + dy / self.zoom_level
            
            # Keep layer within canvas bounds
            new_x = max(0, min(new_x, self.canvas_width - self.drag_layer.width))
            new_y = max(0, min(new_y, self.canvas_height - self.drag_layer.height))
            
            self.drag_layer.set_position(new_x, new_y)
            
            # Update drag start position for next delta
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            # Refresh display
            self.refresh()
    
    def _on_mouse_release(self, event):
        """Handle mouse release"""
        self.dragging = False
        self.drag_layer = None
    
    def _on_double_click(self, event):
        """Handle double click"""
        # Find clicked layer
        clicked_items = self.find_closest(event.x, event.y)
        if clicked_items:
            item = clicked_items[0]
            tags = self.gettags(item)
            
            for tag in tags:
                if tag.startswith("layer_"):
                    layer_id = tag.replace("layer_", "")
                    layer = self.timeline_manager.get_layer(layer_id)
                    if layer:
                        self._select_layer(layer)
                        # Could open layer properties dialog here
                        return
    
    def _on_key_press(self, event):
        """Handle key press"""
        if self.selected_layer:
            if event.keysym == "Delete":
                self._delete_selected_layer()
            elif event.keysym == "Up":
                self._move_selected_layer(0, -5)
            elif event.keysym == "Down":
                self._move_selected_layer(0, 5)
            elif event.keysym == "Left":
                self._move_selected_layer(-5, 0)
            elif event.keysym == "Right":
                self._move_selected_layer(5, 0)
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel for zoom"""
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def _on_mouse_motion(self, event):
        """Handle mouse motion for hover effects"""
        # Find layer under mouse
        clicked_items = self.find_closest(event.x, event.y)
        current_hover_layer = None
        
        if clicked_items:
            item = clicked_items[0]
            tags = self.gettags(item)
            
            # Check if hovering over a layer
            for tag in tags:
                if tag.startswith("layer_"):
                    layer_id = tag.replace("layer_", "")
                    layer = self.timeline_manager.get_layer(layer_id)
                    if layer:
                        current_hover_layer = layer
                        break
        
        # Update hover state
        if current_hover_layer != self.hover_layer:
            self.hover_layer = current_hover_layer
            self._update_hover_effects()
    
    def _on_mouse_leave(self, event):
        """Handle mouse leaving canvas"""
        if self.hover_layer:
            self.hover_layer = None
            self._update_hover_effects()
    
    def _update_hover_effects(self):
        """Update hover effects for layers"""
        # Remove old hover effects
        self.delete("hover")
        
        # Add hover effect for current hover layer
        if self.hover_layer and self.hover_layer != self.selected_layer:
            self._draw_hover_effect(self.hover_layer)
    
    def _draw_hover_effect(self, layer: BaseLayer):
        """Draw hover effect for layer"""
        x = int((layer.x + self.pan_x) * self.zoom_level)
        y = int((layer.y + self.pan_y) * self.zoom_level)
        width = int(layer.width * self.zoom_level)
        height = int(layer.height * self.zoom_level)
        
        # Draw subtle hover rectangle
        self.create_rectangle(
            x - 2, y - 2, x + width + 2, y + height + 2,
            outline="orange", width=1, dash=(2, 2), tags="hover"
        )
    
    def _select_layer(self, layer: BaseLayer):
        """Select a layer"""
        self.selected_layer = layer
        self.timeline_manager.select_layer(layer.layer_id)
        
        if self.on_layer_select:
            self.on_layer_select(layer)
        
        self.refresh()
    
    def _clear_selection(self):
        """Clear layer selection"""
        self.selected_layer = None
        self.timeline_manager.clear_selection()
        
        if self.on_layer_select:
            self.on_layer_select(None)
        
        self.refresh()
    
    def _delete_selected_layer(self):
        """Delete selected layer"""
        if self.selected_layer:
            self.timeline_manager.remove_layer(self.selected_layer.layer_id)
            self._clear_selection()
            self.refresh()
    
    def _move_selected_layer(self, dx: int, dy: int):
        """Move selected layer"""
        if self.selected_layer:
            new_x = self.selected_layer.x + dx / self.zoom_level
            new_y = self.selected_layer.y + dy / self.zoom_level
            self.selected_layer.set_position(new_x, new_y)
            self.refresh()
    
    def _create_text_layer_at_position(self, x: int, y: int):
        """Create text layer at position"""
        # Convert canvas coordinates to layer coordinates
        layer_x = (x - self.pan_x) / self.zoom_level
        layer_y = (y - self.pan_y) / self.zoom_level
        
        layer = self.timeline_manager.create_text_layer("New Text")
        layer.set_position(layer_x, layer_y)
        self._select_layer(layer)
        self.refresh()
    
    def _create_image_layer_at_position(self, x: int, y: int):
        """Create image layer at position"""
        # Default desired placement, ignore click position
        default_x = 0.0
        default_y = 120.0
        
        # Open file dialog to select image first
        from tkinter import filedialog
        image_paths = filedialog.askopenfilenames(
            title="Chọn tệp ảnh",
            filetypes=[("Tệp ảnh", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"), ("Tất cả tệp", "*.*")]
        )
        
        if image_paths:
            # Create sequential layers with shared position
            created = self.timeline_manager.add_sequential_images(
                list(image_paths), duration_per_image=3.0, x=default_x, y=default_y
            )
            if created:
                created[0].load_image(created[0].image_path)
                self._select_layer(created[0])
            # Update time slider in main window if accessible via callback
            self.refresh()
        else:
            print("Không có ảnh nào được chọn")
    
    def _create_box_layer_at_position(self, x: int, y: int):
        """Create box layer at position"""
        # Convert canvas coordinates to layer coordinates
        layer_x = (x - self.pan_x) / self.zoom_level
        layer_y = (y - self.pan_y) / self.zoom_level
        
        layer = self.timeline_manager.create_box_layer()
        layer.set_position(layer_x, layer_y)
        self._select_layer(layer)
        self.refresh()
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        self.refresh()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.1)
        self.refresh()
    
    def reset_zoom(self):
        """Reset zoom level"""
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.refresh()
