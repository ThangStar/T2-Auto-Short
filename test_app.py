"""
Test script for the complete video editor application
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.timeline_manager import TimelineManager
from models.text_layer import TextLayer
from models.image_layer import ImageLayer
from models.box_layer import BoxLayer


def test_timeline_creation():
    """Test timeline and layer creation"""
    print("Testing timeline creation...")
    
    # Create timeline manager
    timeline = TimelineManager()
    timeline.set_total_duration(10.0)
    
    # Create text layer
    text_layer = timeline.create_text_layer("Test Text", 0.0, 5.0)
    text_layer.set_position(100, 100)
    text_layer.set_size(300, 100)
    text_layer.font_size = 24
    text_layer.font_color = "#FFFFFF"
    
    # Create box layer
    box_layer = timeline.create_box_layer(2.0, 8.0)
    box_layer.set_position(200, 200)
    box_layer.set_size(200, 150)
    box_layer.fill_color = "#FF0000"
    box_layer.fill_opacity = 0.7
    
    # Create image layer (with empty path for now)
    image_layer = timeline.create_image_layer("")
    image_layer.set_position(50, 300)
    image_layer.set_size(200, 150)
    
    print(f"Created {len(timeline.get_all_layers())} layers")
    
    # Test layer visibility
    visible_layers = timeline.get_layers_at_time(1.0)
    print(f"Visible layers at time 1.0: {len(visible_layers)}")
    
    # Test export data
    timeline_data = timeline.export_timeline_data()
    print(f"Timeline data exported: {len(timeline_data.get('layers', []))} layers")
    
    return True


def test_layer_properties():
    """Test layer property management"""
    print("Testing layer properties...")
    
    # Test text layer properties
    text_layer = TextLayer("test_text", "Hello World")
    properties = text_layer.get_properties()
    print(f"Text layer properties: {len(properties)} properties")
    
    # Test setting properties
    text_layer.set_property("font_size", 36)
    text_layer.set_property("font_color", "#FF0000")
    print("Text layer properties updated")
    
    # Test box layer properties
    box_layer = BoxLayer("test_box")
    box_properties = box_layer.get_properties()
    print(f"Box layer properties: {len(box_properties)} properties")
    
    # Test image layer properties
    image_layer = ImageLayer("test_image", "")
    image_properties = image_layer.get_properties()
    print(f"Image layer properties: {len(image_properties)} properties")
    
    return True


def test_export_data():
    """Test data export functionality"""
    print("Testing export data...")
    
    timeline = TimelineManager()
    timeline.set_total_duration(5.0)
    
    # Add some layers
    text_layer = timeline.create_text_layer("Export Test", 0.0, 5.0)
    box_layer = timeline.create_box_layer(1.0, 4.0)
    
    # Export timeline data
    timeline_data = timeline.export_timeline_data()
    
    print(f"Exported timeline duration: {timeline_data.get('total_duration')}")
    print(f"Exported layers: {len(timeline_data.get('layers', []))}")
    
    # Test individual layer export
    for layer_data in timeline_data.get('layers', []):
        print(f"Layer type: {layer_data.get('type')}, ID: {layer_data.get('layer_id')}")
    
    return True


def main():
    """Main test function"""
    print("Video Editor Application Test")
    print("============================")
    
    try:
        # Test timeline creation
        if not test_timeline_creation():
            print("❌ Timeline creation test failed")
            return 1
        
        # Test layer properties
        if not test_layer_properties():
            print("❌ Layer properties test failed")
            return 1
        
        # Test export data
        if not test_export_data():
            print("❌ Export data test failed")
            return 1
        
        print("\n✅ All tests passed!")
        print("You can now run 'python main.py' to start the application.")
        
    except Exception as e:
        print(f"❌ Error in tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
