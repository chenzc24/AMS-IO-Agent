import argparse
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Global variable to store auto-discovered models from .env
_ENV_MODELS = {}

def _auto_discover_models_from_env():
    """Auto-discover models from environment variables.

    Looks for environment variable patterns:
        MODELNAME_API_BASE=...
        MODELNAME_MODEL_ID=...
        MODELNAME_API_KEY=...

    And automatically creates model configurations.

    Example:
        CLAUDE_API_BASE=https://api.laozhang.ai/v1
        CLAUDE_MODEL_ID=claude-sonnet-4
        CLAUDE_API_KEY=sk-xxx

        Creates model named "claude" with those settings.
    """
    global _ENV_MODELS

    # Find all model prefixes (e.g., CLAUDE, GPT4O, WANDOU)
    model_prefixes = set()
    for key in os.environ.keys():
        if key.endswith('_API_BASE') or key.endswith('_MODEL_ID') or key.endswith('_API_KEY'):
            # Extract prefix (e.g., "CLAUDE" from "CLAUDE_API_BASE")
            if key.endswith('_API_BASE'):
                prefix = key[:-9]  # Remove "_API_BASE"
            elif key.endswith('_MODEL_ID'):
                prefix = key[:-9]  # Remove "_MODEL_ID"
            elif key.endswith('_API_KEY'):
                prefix = key[:-8]  # Remove "_API_KEY"
            model_prefixes.add(prefix)

    # Create model configs for each complete set
    for prefix in model_prefixes:
        api_base = os.getenv(f"{prefix}_API_BASE")
        model_id = os.getenv(f"{prefix}_MODEL_ID")
        api_key = os.getenv(f"{prefix}_API_KEY")

        # Only create config if all 3 variables are present
        if api_base and model_id and api_key:
            # Convert to lowercase with hyphens (e.g., "GPT4O" -> "gpt-4o")
            model_name = prefix.lower().replace('_', '-')

            # Special case handling for common patterns
            if model_name == "gpt4o":
                model_name = "gpt-4o"
            elif model_name == "gpt4":
                model_name = "gpt-4"
            elif model_name == "claude4":
                model_name = "claude-4"

            _ENV_MODELS[model_name] = {
                "model_type": "OpenAIServerModel",
                "model_id": model_id,
                "api_base": api_base,
                "api_key": api_key
            }

# Auto-discover models on module load
_auto_discover_models_from_env()

def get_model_config(name):
    """Get model configuration.

    Search Priority:
    1. Exact match by model name (from env prefix, e.g., "qwen" from QWEN_*)
    2. Match by MODEL_ID value (e.g., "qwen3-vl-plus" matches QWEN_MODEL_ID=qwen3-vl-plus)

    This allows users to use either:
        - model.active: "qwen"           (prefix-based name)
        - model.active: "qwen3-vl-plus"  (exact MODEL_ID)
    """
    # 1. Check exact model name match (from prefix)
    if name in _ENV_MODELS:
        return _ENV_MODELS[name]

    # 2. Search by MODEL_ID value
    for model_name, config in _ENV_MODELS.items():
        if config.get('model_id') == name:
            return config

    # No match found - provide helpful error
    available = list(_ENV_MODELS.keys())
    model_ids = [config.get('model_id', '') for config in _ENV_MODELS.values()]

    raise ValueError(
        f"Unknown model configuration: {name}\n"
        f"Available model names: {', '.join(sorted(available)) if available else 'none'}\n"
        f"Available model IDs: {', '.join(sorted(model_ids)) if model_ids else 'none'}\n\n"
        f"To add a model, add these to your .env file:\n"
        f"  {name.upper().replace('-', '')}_API_BASE=https://api.example.com/v1\n"
        f"  {name.upper().replace('-', '')}_MODEL_ID=model-name\n"
        f"  {name.upper().replace('-', '')}_API_KEY=your_api_key"
    )

def list_model_names():
    """List all available model names from .env"""
    return sorted(list(_ENV_MODELS.keys()))

def list_model_ids():
    """List all available MODEL_IDs from .env"""
    return sorted([config.get('model_id', '') for config in _ENV_MODELS.values() if config.get('model_id')])

def list_all_models():
    """List all models with both names and IDs.

    Returns dict: {model_name: model_id}
    """
    return {name: config.get('model_id', '') for name, config in _ENV_MODELS.items()}

def load_instructions_from_file(filepath: str) -> str:
    """Load instructions from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Info: Instruction file {filepath} not found, will use default instructions.")
        return ""
    except Exception as e:
        print(f"Error reading instruction file: {e}, will use default instructions.")
        return ""

def load_config_from_yaml(config_path: str = "config.yaml"):
    """Load configuration from YAML file.

    Args:
        config_path: Path to config YAML file (default: config.yaml in project root)

    Returns:
        Dict containing configuration settings
    """
    try:
        # Get project root (assuming this file is in src/app/utils)
        project_root = Path(__file__).parent.parent.parent.parent
        config_file = project_root / config_path

        if not config_file.exists():
            print(f"Warning: Config file {config_file} not found, using defaults")
            return {}

        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Replace environment variable placeholders
        config = _replace_env_vars(config)

        # Models are now auto-discovered from .env, no need to load from YAML

        return config
    except Exception as e:
        print(f"Error loading config file: {e}, using defaults")
        return {}

def _replace_env_vars(config):
    """Recursively replace ${VAR_NAME} with environment variable values."""
    if isinstance(config, dict):
        return {k: _replace_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_replace_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        var_name = config[2:-1]
        return os.getenv(var_name, config)
    return config

class Config:
    """Configuration object with attribute access."""
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

    def get(self, key, default=None):
        """Get attribute with default value."""
        return getattr(self, key, default)

    def __repr__(self):
        return f"Config({self.__dict__})"

def parse_arguments():
    """Parse command line arguments (LEGACY - no longer used, kept for backward compatibility)

    This function is deprecated. The system now uses config.yaml for all configuration.
    """
    parser = argparse.ArgumentParser(description="Run AI Assistant Agent")
    parser.add_argument(
        "--model-name",
        type=str,
        help="Select model by configuration name (priority higher than individual parameters)"
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="OpenAIServerModel",
        help="Model type to use (e.g., OpenAIServerModel, LiteLLMModel, TransformersModel)"
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default="deepseek-chat",
        help="Model ID for the specified model type"
    )
    parser.add_argument(
        "--api-base",
        type=str,
        default="https://api.deepseek.com/v1",
        help="API base URL for the model"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("DEEPSEEK_API_KEY"),
        help="API key for the model"
    )
    parser.add_argument('--webui', action='store_true', help='Launch web UI interface')
    parser.add_argument('--log', action='store_true', help='Enable command line logging functionality')
    parser.add_argument('--temperature', type=float, default=1.0, help='Model output temperature parameter, controls diversity, range 0~2, default 0.7')
    parser.add_argument('--show-code', action='store_true', help='Show "Executing parsed code" blocks (default: hidden)')
    parser.add_argument(
        '--prompt',
        type=str,
        default=None,
        help='Select prompt from config file by key (e.g., --prompt key1). If not specified, use interactive input or user_prompt.txt'
    )
    parser.add_argument(
        '--prompt-text',
        type=str,
        default=None,
        help='Direct prompt text to use (takes precedence over --prompt). Useful for batch experiments.'
    )
    parser.add_argument(
        '--prompt-config',
        type=str,
        default='user_prompt',
        help='Path to directory containing YAML/JSON prompt files. If a file path is provided, its parent directory will be used. All YAML/JSON files in the directory will be searched (default: user_prompt)'
    )
    parser.add_argument(
        '--ramic-host',
        type=str,
        default=None,
        help='RAMIC bridge host (overrides RB_HOST env var)'
    )
    parser.add_argument(
        '--ramic-port',
        type=int,
        default=None,
        help='RAMIC bridge port (overrides RB_PORT env var)'
    )
    return parser.parse_args() 

# =============================================================================
# Test/Debug: Run this file directly to check model discovery
# =============================================================================
if __name__ == "__main__":
    print("="*80)
    print("MODEL DISCOVERY TEST")
    print("="*80)
    print()

    # Show discovered models in a table format
    all_models = list_all_models()

    if not all_models:
        print("No models found!")
        print()
        print("Make sure your .env file has model configurations like:")
        print()
        print("  MODELNAME_API_BASE=https://api.example.com/v1")
        print("  MODELNAME_MODEL_ID=model-name")
        print("  MODELNAME_API_KEY=your_api_key")
        print()
    else:
        print(f"Found {len(all_models)} model(s):")
        print()
        print(f"  {'Model Name':<15} {'MODEL_ID':<30} {'API Base'}")
        print(f"  {'-'*15} {'-'*30} {'-'*40}")

        for model_name in sorted(all_models.keys()):
            config = get_model_config(model_name)
            model_id = config['model_id']
            api_base = config['api_base']
            # Truncate API base if too long
            if len(api_base) > 40:
                api_base = api_base[:37] + "..."
            print(f"  {model_name:<15} {model_id:<30} {api_base}")

        print()
        print("="*80)
        print()
        print("You can use EITHER model name OR MODEL_ID in config.yaml:")
        print()

        # Show examples
        for model_name in sorted(all_models.keys())[:3]:
            model_id = all_models[model_name]
            print(f"  model.active: \"{model_name}\"")
            print(f"  model.active: \"{model_id}\"   # Also works!")
            print()

    print("="*80)
    print()

    # Test search functionality
    print("Testing model search (by name AND by MODEL_ID):")
    print("-"*80)

    # Get all model IDs for testing
    test_cases = []
    for name in sorted(all_models.keys())[:2]:  # First 2 models
        test_cases.append(name)  # Test by name
        test_cases.append(all_models[name])  # Test by MODEL_ID

    for test_model in test_cases:
        try:
            config = get_model_config(test_model)
            print(f"  [OK] '{test_model}' -> model_id: {config['model_id']}")
        except ValueError as e:
            print(f"  [FAIL] '{test_model}' not found")

    print()
    print("="*80)
