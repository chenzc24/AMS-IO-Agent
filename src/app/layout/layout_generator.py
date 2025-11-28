#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layout Generator - Supports complete layout component generation
"""

import math
import sys
import os
import json
from pathlib import Path
from typing import Dict, Tuple, List, Optional

# Import split modules
from .device_classifier import DeviceClassifier
from .voltage_domain import VoltageDomainHandler
from .position_calculator import PositionCalculator
from .filler_generator import FillerGenerator
from .layout_validator import LayoutValidator
from .inner_pad_handler import InnerPadHandler
from .skill_generator import SkillGenerator
from .auto_filler import AutoFillerGenerator

class LayoutGenerator:
    def __init__(self):
        # Default configuration
        self.config = {
            "library_name": "tphn28hpcpgv18",
            "view_name": "layout",
            "pad_width": 20,
            "pad_height": 110,
            "corner_size": 110,
            "pad_spacing": 60,
            "placement_order": "counterclockwise",  # "clockwise" or "counterclockwise"
            "filler_components": {
                "analog_10": "PFILLER10A_G",
                "analog_20": "PFILLER20A_G", 
                "digital_10": "PFILLER10_G",
                "digital_20": "PFILLER20_G",
                "separator": "PRCUTA_G"
            }
        }
        
        # Initialize each module
        self.position_calculator = PositionCalculator(self.config)
        self.voltage_domain_handler = VoltageDomainHandler()
        self.filler_generator = FillerGenerator()
        self.layout_validator = LayoutValidator()
        self.inner_pad_handler = InnerPadHandler(self.config)
        self.skill_generator = SkillGenerator(self.config)
        self.auto_filler_generator = AutoFillerGenerator(self.config)
    
    def set_config(self, config: dict):
        """Set configuration parameters"""
        self.config.update(config)
        # Update configuration for each module
        self.position_calculator.config = self.config
        self.inner_pad_handler.config = self.config
        self.skill_generator.config = self.config
        self.auto_filler_generator.config = self.config
    
    def calculate_chip_size(self, layout_components: List[dict]) -> Tuple[int, int]:
        """Calculate chip size based on layout components"""
        return self.position_calculator.calculate_chip_size(layout_components)
    
    def generate_layout(self, layout_components: List[dict], output_file: str = "generated_layout.il"):
        """Generate complete layout Skill script"""
        print("🚀 Starting Layout Skill script generation...")
        
        width, height = self.calculate_chip_size(layout_components)
        
        print(f"📐 Chip size: {width} x {height}")
        print(f"📊 Total components: {len(layout_components)}")
        
        skill_commands = []
        
        # Add file header comments
        skill_commands.append("; Generated Layout Script")
        skill_commands.append("; Complete Layout Component Generator")
        skill_commands.append(f"; Chip size: {width} x {height}")
        skill_commands.append(f"; Total components: {len(layout_components)}")
        skill_commands.append("")
        skill_commands.append("")
        
        # Group components by type
        corners = []
        pads = []
        fillers = []
        separators = []
        others = []
        
        for component in layout_components:
            component_type = component.get("type", "unknown")
            device_type = component.get("device_type", "")
            
            if component_type == "corner" or DeviceClassifier.is_corner_device(device_type):
                corners.append(component)
            elif component_type == "pad":
                pads.append(component)
            elif component_type == "filler" or DeviceClassifier.is_filler_device(device_type):
                fillers.append(component)
            elif component_type == "separator" or DeviceClassifier.is_separator_device(device_type):
                separators.append(component)
            else:
                others.append(component)
        
        # 1. Corner components
        if corners:
            skill_commands.append("; ==================== Corner Components ====================")
            for i, corner in enumerate(corners):
                name = corner.get("name", f"corner_{i+1}")
                device_type = corner.get("device_type", "PCORNERA_G")
                x, y = corner.get("position", [0, 0])
                orientation = corner.get("orientation", "R0")
                
                skill_commands.append(
                    f'dbCreateParamInstByMasterName(cv "{self.config["library_name"]}" "{device_type}" '
                    f'"{self.config["view_name"]}" "{name}" list({x} {y}) "{orientation}")'
                )
            skill_commands.append("")
        
        # 2. Pad components
        if pads:
            skill_commands.append("; ==================== Pad Components ====================")
            for i, pad in enumerate(pads):
                name = pad.get("name", f"pad_{i+1}")
                device_type = pad.get("device_type", "PDB3AC_V_G")
                x, y = pad.get("position", [0, 0])
                orientation = pad.get("orientation", "R0")
                
                skill_commands.append(
                    f'dbCreateParamInstByMasterName(cv "{self.config["library_name"]}" "{device_type}" '
                    f'"{self.config["view_name"]}" "{name}" list({x} {y}) "{orientation}")'
                )
                
                # Add PAD60GU component
                skill_commands.append(
                    f'dbCreateParamInstByMasterName(cv "PAD" "PAD60GU" "layout" "pad60gu_{i+1}" '
                    f'list({x} {y}) "{orientation}")'
                )
            skill_commands.append("")
        
        # 3. Filler components
        if fillers:
            skill_commands.append("; ==================== Filler Components ====================")
            for i, filler in enumerate(fillers):
                name = filler.get("name", f"filler_{i+1}")
                device_type = filler.get("device_type", "PFILLER20A_G")
                x, y = filler.get("position", [0, 0])
                orientation = filler.get("orientation", "R0")
                
                skill_commands.append(
                    f'dbCreateParamInstByMasterName(cv "{self.config["library_name"]}" "{device_type}" '
                    f'"{self.config["view_name"]}" "{name}" list({x} {y}) "{orientation}")'
                )
            skill_commands.append("")
        
        # 4. Separator components
        if separators:
            skill_commands.append("; ==================== Separator Components ====================")
            for i, separator in enumerate(separators):
                name = separator.get("name", f"separator_{i+1}")
                device_type = separator.get("device_type", "PRCUTA_G")
                x, y = separator.get("position", [0, 0])
                orientation = separator.get("orientation", "R0")
                
                skill_commands.append(
                    f'dbCreateParamInstByMasterName(cv "{self.config["library_name"]}" "{device_type}" '
                    f'"{self.config["view_name"]}" "{name}" list({x} {y}) "{orientation}")'
                )
            skill_commands.append("")
        
        # 5. Other components
        if others:
            skill_commands.append("; ==================== Other Components ====================")
            for i, other in enumerate(others):
                name = other.get("name", f"other_{i+1}")
                device_type = other.get("device_type", "PDB3AC_V_G")
                x, y = other.get("position", [0, 0])
                orientation = other.get("orientation", "R0")
                
                skill_commands.append(
                    f'dbCreateParamInstByMasterName(cv "{self.config["library_name"]}" "{device_type}" '
                    f'"{self.config["view_name"]}" "{name}" list({x} {y}) "{orientation}")'
                )
            skill_commands.append("")
        
        # 6. Digital IO features (if there are digital IO pads)
        digital_io_pads = [pad for pad in pads if DeviceClassifier.is_digital_io_device(pad.get("device_type", ""))]
        if digital_io_pads:
            skill_commands.append("; ==================== Digital IO Features ====================")
            digital_lines = self.generate_digital_io_features_for_pads(digital_io_pads)
            skill_commands.extend(digital_lines)
            skill_commands.append("")
        
        # 7. Pin labels
        if pads:
            skill_commands.append("; ==================== Pin Labels ====================")
            label_lines = self.generate_pin_labels_for_pads(pads)
            skill_commands.extend(label_lines)
            skill_commands.append("")
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(skill_commands))
        
        print(f"✅ Layout Skill script generated: {output_file}")
        return output_file
    
    def generate_layout_with_auto_fillers(self, layout_components: List[dict], output_file: str = "generated_layout.il"):
        """Generate layout with auto-inserted fillers"""
        print("🔧 Auto-inserting filler components...")
        
        # Auto-insert fillers
        components_with_fillers = self.auto_filler_generator.auto_insert_fillers_with_inner_pads(layout_components, [])
        
        print(f"📊 Original components: {len(layout_components)}")
        print(f"📊 Components after adding fillers: {len(components_with_fillers)}")
        
        # Generate layout
        return self.generate_layout(components_with_fillers, output_file)
    
    def convert_relative_to_absolute(self, instances: List[dict], ring_config: dict) -> List[dict]:
        """Convert relative positions to absolute positions, supporting inner pads and fillers"""
        # Save ring_config information for later use
        self.current_ring_config = ring_config
        
        converted_components = []
        inner_pads = []
        
        for instance in instances:
            relative_pos = instance.get("position", "")
            name = instance.get("name", "")
            device_type = instance.get("device_type", "")
            component_type = instance.get("type", "pad")
            io_direction = instance.get("io_direction", "")
            io_type = instance.get("io_type", "")  # New IO direction format
            voltage_domain = instance.get("voltage_domain", {})
            pin_config = instance.get("pin_config", {})
            
            # Only check type field
            if component_type == "inner_pad":
                inner_pads.append(instance)
                continue
            
            # Calculate actual coordinates and orientation
            if component_type == "filler":
                # Filler components use a dedicated relative position parsing function
                position, orientation = self.position_calculator.calculate_filler_position_from_relative(relative_pos, ring_config)
            else:
                # Other components use the original relative position parsing function
                position, orientation = self.position_calculator.calculate_position_from_relative(relative_pos, ring_config)
            
            # Build component configuration
            component = {
                "type": component_type,
                "name": name,
                "device_type": device_type,
                "position": position,
                "orientation": orientation
            }
            
            # Save original relative position information for all components
            if relative_pos:
                component["position_str"] = relative_pos
            
            # Handle IO direction (prioritize io_type, fall back to io_direction)
            if io_type:
                component["io_direction"] = io_type
            elif io_direction:
                component["io_direction"] = io_direction
            
            # If voltage_domain exists, add to configuration
            if voltage_domain:
                component["voltage_domain"] = voltage_domain
            
            # If pin_config exists, add to configuration
            if pin_config:
                component["pin_config"] = pin_config
            
            converted_components.append(component)
        
        # Check if corner components are missing
        has_corners = any(comp.get("type") == "corner" for comp in converted_components)
        if not has_corners:
            raise ValueError("❌ Error: Corner components are missing in the JSON configuration! Please explicitly specify corner components in the 'instances' list.\n"
                           "Example:\n"
                           "{\n"
                           '  "name": "top_left_corner",\n'
                           '  "device_type": "PCORNER_G",\n'
                           '  "position": "top_left",\n'
                           '  "type": "corner"\n'
                           "}")
        
        # Handle inner pad position calculation
        for inner_pad in inner_pads:
            name = inner_pad.get("name", "")
            device_type = inner_pad.get("device_type", "")
            position_str = inner_pad.get("position", "")
            io_direction = inner_pad.get("io_direction", "")
            io_type = inner_pad.get("io_type", "")
            voltage_domain = inner_pad.get("voltage_domain", {})
            pin_config = inner_pad.get("pin_config", {})
            
            # Only use outer pads for sorting and indexing
            outer_pads_for_inner = [comp for comp in converted_components if comp.get("type") == "pad" and not comp.get("inner_pad", False)]
            position, orientation = self.inner_pad_handler.calculate_inner_pad_position(position_str, outer_pads_for_inner, ring_config)
            
            # Build inner pad component configuration
            component = {
                "type": "inner_pad",
                "name": name,
                "device_type": device_type,
                "position": position,
                "orientation": orientation,
                "position_str": position_str  # Save original position string
            }
            
            # Handle IO direction
            if io_type:
                component["io_direction"] = io_type
            elif io_direction:
                component["io_direction"] = io_direction
            
            # If voltage_domain exists, add to configuration
            if voltage_domain:
                component["voltage_domain"] = voltage_domain
            
            # If pin_config exists, add to configuration
            if pin_config:
                component["pin_config"] = pin_config
            
            converted_components.append(component)
        
        return converted_components
    
    def generate_digital_io_features_for_pads(self, digital_io_pads: List[dict]) -> List[str]:
        """Generate features for digital IO pads (simplified version for backward compatibility)"""
        # This can call methods from skill_generator, but to maintain backward compatibility, provide a simplified version
        return []
    
    def generate_pin_labels_for_pads(self, pads: List[dict]) -> List[str]:
        """Generate pin labels for pads (simplified version for backward compatibility)"""
        # This can call methods from skill_generator, but to maintain backward compatibility, provide a simplified version
        return []

def generate_layout_from_config(config_list: List[dict], output_file: str = "generated_layout.il"):
    """Generate layout from a list of configurations"""
    generator = LayoutGenerator()
    return generator.generate_layout(config_list, output_file)

def generate_layout_from_json(json_file: str, output_file: str = "generated_layout.il"):
    """Generate layout from a JSON file, supporting inner pads in instances"""
    print(f"📖 Reading JSON configuration file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Get outer pad configuration
    instances = config.get("instances", [])
    ring_config = config.get("ring_config", {})
    
    # Set configuration
    generator = LayoutGenerator()
    generator.set_config(ring_config)
    if "pad_width" not in ring_config:
        ring_config["pad_width"] = generator.config["pad_width"]
    if "pad_height" not in ring_config:
        ring_config["pad_height"] = generator.config["pad_height"]
    if "corner_size" not in ring_config:
        ring_config["corner_size"] = generator.config["corner_size"]
    if "pad_spacing" not in ring_config:
        ring_config["pad_spacing"] = generator.config["pad_spacing"]
    
    print("✅ Configuration parameters set")
    
    # Convert relative positions to absolute positions
    if any("position" in instance and "_" in str(instance["position"]) for instance in instances):
        instances = generator.convert_relative_to_absolute(instances, ring_config)
    
    # Separate outer pads, inner pads, and corners
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
    
    # Validate layout rules (only validate outer pads and corners)
    validation_components = outer_pads + corners
    validation_result = generator.layout_validator.validate_layout_rules(validation_components)
    if not validation_result["valid"]:
        print(f"❌ Layout rule validation failed: {validation_result['message']}")
        return None
    
    # Check if filler components are already present in instances
    all_instances = instances  # Original instances list
    existing_fillers = [comp for comp in all_instances if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device_type", ""))]
    existing_separators = [comp for comp in all_instances if comp.get("type") == "separator" or DeviceClassifier.is_separator_device(comp.get("device_type", ""))]
    
    if existing_fillers or existing_separators:
        print(f"🔍 Detected filler components in JSON: {len(existing_fillers)} fillers, {len(existing_separators)} separators")
        print("📝 Skipping auto-filler generation, using components defined in JSON")
        # If JSON already has fillers, use validation_components directly
        all_components_with_fillers = validation_components
    else:
        # If JSON does not have fillers, use auto-generated ones
        all_components_with_fillers = generator.auto_filler_generator.auto_insert_fillers_with_inner_pads(validation_components, inner_pads)
    
    # Generate SKILL script
    print("🚀 Starting Layout Skill script generation...")
    skill_commands = []
    
    # File header
    skill_commands.append("; Generated Layout Script with Dual Ring Support")
    skill_commands.append("")
    
    # Sort all components by placement order (including corner and pad)
    placement_order = ring_config.get("placement_order", "counterclockwise")
    all_components = outer_pads + corners
    sorted_components = generator.position_calculator.sort_components_by_position(all_components, placement_order)
    
    # 1. Generate all components in sorted order
    skill_commands.append("; ==================== All Components (Sorted by Placement Order) ====================")
    for i, component in enumerate(sorted_components):
        x, y = component["position"]
        orientation = component["orientation"]
        device_type = component["device_type"]
        name = component["name"]
        component_type = component["type"]
        position_str = component['position_str']
        
        skill_commands.append(f'dbCreateParamInstByMasterName(cv "{ring_config.get("library_name", "tphn28hpcpgv18")}" "{device_type}" "{ring_config.get("view_name", "layout")}" "{name}_{position_str}" list({x} {y}) "{orientation}")')
        
        # Add PAD60GU for pad components
        if component_type == "pad":
            skill_commands.append(f'dbCreateParamInstByMasterName(cv "PAD" "PAD60GU" "layout" "pad60gu_{name}_{position_str}" list({x} {y}) "{orientation}")')
    
    skill_commands.append("")
    
    # 2. Inner Ring Pads (if any)
    if inner_pads:
        skill_commands.append("; ==================== Inner Ring Pads ====================")
        inner_pad_commands = generator.inner_pad_handler.generate_inner_pad_skill_commands(inner_pads, outer_pads, ring_config)
        skill_commands.extend(inner_pad_commands)
        skill_commands.append("")
    
    # 3. Filler components
    skill_commands.append("; ==================== Filler Components ====================")
    
    if existing_fillers or existing_separators:
        # If JSON has fillers, extract filler components from instances
        for instance in all_instances:
            if instance.get("type") == "filler" or DeviceClassifier.is_filler_device(instance.get("device_type", "")):
                # Use already converted absolute positions
                position = instance.get("position", [0, 0])
                orientation = instance.get("orientation", "R0")
                device_type = instance.get("device_type", "")
                name = instance.get("name", "")
                x, y = position
                skill_commands.append(f'dbCreateParamInstByMasterName(cv "{ring_config.get("library_name", "tphn28hpcpgv18")}" "{device_type}" "{ring_config.get("view_name", "layout")}" "{name}" list({x} {y}) "{orientation}")')
    else:
        # If JSON does not have fillers, use auto-generated fillers
        for filler in all_components_with_fillers[len(validation_components):]:  # Only process filler part
            x, y = filler["position"]
            orientation = filler["orientation"]
            device_type = filler["device_type"]
            name = filler["name"]
            skill_commands.append(f'dbCreateParamInstByMasterName(cv "{ring_config.get("library_name", "tphn28hpcpgv18")}" "{device_type}" "{ring_config.get("view_name", "layout")}" "{name}" list({x} {y}) "{orientation}")')
    
    skill_commands.append("")
    
    # 4. Digital IO features (with inner pad support)
    skill_commands.append("; ==================== Digital IO Features (with Inner Pad Support) ====================")
    digital_io_commands = generator.skill_generator.generate_digital_io_features_with_inner(outer_pads, inner_pads, ring_config)
    skill_commands.extend(digital_io_commands)
    skill_commands.append("")
    
    # 5. Pin labels (with inner pad support)
    skill_commands.append("; ==================== Pin Labels (with Inner Pad Support) ====================")
    pin_label_commands = generator.skill_generator.generate_pin_labels_with_inner(outer_pads, inner_pads, ring_config)
    skill_commands.extend(pin_label_commands)
    skill_commands.append("")
    skill_commands.append("dbSave(cv)")
    skill_commands.append("t")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(skill_commands))
    
    # Calculate chip size
    chip_width, chip_height = generator.calculate_chip_size(validation_components)
    total_components = len(all_components_with_fillers) + len(inner_pads) * 2  # Inner pads generate 2 components each
    
    print(f"📐 Chip size: {chip_width} x {chip_height}")
    print(f"📊 Total components: {total_components}")
    if inner_pads:
        print(f"📊 Inner ring pads: {len(inner_pads)}")
    print(f"✅ Layout Skill script generated: {output_file}")
    
    return output_file

def validate_layout_config(json_file: str) -> dict:
    """Validate JSON configuration file"""
    print(f"🔍 Validating JSON configuration file: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        return {"valid": False, "message": f"Configuration file not found: {json_file}"}
    except json.JSONDecodeError as e:
        return {"valid": False, "message": f"JSON format error - {e}"}
    
    generator = LayoutGenerator()
    
    # Check if it's the new relative position format
    if "ring_config" in config_data and "instances" in config_data:
        print("🔧 Detected relative position format, converting for validation...")
        
        # Convert relative positions to absolute positions
        instances = config_data["instances"]
        ring_config = config_data["ring_config"]
        layout_components = generator.convert_relative_to_absolute(instances, ring_config)
        
        print(f"📊 Conversion completed: {len(instances)} relative positions -> {len(layout_components)} absolute positions")
        
    else:
        # Old format handling
        if "layout_components" not in config_data:
            return {"valid": False, "message": "Missing 'layout_components' or 'instances' field"}
        
        layout_components = config_data["layout_components"]
    
    # Validate layout rules
    validation_result = generator.layout_validator.validate_layout_rules(layout_components)
    
    return validation_result