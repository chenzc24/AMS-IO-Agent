#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Main - Entry point for master-worker agent system
Uses config.yaml for all configuration (no command-line arguments needed)
"""

from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.app.utils.config_utils import load_config_from_yaml, get_model_config, Config, list_model_names
from src.app.utils.logging_utils import setup_logging, finalize_logging
from src.app.utils.multi_agent_factory import create_master_agent_with_workers
from src.app.utils.agent_factory import run_cli_interface, start_web_ui
from src.app.utils.agent_utils import save_agent_memory
from src.app.utils.system_prompt_builder import load_system_prompt_with_profile


def main():
    """Main entry point for multi-agent system"""

    # Load configuration from YAML file
    print("\n" + "="*80)
    print("📝 Loading configuration from config.yaml...")
    print("="*80)

    config_dict = load_config_from_yaml("config.yaml")
    config = Config(config_dict)

    # Display loaded configuration
    model_name = None
    if hasattr(config, 'model'):
        # Support both 'active' (new) and 'name' (old) for backward compatibility
        model_name = getattr(config.model, 'active', getattr(config.model, 'name', 'claude'))
    else:
        model_name = 'claude'

    # Get list of available models
    available_models = list_model_names()

    print(f"\n✅ Configuration loaded:")
    print(f"   Model: {model_name}")
    print(f"   Available models: {', '.join(available_models)}")
    print(f"   Interface: {config.interface.mode if hasattr(config, 'interface') else 'cli'}")
    print(f"   Multi-Agent: {config.system.multi_agent if hasattr(config, 'system') else True}")

    # Set RAMIC bridge host/port from config if provided
    if hasattr(config, 'ramic_bridge'):
        if config.ramic_bridge.host:
            os.environ["RB_HOST"] = config.ramic_bridge.host
        if config.ramic_bridge.port:
            os.environ["RB_PORT"] = str(config.ramic_bridge.port)

    # Setup logging
    class Args:
        """Mock args object for compatibility with existing logging_utils"""
        def __init__(self, cfg):
            self.log = cfg.interface.logging if hasattr(cfg, 'interface') else True
            self.show_code = cfg.interface.show_code if hasattr(cfg, 'interface') else False

    args = Args(config)
    log_file, start_time = setup_logging(args)

    # Get model configuration
    model_config = get_model_config(model_name)

    # Update temperature if specified in config
    if hasattr(config, 'model') and hasattr(config.model, 'temperature'):
        model_config['temperature'] = config.model.temperature

    # Load system prompt with user profile
    system_prompt = load_system_prompt_with_profile()

    # Create master agent with IO tools
    print("\n" + "="*80)
    print("🤖 Initializing IO Agent System")
    print("="*80)
    print("\n📦 Loading agent with IO tools...")

    tools_config_path = config.tools.config_path if hasattr(config, 'tools') else "config/tools_config.yaml"
    master_agent = create_master_agent_with_workers(
        model_config,
        tools_config_path=tools_config_path
    )

    print("\n✅ IO Agent system ready!")
    print("\n💡 Available capabilities:")
    print("   - IO Ring generation and layout")
    print("   - EDA tools (Virtuoso, DRC, LVS, PEX, etc.)")
    print("   - Knowledge base & tool management")
    print("\n" + "="*80)

    # Inject master agent system prompt (append to existing)
    master_agent.instructions = f"{system_prompt}\n\n{master_agent.instructions}"

    # Check interface mode from config
    interface_mode = config.interface.mode if hasattr(config, 'interface') else "cli"

    if interface_mode == "webui":
        # Start web UI (doesn't return, blocks until UI is closed)
        print("\n🌐 Starting Web UI...")
        start_web_ui(master_agent)
    else:
        # Run CLI interface
        print("\n💬 Starting CLI interface...")

        # Get prompt configuration
        # Priority: 1. Environment variable PROMPT_TEXT, 2. Config file
        prompt_text = os.environ.get('PROMPT_TEXT')
        if not prompt_text:
            prompt_key = config.prompt.key if hasattr(config, 'prompt') else None
            prompt_text = config.prompt.text if hasattr(config, 'prompt') else None
        else:
            prompt_key = None  # Don't use prompt_key if PROMPT_TEXT is set
        prompt_config = config.prompt.config_path if hasattr(config, 'prompt') else 'user_prompt'

        first_user_input, interrupted = run_cli_interface(
            master_agent,
            prompt_key=prompt_key,
            prompt_text=prompt_text,
            prompt_config_file=prompt_config
        )

        # Save memory
        config_info = {
            "model_name": model_config.get("model_id"),
            "first_user_input": first_user_input,
            "agent_type": "io_agent"
        }
        save_agent_memory(master_agent, config_info=config_info)
        master_agent.memory.reset()

        # Finalize logging
        finalize_logging(log_file, start_time, interrupted)


if __name__ == "__main__":
    main()
