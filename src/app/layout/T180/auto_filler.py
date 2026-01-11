#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Filler Component Generation Module for T180
Supports blank type for domain mismatch cases
"""

from typing import List
from ..device_classifier import DeviceClassifier
from ..position_calculator import PositionCalculator
from ..T28.inner_pad_handler import InnerPadHandler
from ..T28.auto_filler import get_corner_domain
from ..process_node_config import get_process_node_config

def get_corner_domain(oriented_pads, corner_orientation) -> str:
    """Get corner domain based on the two pads around the corner.

    If the two adjacent pads share the same domain, return that domain;
    otherwise, default to "analog". If either pad is missing, also
    default to "analog".
    """
    pad1 = None
    pad2 = None
    if corner_orientation == "R180":  # Top edge
        left_pads = oriented_pads.get("R270", [])
        top_pads = oriented_pads.get("R180", [])
        pad1 = left_pads[-1] if left_pads else None
        pad2 = top_pads[0] if top_pads else None
    elif corner_orientation == "R90":  # Right edge
        top_pads = oriented_pads.get("R180", [])
        right_pads = oriented_pads.get("R90", [])
        pad1 = top_pads[-1] if top_pads else None
        pad2 = right_pads[0] if right_pads else None
    elif corner_orientation == "R0":  # Bottom edge
        right_pads = oriented_pads.get("R90", [])
        bottom_pads = oriented_pads.get("R0", [])
        pad1 = right_pads[-1] if right_pads else None
        pad2 = bottom_pads[0] if bottom_pads else None
    elif corner_orientation == "R270":  # Left edge
        bottom_pads = oriented_pads.get("R0", [])
        left_pads = oriented_pads.get("R270", [])
        pad1 = bottom_pads[-1] if bottom_pads else None
        pad2 = left_pads[0] if left_pads else None

    if not pad1 or not pad2:
        return "analog"

    domain1 = pad1.get("domain")
    domain2 = pad2.get("domain")

    if domain1 and domain1 == domain2:
        return domain1
    return pad1.get("domain", "analog")


class AutoFillerGeneratorT180:
    """Auto Filler Component Generator for T180 process node"""
    
    def __init__(self, config: dict):
        self.config = config
        self.position_calculator = PositionCalculator(config)
        self.inner_pad_handler = InnerPadHandler(config)
        self.classifier = DeviceClassifier(process_node="T180")
        
        # Get corner filler device from config
        process_config = get_process_node_config("T180")
        device_masters = process_config.get("device_masters", {})
        self.corner_filler = device_masters.get("corner_filler", "PFILLER10")

    def auto_insert_fillers_with_inner_pads(self, layout_components: List[dict], inner_pads: List[dict]) -> List[dict]:
        """Auto-insert filler components for 180nm, supporting blank type for domain mismatch"""
        # Check if filler components are already included
        existing_fillers = [comp for comp in layout_components if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device", ""), "T180")]
        
        if existing_fillers:
            print(f"🔍 Detected filler components in intent graph: {len(existing_fillers)} fillers")
            print("📝 Skipping auto-filler generation, using components defined in intent graph")
            return layout_components
        
        # Get placement order
        placement_order = self.config.get("placement_order", "counterclockwise")
        
        # Sort components by position
        sorted_components = self.position_calculator.sort_components_by_position(layout_components, placement_order)
        
        # Separate pads and corners
        pads = [comp for comp in sorted_components if comp.get("type") == "pad"]
        corners = [comp for comp in sorted_components if comp.get("type") == "corner"]
        
        # Group pads by orientation
        oriented_pads = {"R0": [], "R90": [], "R180": [], "R270": []}
        for pad in pads:
            orientation = pad.get("orientation", "")
            if orientation in oriented_pads:
                oriented_pads[orientation].append(pad)
        
        # Get configuration parameters
        corner_size = self.config.get("corner_size", 130)
        chip_width = self.config.get("chip_width", 2250)
        chip_height = self.config.get("chip_height", 2160)
        pad_width = self.config.get("pad_width", 80)
        pad_height = self.config.get("pad_height", 120)
        
        fillers = []
        
        # Process each orientation's pads
        for orientation, pad_list in oriented_pads.items():
            if not pad_list:
                continue
            
            # 1. Filler between corner and first pad (with blank support for domain mismatch)
            if orientation == "R180":  # Top edge
                # Between top-left corner and first pad
                first_pad = pad_list[0]
                fpw = first_pad.get("pad_width") or pad_width
                fph = first_pad.get("pad_height") or pad_height
                x = first_pad["position"][0] - fpw
                y = chip_height
                corner_domain = get_corner_domain(oriented_pads, "R180")
                first_pad_domain = first_pad.get("domain") or "analog"
                if first_pad_domain == "null":
                    first_pad_domain = "analog"
                if corner_domain == first_pad_domain:
                    fillers.append({
                        "view_name": "layout",
                        "type": "filler",
                        "name": "sep_top_left_corner",
                        "device": self.corner_filler,
                        "position": [x, y],
                        "orientation": "R180"
                    })
                else:
                    # Domain mismatch: insert blank
                    fillers.append({
                        "type": "blank",
                        "position": [x, y],
                        "orientation": "R180"
                    })
                
                # Between last pad and top-right corner
                last_pad = pad_list[-1]
                lpw = last_pad.get("pad_width") or pad_width
                lph = last_pad.get("pad_height") or pad_height
                x = last_pad["position"][0] + 10
                y = chip_height
                fillers.append({
                    "view_name": "layout",
                    "type": "filler",
                    "name": "filler_top_right_corner",
                    "device": "PFILLER10",
                    "position": [x, y],
                    "orientation": "R180"
                })
                
            elif orientation == "R90":  # Right edge
                # Between top-right corner and first pad
                first_pad = pad_list[0]
                fpw = first_pad.get("pad_width") or pad_width
                fph = first_pad.get("pad_height") or pad_height
                x = chip_width
                y = first_pad["position"][1] + fpw
                corner_domain = get_corner_domain(oriented_pads, "R90")
                first_pad_domain = first_pad.get("domain") or "analog"
                if first_pad_domain == "null":
                    first_pad_domain = "analog"
                if corner_domain == first_pad_domain:
                    fillers.append({
                        "view_name": "layout",
                        "type": "filler",
                        "name": "filler_right_top_corner",
                        "device": self.corner_filler,
                        "position": [x, y],
                        "orientation": "R90"
                    })
                else:
                    # Domain mismatch: insert blank
                    fillers.append({
                        "type": "blank",
                        "position": [x, y],
                        "orientation": "R90"
                    })

                # Between last pad and bottom-right corner
                last_pad = pad_list[-1]
                lpw = last_pad.get("pad_width") or pad_width
                lph = last_pad.get("pad_height") or pad_height
                x = chip_width
                y = last_pad["position"][1] - 10
                fillers.append({
                    "view_name": "layout",
                    "type": "filler",
                    "name": "filler_right_bottom_corner",
                    "device": "PFILLER10",
                    "position": [x, y],
                    "orientation": "R90"
                })
                
            elif orientation == "R0":  # Bottom edge
                # Between bottom-right corner and first pad
                first_pad = pad_list[0]
                fpw = first_pad.get("pad_width") or pad_width
                x = first_pad["position"][0] + fpw
                y = 0
                corner_domain = get_corner_domain(oriented_pads, "R0")
                first_pad_domain = first_pad.get("domain") or "analog"
                if first_pad_domain == "null":
                    first_pad_domain = "analog"
                if corner_domain == first_pad_domain:
                    fillers.append({
                        "view_name": "layout",
                        "type": "filler",
                        "name": "sep_bottom_right_corner",
                        "device": self.corner_filler,
                        "position": [x, y],
                        "orientation": "R0"
                    })
                else:
                    # Domain mismatch: insert blank
                    fillers.append({
                        "type": "blank",
                        "position": [x, y],
                        "orientation": "R0"
                    })

                # Between last pad and bottom-left corner
                last_pad = pad_list[-1]
                lpw = last_pad.get("pad_width") or pad_width
                x = last_pad["position"][0] - 10
                y = 0
                fillers.append({
                    "view_name": "layout",
                    "type": "filler",
                    "name": "filler_bottom_left_corner",
                    "device": "PFILLER10",
                    "position": [x, y],
                    "orientation": "R0"
                })
                
            elif orientation == "R270":  # Left edge
                # Between bottom-left corner and first pad
                first_pad = pad_list[0]
                fpw = first_pad.get("pad_width") or pad_width
                x = 0
                y = first_pad["position"][1] - fpw
                corner_domain = get_corner_domain(oriented_pads, "R270")
                first_pad_domain = first_pad.get("domain") or "analog"
                if first_pad_domain == "null":
                    first_pad_domain = "analog"
                if corner_domain == first_pad_domain:
                    fillers.append({
                        "view_name": "layout",
                        "type": "filler",
                        "name": "filler_left_bottom_corner",
                        "device": self.corner_filler,
                        "position": [x, y],
                        "orientation": "R270"
                    })
                else:
                    # Domain mismatch: insert blank
                    fillers.append({
                        "type": "blank",
                        "position": [x, y],
                        "orientation": "R270"
                    })
                
                # Between last pad and top-left corner
                last_pad = pad_list[-1]
                lpw = last_pad.get("pad_width") or pad_width
                x = 0
                y = last_pad["position"][1] + 10
                fillers.append({
                    "view_name": "layout",
                    "type": "filler",
                    "name": "sep_left_top_corner",
                    "device": "PFILLER10",
                    "position": [x, y],
                    "orientation": "R270"
                })
            
            # 2. Filler between pads (with blank support for domain mismatch)
            for i in range(len(pad_list) - 1):
                curr_pad = pad_list[i]
                next_pad = pad_list[i + 1]
                
                # Calculate filler position
                if orientation == "R0":  # Bottom edge
                    x = curr_pad["position"][0] - 10
                    y = 0
                elif orientation == "R90":  # Right edge
                    x = chip_width
                    y = curr_pad["position"][1] - 10
                elif orientation == "R180":  # Top edge
                    x = curr_pad["position"][0] + 10
                    y = chip_height
                elif orientation == "R270":  # Left edge
                    x = 0
                    y = curr_pad["position"][1] + 10
                
                # Check if domains match
                curr_domain = curr_pad.get("domain") or "analog"
                next_domain = next_pad.get("domain") or "analog"
                if curr_domain == "null":
                    curr_domain = "analog"
                if next_domain == "null":
                    next_domain = "analog"
                
                if curr_domain == next_domain:
                    fillers.append({
                        "view_name": curr_pad.get("view_name", self.config.get("view_name", "layout")),
                        "type": "filler",
                        "name": f"filler_{orientation}_{i+1}_1",
                        "device": "PFILLER10",
                        "position": [x, y],
                        "orientation": orientation
                    })
                else:
                    # Domain mismatch: insert blank
                    fillers.append({
                        "type": "blank",
                        "position": [x, y],
                        "orientation": orientation
                    })

        return layout_components + fillers

