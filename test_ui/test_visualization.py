
import sys
import os
import io

# Add project root to sys.path so we can import from src
sys.path.append(os.getcwd())

try:
    from src.app.utils.visualization import get_io_ring_editor_html
except ImportError:
    print("Could not import get_io_ring_editor_html. Check your PYTHONPATH.")
    sys.exit(1)

def test_visualization():
    import json
    from pathlib import Path

    # Attempt to find the specific large config file mentioned in context
    # or look for any recent valid generated config
    target_file = Path("output/generated/20260112_104156/io_ring_config.json")
    
    if not target_file.exists():
        # Fallback to finding any json in output/generated
        print(f"File {target_file} not found. Searching for others...")
        found_files = list(Path("output/generated").glob("**/io_ring_config.json"))
        if found_files:
            target_file = found_files[-1] # Pick last one
            
    if target_file.exists():
        print(f"Using configuration from: {target_file}")
        with open(target_file, "r") as f:
            data = json.load(f)
    else:
        print("No configuration file found. Using dummy fallback data.")
        data = {
            "ring_config": {
                "chip_width": 1000,
                "chip_height": 1000,
                "pad_spacing": 90,
                "pad_width": 80,
                "pad_height": 120,
                "corner_size": 130,
                "placement_order": "clockwise"
            },
            "instances": [
                 { "name": "TEST_PAD_1", "device": "PVDD", "position": "top_0", "type": "pad", "domain": "analog" },
                 { "name": "TEST_PAD_2", "device": "PVSS", "position": "bottom_1", "type": "pad", "domain": "digital" },
            ]
        }

    try:
        html_code = get_io_ring_editor_html(data)
        
        output_file = "test_editor_output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_code)
            
        print(f"SUCCESS: Generated {output_file} (Size: {len(html_code)} bytes)")
        print(f"Please check this file in your browser: {os.path.abspath(output_file)}")

    except Exception as e:
        print(f"FAILURE: An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_visualization()
