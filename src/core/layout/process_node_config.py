#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Node Configuration - Support multiple process nodes (28nm and 180nm)
Loads configuration from JSON files for better maintainability
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Get config directory path
# process_node_config.py is in src/app/layout/
# config files are in src/app/layout/config/
_CONFIG_DIR = Path(__file__).parent / "config"

def _process_node_to_config_file(process_node: str) -> str:
    """Convert process node to config file number
    
    Args:
        process_node: Process node string ("T28" or "T180")
    
    Returns:
        Config file number ("28" or "180")
    """
    if process_node == "T28":
        return "28"
    elif process_node == "T180":
        return "180"
    else:
        raise ValueError(f"Invalid process node: {process_node}")


def _load_device_config(process_node: str) -> Optional[Dict[str, Any]]:
    """Load device configuration from JSON file"""
    # Config file names are lydevices_28.json and lydevices_180.json
    config_num = _process_node_to_config_file(process_node)
    config_file = _CONFIG_DIR / f"lydevices_{config_num}.json"
    
    if not config_file.exists():
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


# Base configuration (fallback if JSON files not found)
PROCESS_NODE_CONFIGS = {
    "T28": {
        "library_name": "tphn28hpcpgv18",
        "pad_width": 20,
        "pad_height": 110,
        "corner_size": 110,
        "pad_spacing": 60,
        "device_offset_rules": {
            "PDB3AC": 1.5 * 0.125,  # Analog signal
            "PDDW16SDGZ": -5.5 * 0.125,  # Digital IO
            "PVDD1DGZ": -8 * 0.125,  # Digital power/ground
            "PVSS1DGZ": -8 * 0.125,
            "PVDD2POC": -8 * 0.125,
            "PVSS2DGZ": -8 * 0.125,
            "default": 1.5 * 0.125
        },
        "template_files": [
            "device_templates.json",
            "IO_device_info_T28.json"
        ],
        "filler_components": {
            "analog_10": "PFILLER10A_G",
            "analog_20": "PFILLER20A_G",
            "digital_10": "PFILLER10_G",
            "digital_20": "PFILLER20_G",
            "separator": "PRCUTA_G"
        }
    },
    "T180": {
        "library_name": "tpd018bcdnv5",
        "pad_width": 80,
        "pad_height": 120,
        "corner_size": 130,
        "pad_spacing": 90,
        "device_offset_rules": {
            "PVSS2": 1.5 * 0.125,  # power/ground
            "PVDD2": 1.5 * 0.125,
            "PDDW04": -5.5 * 0.125,  # Digital IO
            "PVDD1": -8 * 0.125,  # Analog I/O
            "PVSS1": -8 * 0.125,
            "default": 1.5 * 0.125
        },
        "template_files": [
            "device_templates_180.json"
        ],
        "filler_components": {
            "analog_10": "PFILLER10",
            "analog_20": "PFILLER20",
            "digital_10": "PFILLER10",
            "digital_20": "PFILLER20",
            "separator": "PFILLER10"
        }
    }
}


def get_process_node_config(process_node: str = "T28") -> Dict[str, Any]:
    """
    Get configuration for specified process node
    Loads from JSON file if available, falls back to hardcoded config
    
    Args:
        process_node: Process node name ("T28" or "T180")
        
    Returns:
        Configuration dictionary for the process node
        
    Raises:
        ValueError: If process node is not supported
    """
    if process_node not in PROCESS_NODE_CONFIGS:
        supported = list(PROCESS_NODE_CONFIGS.keys())
        raise ValueError(
            f"Unsupported process node: {process_node}. "
            f"Supported nodes: {', '.join(supported)}"
        )
    
    # Start with base config
    config = PROCESS_NODE_CONFIGS[process_node].copy()
    
    # Try to load from JSON file and merge
    device_config = _load_device_config(process_node)
    if device_config:
        # Merge layout_params if present
        if "layout_params" in device_config:
            layout_params = device_config["layout_params"]
            config.update({
                "pad_width": layout_params.get("pad_width", config["pad_width"]),
                "pad_height": layout_params.get("pad_height", config["pad_height"]),
                "corner_size": layout_params.get("corner_size", config["corner_size"]),
                "pad_spacing": layout_params.get("pad_spacing", config["pad_spacing"]),
                "pad_offset": layout_params.get("pad_offset", 20 if process_node == "T28" else 10),
            })
            # Store full layout_params for access
            config["layout_params"] = layout_params
        
        # Merge skill_params if present
        if "skill_params" in device_config:
            config["skill_params"] = device_config["skill_params"]
        
        # Merge device_masters if present
        if "device_masters" in device_config:
            config["device_masters"] = device_config["device_masters"]
            if "default_library" in device_config["device_masters"]:
                config["library_name"] = device_config["device_masters"]["default_library"]
        
        # Update filler_components from JSON
        if "analog_filler" in device_config and "digital_filler" in device_config:
            analog_fillers = device_config["analog_filler"]
            digital_fillers = device_config["digital_filler"]
            cut_devices = device_config.get("cut_devices", [])
            
            config["filler_components"] = {
                "analog_10": analog_fillers[0] if len(analog_fillers) > 0 else config["filler_components"]["analog_10"],
                "analog_20": analog_fillers[1] if len(analog_fillers) > 1 else analog_fillers[0] if len(analog_fillers) > 0 else config["filler_components"]["analog_20"],
                "digital_10": digital_fillers[0] if len(digital_fillers) > 0 else config["filler_components"]["digital_10"],
                "digital_20": digital_fillers[1] if len(digital_fillers) > 1 else digital_fillers[0] if len(digital_fillers) > 0 else config["filler_components"]["digital_20"],
                "separator": cut_devices[0] if len(cut_devices) > 0 else config["filler_components"]["separator"]
            }
        
        # Store device lists for use by device_classifier
        config["device_lists"] = {
            "digital_devices": device_config.get("digital_devices", []),
            "analog_devices": device_config.get("analog_devices", []),
            "digital_io": device_config.get("digital_io", []),
            "analog_io": device_config.get("analog_io", []),
            "corner_devices": device_config.get("corner_devices", []),
            "filler_devices": device_config.get("filler_devices", []),
            "cut_devices": device_config.get("cut_devices", []),
            "digital_pins": device_config.get("digital_pins", []),
            "analog_pins": device_config.get("analog_pins", []),
        }
    
    return config


def get_device_offset(process_node: str, device_type: str) -> float:
    """
    Get device offset based on process node and device type
    
    Args:
        process_node: Process node name ("T28" or "T180")
        device_type: Device type string (e.g., "PDB3AC_V_G", "PVDD1DGZ_H_G")
        
    Returns:
        Offset value in microns
    """
    config = get_process_node_config(process_node)
    rules = config["device_offset_rules"]
    
    # Check for exact match first
    if device_type in rules:
        return rules[device_type]
    
    # Check for prefix match (device_type may have suffix like _V_G, _H_G)
    for prefix, offset in rules.items():
        if prefix != "default" and device_type.startswith(prefix):
            return offset
    
    # Return default
    return rules.get("default", 1.5 * 0.125)


def get_template_file_paths(process_node: str) -> list:
    """
    Get possible template file paths for a process node
    
    Args:
        process_node: Process node name ("T28" or "T180")
        
    Returns:
        List of possible template file names
    """
    config = get_process_node_config(process_node)
    return config.get("template_files", [])


def list_supported_process_nodes() -> list:
    """
    List all supported process nodes
    
    Returns:
        List of supported process node names
    """
    return list(PROCESS_NODE_CONFIGS.keys())

