# How to Configure Models in AMS-IO-Agent

All model configurations are now in the `.env` file for better security and easier management!

## Quick Start: Using a Pre-configured Model

### Step 1: Check Your `.env` File

Your `.env` file already has all the pre-configured models. Just make sure you have the correct API keys:

```bash
# Main API keys (update these with your actual keys)
ZHANG_API_KEY=your_zhang_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
WANDOU_API_KEY=sk-foFjMhriqthtEOBDT7AILJIj14YHtgysFDFg3oQUqJGiB00f
```

### Step 2: Select Your Model in `config.yaml`

Just change the `active` field:

```yaml
model:
  active: "wandou"  # Choose: claude, gpt-4o, gpt-4, claude-4, deepseek, wandou
  temperature: 1.0
```

### Step 3: Run

```powershell
python main.py
```

That's it! No need to edit model configurations.

## Adding a Custom Model

### Example: Adding a New Model via Custom API

**Step 1: Add to `.env`**

Add your model configuration to the `.env` file:

```bash
# =============================================================================
# MY CUSTOM MODEL CONFIGURATION
# =============================================================================
MYCUSTOM_API_BASE=https://api.myservice.com/v1
MYCUSTOM_MODEL_ID=gpt-4-turbo
MYCUSTOM_API_KEY=sk-xxxxxxxxxxxxxxx
```

**Step 2: Add to `config.yaml`**

Add your model under the `models:` section:

```yaml
models:
  # ... existing models ...

  # My Custom Model
  my-custom:
    type: "OpenAIServerModel"
    id: "${MYCUSTOM_MODEL_ID}"
    api_base: "${MYCUSTOM_API_BASE}"
    api_key: "${MYCUSTOM_API_KEY}"
```

**Step 3: Activate It**

```yaml
model:
  active: "my-custom"
  temperature: 1.0
```

## Pre-configured Models

All these models are ready to use - just set `model.active` in `config.yaml`:

| Model Name | Provider | Model ID | Configured in .env |
|------------|----------|----------|-------------------|
| `claude` | laozhang.ai | claude-sonnet-4-20250514 | ✅ |
| `gpt-4o` | laozhang.ai | gpt-4o | ✅ |
| `gpt-4` | laozhang.ai | gpt-4.1 | ✅ |
| `claude-4` | OpenRouter | anthropic/claude-sonnet-4 | ✅ |
| `deepseek` | OpenRouter | deepseek-chat-v3 | ✅ |
| `wandou` | XHub | gpt-4 | ✅ |

## Environment Variable Reference

Each model needs 3 environment variables:

```bash
MODELNAME_API_BASE=https://api.provider.com/v1
MODELNAME_MODEL_ID=model-identifier
MODELNAME_API_KEY=your_api_key_here
```

### Example: Wandou Configuration

```bash
# In .env
WANDOU_API_BASE=https://api3.xhub.chat/v1
WANDOU_MODEL_ID=gpt-4
WANDOU_API_KEY=sk-foFjMhriqthtEOBDT7AILJIj14YHtgysFDFg3oQUqJGiB00f
```

```yaml
# In config.yaml
wandou:
  type: "OpenAIServerModel"
  id: "${WANDOU_MODEL_ID}"
  api_base: "${WANDOU_API_BASE}"
  api_key: "${WANDOU_API_KEY}"
```

## Switching Between Models

Super easy! Just change one line in `config.yaml`:

```yaml
# Use Wandou GPT-4
model:
  active: "wandou"

# Switch to Claude
model:
  active: "claude"

# Switch to DeepSeek
model:
  active: "deepseek"
```

No restart needed - it loads on next run.

## Temperature Settings

Controls output randomness:

- `0.0` - Deterministic, consistent (good for code)
- `0.5-0.7` - Balanced
- `1.0` - Default, moderate creativity
- `1.5-2.0` - High creativity (brainstorming)

```yaml
model:
  active: "claude"
  temperature: 0.7  # Adjust here
```

## Complete Example: Adding Claude Official API

**File: `.env`**
```bash
# =============================================================================
# CLAUDE OFFICIAL API CONFIGURATION
# =============================================================================
CLAUDE_OFFICIAL_API_BASE=https://api.anthropic.com/v1
CLAUDE_OFFICIAL_MODEL_ID=claude-3-5-sonnet-20241022
CLAUDE_OFFICIAL_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**File: `config.yaml`**
```yaml
models:
  # ... existing models ...

  claude-official:
    type: "OpenAIServerModel"
    id: "${CLAUDE_OFFICIAL_MODEL_ID}"
    api_base: "${CLAUDE_OFFICIAL_API_BASE}"
    api_key: "${CLAUDE_OFFICIAL_API_KEY}"

model:
  active: "claude-official"
  temperature: 1.0
```

## Benefits of This Approach

✅ **Security**: API keys stay in `.env` (not committed to git)
✅ **Simplicity**: Change models by editing just one line
✅ **Flexibility**: Easy to add new models without touching code
✅ **Organization**: All credentials in one place
✅ **Portability**: Same config works across different environments

## Troubleshooting

### Error: "Unknown model configuration: xxx"

**Problem**: Model not defined in `config.yaml`

**Solution**: Add the model configuration to the `models:` section

### Error: Environment variable not set

**Problem**: Missing configuration in `.env`

**Solution**:
1. Check `.env` file exists and has the required variables
2. Restart your terminal after editing `.env`
3. Verify format: `MODELNAME_API_BASE=...` (no spaces around `=`)

### Model responds with authentication error

**Problem**: Invalid API key

**Solution**:
1. Verify the API key in `.env` is correct
2. Check the environment variable name matches between `.env` and `config.yaml`
3. Example: `${WANDOU_API_KEY}` in config.yaml → `WANDOU_API_KEY=...` in .env

### Can't find `.env` file

Create it from the template:

```powershell
cp .env.example .env
```

Then edit `.env` with your actual API keys.

## Getting API Keys

- **OpenRouter**: https://openrouter.ai/keys (supports 100+ models)
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Laozhang**: Contact your service provider
- **Wandou/XHub**: Contact your service provider
