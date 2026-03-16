# AMS-IO-Agent

An AI-powered integrated circuit (IC) design automation agent specialized for Cadence Virtuoso EDA environments. This system automates IO ring generation and verification workflows using LLM-driven intelligent agents.

## Overview

AMS-IO-Agent leverages large language models to automate complex analog and mixed-signal IC design tasks, specifically focusing on IO ring design. It combines domain knowledge bases, specialized tools, and intelligent agent architectures to generate schematic and layout designs for IO rings while ensuring design rule compliance.

## Key Features

- **Automated IO Ring Generation** - Generate IO pad ring schematics and layouts automatically based on requirements
- **Verification Automation** - Integrated DRC, LVS, and PEX verification workflows
- **Multi-Model Support** - Compatible with Claude, GPT-4, DeepSeek, and other OpenAI-compatible APIs
- **Knowledge-Driven Design** - Structured knowledge bases for technology nodes and IO design
- **Web UI** - Optional Gradio-based web interface for interactive use
- **Benchmark Suite** - Comprehensive test cases in AMS-IO-Bench for validation
- **Image Vision Analysis** - Analyze screenshots, layouts, and schematics using vision models
- **User Profile Management** - Customizable user profiles for personalized design preferences
- **Tool Statistics & Analytics** - Track tool usage and performance metrics
- **Task History & Query** - Query and analyze past task executions
- **Health Check System** - Automated system diagnostics and verification

## Quick Start

### Prerequisites

- Python 3.8 or higher
- `csh` (C Shell) - usually pre-installed on Linux/macOS
- Cadence Virtuoso (for actual design execution)
- API key for supported LLM providers (Claude, OpenAI, DeepSeek, etc.)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AMS-IO-Agent.git
   cd AMS-IO-Agent
   ```

2. **Run the quick setup script (Recommended):**
   
   **For Linux/macOS (csh):**
   ```csh
   ./quick_start.csh
   ```
   
   **For Windows (PowerShell - Recommended):**
   ```powershell
   .\quick_start.ps1
   ```
   
   **For Windows (CMD):**
   ```cmd
   quick_start.bat
   ```
   
   This one-command script will:
   - ✅ Automatically fix executable permissions (Linux/macOS)
   - ✅ Create Python virtual environment
   - ✅ Install all dependencies
   - ✅ Generate configuration files
   - ✅ Set up Virtuoso integration

   The setup script will:
   - Create a Python virtual environment using `uv`
   - Install all dependencies from `requirements.txt`
   - Generate a `.env` configuration file template
   - Set up Virtuoso integration files

3. **Configure environment variables:**

   Edit `.env` with your API keys:
   ```env
   # Choose your preferred LLM provider
   CLAUDE_API_BASE=https://api.anthropic.com/v1
   CLAUDE_MODEL_ID=claude-sonnet-4-20250514
   CLAUDE_API_KEY=your_api_key_here

   # Or use OpenAI
   GPT4_API_BASE=https://api.openai.com/v1
   GPT4_MODEL_ID=gpt-4-turbo
   GPT4_API_KEY=your_openai_key_here

   # Virtuoso bridge configuration (optional)
   RB_HOST=localhost
   RB_PORT=9123
   ```

4. **Configure the agent:**

   Edit `config.yaml` to set your preferences:
   ```yaml
   model:
     active: "claude"  # or "gpt4", "deepseek", etc.
     temperature: 1.0

   interface:
     mode: "cli"  # or "webui" for web interface
     logging: true
   ```

### Basic Usage

**Run the agent in CLI mode:**
```bash
python main.py
```

**Run with web interface:**
```bash
# Edit config.yaml and set interface.mode: "webui"
python main.py
```

**Auto-load a benchmark prompt:**
```bash
# Edit config.yaml:
# prompt:
#   key: "IO_28nm_3x3_single_ring_digital"
python main.py
```

## Project Structure

```
AMS-IO-Agent/
├── main.py                           # Main entry point
├── api_server.py                     # FastAPI server entry point
├── config.yaml                       # Main configuration file
├── requirements.txt                  # Python dependencies
├── README.md
│
├── src/                              # Core source code
│   ├── app/
│   │   ├── intent_graph/             # Intent graph generation and validation
│   │   ├── layout/                   # IO ring layout generation
│   │   ├── schematic/                # IO ring schematic generation
│   │   └── utils/                    # App-level shared utilities
│   ├── tools/                        # Agent tools and tool config
│   │   ├── tools_config.yaml
│   │   └── python_helpers/
│   ├── scripts/                      # EDA bridge and verification scripts
│   │   ├── ramic_bridge/
│   │   ├── calibre/
│   │   └── devices/
│   ├── skill/                        # Reusable Virtuoso SKILL snippets
│   └── agent_generated/              # Agent-generated Python helpers
│
├── Knowledge_Base/                   # Structured design knowledge base
│   ├── 00_META/
│   ├── 01_CORE/
│   ├── 02_TECHNOLOGY/
│   ├── 03_DESIGN_BLOCKS/
│   └── 04_ERRORS/
│
├── AMS-IO-Bench/                     # Benchmark prompts and scenarios
│   ├── 28nm_wirebonding/
│   └── 180nm_wirebonding/
│
├── tests/                            # Unit/integration and flow tests
│   ├── run_IO_Ring_batch.py
│   ├── test_io_ring_tool.py
│   ├── test_drc_runner_tool.py
│   ├── test_lvs_runner_tool.py
│   ├── test_pex_runner_tool.py
│   └── ...
│
├── setup/                            # Cross-platform setup scripts
├── docs/                             # Additional technical docs
├── user_data/                        # User profiles and per-user artifacts
├── output/                           # Generated design artifacts
├── logs/                             # Runtime logs
└── uploads/                          # Uploaded files for API/Web flows
```

## Core Components

### Entry Point

- **`main.py`** - Agent system entry point with IO ring design capabilities

### Agent Tools

| Tool | Purpose |
|------|---------|
| `il_runner_tool.py` | Execute SKILL files in Cadence Virtuoso |
| `drc_runner_tool.py` | Run Design Rule Check verification |
| `lvs_runner_tool.py` | Run Layout vs Schematic verification |
| `pex_runner_tool.py` | Run parasitic extraction |
| `io_ring_generator_tool.py` | Generate IO ring schematics and layouts |
| `knowledge_loader_tool.py` | Dynamically load knowledge from markdown files |
| `skill_tools_manager.py` | Manage and execute reusable SKILL utilities |
| `bridge_utils.py` | Virtuoso communication (RAMIC/skillbridge) |
| `image_vision_tool.py` | Analyze images (screenshots, layouts, schematics) |
| `user_profile_tool.py` | Manage user profile and preferences |
| `health_check_tool.py` | System health diagnostics and verification |
| `task_query_tool.py` | Query and analyze task history |
| `tool_stats_tool.py` | Track and analyze tool usage statistics |
| `python_tool_creator.py` | Create and manage Python helper tools |

### Layout Generation (`src/app/layout/`)

| Module | Purpose |
|--------|---------|
| `layout_generator.py` | Main layout generation orchestrator |
| `position_calculator.py` | Calculate pad positions for IO rings |
| `voltage_domain.py` | Handle voltage domain logic |
| `skill_generator.py` | Generate SKILL code for layouts |
| `auto_filler.py` | Automatic filler cell generation |

### Schematic Generation (`src/app/schematic/`)

| Module | Purpose |
|--------|---------|
| `schematic_generator.py` | Generate SKILL code for schematics |
| `json_validator.py` | Validate intent graph files |

## Workflows

### IO Ring Generation Workflow

1. Generate JSON configuration from natural language requirements
2. Validate configuration against templates
3. Generate schematic SKILL code
4. Generate layout SKILL code
5. Execute in Virtuoso via bridge
6. Run DRC/LVS verification
7. Iterate if errors detected

## Knowledge Bases

The system uses a unified Knowledge_Base folder with specialized modules:

### 01_CORE - Core Design Knowledge
- Universal design principles
- Python-SKILL integration patterns

### 02_TECHNOLOGY - Technology-Specific Parameters
- 28nm process parameters
- 180nm process parameters
- Technology-specific design rules

### 03_DESIGN_BLOCKS - Design-Specific Knowledge
- **IO_RING**: IO pad selection, corner devices, voltage domains

### 04_ERRORS
- Common error documentation
- Error patterns and solutions learned during development
- Verification errors and troubleshooting

## Technologies

| Technology | Usage |
|------------|-------|
| **Python 3.x** | Main programming language |
| **smolagents** | AI agent framework from Hugging Face |
| **OpenAI-compatible APIs** | LLM backend (Claude, GPT-4, DeepSeek) |
| **Cadence Virtuoso** | Target EDA environment |
| **SKILL** | Virtuoso scripting language |
| **Gradio** | Optional web UI interface |

### Virtuoso Bridge Options

- **RAMIC Bridge** (Recommended) - Socket-based communication, supports cross-server connections
- **skillbridge** - Direct Python-Virtuoso integration via IPC

## Supported Models

The system supports any OpenAI-compatible API. Pre-configured models include:

- Claude Sonnet 4 (via Anthropic or proxies)
- GPT-4 / GPT-4o (via OpenAI or proxies)
- DeepSeek Chat v3 (via OpenRouter)
- Custom models (add to `.env`)

To add a new model, simply add three environment variables to `.env`:
```env
MYMODEL_API_BASE=https://api.provider.com/v1
MYMODEL_MODEL_ID=model-name
MYMODEL_API_KEY=your_key_here
```

Then use it in `config.yaml`:
```yaml
model:
  active: "mymodel"
```

## Batch Experiments

### IO Ring Experiments

Run batch IO ring experiments:

```bash
python tests/run_IO_Ring_batch.py
```

Features:
- Test cases from 3x3 to 18x18 pad configurations
- Single and double ring topologies
- Digital, analog, and mixed-signal designs
- Multi-voltage domain support

## Testing

Run individual tests from the project root:

```bash
# Quick flow test
python tests/test_quick_flow.py

# IO ring tool test
python tests/test_io_ring_tool.py

# Verification tests
python tests/test_drc_runner_tool.py
python tests/test_lvs_runner_tool.py
python tests/test_pex_runner_tool.py

# System and utility tests
python tests/test_health_check.py
python tests/test_image_vision_tool.py
python tests/test_user_profile.py
python tests/test_python_helper.py
```

## Configuration

### Main Configuration (`config.yaml`)

All non-sensitive configuration is in `config.yaml`:

```yaml
model:
  active: "claude"      # Model to use
  temperature: 1.0      # Creativity level (0.0-2.0)

interface:
  mode: "cli"           # "cli" or "webui"
  logging: true         # Save conversation logs
  show_code: false      # Show code execution details

prompt:
  key: null             # Auto-load benchmark (e.g., "IO_28nm_3x3_single_ring_digital")
  text: null            # Or provide direct prompt text
  config_path: "user_prompt"  # Directory for custom prompts

ramic_bridge:
  host: null            # RAMIC server host (null = use RB_HOST env var)
  port: null            # RAMIC server port (null = use RB_PORT env var)
```

### Environment Variables (`.env`)

All sensitive data and API keys go in `.env`:

```env
# Model API Keys
CLAUDE_API_KEY=your_key
GPT4_API_KEY=your_key
DEEPSEEK_API_KEY=your_key

# Model Endpoints
CLAUDE_API_BASE=https://api.anthropic.com/v1
CLAUDE_MODEL_ID=claude-sonnet-4-20250514

# Virtuoso Bridge
RB_HOST=localhost
RB_PORT=9123

# User Profile
USER_PROFILE_PATH=user_data/default_user_profile.md
```

## Architecture

### Agent System

The system uses a specialized agent architecture focused on IO ring design:

- **IO Agent**: Coordinates IO ring generation, verification, and knowledge management
- **Tool Suite**: Comprehensive EDA tools for Virtuoso integration and verification

Benefits:
- Focused expertise on IO ring design
- Streamlined workflow for pad ring generation
- Direct access to all necessary EDA tools

### Tool Loading

Tools are configured via `src/tools/tools_config.yaml` and loaded dynamically based on the use case. This allows flexible tool composition for different agent types.

### Dynamic Knowledge Loading

Knowledge modules are loaded on-demand from markdown files in the knowledge bases, enabling:
- Efficient memory usage
- Targeted expertise injection
- Easy knowledge base updates without code changes

## Contributing

This project is under active development. Contributions are welcome in the following areas:

- Additional technology node support
- New IO pad types and configurations
- Improved error handling and recovery
- Documentation and examples
- Test coverage

## Troubleshooting

### Common Issues

**API Connection Errors:**
- Verify API keys in `.env`
- Check API base URLs
- Ensure network connectivity

**Virtuoso Bridge Issues:**
- Verify RAMIC bridge is running
- Check `RB_HOST` and `RB_PORT` settings
- Test with `tests/test_il_runner_ramicbridge.py`

**Tool Loading Errors:**
- Check `src/tools/tools_config.yaml` syntax
- Verify all tool files exist
- Review logs in `logs/` directory

**Knowledge Base Not Loading:**
- Verify Knowledge_Base directory structure
- Check markdown file syntax
- Review knowledge loader tool logs

## License

Proprietary - All rights reserved.

## Acknowledgments

- Built with [smolagents](https://github.com/huggingface/smolagents) from Hugging Face
- Uses [skillbridge](https://github.com/unihd-cag/skillbridge) for Virtuoso integration
- Powered by large language models from Anthropic, OpenAI, and DeepSeek

## Contact

For questions, issues, or collaboration inquiries, please open an issue on GitHub.

---

**Note:** This tool is designed for research and development purposes in IC design automation. Always verify generated designs meet your specific requirements and design rules before fabrication.
