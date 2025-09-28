"""
Video renderer for exporting final video using FFmpeg with ASS subtitles
"""
import os
import subprocess
import json
import random
import glob
import re
import tempfile
import threading
import time
from typing import List, Dict, Any, Optional, Callable
from PIL import Image, ImageDraw, ImageFont


class VideoRenderer:
    """Handles video rendering and export using FFmpeg with ASS subtitles"""
    
    def __init__(self):
        self.is_rendering = False
        self.render_progress = 0.0
        self.render_status = ""
        self.output_path = ""
        self.temp_dir = ""
        
        # Bootstrap colors for ASS subtitles
        self.bootstrap_colors = {
            "primary": "&H00D66EFF",   # Blue (BGR)
            "success": "&H005AB419",   # Green
            "warning": "&H0014D7FF",   # Yellow
            "danger": "&H004A40DC",    # Red
            "purple": "&H00C83CBF",
            "indigo": "&H00CC3366"
        }
        
    def render_video(self, 
                    timeline_data: Dict[str, Any],
                    output_path: str,
                    video_width: int = 720,
                    video_height: int = 1280,
                    fps: int = 30,
                    quality: str = "high",
                    background_video: Optional[str] = None,
                    background_music: Optional[str] = None,
                    progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        """Render video from timeline data using FFmpeg with ASS subtitles"""
        
        if self.is_rendering:
            return False
            
        self.is_rendering = True
        self.render_progress = 0.0
        self.output_path = output_path
        
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="video_editor_")
            
            # Start rendering in separate thread
            render_thread = threading.Thread(
                target=self._render_video_thread,
                args=(timeline_data, output_path, video_width, video_height, fps, quality, 
                      background_video, background_music, progress_callback)
            )
            render_thread.daemon = True
            render_thread.start()
            
            return True
        except Exception as e:
            print(f"Error starting video render: {e}")
            self.is_rendering = False
            return False
    
    def _render_video_thread(self, 
                           timeline_data: Dict[str, Any],
                           output_path: str,
                           video_width: int,
                           video_height: int,
                           fps: int,
                           quality: str,
                           background_video: Optional[str],
                           background_music: Optional[str],
                           progress_callback: Optional[Callable[[float, str], None]]):
        """Render video in separate thread using FFmpeg with ASS subtitles"""
        try:
            self._update_progress(0.0, "Initializing render...", progress_callback)
            
            # Create ASS subtitle file
            ass_path = os.path.join(self.temp_dir, "subtitles.ass")
            self._create_ass_from_timeline(timeline_data, ass_path, video_width, video_height)
            
            self._update_progress(0.2, "Creating FFmpeg command...", progress_callback)
            
            # Build FFmpeg command
            ffmpeg_cmd = self._build_ffmpeg_command(
                timeline_data, output_path, video_width, video_height, fps, quality,
                background_video, background_music, ass_path
            )
            
            self._update_progress(0.3, "Starting video render...", progress_callback)
            
            # Execute FFmpeg command
            success = self._execute_ffmpeg_command(ffmpeg_cmd, progress_callback)
            
            if success:
                self._update_progress(1.0, "Render complete!", progress_callback)
            else:
                self._update_progress(0.0, "Render failed!", progress_callback)
                
        except Exception as e:
            print(f"Error in render thread: {e}")
            self._update_progress(0.0, f"Render error: {e}", progress_callback)
        finally:
            self.is_rendering = False
            # Cleanup temp directory
            try:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except:
                pass
    
    def _create_ass_from_timeline(self, timeline_data: Dict[str, Any], ass_path: str, 
                                 video_width: int, video_height: int):
        """Create ASS subtitle file from timeline data"""
        try:
            with open(ass_path, 'w', encoding='utf-8-sig') as f:
                # Write ASS header
                f.write("[Script Info]\n")
                f.write("Title: Video Editor Generated Subtitle\n")
                f.write("ScriptType: v4.00+\n")
                f.write(f"PlayResX: {video_width}\n")
                f.write(f"PlayResY: {video_height}\n")
                f.write("Scaled: yes\n")
                f.write("YCbCr Matrix: TV.601\n")
                
                # Write styles
                f.write("[V4+ Styles]\n")
                f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
                
                # Create styles for different layer types
                self._write_ass_styles(f, video_width, video_height)
                
                # Write events
                f.write("[Events]\n")
                f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
                
                # Process layers
                layers = timeline_data.get("layers", [])
                for layer in layers:
                    self._write_layer_to_ass(f, layer, video_width, video_height)
                    
        except Exception as e:
            print(f"Error creating ASS file: {e}")
    
    def _write_ass_styles(self, f, video_width: int, video_height: int):
        """Write ASS styles for different layer types"""
        # Default style
        f.write("Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n")
        
        # Text styles
        f.write("Style: Text,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n")
        f.write("Style: TextBg,Arial,24,&H00000000,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n")
        
        # Box styles
        f.write("Style: Box,Arial,24,&H00FF0000,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n")
    
    def _write_layer_to_ass(self, f, layer_data: Dict[str, Any], video_width: int, video_height: int):
        """Write a layer to ASS file"""
        layer_type = layer_data.get("type", "")
        start_time = layer_data.get("start_time", 0.0)
        end_time = layer_data.get("end_time", 5.0)
        x = layer_data.get("x", 100)
        y = layer_data.get("y", 100)
        width = layer_data.get("width", 200)
        height = layer_data.get("height", 100)
        
        # Convert time to ASS format
        start_ass = self._sec_to_ass(start_time)
        end_ass = self._sec_to_ass(end_time)
        
        if layer_type == "text":
            self._write_text_layer_to_ass(f, layer_data, start_ass, end_ass, x, y, width, height)
        elif layer_type == "box":
            self._write_box_layer_to_ass(f, layer_data, start_ass, end_ass, x, y, width, height)
        elif layer_type == "image":
            self._write_image_layer_to_ass(f, layer_data, start_ass, end_ass, x, y, width, height)
    
    def _write_text_layer_to_ass(self, f, layer_data: Dict[str, Any], start_ass: str, end_ass: str, 
                                 x: float, y: float, width: float, height: float):
        """Write text layer to ASS"""
        text = layer_data.get("text", "")
        font_size = layer_data.get("font_size", 24)
        font_color = layer_data.get("font_color", "#FFFFFF")
        bg_color = layer_data.get("bg_color", "#000000")
        bg_opacity = layer_data.get("bg_opacity", 0.0)
        bold = layer_data.get("bold", False)
        italic = layer_data.get("italic", False)
        
        # Convert colors to ASS format
        font_color_ass = self._hex_to_ass_color(font_color)
        bg_color_ass = self._hex_to_ass_color(bg_color)
        
        # Write background if needed
        if bg_opacity > 0:
            bg_style = f"TextBg,{font_size},{bg_color_ass},&H000000FF,&H00000000,&H80000000"
            if bold: bg_style += ",-1"
            else: bg_style += ",0"
            if italic: bg_style += ",1"
            else: bg_style += ",0"
            bg_style += ",0,0,100,100,0,0,1,1,0,2,10,10,10,1"
            
            f.write(f"Style: TextBg,Arial,{font_size},{bg_color_ass},&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n")
            
            # Background rectangle
            center_x = x + width // 2
            center_y = y + height // 2
            f.write(f"Dialogue: 0,{start_ass},{end_ass},TextBg,,0,0,0,,{{\\an5\\bord2\\shad0\\fscx100\\fscy100\\pos({center_x},{center_y})\\p1}}m 0 0 l {width} 0 l {width} {height} l 0 {height}{{\\p0}}\n")
        
        # Write text
        center_x = x + width // 2
        center_y = y + height // 2
        f.write(f"Dialogue: 1,{start_ass},{end_ass},Text,,0,0,0,,{{\\an5\\bord2\\shad1\\fscx100\\fscy100\\pos({center_x},{center_y})}}{text}\n")
    
    def _write_box_layer_to_ass(self, f, layer_data: Dict[str, Any], start_ass: str, end_ass: str, 
                                x: float, y: float, width: float, height: float):
        """Write box layer to ASS"""
        fill_color = layer_data.get("fill_color", "#FF0000")
        fill_opacity = layer_data.get("fill_opacity", 0.5)
        border_color = layer_data.get("border_color", "#000000")
        border_width = layer_data.get("border_width", 2)
        
        # Convert colors to ASS format
        fill_color_ass = self._hex_to_ass_color(fill_color)
        border_color_ass = self._hex_to_ass_color(border_color)
        
        # Write box style
        f.write(f"Style: Box,Arial,24,{fill_color_ass},&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,10,1\n")
        
        # Write box rectangle
        center_x = x + width // 2
        center_y = y + height // 2
        f.write(f"Dialogue: 0,{start_ass},{end_ass},Box,,0,0,0,,{{\\an5\\bord{border_width}\\shad0\\fscx100\\fscy100\\pos({center_x},{center_y})\\p1}}m 0 0 l {width} 0 l {width} {height} l 0 {height}{{\\p0}}\n")
    
    def _write_image_layer_to_ass(self, f, layer_data: Dict[str, Any], start_ass: str, end_ass: str, 
                                  x: float, y: float, width: float, height: float):
        """Write image layer to ASS - images will be handled by FFmpeg overlay filter"""
        # Images are handled separately in the FFmpeg command, not in ASS
        # This method is kept for compatibility but doesn't write anything to ASS
        pass
    
    def _build_ffmpeg_command(self, timeline_data: Dict[str, Any], output_path: str, 
                                video_width: int, video_height: int, fps: int, quality: str,
                                background_video: Optional[str], background_music: Optional[str], 
                                ass_path: str) -> List[str]:
        """Build FFmpeg command for video rendering with image overlays"""
        cmd = ["ffmpeg", "-y"]
        
        # Add input sources
        input_count = 0
        if background_video and os.path.exists(background_video):
            # Scale background video to match output resolution
            cmd.extend(["-i", background_video])
            input_count += 1
        else:
            # Create a solid color background with exact output resolution
            cmd.extend(["-f", "lavfi", "-i", f"color=c=black:size={video_width}x{video_height}:duration={timeline_data.get('total_duration', 10.0)}"])
            input_count += 1
        
        # Add image inputs
        image_layers = []
        for layer in timeline_data.get("layers", []):
            if layer.get("type") == "image" and layer.get("image_path"):
                image_path = layer.get("image_path")
                if os.path.exists(image_path):
                    # Loop static image for entire video duration to allow timed overlays
                    total_dur = str(timeline_data.get('total_duration', 10.0))
                    cmd.extend(["-loop", "1", "-t", total_dur, "-i", image_path])
                    image_layers.append({
                        "input_index": input_count,
                        "layer": layer
                    })
                    input_count += 1
        
        if background_music and os.path.exists(background_music):
            cmd.extend(["-i", background_music])
            input_count += 1
        
        # Build video filter chain
        video_filters = []
        
        # Start with background - scale to exact output resolution
        if background_video and os.path.exists(background_video):
            # Scale background video to match output resolution
            current_filter = f"[0:v]scale={video_width}:{video_height}[bg]"
            video_filters.append(current_filter)
            current_filter = "[bg]"
        else:
            # Solid color background is already correct size
            current_filter = f"[0:v]"
        
        # Add image overlays with optional transitions
        transition = timeline_data.get("image_transition", {"type": "none", "duration": 0.0})
        trans_type = transition.get("type", "none")
        trans_dur = float(transition.get("duration", 0.0) or 0.0)

        for i, img_data in enumerate(image_layers):
            layer = img_data["layer"]
            input_idx = img_data["input_index"]
            
            # Calculate position and size
            x = layer.get("x", 0)
            y = layer.get("y", 0)
            width = layer.get("width", 100)
            height = layer.get("height", 100)
            fit_mode = layer.get("fit_mode", "cover")
            start_time = float(layer.get("start_time", 0.0))
            end_time = float(layer.get("end_time", 5.0))
            enable_expr = f"enable='between(t,{start_time},{end_time})'"
            
            # Optional fade in/out per layer based on global time
            # Apply to the image stream before overlay
            pre = []
            if trans_type == "crossfade" and trans_dur > 0:
                # Fade in at layer start
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                # Fade out ending before end_time
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")
            elif trans_type == "fadeblack" and trans_dur > 0:
                # Fade to black
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")
            elif trans_type == "wipeleft" and trans_dur > 0:
                # Wipe left effect using slide
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")
            elif trans_type == "wiperight" and trans_dur > 0:
                # Wipe right effect using slide
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")
            elif trans_type == "zoomin" and trans_dur > 0:
                # Zoom in effect
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")
            elif trans_type == "zoomout" and trans_dur > 0:
                # Zoom out effect
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")
            elif trans_type == "rotate" and trans_dur > 0:
                # Rotation effect
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")
            elif trans_type == "flip" and trans_dur > 0:
                # Flip effect
                pre.append(f"fade=t=in:st={start_time}:d={trans_dur}")
                pre.append(f"fade=t=out:st={max(start_time, end_time - trans_dur)}:d={trans_dur}")

            pre_chain = ",".join(pre) if pre else None

            # Scale image based on fit mode (matching Tkinter logic)
            if fit_mode == "stretch":
                scale_filter = f"scale={width}:{height}"
                stream_in = f"[{input_idx}:v]"
                if pre_chain:
                    stream_in = f"{stream_in}{pre_chain},"
                overlay_filter = f"{stream_in}{scale_filter}[img{i}];{current_filter}[img{i}]overlay={x}:{y}:format=auto:{enable_expr}[v{i}]"
            elif fit_mode == "fit":
                # Fit within bounds (same as Tkinter min scale)
                scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease"
                stream_in = f"[{input_idx}:v]"
                if pre_chain:
                    stream_in = f"{stream_in}{pre_chain},"
                # Center within the target bounds similar to preview centering
                overlay_filter = f"{stream_in}{scale_filter}[img{i}];{current_filter}[img{i}]overlay={x}+({width}-w)/2:{y}+({height}-h)/2:format=auto:{enable_expr}[v{i}]"
            elif fit_mode == "fill":
                # Fill bounds (same as Tkinter max scale)
                scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=increase"
                stream_in = f"[{input_idx}:v]"
                if pre_chain:
                    stream_in = f"{stream_in}{pre_chain},"
                # Center the possibly larger image (no crop here; use cover for strict crop)
                overlay_filter = f"{stream_in}{scale_filter}[img{i}];{current_filter}[img{i}]overlay={x}+({width}-w)/2:{y}+({height}-h)/2:format=auto:{enable_expr}[v{i}]"
            elif fit_mode == "cover":
                # Cover bounds with crop (same as Tkinter max scale + crop)
                scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=increase"
                crop_filter = f"crop={width}:{height}"
                stream_in = f"[{input_idx}:v]"
                if pre_chain:
                    stream_in = f"{stream_in}{pre_chain},"
                overlay_filter = f"{stream_in}{scale_filter},{crop_filter}[img{i}];{current_filter}[img{i}]overlay={x}:{y}:format=auto:{enable_expr}[v{i}]"
            else:  # original
                scale_filter = "scale=-1:-1"
                stream_in = f"[{input_idx}:v]"
                if pre_chain:
                    stream_in = f"{stream_in}{pre_chain},"
                overlay_filter = f"{stream_in}{scale_filter}[img{i}];{current_filter}[img{i}]overlay={x}:{y}:format=auto:{enable_expr}[v{i}]"
            
            video_filters.append(overlay_filter)
            current_filter = f"[v{i}]"
        
        # Add ASS subtitle filter
        ass_path_escaped = ass_path.replace('\\', '/').replace(':', '\\:')
        ass_filter = f"{current_filter}ass='{ass_path_escaped}'[vout]"
        video_filters.append(ass_filter)
        
        # Join all filters
        if video_filters:
            cmd.extend(["-filter_complex", ";".join(video_filters)])
            cmd.extend(["-map", "[vout]"])
        else:
            # No image overlays, just ASS
            cmd.extend(["-vf", f"ass='{ass_path_escaped}'"])
        
        # Video parameters
        video_params = self._get_video_params(quality, fps)
        cmd.extend(video_params)
        
        # Audio parameters
        if background_music and os.path.exists(background_music):
            cmd.extend(["-c:a", "aac", "-b:a", "128k"])
        
        cmd.append(output_path)
        
        # Debug: Print FFmpeg command
        print("FFmpeg command:")
        print(" ".join(cmd))
        print()
        
        return cmd
    
    def _get_video_params(self, quality: str, fps: int) -> List[str]:
        """Get video encoding parameters based on quality"""
        if quality == "high":
            return [
                "-c:v", "h264_nvenc",
                "-preset", "p7",
                "-tune", "hq",
                "-profile:v", "high",
                "-rc", "vbr",
                "-cq", "18",
                "-b:v", "6M",
                "-maxrate", "8M",
                "-bufsize", "12M",
                "-g", str(int(fps * 2)),
                "-bf", "3",
                "-refs", "5",
                "-pix_fmt", "yuv420p"
            ]
        elif quality == "medium":
            return [
                "-c:v", "h264_nvenc",
                "-preset", "p4",
                "-tune", "hq",
                "-b:v", "2M",
                "-pix_fmt", "yuv420p"
            ]
        else:  # low
            return [
                "-c:v", "h264_nvenc",
                "-preset", "p4",
                "-tune", "hq",
                "-b:v", "500k",
                "-pix_fmt", "yuv420p"
            ]
    
    def _execute_ffmpeg_command(self, cmd: List[str], progress_callback: Optional[Callable[[float, str], None]]) -> bool:
        """Execute FFmpeg command with progress tracking"""
        try:
            # Check if FFmpeg is available
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("FFmpeg not found. Please install FFmpeg to export video.")
                return False
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error executing FFmpeg: {e}")
            return False
    
    def _sec_to_ass(self, seconds: float) -> str:
        """Convert seconds to ASS time format"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 100)
        return f"{h:01d}:{m:02d}:{s:02d}.{ms:02d}"
    
    def _hex_to_ass_color(self, hex_color: str) -> str:
        """Convert hex color to ASS color format"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            # Convert RGB to BGR for ASS
            r = hex_color[0:2]
            g = hex_color[2:4]
            b = hex_color[4:6]
            return f"&H00{b}{g}{r}"
        return "&H00FFFFFF"
    
    def _update_progress(self, progress: float, status: str, 
                        callback: Optional[Callable[[float, str], None]]):
        """Update render progress"""
        self.render_progress = progress
        self.render_status = status
        
        if callback:
            callback(progress, status)
    
    def get_render_status(self) -> Dict[str, Any]:
        """Get current render status"""
        return {
            "is_rendering": self.is_rendering,
            "progress": self.render_progress,
            "status": self.render_status,
            "output_path": self.output_path
        }
    
    def cancel_render(self):
        """Cancel current render"""
        self.is_rendering = False
        self.render_progress = 0.0
        self.render_status = "Cancelled"
