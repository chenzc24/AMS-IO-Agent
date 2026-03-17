# AMS-IO-Agent - Pure Claude Code Version

IC Design automation for IO Ring generation (T28/T180 process nodes).

## Architecture

```
AMS-IO-Agent/
├── cli.py                    # Simple CLI (optional, for testing)
├── requirements.txt          # Pure Python dependencies (no smolagents)
└── src/
    ├── core/                 # Core generation logic
    │   ├── schematic/        # Schematic generators (T28/T180)
    │   ├── layout/           # Layout generators (T28/T180)
    │   └── intent_graph/     # JSON validation
    ├── utils/                # Utilities
    ├── scripts/              # Device parsers, RAMIC bridge
    └── _archived/            # Deprecated smolagents code
```

## Usage

### Option 1: Claude Code (Recommended)

MCP server provides tools directly to Claude Code:

```bash
cd /path/to/mcp_server
python server.py
```

Then in Claude Code:
```
Generate a 12x12 IO ring for T28 with [signals...]
```

**Available MCP Tools (16 total):**
- Core generation: `validate_intent_graph`, `build_io_ring_confirmed_config`, `generate_io_ring_schematic`, `generate_io_ring_layout`
- Execution: `run_il_with_screenshot`, `check_virtuoso_connection`
- Verification: `run_drc`, `run_lvs`, `run_pex`
- Image vision: `analyze_image`, `analyze_image_base64`
- SKILL manager: `list_skill_tools`, `run_skill_tool`, `create_skill_tool`
- System health: `system_health_check`, `quick_diagnostic`

### Option 2: Direct CLI (Testing)

```bash
# Validate JSON
python cli.py validate path/to/config.json

# Generate schematic
python cli.py schematic path/to/config.json T28

# Generate layout
python cli.py layout path/to/config.json T28

# Show help
python cli.py help
```

## Migration from Smolagents

All smolagents code has been archived to `src/_archived/smolagents_2026_03_17/`.

See migration details: `src/_archived/smolagents_2026_03_17/README.md`

**Key Changes:**
- ❌ No more smolagents dependency
- ❌ No more @tool decorators
- ❌ No more CodeAgent orchestration
- ✅ Pure Python core logic
- ✅ MCP tools for Claude Code
- ✅ Simple CLI for direct calls

## Installation

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.9+
- skillbridge (for Virtuoso integration)
- Other standard dependencies (no smolagents)

## Development

**Directory Structure:**
- `src/core/` - Pure generation logic (no external dependencies)
- `src/utils/` - Standalone utility functions
- `src/scripts/` - Device parsers, RAMIC bridge
- `mcp_server/` - MCP tools for Claude Code (in parent directory)

**Import Pattern:**
```python
from src.core.schematic import generate_T28, generate_T180
from src.core.layout import generate_layout_from_json
from src.core.intent_graph import validate_config
```

## Rollback

If needed, restore from git:
```bash
git checkout smolagents-complete-removal~1
```

Or from archive:
```bash
cd src
cp _archived/smolagents_2026_03_17/tools/* tools/
```
