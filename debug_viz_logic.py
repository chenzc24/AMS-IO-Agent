
import json
import sys
import os

sys.path.append(os.getcwd())

from src.app.utils.visualization import _calculate_instance_geometry

def test_logic():
    try:
        path = "output/generated/20260112_104156/io_ring_config.json"
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return

        with open(path, "r") as f:
            data = json.load(f)
        
        print(f"Testing logic with order: {data['ring_config'].get('placement_order')}")
        
        _calculate_instance_geometry(data["instances"], data["ring_config"])
        
        # Check first few pads
        for inst in data["instances"][:20]:
            print(f"Inst {inst['name']} ({inst['position']}): X={inst.get('ui_x')}, Y={inst.get('ui_y')}, Rot={inst.get('ui_rot')}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logic()
