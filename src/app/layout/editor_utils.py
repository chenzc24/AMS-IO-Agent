# -*- coding: utf-8 -*-
"""
Editor Utils - Helper functions to bridge Layout Generator and Layout Editor (GUI)
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from copy import deepcopy


def parse_relative_position(pos: Any):
    """Parse relative position string like top_0/right_1/top_left."""
    if not isinstance(pos, str):
        return None, None, None

    if pos in {"top_left", "top_right", "bottom_left", "bottom_right"}:
        return "corner", None, pos

    parts = pos.split("_")
    if len(parts) == 2 and parts[0] in {"top", "right", "bottom", "left"} and parts[1].isdigit():
        return parts[0], int(parts[1]), None

    return None, None, None

def classify_side_by_position(x: float, y: float, 
                             chip_width: float, chip_height: float, 
                             corner_size: float, pad_height: float) -> str:
    """
    Determine which side a component belongs to based on its coordinates
    Process-agnostic logic assuming a standard ring structure
    """
    # Precision tolerance
    epsilon = 1.0
    
    # Check Corner Areas first
    # Bottom Left
    if x < corner_size and y < corner_size:
        return "corner_bottom_left"
    # Bottom Right
    if x > (chip_width - corner_size) and y < corner_size:
        return "corner_bottom_right"
    # Top Right
    if x > (chip_width - corner_size) and y > (chip_height - corner_size):
        return "corner_top_right"
    # Top Left
    if x < corner_size and y > (chip_height - corner_size):
        return "corner_top_left"
        
    # Check Sides
    # Bottom side: y is usually 0 or near 0 (depending on anchor)
    if y < pad_height + epsilon: 
        return "bottom"
    # Top side
    if y > (chip_height - pad_height - epsilon):
        return "top"
    # Left side
    if x < pad_height + epsilon:
        return "left"
    # Right side
    if x > (chip_width - pad_height - epsilon):
        return "right"
        
    return "unknown"

def export_to_editor_json(
    components: List[Dict], 
    ring_config: Dict, 
    visual_colors: Dict,
    output_path: str
) -> str:
    """
    Export layout components to IO Editor compatible JSON format
    
    Args:
        components: List of component dicts (including fillers)
        ring_config: Configuration dict containing chip dimensions etc.
        visual_colors: Dictionary of device colors from Visualizer
        output_path: Path to save the JSON file
    """
    
    chip_width = ring_config.get("chip_width", 0)
    chip_height = ring_config.get("chip_height", 0)
    process_node = ring_config.get("process_node", "T180")
    placement_order = str(ring_config.get("placement_order", "counterclockwise")).lower()
    
    # Dimensions for logic calculation (T180 default fallback)
    pad_h = ring_config.get("pad_height", 120)
    corner_s = ring_config.get("corner_size", 130)
    pad_w = ring_config.get("pad_width", 80)
    
    # 1. Structure the Graph
    # Preserve ring_config shape instead of trimming to a subset.
    ring_config_preserved = deepcopy(ring_config) if isinstance(ring_config, dict) else {}
    # `width`/`height` are not part of the desired confirmed contract.
    ring_config_preserved.pop("width", None)
    ring_config_preserved.pop("height", None)

    # Keep original ring_config shape intact.
    # Only build a minimal fallback when ring_config is completely missing/empty.
    if not ring_config_preserved:
        ring_config_preserved = {
            "chip_width": chip_width,
            "chip_height": chip_height,
            "placement_order": "counterclockwise",
            "process_node": process_node,
        }

    intent_graph = {
        "ring_config": ring_config_preserved,
        "visual_metadata": {
            "colors": visual_colors,
            "dimensions": {
                "pad_width": pad_w,
                "pad_height": pad_h,
                "corner_size": corner_s,
                "filler_10_width": 10 
            }
        },
        "instances": []
    }
    
    # 2. Buckets for sorting
    # Side buckets keep ephemeral coordinates for sorting only:
    # (instance, x, y)
    bottom_side = []
    right_side = []
    top_side = []
    left_side = []
    corners_list = []
    
    def to_persist_instance(editor_instance: Dict[str, Any]) -> Dict[str, Any]:
        """Convert editor runtime shape to persisted position-only shape."""
        persisted = dict(editor_instance)
        side = persisted.get("side")
        order = persisted.get("order")
        meta = persisted.get("meta") if isinstance(persisted.get("meta"), dict) else {}

        position = persisted.get("position") if isinstance(persisted.get("position"), str) else None
        if side in {"top", "right", "bottom", "left"} and isinstance(order, int) and order >= 1:
            position = f"{side}_{order - 1}"
        elif side == "corner":
            location = meta.get("location")
            if location in {"top_left", "top_right", "bottom_left", "bottom_right"}:
                position = location

        if not isinstance(position, str) or not position:
            fallback_rel = meta.get("_relative_position")
            if isinstance(fallback_rel, str) and fallback_rel:
                position = fallback_rel

        if isinstance(position, str) and position:
            persisted["position"] = position

        for runtime_key in ("side", "order", "meta", "position_str", "_relative_position", "_order_from_relative"):
            persisted.pop(runtime_key, None)

        return persisted

    # 3. Convert Components
    for idx, comp in enumerate(components):
        # Ensure position is valid
        pos = comp.get("position", [0, 0])
        if isinstance(pos, (list, tuple)) and len(pos) >= 2:
            x, y = pos[0], pos[1]
        else:
            x, y = 0, 0

        rel_pos = comp.get("position_str")
        if not isinstance(rel_pos, str):
            rel_pos = comp.get("position") if isinstance(comp.get("position"), str) else None

        rel_side, rel_index, rel_corner = parse_relative_position(rel_pos)

        # Determine side (prefer explicit relative position semantics)
        if rel_side:
            if rel_side == "corner":
                raw_side = f"corner_{rel_corner}"
            else:
                raw_side = rel_side
        else:
            raw_side = classify_side_by_position(x, y, chip_width, chip_height, corner_s, pad_h)
        
        instance_type = comp.get("type", "pad")
        
        # Prepare Instance Object
        instance = {
            "id": f"inst_{idx}", # Temporary ID
            # Use name from component if available, else generate one
            "name": comp.get("name", f"{instance_type}_{idx}"),
            "device": comp.get("device", ""),
            "type": instance_type,
            "position": rel_pos if isinstance(rel_pos, str) else "",
            "order": 0, # Placeholder
            "side": "", # Placeholder
            "meta": {
                "_original_position": raw_side,
            }
        }

        # Preserve business fields at top-level (not only meta) for round-trip integrity.
        preserved_fields = [
            "view_name", "domain", "pad_width", "pad_height",
            "pin_config", "io_type", "io_direction", "voltage_domain",
            "orientation"
        ]
        for field in preserved_fields:
            if field in comp:
                instance[field] = comp[field]

        if rel_pos:
            instance["meta"]["_relative_position"] = rel_pos
        
        # Add extra properties if available
        for prop in ["io_direction", "voltage_domain", "orientation", "view_name"]:
            if prop in comp:
                instance["meta"][prop] = comp[prop]

        if rel_side in {"top", "right", "bottom", "left"} and rel_index is not None:
            instance["order"] = rel_index + 1
            instance["meta"]["_order_from_relative"] = True
                
        # Map to Editor Sides and Buckets
        if "corner" in raw_side:
            instance["side"] = "corner"
            # Map specific corner location to meta for editor to place correctly
            if "bottom_left" in raw_side: instance["meta"]["location"] = "bottom_left"
            elif "bottom_right" in raw_side: instance["meta"]["location"] = "bottom_right"
            elif "top_right" in raw_side: instance["meta"]["location"] = "top_right"
            elif "top_left" in raw_side: instance["meta"]["location"] = "top_left"
            corners_list.append(instance)
        elif raw_side == "bottom":
            instance["side"] = "bottom"
            bottom_side.append((instance, x, y))
        elif raw_side == "right":
            instance["side"] = "right"
            right_side.append((instance, x, y))
        elif raw_side == "top":
            instance["side"] = "top"
            top_side.append((instance, x, y))
        elif raw_side == "left":
            instance["side"] = "left"
            left_side.append((instance, x, y))
            
    # 4. Assign Logical Order (prefer relative order when present)
    def assign_side_order(side_list, key_fn, reverse=False):
        has_relative_order = side_list and all(item[0]["meta"].get("_order_from_relative") for item in side_list)
        if has_relative_order:
            side_list.sort(key=lambda item: item[0]["order"])
            return

        side_list.sort(key=key_fn, reverse=reverse)
        for i, (inst, _, _) in enumerate(side_list):
            inst["order"] = i + 1

    # Side ordering depends on placement order semantics.
    # key_fn is ascending axis; reverse decides direction for that side.
    # - counterclockwise: bottom L->R, right B->T, top R->L, left T->B
    # - clockwise:        bottom R->L, right T->B, top L->R, left B->T
    is_cw = placement_order == "clockwise"
    side_reverse = {
        "bottom": is_cw,
        "right": is_cw,
        "top": not is_cw,
        "left": not is_cw,
    }

    assign_side_order(bottom_side, key_fn=lambda item: item[1], reverse=side_reverse["bottom"])
    assign_side_order(right_side, key_fn=lambda item: item[2], reverse=side_reverse["right"])
    assign_side_order(top_side, key_fn=lambda item: item[1], reverse=side_reverse["top"])
    assign_side_order(left_side, key_fn=lambda item: item[2], reverse=side_reverse["left"])
        
    # Add to graph (persist only position-based fields; side/order/meta are runtime-only)
    ordered_instances = [item[0] for item in bottom_side]
    ordered_instances.extend([item[0] for item in right_side])
    ordered_instances.extend([item[0] for item in top_side])
    ordered_instances.extend([item[0] for item in left_side])
    ordered_instances.extend(corners_list)

    intent_graph["instances"].extend([to_persist_instance(inst) for inst in ordered_instances])
    
    # 5. Write to File
    out_file = Path(output_path)
    # Ensure directory
    if not out_file.parent.exists():
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(intent_graph, f, indent=2)
        
    return str(out_file)
