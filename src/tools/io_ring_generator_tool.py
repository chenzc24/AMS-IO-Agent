from pathlib import Path
from typing import Optional, Dict, Any
import os
import sys
import json
from smolagents import tool

from src.app.schematic.schematic_generator_T28 import generate_multi_device_schematic as generate_multi_device_schematic_28nm
from src.app.schematic.schematic_generator_T180 import generate_multi_device_schematic as generate_multi_device_schematic_180nm
from src.app.intent_graph.json_validator import validate_config, convert_config_to_list, get_config_statistics
from src.app.layout.layout_generator_factory import generate_layout_from_json, create_layout_generator
from src.app.layout.T28.layout_visualizer import visualize_layout, visualize_layout_from_components
from src.app.layout.T180.layout_visualizer import visualize_layout_T180
from src.app.layout.T180.confirmed_config_builder import build_confirmed_config_from_io_config
from src.app.layout.device_classifier import DeviceClassifier, _normalize_process_node
from src.app.layout.process_node_config import get_process_node_config, get_template_file_paths, list_supported_process_nodes


def _normalize_supported_process_node(process_node: str) -> str:
    try:
        normalized = _normalize_process_node(process_node)
    except ValueError as e:
        raise ValueError(str(e))

    supported_nodes = list_supported_process_nodes()
    if normalized not in supported_nodes:
        raise ValueError(f"Unsupported process node '{normalized}'. Supported nodes: {', '.join(supported_nodes)}")
    return normalized


def _resolve_confirmed_config_path(config_path: Path, process_node: str, consume_confirmed_only: bool) -> Path:
    if not consume_confirmed_only:
        return config_path

    if config_path.name.endswith("_confirmed.json"):
        return config_path

    expected_confirmed = config_path.with_name(f"{config_path.stem}_confirmed.json")
    if expected_confirmed.exists():
        return expected_confirmed

    if process_node == "T180":
        generated_confirmed = Path(build_confirmed_config_from_io_config(str(config_path)))
        if generated_confirmed.exists():
            return generated_confirmed

    raise ValueError(
        "Editor-confirmed config required. "
        f"Expected: {expected_confirmed}. "
        "Please run build_io_ring_confirmed_config first."
    )

@tool
def build_io_ring_confirmed_config(
    config_file_path: str,
    confirmed_output_path: Optional[str] = None,
    process_node: str = "T180"
) -> str:
    """Build confirmed IO config from initial io_config (filler + IO editor confirmation only).

    Args:
        config_file_path: Path to the initial intent-graph JSON file.
        confirmed_output_path: Optional output path for the confirmed JSON file.
        process_node: Process node selector (currently supports "T180" only).

    Returns:
        String description of confirmation result and generated file path.

    Note:
        This tool is independent from layout/schematic SKILL generation.
    """
    try:
        config_path = Path(config_file_path)
        if not config_path.exists():
            return f"❌ Error: Intent graph file {config_path} does not exist"
        if config_path.suffix.lower() != '.json':
            return f"❌ Error: File {config_path} is not a valid JSON file"

        try:
            process_node = _normalize_process_node(process_node)
        except ValueError as e:
            return f"❌ Error: {e}"

        if process_node != "T180":
            return "❌ Error: build_io_ring_confirmed_config currently supports T180 only"

        confirmed_path = build_confirmed_config_from_io_config(
            source_json_path=str(config_path),
            confirmed_output_path=confirmed_output_path,
        )

        return (
            f"✅ Confirmed IO config generated successfully: {confirmed_path}\n"
            "💡 This file is ready for downstream layout/schematic generation."
        )
    except Exception as e:
        return f"❌ Error occurred while building confirmed IO config: {e}"

@tool
def generate_io_ring_schematic(
    config_file_path: str, 
    output_file_path: Optional[str] = None,
    process_node: str = "T28",
    consume_confirmed_only: bool = True,
    ) -> str:
    """
    Generate IO ring schematic SKILL code from intent graph file
    
    Args:
        config_file_path: Path to intent graph file (REQUIRED - use absolute path for better file management)
        output_file_path: Complete path for output file (STRONGLY RECOMMENDED - specify explicit path for better file organization. If not provided, defaults to output directory based on config filename)
        process_node: Process node to use ("T28" or "T180", default: "T28")
        consume_confirmed_only: If True, require and consume editor-confirmed JSON (or auto-resolve/build it for T180); if False, allow direct consumption of the provided JSON.
        
    Returns:
        String description of generation result, including file path and statistics
        
    Note:
        For better file management, it is STRONGLY RECOMMENDED to:
        1. Use absolute paths for both input and output files
        2. Explicitly specify output_file_path to organize files in timestamped directories
        3. Keep related files (intent graph, schematic, layout) in the same directory
        
    Supported process nodes:
        - "T28": 28nm process node (default, uses tphn28hpcpgv18 library)
        - "T180": 180nm process node (uses tpd018bcdnv5 library)
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        if not config_path.exists():
            return f"❌ Error: Intent graph file {config_path} does not exist"

        try:
            process_node = _normalize_supported_process_node(process_node)
            config_path = _resolve_confirmed_config_path(config_path, process_node, consume_confirmed_only)
        except ValueError as e:
            return f"❌ Error: {e}"
        
        # Check file extension
        if config_path.suffix.lower() != '.json':
            return f"❌ Error: File {config_path} is not a valid JSON file"
        
        # Get process node configuration
        node_config = get_process_node_config(process_node)
        
        # Check if template file exists (try multiple locations and filenames based on process node)
        template_file = None
        template_file_names = get_template_file_paths(process_node)
        
        # Build possible paths for each template file name
        possible_paths = []
        for template_name in template_file_names:
            possible_paths.extend([
                Path("src/app/schematic") / template_name,
                Path("src/schematic") / template_name,
                Path("device_templates.json") if template_name == "device_templates.json" else Path(template_name),
                Path("src/scripts/devices") / template_name,
            ])
        
        # For 28nm, also check for IO_device_info_T28.json
        if process_node == "T28":
            possible_paths.extend([
                Path("src/app/schematic") / "IO_device_info_T28.json",
            Path("src/schematic") / "IO_device_info_T28.json",
                Path("IO_device_info_T28.json"),
                Path("src/scripts/devices") / "IO_device_info_T28.json",
            ])
        # For 180nm, also check for IO_device_info_T180.json
        elif process_node == "T180":
            possible_paths.extend([
                Path("src/app/schematic") / "IO_device_info_T180.json",
                Path("src/schematic") / "IO_device_info_T180.json",
                Path("IO_device_info_T180.json"),
                Path("src/scripts/devices") / "IO_device_info_T180.json",
            ])
        
        for path in possible_paths:
            if path.exists():
                template_file = path
                break
        
        if template_file is None:
            expected_files = ", ".join(template_file_names)
            return f"❌ Error: device template file not found for {process_node} process node.\n" \
                   f"Expected files: {expected_files}\n" \
                   f"Please check if the file exists in one of these locations:\n" \
                   f"  - src/app/schematic/\n" \
                   f"  - src/schematic/\n" \
                   f"  - src/scripts/devices/\n" \
                   f"  - project root directory\n" \
                   f"Or generate it by running the appropriate parser script."
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ Error: JSON format error {e}"
        except Exception as e:
            return f"❌ Error: Failed to load intent graph file {e}"
        
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
        
        # Check if process_node is specified in config (override parameter)
        if isinstance(config, dict) and "ring_config" in config:
            if "process_node" in config["ring_config"]:
                config_process_node = config["ring_config"]["process_node"]
                # Normalize process node from config (e.g., "180nm" -> "T180")
                try:
                    process_node = _normalize_process_node(config_process_node)
                except ValueError:
                    # If normalization fails, keep original and let validation catch it
                    process_node = config_process_node
        
        # Normalize process node parameter
        try:
            process_node = _normalize_supported_process_node(process_node)
        except ValueError as e:
            return f"❌ Error: {e}"
        
        # Generate schematic with process node
        # Library name, cell name, and view name are read from config or use defaults
        try:
            # Select appropriate generator based on process node
            if process_node == "T28":
                generate_multi_device_schematic_28nm(config_list, str(output_path))
            elif process_node == "T180":
                generate_multi_device_schematic_180nm(config_list, str(output_path))
            else:
                supported_nodes = list_supported_process_nodes()
                return f"❌ Error: Unsupported process node '{process_node}'. Supported nodes: {', '.join(supported_nodes)}"
            
            # Get statistics from config_list (filter out ring_config items)
            device_instances = [item for item in config_list if isinstance(item, dict) and 'device' in item]
            device_count = len(device_instances)
            device_types = set()
            for item in device_instances:
                if 'device' in item:
                    device_types.add(item['device'])
            
            result = f"✅ Successfully generated schematic file: {output_path}\n"
            result += f"📊 Statistics:\n"
            result += f"  - Device instance count: {device_count}\n"
            if device_types:
                result += f"  - Device types used: {', '.join(sorted(device_types))}\n"
            
            return result
            
        except Exception as e:
            return f"❌ Failed to generate schematic: {e}"
            
    except Exception as e:
        return f"❌ Error occurred while generating IO ring schematic: {e}"

@tool
def generate_io_ring_layout(
    config_file_path: str, 
    output_file_path: Optional[str] = None,
    process_node: str = "T28",
    consume_confirmed_only: bool = True,
) -> str:
    """
    Generate IO ring layout SKILL code from intent graph file
    
    Args:
        config_file_path: Path to intent graph file (REQUIRED - use absolute path for better file management)
        output_file_path: Complete path for output file (STRONGLY RECOMMENDED - specify explicit path for better file organization. If not provided, defaults to output directory based on config filename)
        process_node: Process node to use ("T28" or "T180", default: "T28")
        consume_confirmed_only: If True, require and consume editor-confirmed JSON (or auto-resolve/build it for T180); if False, allow direct consumption of the provided JSON.
        
    Returns:
        String description of generation result, including file path and statistics
        
    Note:
        For better file management, it is STRONGLY RECOMMENDED to:
        1. Use absolute paths for both input and output files
        2. Explicitly specify output_file_path to organize files in timestamped directories
        3. Keep related files (intent graph, schematic, layout) in the same directory
        
    Supported process nodes:
        - "T28": 28nm process node (default, uses tphn28hpcpgv18 library)
        - "T180": 180nm process node (uses tpd018bcdnv5 library)
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        if not config_path.exists():
            return f"❌ Error: Intent graph file {config_path} does not exist"

        try:
            process_node = _normalize_supported_process_node(process_node)
            config_path = _resolve_confirmed_config_path(config_path, process_node, consume_confirmed_only)
        except ValueError as e:
            return f"❌ Error: {e}"
        
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
            return f"❌ Error: Failed to load intent graph file {e}"
        
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
        
        # Generate layout with process node configuration
        # Library name, cell name, and view name are read from config or use defaults
        try:
            result_file = generate_layout_from_json(str(config_path), str(output_path), process_node)
            
            # Automatically generate visualization (use process-node-specific visualizer)
            vis_output_path = None
            try:
                vis_output_path = output_path.parent / f"{output_path.stem}_visualization.png"
                if process_node == "T180":
                    visualize_layout_T180(str(output_path), str(vis_output_path))
                else:
                    visualize_layout(str(output_path), str(vis_output_path))
            except Exception as vis_e:
                # Visualization is optional, don't fail if it doesn't work
                pass
            
            # Return success message with visualization info if generated
            if vis_output_path and vis_output_path.exists():
                return f"✅ Successfully generated layout file: {output_path}\n" \
                       f"📊 Layout visualization generated: {vis_output_path}\n" \
                       f"💡 Tip: Review the visualization image to verify the layout arrangement."
            else:
                return f"✅ Successfully generated layout file: {output_path}"
        except Exception as e:
            return f"❌ Failed to generate layout: {e}"
    except Exception as e:
        return f"❌ Error occurred while generating IO ring layout: {e}"


@tool
def generate_io_ring_confirmed_artifacts(
    config_file_path: str,
    output_dir: Optional[str] = None,
    process_node: str = "T180",
) -> str:
    """Fixed-order orchestrator: confirmed config -> layout -> schematic.
    
    Args:
        config_file_path: Path to the initial intent-graph JSON file.
        output_dir: Optional output directory for the generated artifacts.
        process_node: Process node selector (currently supports "T180" only).
        
    Returns:
        String description of generation result.
    """
    try:
        source_path = Path(config_file_path)
        if not source_path.exists():
            return f"❌ Error: Intent graph file {source_path} does not exist"
        if source_path.suffix.lower() != ".json":
            return f"❌ Error: File {source_path} is not a valid JSON file"

        try:
            process_node = _normalize_supported_process_node(process_node)
        except ValueError as e:
            return f"❌ Error: {e}"

        out_dir = Path(output_dir) if output_dir else source_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        confirmed_path = out_dir / f"{source_path.stem}_confirmed.json"
        layout_path = out_dir / f"{source_path.stem}_layout.il"
        schematic_path = out_dir / f"{source_path.stem}_schematic.il"

        confirmed_built = build_confirmed_config_from_io_config(
            source_json_path=str(source_path),
            confirmed_output_path=str(confirmed_path),
        )

        layout_result = generate_io_ring_layout(
            config_file_path=str(confirmed_path),
            output_file_path=str(layout_path),
            process_node=process_node,
            consume_confirmed_only=True,
        )
        if layout_result.startswith("❌"):
            return f"❌ Orchestration failed at layout step:\n{layout_result}"

        schematic_result = generate_io_ring_schematic(
            config_file_path=str(confirmed_path),
            output_file_path=str(schematic_path),
            process_node=process_node,
            consume_confirmed_only=True,
        )
        if schematic_result.startswith("❌"):
            return f"❌ Orchestration failed at schematic step:\n{schematic_result}"

        return (
            "✅ Fixed-order orchestration completed successfully.\n"
            f"1) Confirmed config: {confirmed_built}\n"
            f"2) Layout: {layout_path}\n"
            f"3) Schematic: {schematic_path}"
        )
    except Exception as e:
        return f"❌ Error occurred during fixed-order orchestration: {e}"

@tool
def list_intent_graphs(directory: str = "output") -> str:
    """
    List all intent graph files in the specified directory
    
    Args:
        directory: Directory path to search, defaults to output directory
        
    Returns:
        String containing list of intent graph files
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            # Try alternative locations
            alt_paths = [
                Path("output/generated"),
                Path("src/schematic"),
                Path("output"),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    dir_path = alt_path
                    break
            else:
                return f"❌ Error: Directory {directory} does not exist. Tried: {directory}, output/generated, src/schematic, output"
        
        # Collect all JSON files
        json_files = list(dir_path.glob("*.json"))
        
        if not json_files:
            return f"No JSON files found in directory {directory}"
        
        # Filter files that might be intent graphs
        intent_graphs = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'ring_config' in config and 'instances' in config:
                        ring_config = config['ring_config']
                        instances = config['instances']
                        intent_graphs.append({
                            'file': json_file.name,
                            'size': f"{ring_config.get('width', 'N/A')}x{ring_config.get('height', 'N/A')}",
                            'pads': len(instances)
                        })
            except:
                continue
        
        if not intent_graphs:
            return f"No valid intent graph files found in directory {directory}"
        
        result = f"Found the following intent graph files in directory {directory}:\n"
        for config in intent_graphs:
            result += f"  - {config['file']}: {config['size']} scale, {config['pads']} pads\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error occurred while listing intent graph files: {e}"

@tool
def visualize_io_ring_layout(il_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate visual diagram from SKILL layout file
    
    This tool creates a visual representation of the IO ring layout without requiring Virtuoso.
    It parses the SKILL code and generates a diagram with colored rectangles representing different device types.
    
    Args:
        il_file_path: Path to SKILL layout file (.il file)
        output_file_path: Optional path for output image (defaults to same directory as input with _visualization.png suffix)
        
    Returns:
        String description of visualization result, including file path
    """
    try:
        il_path = Path(il_file_path)
        if not il_path.exists():
            return f"❌ Error: Layout file {il_file_path} does not exist"
        
        if il_path.suffix.lower() != '.il':
            return f"❌ Error: File {il_file_path} is not a valid SKILL layout file (.il)"
        
        # Process output file path
        if output_file_path is None:
            output_path = il_path.parent / f"{il_path.stem}_visualization.png"
        else:
            output_path = Path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output_path.suffix.lower() != '.png':
                output_path = output_path.with_suffix('.png')
        
        # Try to detect process node from file content or use default
        # For now, try 180nm first, then fallback to 28nm
        process_node = "T28"  # Default
        try:
            with open(il_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for 180nm indicators
                if 'tpd018bcdnv5' in content or 'PAD70LU_TRL' in content:
                    process_node = "T180"
        except:
            pass
        
        # Generate visualization (use process-node-specific visualizer)
        try:
            if process_node == "T180":
                result_path = visualize_layout_T180(str(il_path), str(output_path))
            else:
                result_path = visualize_layout(str(il_path), str(output_path))
            return f"✅ Visualization generated successfully!\n📁 Output file: {result_path}\n\n" \
                   f"The visualization shows the IO ring layout with:\n" \
                   f"  - Colored rectangles representing different device types\n" \
                   f"  - Device names labeled in the center of each rectangle\n" \
                   f"  - Rectangles arranged in a ring formation"
        except Exception as e:
            return f"❌ Failed to generate visualization: {e}"
            
    except Exception as e:
        return f"❌ Error occurred while visualizing layout: {e}"

@tool
def visualize_io_ring_from_json(config_file_path: str, output_file_path: Optional[str] = None) -> str:
    """
    Generate visual diagram directly from JSON intent graph file (without generating SKILL file)
    
    This tool creates a visual representation of the IO ring layout directly from the JSON intent graph,
    without requiring an intermediate SKILL file. It's equivalent to generating layout and then visualizing,
    but more efficient when you only need the visualization.
    
    Args:
        config_file_path: Path to JSON intent graph file (can be relative or absolute path)
        output_file_path: Optional path for output image (defaults to same directory as config with _visualization.png suffix)
        
    Returns:
        String description of visualization result, including file path
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        if not config_path.exists():
            return f"❌ Error: Intent graph file {config_file_path} does not exist"
        
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
            return f"❌ Error: Failed to load intent graph file {e}"
        
        # Validate intent graph
        if not validate_config(config):
            return "❌ Error: Intent graph validation failed"
        
        # Get instances and ring_config
        instances = config.get("instances", [])
        ring_config = config.get("ring_config", {})
        
        # Get process node from ring_config or default to 28nm
        process_node = ring_config.get("process_node", "T28")
        
        # Merge top-level library_name and cell_name into ring_config if they exist
        if "library_name" in config and "library_name" not in ring_config:
            ring_config["library_name"] = config["library_name"]
        if "cell_name" in config and "cell_name" not in ring_config:
            ring_config["cell_name"] = config["cell_name"]
        
        # Initialize layout generator using factory
        generator = create_layout_generator(process_node)
        generator.set_config(ring_config)
        
        # Set defaults if not provided
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
        
        # Convert relative positions to absolute positions
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
        
        # Check if filler components are already present
        all_instances = instances
        existing_fillers = [comp for comp in all_instances if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device", ""))]
        existing_separators = [comp for comp in all_instances if comp.get("type") == "separator" or DeviceClassifier.is_separator_device(comp.get("device", ""))]
        
        if existing_fillers or existing_separators:
            # Use existing fillers from JSON
            validation_components = outer_pads + corners
            all_components_with_fillers = validation_components
            # Add existing fillers and separators
            for comp in all_instances:
                if comp.get("type") == "filler" or DeviceClassifier.is_filler_device(comp.get("device", "")):
                    all_components_with_fillers.append(comp)
                elif comp.get("type") == "separator" or DeviceClassifier.is_separator_device(comp.get("device", "")):
                    all_components_with_fillers.append(comp)
        else:
            # Auto-generate fillers
            validation_components = outer_pads + corners
            all_components_with_fillers = generator.auto_filler_generator.auto_insert_fillers_with_inner_pads(validation_components, inner_pads)
        
        # Add inner pads to components list
        all_components_with_fillers.extend(inner_pads)
        
        # Process output file path
        if output_file_path is None:
            output_path = config_path.parent / f"{config_path.stem}_visualization.png"
        else:
            output_path = Path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output_path.suffix.lower() != '.png':
                output_path = output_path.with_suffix('.png')
        
        # Generate visualization directly from components
        try:
            result_path = visualize_layout_from_components(all_components_with_fillers, str(output_path))
            return f"✅ Visualization generated successfully from JSON!\n📁 Output file: {result_path}\n\n" \
                   f"The visualization shows the IO ring layout with:\n" \
                   f"  - Colored rectangles representing different device types\n" \
                   f"  - Device names labeled in the center of each rectangle\n" \
                   f"  - Rectangles arranged in a ring formation"
        except Exception as e:
            return f"❌ Failed to generate visualization: {e}"
            
    except Exception as e:
        return f"❌ Error occurred while visualizing layout from JSON: {e}"

@tool
def validate_intent_graph(config_file_path: str) -> str:
    """
    Validate the format and content of intent graph file
    
    Args:
        config_file_path: Path to JSON intent graph file
        
    Returns:
        String description of validation result
    """
    try:
        # Check if intent graph file exists
        config_path = Path(config_file_path)
        
        # Load intent graph
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return f"❌ JSON format error: {e}"
        except Exception as e:
            return f"❌ Failed to load intent graph file: {e}"
        
        # Validate intent graph
        if not validate_config(config):
            return "❌ Intent graph validation failed"
        
        # Get intent graph statistics
        stats = get_config_statistics(config)
        
        result = f"✅ Intent graph file validation passed!\n"
        result += f"📊 Intent graph statistics:\n"
        result += f"  - IO ring scale: {stats['ring_size']}\n"
        result += f"  - Total pad count: {stats['total_pads']}\n"
        result += f"  - Device types: {stats['device_types']}\n"
        if stats['digital_ios'] > 0:
            result += f"  - Digital IOs: {stats['digital_ios']} ({stats['input_ios']} inputs, {stats['output_ios']} outputs)\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error occurred while validating intent graph file: {e}" 