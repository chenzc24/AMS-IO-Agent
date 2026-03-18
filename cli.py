#!/usr/bin/env python3
"""
Simple CLI for AMS-IO-Agent
Direct function calls, no agent orchestration
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.core.schematic.schematic_generator_T28 import generate_multi_device_schematic as gen_schematic_t28
from src.core.schematic.schematic_generator_T180 import generate_multi_device_schematic as gen_schematic_t180
from src.core.layout.layout_generator_factory import generate_layout_from_json
from src.core.intent_graph.json_validator import validate_config, convert_config_to_list


def print_banner():
    """Print CLI banner"""
    print("=" * 80)
    print("AMS-IO-Agent - Pure Claude Code Version")
    print("=" * 80)
    print("\nThis backend runs with direct script execution (no MCP server required).")


def print_help():
    """Print help message"""
    print_banner()
    print("\nAvailable Commands:")
    print()
    print("  Validation:")
    print("    python cli.py validate <json_path>")
    print("      Validate IO ring intent graph JSON file")
    print()
    print("  Schematic Generation:")
    print("    python cli.py schematic <json_path> <process_node>")
    print("      Generate schematic SKILL code")
    print("      process_node: T28 or T180")
    print()
    print("  Layout Generation:")
    print("    python cli.py layout <json_path> <process_node>")
    print("      Generate layout SKILL code")
    print("      process_node: T28 or T180")
    print()
    print("For full workflow, use the orchestrator scripts under:")
    print("  claude-code-skills/T28/io-ring-orchestrator-T28/scripts/")
    print("  claude-code-skills/T180/io-ring-orchestrator-T180/scripts/")
    print()
    print("=" * 80)


def cmd_validate(json_path: str):
    """Validate JSON file"""
    import json

    json_file = Path(json_path)
    if not json_file.exists():
        print(f"❌ Error: File not found: {json_path}")
        return 1

    try:
        with open(json_file, 'r') as f:
            config = json.load(f)

        # Validate config
        is_valid = validate_config(config)

        if is_valid:
            # Get statistics
            from src.core.intent_graph.json_validator import get_config_statistics
            stats = get_config_statistics(config)

            print(f"✅ Valid IO ring configuration!")
            print(f"\n📊 Configuration Statistics:")
            print(f"   Total instances: {stats.get('total_instances', 'N/A')}")
            print(f"   Total pads: {stats.get('total_pads', 'N/A')}")
            print(f"   Total corners: {stats.get('total_corners', 'N/A')}")
            print(f"   Analog pads: {stats.get('analog_count', 'N/A')}")
            print(f"   Digital pads: {stats.get('digital_count', 'N/A')}")
            print(f"   Process node: {stats.get('process_node', 'N/A')}")

            return 0
        else:
            print(f"❌ Invalid configuration")
            return 1

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_schematic(json_path: str, process_node: str):
    """Generate schematic SKILL code"""
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"❌ Error: File not found: {json_path}")
        return 1

    process_node = process_node.upper()
    if process_node not in ["T28", "T180"]:
        print(f"❌ Error: Unsupported process node: {process_node}")
        print(f"   Supported: T28, T180")
        return 1

    try:
        print(f"🔧 Generating schematic SKILL code...")
        print(f"   Input: {json_path}")
        print(f"   Process: {process_node}")

        if process_node == "T28":
            output_path = gen_schematic_t28(str(json_file))
        else:  # T180
            output_path = gen_schematic_t180(str(json_file))

        print(f"\n✅ Schematic SKILL generated successfully!")
        print(f"   Output: {output_path}")
        return 0

    except Exception as e:
        print(f"\n❌ Error generating schematic: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_layout(json_path: str, process_node: str):
    """Generate layout SKILL code"""
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"❌ Error: File not found: {json_path}")
        return 1

    process_node = process_node.upper()
    if process_node not in ["T28", "T180"]:
        print(f"❌ Error: Unsupported process node: {process_node}")
        print(f"   Supported: T28, T180")
        return 1

    try:
        print(f"🔧 Generating layout SKILL code...")
        print(f"   Input: {json_path}")
        print(f"   Process: {process_node}")

        output_path = generate_layout_from_json(
            json_path=str(json_file),
            process_node=process_node
        )

        print(f"\n✅ Layout SKILL generated successfully!")
        print(f"   Output: {output_path}")
        return 0

    except Exception as e:
        print(f"\n❌ Error generating layout: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_help()
        return 0

    command = sys.argv[1].lower()

    if command in ["help", "-h", "--help"]:
        print_help()
        return 0

    elif command == "validate":
        if len(sys.argv) < 3:
            print("❌ Usage: python cli.py validate <json_path>")
            return 1
        return cmd_validate(sys.argv[2])

    elif command == "schematic":
        if len(sys.argv) < 4:
            print("❌ Usage: python cli.py schematic <json_path> <process_node>")
            print("   process_node: T28 or T180")
            return 1
        return cmd_schematic(sys.argv[2], sys.argv[3])

    elif command == "layout":
        if len(sys.argv) < 4:
            print("❌ Usage: python cli.py layout <json_path> <process_node>")
            print("   process_node: T28 or T180")
            return 1
        return cmd_layout(sys.argv[2], sys.argv[3])

    else:
        print(f"❌ Unknown command: {command}")
        print()
        print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
