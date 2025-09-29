"""
Configuration settings for Video Editor
"""
import os

# Application settings
APP_NAME = "Video Editor"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Video Editor Team"

# Default video settings
DEFAULT_VIDEO_WIDTH = 1280
DEFAULT_VIDEO_HEIGHT = 720
DEFAULT_FPS = 30
DEFAULT_DURATION = 10.0

# Preview settings
PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 360
PREVIEW_BG_COLOR = "#000000"

# Timeline settings
TIMELINE_HEIGHT = 200
TIMELINE_LAYER_HEIGHT = 30

# Export settings
EXPORT_QUALITY_OPTIONS = {
    "high": {"crf": 18, "preset": "slow"},
    "medium": {"crf": 23, "preset": "medium"},
    "low": {"crf": 28, "preset": "fast"}
}

# Supported file formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']

# UI settings
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 800

# Property panel settings
PROPERTY_PANEL_WIDTH = 300
PROPERTY_ENTRY_WIDTH = 20

# Color settings
DEFAULT_COLORS = {
    "text": "#FFFFFF",
    "background": "#000000",
    "border": "#000000",
    "selection": "#FFFF00"
}

# Font settings
DEFAULT_FONT_FAMILY = "Arial"
DEFAULT_FONT_SIZE = 24
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 72

# Layer settings
DEFAULT_LAYER_WIDTH = 720
DEFAULT_LAYER_HEIGHT = 150
MIN_LAYER_SIZE = 10
MAX_LAYER_SIZE = 2000

# Animation settings
PREVIEW_FPS = 10  # FPS for preview playback
ZOOM_FACTOR = 1.2
MIN_ZOOM = 0.1
MAX_ZOOM = 5.0

# File paths
TEMP_DIR = "temp"
EXPORT_DIR = "exports"
PROJECT_DIR = "projects"

# Create directories if they don't exist
for directory in [TEMP_DIR, EXPORT_DIR, PROJECT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Debug settings
DEBUG_MODE = False
VERBOSE_LOGGING = False
CANVAS_PREVIEW_SCALE = 1


# Performance settings
MAX_CACHE_SIZE = 100  # Maximum number of cached assets
PREVIEW_UPDATE_INTERVAL = 100  # Milliseconds between preview updates
RENDER_CHUNK_SIZE = 100  # Number of frames to process at once

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    "new_project": "<Control-n>",
    "open_project": "<Control-o>",
    "save_project": "<Control-s>",
    "export_video": "<Control-e>",
    "delete_layer": "<Delete>",
    "play_pause": "<space>",
    "zoom_in": "<Control-plus>",
    "zoom_out": "<Control-minus>",
    "reset_zoom": "<Control-0>"
}
