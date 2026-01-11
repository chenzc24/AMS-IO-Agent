#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T180 Layout Generator - Complete independent implementation for T180 process node
No inheritance, completely standalone
Includes PSUB2 generation specific to T180
"""

import os
import json
from typing import Dict, Tuple, List

from ..device_classifier import DeviceClassifier
from ..voltage_domain import VoltageDomainHandler
from ..position_calculator import PositionCalculator
from ..filler_generator import FillerGenerator
from ..layout_validator import LayoutValidator
from ..T28.inner_pad_handler import InnerPadHandler
from .skill_generator import SkillGeneratorT180
from .auto_filler import AutoFillerGeneratorT180
from ..process_node_config import get_process_node_config
from .layout_visualizer import visualize_layout_T180, visualize_layout_from_components_T180
from pathlib import Path


class LayoutGeneratorT180:
    """T180 Layout Generator - Standalone implementation"""
    
    def __init__(self):
        # Get 180nm configuration
        node_config = get_process_node_config("T180")
        
        # Default configuration for 180nm
        self.config = {
            "library_name": node_config["library_name"],
            "view_name": "layout",
            "pad_width": node_config["pad_width"],
            "pad_height": node_config["pad_height"],
            "corner_size": node_config["corner_size"],
            "pad_spacing": node_config["pad_spacing"],
            "placement_order": "counterclockwise",
            "filler_components": node_config["filler_components"],
            "process_node": "T180"
        }
        
        # Store device_masters from config
        if "device_masters" in node_config:
            self.config["device_masters"] = node_config["device_masters"]
        
        # Initialize modules
        self.position_calculator = PositionCalculator(self.config)
        self.voltage_domain_handler = VoltageDomainHandler()
        self.filler_generator = FillerGenerator()
        self.layout_validator = LayoutValidator()
        self.inner_pad_handler = InnerPadHandler(self.config)
        self.skill_generator = SkillGeneratorT180(self.config)
        self.auto_filler_generator = AutoFillerGeneratorT180(self.config)
        # Instantiate classifier for instance-based queries (matching merge_source)
        self.classifier = DeviceClassifier(process_node="T180")
    
    def sanitize_skill_instance_name(self, name: str) -> str:
        """Sanitize instance names for SKILL compatibility"""
        sanitized = name.replace('<', '_').replace('>', '_')
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        return sanitized
    
    def set_config(self, config: dict):
        """Set configuration parameters"""
        self.config.update(config)
        self.position_calculator.config = self.config
        self.inner_pad_handler.config = self.config
        self.skill_generator.config = self.config
        self.auto_filler_generator.config = self.config
    
    def calculate_chip_size(self, layout_components: List[dict]) -> Tuple[int, int]:
        """Calculate chip size based on layout components"""
        return self.position_calculator.calculate_chip_size(layout_components)
    
    def convert_relative_to_absolute(self, instances: List[dict], ring_config: dict) -> List[dict]:
        """Convert relative positions to absolute positions for 180nm format"""
        converted_components = []
        inner_pads = []
        
        for instance in instances:
            relative_pos = instance.get("position", "")
            name = instance.get("name", "")
            # Use device field
            device = instance.get("device", "")
            if not device:
                raise ValueError(f"❌ Error: Instance '{name}' must have 'device' field")
            
            component_type = instance.get("type")
            if not component_type:
                # Infer type from device
                if DeviceClassifier.is_corner_device(device, "T180"):
                    component_type = "corner"
                elif DeviceClassifier.is_filler_device(device, "T180"):
                    component_type = "filler"
                else:
                    component_type = "pad"
            
            io_direction = instance.get("io_direction", "")
            io_type = instance.get("io_type", "")
            voltage_domain = instance.get("voltage_domain", {})
            pin_config = instance.get("pin_config", {})
            domain = instance.get("domain", "")
            view_name = instance.get("view_name", "layout")
            pad_width = instance.get("pad_width")
            pad_height = instance.get("pad_height")
            
            if component_type == "inner_pad":
                inner_pads.append(instance)
                continue
            
            # Calculate position (matching merge_source: pass instance parameter)
            if component_type == "filler":
                position, orientation = self.position_calculator.calculate_filler_position_from_relative(relative_pos, ring_config, instance)
            else:
                position, orientation = self.position_calculator.calculate_position_from_relative(relative_pos, ring_config, instance)
            
            # Build component configuration - use device field
            component = {
                "view_name": view_name,
                "type": component_type,
                "name": name,
                "device": device,  # Use device field
                "domain": domain,
                "position": position,
                "orientation": orientation,
                "pad_width": pad_width,
                "pad_height": pad_height
            }
            
            if relative_pos:
                component["position_str"] = relative_pos
            
            # 180nm uses io_type, fallback to io_direction
            if io_type:
                component["io_direction"] = io_type
            elif io_direction:
                component["io_direction"] = io_direction
            
            if voltage_domain:
                component["voltage_domain"] = voltage_domain
            if pin_config:
                component["pin_config"] = pin_config  # Use pin_config for 180nm
            
            converted_components.append(component)
        
        # Check corners
        has_corners = any(comp.get("type") == "corner" for comp in converted_components)
        if not has_corners:
            raise ValueError("❌ Error: Corner components are missing in the intent graph!")
        
        # Handle inner pads
        for inner_pad in inner_pads:
            name = inner_pad.get("name", "")
            device = inner_pad.get("device", "")
            if not device:
                raise ValueError(f"❌ Error: Inner pad '{name}' must have 'device' field")
            
            position_str = inner_pad.get("position", "")
            io_type = inner_pad.get("io_type", "")
            io_direction = inner_pad.get("io_direction", "")
            voltage_domain = inner_pad.get("voltage_domain", {})
            pin_config = inner_pad.get("pin_config", {})
            
            outer_pads_for_inner = [comp for comp in converted_components if comp.get("type") == "pad"]
            position, orientation = self.inner_pad_handler.calculate_inner_pad_position(position_str, outer_pads_for_inner, ring_config)
            
            component = {
                "type": "inner_pad",
                "name": name,
                "device": device,  # Use device field
                "position": position,
                "orientation": orientation,
                "position_str": position_str
            }
            
            if io_type:
                component["io_direction"] = io_type
            elif io_direction:
                component["io_direction"] = io_direction
            if voltage_domain:
                component["voltage_domain"] = voltage_domain
            if pin_config:
                component["pin_config"] = pin_config  # Use pin_config for 180nm
            
            converted_components.append(component)
        
        return converted_components


def generate_layout_from_json(json_file: str, output_file: str = "generated_layout.il"):
    """Generate 180nm layout from JSON file"""
    print(f"📖 Reading intent graph file: {json_file}")
    print(f"🔧 Using process node: 180nm")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    instances = config.get("instances", [])
    ring_config = config.get("ring_config", {})
    
    # Override process_node if specified
    if "process_node" in ring_config:
        ring_config["process_node"] = "T180"
    
    generator = LayoutGeneratorT180()
    
    # Normalize ring_config format
    if "width" in ring_config and "chip_width" not in ring_config:
        width = ring_config.get("width", 3)
        height = ring_config.get("height", 3)
        pad_width = ring_config.get("pad_width", generator.config["pad_width"])
        pad_height = ring_config.get("pad_height", generator.config["pad_height"])
        corner_size = ring_config.get("corner_size", generator.config["corner_size"])
        pad_spacing = ring_config.get("pad_spacing", generator.config["pad_spacing"])
        
        ring_config["chip_width"] = width * pad_spacing + corner_size * 2
        ring_config["chip_height"] = height * pad_spacing + corner_size * 2
        
        if "top_count" not in ring_config:
            ring_config["top_count"] = width
        if "bottom_count" not in ring_config:
            ring_config["bottom_count"] = width
        if "left_count" not in ring_config:
            ring_config["left_count"] = height
        if "right_count" not in ring_config:
            ring_config["right_count"] = height
    
    # Merge top-level config
    if "library_name" in config and "library_name" not in ring_config:
        ring_config["library_name"] = config["library_name"]
    if "cell_name" in config and "cell_name" not in ring_config:
        ring_config["cell_name"] = config["cell_name"]
    
    generator.set_config(ring_config)
    if "pad_width" not in ring_config:
        ring_config["pad_width"] = generator.config["pad_width"]
    if "pad_height" not in ring_config:
        ring_config["pad_height"] = generator.config["pad_height"]
    if "corner_size" not in ring_config:
        ring_config["corner_size"] = generator.config["corner_size"]
    if "pad_spacing" not in ring_config:
        ring_config["pad_spacing"] = generator.config["pad_spacing"]
    if "library_name" not in ring_config:
        ring_config["library_name"] = generator.config["library_name"]
    if "view_name" not in ring_config:
        ring_config["view_name"] = generator.config["view_name"]
    if "device_masters" not in ring_config:
        ring_config["device_masters"] = generator.config.get("device_masters", {})
    
    print("✅ Configuration parameters set")
    
    # Convert relative positions
    if any("position" in instance and "_" in str(instance["position"]) for instance in instances):
        instances = generator.convert_relative_to_absolute(instances, ring_config)
    
    # Separate components
    outer_pads = []
    inner_pads = []
    corners = []
    
    for instance in instances:
        if instance.get("type") == "inner_pad":
            inner_pads.append(instance)
        elif instance.get("type") == "pad":
            outer_pads.append(instance)
        elif instance.get("type") == "corner":
            corners.append(instance)
    
    print(f"📊 Outer ring pads: {len(outer_pads)}")
    print(f"📊 Inner ring pads: {len(inner_pads)}")
    print(f"📊 Corners: {len(corners)}")
    
    # Validate
    validation_components = outer_pads + corners
    process_node = ring_config.get("process_node", "T180")
    validation_result = generator.layout_validator.validate_layout_rules(validation_components, process_node)
    if not validation_result["valid"]:
        print(f"❌ Layout rule validation failed: {validation_result['message']}")
        return None
    
    # Check fillers - use device field
    all_instances = instances
    existing_fillers = [comp for comp in all_instances if comp.get("type") == "filler" or 
                        generator.classifier.is_filler(comp.get("device", ""))]
    
    if existing_fillers:
        print(f"🔍 Detected filler components in JSON: {len(existing_fillers)} fillers")
        print("📝 Skipping auto-filler generation, using components defined in JSON")
        all_components_with_fillers = validation_components
    else:
        all_components_with_fillers = generator.auto_filler_generator.auto_insert_fillers_with_inner_pads(validation_components, inner_pads)
    
    # Generate SKILL script
    print("🚀 Starting Layout Skill script generation...")
    skill_commands = []
    
    skill_commands.append("cv = geGetWindowCellView()")
    # File header
    skill_commands.append("; Generated Layout Script with Dual Ring Support")
    skill_commands.append("")
    
    # Sort components
    placement_order = ring_config.get("placement_order", "counterclockwise")
    all_components = outer_pads + corners
    sorted_components = generator.position_calculator.sort_components_by_position(all_components, placement_order)
    
    # 1. Generate all components (matching merge_source format)
    skill_commands.append("; ==================== All Components (Sorted by Placement Order) ====================")
    for i, component in enumerate(sorted_components):
        x, y = component["position"]
        orientation = component["orientation"]
        device = component["device"]  # Use device field
        name = component["name"]
        component_type = component["type"]
        position_str = component.get('position_str', 'abs')
        lib = ring_config.get("library_name", generator.config.get("library_name", "tpd018bcdnv5"))
        view = component.get("view_name", ring_config.get("view_name", "layout"))
        
        # Use name_position_str format (matching merge_source, no sanitization)
        skill_commands.append(f'dbCreateParamInstByMasterName(cv "{lib}" "{device}" "{view}" "{name}_{position_str}" list({x} {y}) "{orientation}")')
        
        # Add PAD70 for pad components with adjusted orientation/position (matching merge_source)
        if component_type == "pad":
            orient_map = {"R0": "R180", "R90": "R270", "R180": "R0", "R270": "R90"}
            pad70_orient = orient_map.get(orientation, "R0")
            
            # Centering along tangent using |pad_width - 70| correction (half for centering)
            pad_w = component.get("pad_width", ring_config.get("pad_width", 80))
            PAD_width = 70
            center_correction = abs(pad_w - PAD_width) / 2
            
            # Initialize defaults to current pad origin if not set by branch
            x70 = x
            y70 = y
            if orientation == "R0":          # bottom edge, tangent: +X
                x70 = x + pad_w - center_correction
            elif orientation == "R180":      # top edge, tangent: +X
                x70 = x + center_correction - pad_w
            elif orientation == "R90":       # right edge, tangent: +Y
                y70 = y + pad_w - center_correction
            elif orientation == "R270":      # left edge, tangent: +Y
                y70 = y + center_correction - pad_w
            # Get pad library and master from config
            device_masters = ring_config.get("device_masters", {})
            pad_library = device_masters.get("pad_library", "tpb018v_cup_6lm")
            pad_master = device_masters.get("pad_master", "PAD70LU_TRL")
            skill_commands.append(
                f'dbCreateParamInstByMasterName(cv "{pad_library}" "{pad_master}" "layout" "pad70lu_{name}_{position_str}" list({x70} {y70}) "{pad70_orient}")'
            )
    
    skill_commands.append("")
    
    # 2. PSUB2_layer Drawing (matching merge_source)
    skill_commands.append("; ==================== PSUB2 Layer ====================")
    PSUB2_commands = generator.skill_generator.generate_psub2(outer_pads, corners, ring_config)
    skill_commands.extend(PSUB2_commands)
    skill_commands.append("")
    
    # 3. Filler components (matching merge_source)
    skill_commands.append("; ==================== Filler Components ====================")
    
    if existing_fillers:
        # If JSON has fillers, extract filler components from instances
        for instance in all_instances:
            if instance.get("type") == "filler" or generator.classifier.is_filler(instance.get("device", "")):
                # Use already converted absolute positions
                position = instance.get("position", [0, 0])
                orientation = instance.get("orientation", "R0")
                device = instance.get("device", "")
                name = instance.get("name", "")
                x, y = position
                lib = ring_config.get("library_name", generator.config.get("library_name", "tpd018bcdnv5"))
                view = instance.get("view_name", ring_config.get("view_name", "layout"))
                skill_commands.append(f'dbCreateParamInstByMasterName(cv "{lib}" "{device}" "{view}" "{name}" list({x} {y}) "{orientation}")')
    else:
        # If JSON does not have fillers, use auto-generated fillers
        # Skip blank types (they are for visualization only, not SKILL generation)
        for filler in all_components_with_fillers[len(validation_components):]:  # Only process filler part
            if filler.get("type") == "filler":
                x, y = filler["position"]
                orientation = filler["orientation"]
                # Support both device and device_type fields (180nm uses device_type)
                device = filler.get("device", "PFILLER10")
                name = filler["name"]
                lib = ring_config.get("library_name", generator.config.get("library_name", "tpd018bcdnv5"))
                view = filler.get("view_name", ring_config.get("view_name", "layout"))
                skill_commands.append(f'dbCreateParamInstByMasterName(cv "{lib}" "{device}" "{view}" "{name}" list({x} {y}) "{orientation}")')
            # Skip blank types - they are for visualization only
  
    skill_commands.append("")
    
    # 5. Digital IO features
    skill_commands.append("; ==================== Digital IO Features (with Inner Pad Support) ====================")
    digital_io_commands = generator.skill_generator.generate_digital_io_features_with_inner(outer_pads, inner_pads, ring_config)
    skill_commands.extend(digital_io_commands)
    skill_commands.append("")
    
    # 6. Pin labels
    skill_commands.append("; ==================== Pin Labels (with Inner Pad Support) ====================")
    pin_label_commands = generator.skill_generator.generate_pin_labels_with_inner(outer_pads, inner_pads, ring_config)
    skill_commands.extend(pin_label_commands)
    skill_commands.append("")
    skill_commands.append("dbSave(cv)")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(skill_commands))
    
    # Generate visualization (T180 uses layout_visualizer_T180)
    try:
        output_dir = os.path.dirname(output_file) or "output"
        vis_name = os.path.splitext(os.path.basename(output_file))[0] + "_visualization.png"
        visualization_path = os.path.join(output_dir, vis_name)
        os.makedirs(output_dir, exist_ok=True)
        # Use component-based visualization to support blank types
        visualize_layout_from_components_T180(all_components_with_fillers, visualization_path, ring_config)
        print(f"📊 Visualization generated: {visualization_path}")
    except Exception as e:
        print(f"⚠️  Visualization generation failed: {e}")
    
    # Calculate chip size (matching merge_source)
    chip_width, chip_height = ring_config.get("chip_width", 2250), ring_config.get("chip_height", 2160)
    total_components = len(all_components_with_fillers) + len(inner_pads) * 2  # Inner pads generate 2 components each
    
    print(f"📐 Chip size: {chip_width} x {chip_height}")
    print(f"📊 Total components: {total_components}")
    if inner_pads:
        print(f"📊 Inner ring pads: {len(inner_pads)}")
    print(f"✅ Layout Skill script generated: {output_file}")
    
    return output_file

