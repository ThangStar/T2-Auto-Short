"""
Image layer model for video editor
"""
from typing import Dict, Any, Optional
import tkinter as tk
from PIL import Image, ImageTk
import os
from .base_layer import BaseLayer


class ImageLayer(BaseLayer):
    """Image layer for displaying images in video"""
    
    def __init__(self, layer_id: str, image_path: str = "", start_time: float = 0.0, end_time: float = 5.0):
        super().__init__(layer_id, start_time, end_time)
        self.image_path = image_path
        self.original_image = None
        self.scaled_image = None
        self.photo_image = None  # Keep reference to PhotoImage
        self.aspect_ratio = 1.0
        self.fit_mode = "cover"  # stretch, fit, fill, cover, original
        self.rotation = 0.0
        self.flip_horizontal = False
        self.flip_vertical = False
        self.brightness = 1.0
        self.contrast = 1.0
        self.saturation = 1.0
        
        if image_path and os.path.exists(image_path):
            self.load_image(image_path)
    
    def load_image(self, image_path: str) -> bool:
        """Load image from file"""
        try:
            self.image_path = image_path
            self.original_image = Image.open(image_path)
            self.aspect_ratio = self.original_image.width / self.original_image.height
            self._update_scaled_image()
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def _update_scaled_image(self):
        """Update scaled image based on current size and fit mode"""
        if not self.original_image:
            return
            
        if self.fit_mode == "original":
            self.scaled_image = self.original_image
        elif self.fit_mode == "stretch":
            self.scaled_image = self.original_image.resize((int(self.width), int(self.height)), Image.Resampling.LANCZOS)
        elif self.fit_mode == "fit":
            # Fit image within bounds while maintaining aspect ratio
            scale_w = self.width / self.original_image.width
            scale_h = self.height / self.original_image.height
            scale = min(scale_w, scale_h)
            new_w = int(self.original_image.width * scale)
            new_h = int(self.original_image.height * scale)
            self.scaled_image = self.original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        elif self.fit_mode == "fill":
            # Fill bounds while maintaining aspect ratio (may crop)
            scale_w = self.width / self.original_image.width
            scale_h = self.height / self.original_image.height
            scale = max(scale_w, scale_h)
            new_w = int(self.original_image.width * scale)
            new_h = int(self.original_image.height * scale)
            self.scaled_image = self.original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        elif self.fit_mode == "cover":
            # Cover bounds while maintaining aspect ratio (crop to fill)
            scale_w = self.width / self.original_image.width
            scale_h = self.height / self.original_image.height
            scale = max(scale_w, scale_h)
            new_w = int(self.original_image.width * scale)
            new_h = int(self.original_image.height * scale)
            
            # Resize first
            resized = self.original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Then crop to exact size
            left = (new_w - self.width) // 2
            top = (new_h - self.height) // 2
            right = left + self.width
            bottom = top + self.height
            
            self.scaled_image = resized.crop((left, top, right, bottom))
    
    def get_properties(self) -> Dict[str, Any]:
        """Get all image properties"""
        return {
            "image_path": self.image_path,
            "fit_mode": self.fit_mode,
            "rotation": self.rotation,
            "flip_horizontal": self.flip_horizontal,
            "flip_vertical": self.flip_vertical,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "saturation": self.saturation,
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
        """Set an image property"""
        if hasattr(self, property_name):
            setattr(self, property_name, value)
            if property_name in ["width", "height", "fit_mode"]:
                self._update_scaled_image()
            return True
        return False
    
    def render_preview(self, canvas: tk.Canvas, current_time: float) -> None:
        """Render image on preview canvas"""
        if not self.is_visible_at_time(current_time):
            return
        
        try:
            # Load image if not already loaded
            if not self.original_image and self.image_path and os.path.exists(self.image_path):
                print(f"Loading image: {self.image_path}")
                self.load_image(self.image_path)
            
            if not self.original_image:
                # Draw placeholder rectangle if no image
                print(f"Drawing placeholder for layer {self.layer_id} at ({self.x}, {self.y})")
                canvas.create_rectangle(
                    self.x, self.y, self.x + self.width, self.y + self.height,
                    fill="white", outline="gray", width=2, dash=(3, 3)
                )
                canvas.create_text(
                    self.x + self.width // 2, self.y + self.height // 2,
                    text="No Image", fill="gray", anchor="center", font=("Arial", 10)
                )
                return
            
            # Update scaled image if needed
            if not self.scaled_image:
                print(f"Updating scaled image for layer {self.layer_id}")
                self._update_scaled_image()
            
            if not self.scaled_image:
                print(f"No scaled image for layer {self.layer_id}")
                return
            
            # Apply transformations
            img = self.scaled_image.copy()
            
            # Apply rotation
            if self.rotation != 0:
                img = img.rotate(self.rotation, expand=True)
            
            # Apply flips
            if self.flip_horizontal:
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flip_vertical:
                img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            
            # Apply opacity if needed
            if self.opacity < 1.0:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                alpha = int(max(0.0, min(1.0, self.opacity)) * 255)
                r, g, b, *rest = img.split() if img.mode == "RGBA" else (*img.split(),)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                a = Image.new("L", img.size, color=alpha)
                img.putalpha(a)
            
            # Convert to PhotoImage and keep reference
            self.photo_image = ImageTk.PhotoImage(img)
            
            # Calculate position for display
            if self.fit_mode in ["fit", "fill"]:
                # Center the image (scaled image is smaller than bounds)
                img_w, img_h = self.photo_image.width(), self.photo_image.height()
                x = self.x + (self.width - img_w) // 2
                y = self.y + (self.height - img_h) // 2
                print(f"Rendering image at centered position ({x}, {y})")
                image_item = canvas.create_image(x, y, image=self.photo_image, anchor="nw")
            elif self.fit_mode == "cover":
                # Cover mode: image fills exact bounds (already cropped)
                print(f"Rendering cover image at position ({self.x}, {self.y})")
                image_item = canvas.create_image(self.x, self.y, image=self.photo_image, anchor="nw")
            else:
                # stretch, original: use exact position
                print(f"Rendering image at position ({self.x}, {self.y})")
                image_item = canvas.create_image(self.x, self.y, image=self.photo_image, anchor="nw")
                
        except Exception as e:
            print(f"Error rendering image: {e}")
            import traceback
            traceback.print_exc()
    
    def render_preview_with_opacity(self, canvas: tk.Canvas, opacity: float) -> None:
        """Render image ignoring visibility window with a specific opacity (0..1)."""
        try:
            # Load image if not already loaded
            if not self.original_image and self.image_path and os.path.exists(self.image_path):
                self.load_image(self.image_path)
            if not self.original_image:
                return
            if not self.scaled_image:
                self._update_scaled_image()
            if not self.scaled_image:
                return
            img = self.scaled_image.copy()
            if self.rotation != 0:
                img = img.rotate(self.rotation, expand=True)
            if self.flip_horizontal:
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flip_vertical:
                img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            # Apply custom opacity
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            alpha = int(max(0.0, min(1.0, opacity)) * 255)
            a = Image.new("L", img.size, color=alpha)
            img.putalpha(a)
            self.photo_image = ImageTk.PhotoImage(img)
            if self.fit_mode in ["fit", "fill"]:
                img_w, img_h = self.photo_image.width(), self.photo_image.height()
                x = self.x + (self.width - img_w) // 2
                y = self.y + (self.height - img_h) // 2
                canvas.create_image(x, y, image=self.photo_image, anchor="nw")
            elif self.fit_mode == "cover":
                canvas.create_image(self.x, self.y, image=self.photo_image, anchor="nw")
            else:
                canvas.create_image(self.x, self.y, image=self.photo_image, anchor="nw")
        except Exception as e:
            print(f"Error rendering image with custom opacity: {e}")
            import traceback
            traceback.print_exc()

    def export_data(self) -> Dict[str, Any]:
        """Export image layer data for video rendering"""
        return {
            "type": "image",
            "layer_id": self.layer_id,
            "image_path": self.image_path,
            "fit_mode": self.fit_mode,
            "rotation": self.rotation,
            "flip_horizontal": self.flip_horizontal,
            "flip_vertical": self.flip_vertical,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "saturation": self.saturation,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "opacity": self.opacity,
            "visible": self.visible
        }
