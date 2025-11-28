from pathlib import Path
from typing import Optional, Dict, Any
import os
import sys
import json
from smolagents import tool

from src.app.schematic.schematic_generator import generate_multi_device_schematic
from src.app.schematic.json_validator import validate_config, convert_config_to_list, get_config_statistics
from src.app.layout.layout_generator import generate_layout_from_json

@tool
def generate_io_ring_schematic(config_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate IO ring schematic SKILL code from JSON configuration file
    
    Args:
        config_file_path: Path to JSON configuration file (can be relative or absolute path)
        output_file_path: Complete path for output file (optional, defaults to output directory based on config filename)
        
    Returns:
        String description of generation result, including file path and statistics
    """
    try:
        # Check if configuration file exists
        config_path = Path(config_file_path)
        
        # Check file extension
        if config_path.suffix.lower() != '.json':
            return f"❌ Error: File {config_path} is not a valid JSON file"
        
        # Check if template file exists
        template_file = Path("src/schematic") / "device_templates.json"
        if not template_file.exists():
            return "❌ Error: device_templates.json file not found, please run: cd src/schematic && python device_template_parser.py"
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ Error: JSON format error {e}"
        except Exception as e:
            return f"❌ Error: Failed to load configuration file {e}"
        
        # Convert configuration format
        config_list = convert_config_to_list(config)
        
        # Process output file path
        if output_file_path is None:
            # Default output to output directory
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{config_path.stem}_generated.il"
        else:
            # Use user-specified output path
            output_path = Path(output_file_path)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # If user didn't specify file extension, automatically add .il
            if output_path.suffix.lower() != '.il':
                output_path = output_path.with_suffix('.il')
        
        # Generate schematic
        # Library name, cell name, and view name are read from config or use defaults
        try:
            generate_multi_device_schematic(config_list, str(output_path))
            return ""
            
        except Exception as e:
            return f"❌ Failed to generate schematic: {e}"
            
    except Exception as e:
        return f"❌ Error occurred while generating IO ring schematic: {e}"

@tool
def generate_io_ring_layout(config_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate IO ring layout SKILL code from JSON configuration file
    
    Args:
        config_file_path: Path to JSON configuration file (can be relative or absolute path)
        output_file_path: Complete path for output file (optional, defaults to output directory based on config filename)
        
    Returns:
        String description of generation result, including file path and statistics
    """
    try:
        # Check if configuration file exists
        config_path = Path(config_file_path)
        if not config_path.exists():
            return f"❌ Error: Configuration file {config_file_path} does not exist"
        
        # Check file extension
        if config_path.suffix.lower() != '.json':
            return f"❌ Error: File {config_path} is not a valid JSON file"
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ Error: JSON format error {e}"
        except Exception as e:
            return f"❌ Error: Failed to load configuration file {e}"
        
        # Process output file path
        if output_file_path is None:
            # Default output to output directory
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{config_path.stem}_layout.il"
        else:
            # Use user-specified output path
            output_path = Path(output_file_path)
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # If user didn't specify file extension, automatically add .il
            if output_path.suffix.lower() != '.il':
                output_path = output_path.with_suffix('.il')
        
        # Generate layout
        # Library name, cell name, and view name are read from config or use defaults
        try:
            result_file = generate_layout_from_json(str(config_path), str(output_path))
            return ""
        except Exception as e:
            return f"❌ Failed to generate layout: {e}"
    except Exception as e:
        return f"❌ Error occurred while generating IO ring layout: {e}"

@tool
def list_io_ring_configs(directory: str = "src/schematic") -> str:
    """
    List all IO ring configuration files in the specified directory
    
    Args:
        directory: Directory path to search, defaults to schematic directory
        
    Returns:
        String containing list of IO ring configuration files
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"❌ Error: Directory {directory} does not exist"
        
        # Collect all JSON files
        json_files = list(dir_path.glob("*.json"))
        
        if not json_files:
            return f"No JSON files found in directory {directory}"
        
        # Filter files that might be IO ring configurations
        io_ring_configs = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'ring_config' in config and 'instances' in config:
                        ring_config = config['ring_config']
                        instances = config['instances']
                        io_ring_configs.append({
                            'file': json_file.name,
                            'size': f"{ring_config.get('width', 'N/A')}x{ring_config.get('height', 'N/A')}",
                            'pads': len(instances)
                        })
            except:
                continue
        
        if not io_ring_configs:
            return f"No valid IO ring configuration files found in directory {directory}"
        
        result = f"Found the following IO ring configuration files in directory {directory}:\n"
        for config in io_ring_configs:
            result += f"  - {config['file']}: {config['size']} scale, {config['pads']} pads\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error occurred while listing IO ring configuration files: {e}"

@tool
def validate_io_ring_config(config_file_path: str) -> str:
    """
    Validate the format and content of IO ring configuration file
    
    Args:
        config_file_path: Path to JSON configuration file
        
    Returns:
        String description of validation result
    """
    try:
        # Check if configuration file exists
        config_path = Path(config_file_path)
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ JSON format error: {e}"
        except Exception as e:
            return f"❌ Failed to load configuration file: {e}"
        
        # Validate configuration
        if not validate_config(config):
            return "❌ Configuration validation failed"
        
        # Get configuration statistics
        stats = get_config_statistics(config)
        
        result = f"✅ Configuration file validation passed!\n"
        result += f"📊 Configuration statistics:\n"
        result += f"  - IO ring scale: {stats['ring_size']}\n"
        result += f"  - Total pad count: {stats['total_pads']}\n"
        result += f"  - Device types: {stats['device_types']}\n"
        if stats['digital_ios'] > 0:
            result += f"  - Digital IOs: {stats['digital_ios']} ({stats['input_ios']} inputs, {stats['output_ios']} outputs)\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error occurred while validating configuration file: {e}" 