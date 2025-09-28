"""
Asset loader for handling images, videos, and other media files
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox


class AssetLoader:
    """Handles loading and managing media assets"""
    
    def __init__(self):
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        self.assets_cache: Dict[str, Any] = {}
        self.thumbnails_cache: Dict[str, ImageTk.PhotoImage] = {}
        
    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from file"""
        try:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return None
                
            image = Image.open(image_path)
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Cache the image
            self.assets_cache[image_path] = image
            return image
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def load_multiple_images(self, image_paths: List[str]) -> List[Tuple[str, Image.Image]]:
        """Load multiple images"""
        loaded_images = []
        for path in image_paths:
            image = self.load_image(path)
            if image:
                loaded_images.append((path, image))
        return loaded_images
    
    def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (100, 100)) -> Optional[ImageTk.PhotoImage]:
        """Create thumbnail for image"""
        try:
            if image_path in self.thumbnails_cache:
                return self.thumbnails_cache[image_path]
                
            image = self.load_image(image_path)
            if not image:
                return None
                
            # Create thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(thumbnail)
            self.thumbnails_cache[image_path] = photo
            return photo
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")
            return None
    
    def get_image_info(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Get image information"""
        try:
            image = self.load_image(image_path)
            if not image:
                return None
                
            return {
                "path": image_path,
                "filename": os.path.basename(image_path),
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": os.path.getsize(image_path)
            }
        except Exception as e:
            print(f"Error getting image info for {image_path}: {e}")
            return None
    
    def select_image_files(self, parent_window=None) -> List[str]:
        """Open file dialog to select image files"""
        try:
            filetypes = [
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
            
            files = filedialog.askopenfilenames(
                parent=parent_window,
                title="Select Image Files",
                filetypes=filetypes
            )
            return list(files)
        except Exception as e:
            print(f"Error selecting image files: {e}")
            return []
    
    def select_video_file(self, parent_window=None) -> Optional[str]:
        """Open file dialog to select video file"""
        try:
            filetypes = [
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("All files", "*.*")
            ]
            
            file_path = filedialog.askopenfilename(
                parent=parent_window,
                title="Select Video File",
                filetypes=filetypes
            )
            return file_path if file_path else None
        except Exception as e:
            print(f"Error selecting video file: {e}")
            return None
    
    def create_slideshow_from_images(self, image_paths: List[str], duration_per_image: float = 2.0) -> List[Dict[str, Any]]:
        """Create slideshow data from image list"""
        slideshow_data = []
        current_time = 0.0
        
        for i, image_path in enumerate(image_paths):
            image_info = self.get_image_info(image_path)
            if not image_info:
                continue
                
            slide_data = {
                "image_path": image_path,
                "start_time": current_time,
                "end_time": current_time + duration_per_image,
                "duration": duration_per_image,
                "order": i,
                "width": image_info["width"],
                "height": image_info["height"]
            }
            slideshow_data.append(slide_data)
            current_time += duration_per_image
            
        return slideshow_data
    
    def validate_asset(self, asset_path: str) -> bool:
        """Validate if asset file is supported and accessible"""
        try:
            if not os.path.exists(asset_path):
                return False
                
            file_ext = os.path.splitext(asset_path)[1].lower()
            
            if file_ext in self.supported_image_formats:
                # Try to open as image
                with Image.open(asset_path) as img:
                    img.verify()
                return True
            elif file_ext in self.supported_video_formats:
                # For video files, just check if file exists and is readable
                return os.access(asset_path, os.R_OK)
            else:
                return False
        except Exception as e:
            print(f"Error validating asset {asset_path}: {e}")
            return False
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats"""
        return {
            "images": self.supported_image_formats,
            "videos": self.supported_video_formats
        }
    
    def clear_cache(self):
        """Clear asset and thumbnail cache"""
        self.assets_cache.clear()
        self.thumbnails_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            "cached_assets": len(self.assets_cache),
            "cached_thumbnails": len(self.thumbnails_cache),
            "total_memory_usage": "N/A"  # Could be calculated if needed
        }
    
    def export_asset_list(self, output_path: str) -> bool:
        """Export list of loaded assets to JSON file"""
        try:
            asset_list = []
            for path, image in self.assets_cache.items():
                asset_info = self.get_image_info(path)
                if asset_info:
                    asset_list.append(asset_info)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asset_list, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting asset list: {e}")
            return False
