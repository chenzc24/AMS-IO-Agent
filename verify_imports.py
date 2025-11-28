#!/usr/bin/env python3
"""Quick script to verify all imports work correctly"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

print("Verifying imports...")
print("=" * 60)

try:
    print("[OK] Testing config_utils imports...")
    from src.app.utils.config_utils import load_config_from_yaml, get_model_config, Config

    print("[OK] Testing logging_utils imports...")
    from src.app.utils.logging_utils import setup_logging, finalize_logging

    print("[OK] Testing multi_agent_factory imports...")
    from src.app.utils.multi_agent_factory import create_master_agent_with_workers

    print("[OK] Testing agent_factory imports...")
    from src.app.utils.agent_factory import run_cli_interface, start_web_ui

    print("[OK] Testing agent_utils imports...")
    from src.app.utils.agent_utils import save_agent_memory

    print("[OK] Testing system_prompt_builder imports...")
    from src.app.utils.system_prompt_builder import load_system_prompt_with_profile

    print("[OK] Testing io_ring_generator_tool imports...")
    from src.tools.io_ring_generator_tool import generate_io_ring_schematic

    print("[OK] Testing user_profile_tool imports...")
    from src.tools.user_profile_tool import get_profile_path

    print("[OK] Testing cdac_agent imports...")
    from src.app.cdac.cdac_agent import ObserveExcelTool

    print("=" * 60)
    print("SUCCESS: All imports successful!")
    print("=" * 60)

except ModuleNotFoundError as e:
    print(f"ERROR: Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Unexpected Error: {e}")
    sys.exit(1)
