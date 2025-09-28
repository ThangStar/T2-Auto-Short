"""
Demo script for Video Editor
This script demonstrates how to use the video editor programmatically
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer


def create_demo_project():
    """Create a demo project with sample layers"""
    print("Creating demo project...")
    
    # Create timeline manager
    timeline = TimelineManager()
    timeline.set_total_duration(10.0)
    
    # Add text layer
    text_layer = timeline.create_text_layer("Hello World!", 0.0, 5.0)
    text_layer.set_position(100, 100)
    text_layer.set_size(300, 100)
    text_layer.font_size = 32
    text_layer.font_color = "#FFFFFF"
    text_layer.bg_color = "#0000FF"
    text_layer.bg_opacity = 0.5
    
    # Add box layer
    box_layer = timeline.create_box_layer(2.0, 8.0)
    box_layer.set_position(200, 200)
    box_layer.set_size(200, 150)
    box_layer.fill_color = "#FF0000"
    box_layer.fill_opacity = 0.7
    box_layer.border_color = "#FFFFFF"
    box_layer.border_width = 3
    
    # Add another text layer
    text_layer2 = timeline.create_text_layer("Video Editor Demo", 5.0, 10.0)
    text_layer2.set_position(50, 300)
    text_layer2.set_size(400, 80)
    text_layer2.font_size = 24
    text_layer2.font_color = "#FFFF00"
    text_layer2.bold = True
    
    print(f"Created project with {len(timeline.get_all_layers())} layers")
    
    # Print timeline summary
    summary = timeline.get_timeline_summary()
    print(f"Total duration: {summary['total_duration']} seconds")
    print("Layers:")
    for layer_info in summary['layers']:
        print(f"  - {layer_info['type']}: {layer_info['id']} ({layer_info['start_time']}-{layer_info['end_time']})")
    
    return timeline


def export_demo_data(timeline):
    """Export demo project data"""
    print("\nExporting project data...")
    
    # Export timeline data
    timeline_data = timeline.export_timeline_data()
    
    # Save to JSON file
    import json
    with open("demo_project.json", "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)
    
    print("Project saved to demo_project.json")
    
    return timeline_data


def main():
    """Main demo function"""
    print("Video Editor Demo")
    print("================")
    
    try:
        # Create demo project
        timeline = create_demo_project()
        
        # Export data
        timeline_data = export_demo_data(timeline)
        
        print("\nDemo completed successfully!")
        print("You can now run 'python main.py' to open the GUI application.")
        
    except Exception as e:
        print(f"Error in demo: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
