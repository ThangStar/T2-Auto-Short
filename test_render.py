"""
Test script for video rendering with FFmpeg
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from core.video_renderer import VideoRenderer
from models.text_layer import TextLayer
from models.box_layer import BoxLayer


def create_test_project():
    """Create a test project for rendering"""
    print("Creating test project...")
    
    # Create timeline manager
    timeline = TimelineManager()
    timeline.set_total_duration(5.0)
    
    # Add text layer
    text_layer = timeline.create_text_layer("Hello FFmpeg!", 0.0, 5.0)
    text_layer.set_position(100, 100)
    text_layer.set_size(400, 100)
    text_layer.font_size = 36
    text_layer.font_color = "#FFFFFF"
    text_layer.bg_color = "#0000FF"
    text_layer.bg_opacity = 0.8
    text_layer.bold = True
    
    # Add box layer
    box_layer = timeline.create_box_layer(1.0, 4.0)
    box_layer.set_position(200, 250)
    box_layer.set_size(300, 150)
    box_layer.fill_color = "#FF0000"
    box_layer.fill_opacity = 0.6
    box_layer.border_color = "#FFFFFF"
    box_layer.border_width = 3
    
    # Add another text layer
    text_layer2 = timeline.create_text_layer("Video Editor with FFmpeg", 2.0, 5.0)
    text_layer2.set_position(50, 450)
    text_layer2.set_size(500, 80)
    text_layer2.font_size = 28
    text_layer2.font_color = "#FFFF00"
    text_layer2.bold = True
    text_layer2.italic = True
    
    print(f"Created test project with {len(timeline.get_all_layers())} layers")
    return timeline


def test_render_video():
    """Test video rendering with FFmpeg"""
    print("Testing video rendering...")
    
    # Create test project
    timeline = create_test_project()
    
    # Create video renderer
    renderer = VideoRenderer()
    
    # Export timeline data
    timeline_data = timeline.export_timeline_data()
    
    # Test render
    output_path = "test_output.mp4"
    
    def progress_callback(progress, status):
        print(f"Progress: {progress:.1%} - {status}")
    
    print("Starting video render...")
    success = renderer.render_video(
        timeline_data=timeline_data,
        output_path=output_path,
        video_width=1280,
        video_height=720,
        fps=30,
        quality="medium",
        progress_callback=progress_callback
    )
    
    if success:
        print(f"✅ Video rendered successfully: {output_path}")
    else:
        print("❌ Video rendering failed")
    
    return success


def main():
    """Main test function"""
    print("FFmpeg Video Renderer Test")
    print("==========================")
    
    try:
        # Test video rendering
        success = test_render_video()
        
        if success:
            print("\n✅ All tests passed!")
            print("You can now run 'python main.py' to use the full application.")
        else:
            print("\n❌ Tests failed!")
            print("Make sure FFmpeg is installed and accessible.")
            return 1
        
    except Exception as e:
        print(f"Error in test: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
