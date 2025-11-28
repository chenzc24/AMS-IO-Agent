# Testing Model Discovery

## How to Test What Models Are Discovered

Run this command in your PowerShell (with .venv activated):

```powershell
python src/app/utils/config_utils.py
```

This will show:
1. ✅ All discovered models from your `.env` file
2. 📦 Each model's configuration (API base, model ID, API key preview)
3. 🧪 Test results for specific models

## Understanding Model Names

**IMPORTANT**: Model names come from the **environment variable PREFIX**, not the MODEL_ID!

### Example from your `.env`:

```bash
QWEN_API_BASE=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_ID=qwen3-vl-plus
QWEN_API_KEY=sk-44a4605067f54438954a442d58dc7772
```

| Environment Variable | Value | Purpose |
|---------------------|-------|---------|
| `QWEN_API_BASE` | API endpoint | Where to send requests |
| `QWEN_MODEL_ID` | `qwen3-vl-plus` | What model to use (sent to API) |
| `QWEN_API_KEY` | Your key | Authentication |

**Model Name**: `qwen` (from the `QWEN_` prefix)

### In config.yaml, use:

```yaml
model:
  active: "qwen"  # ✅ Correct - use the prefix
  # NOT "qwen3-vl-plus" ❌ (that's the MODEL_ID)
```

## Your Current Models

Based on your `.env`:

| Model Name | MODEL_ID | API Provider |
|------------|----------|--------------|
| `claude` | claude-sonnet-4-20250514 | laozhang.ai |
| `gpt-4o` | gpt-4o | laozhang.ai |
| `gpt-4` | gpt-4.1 | laozhang.ai |
| `claude-4` | anthropic/claude-sonnet-4 | OpenRouter |
| `deepseek` | deepseek-chat-v3 | DeepSeek API |
| `wandou` | gpt-4 | XHub |
| `qwen` | qwen3-vl-plus | Aliyun |

## Quick Test Command

```powershell
# Test model discovery
python src/app/utils/config_utils.py

# Then run main.py to use the selected model
python main.py
```

## Troubleshooting

### Model name doesn't work?

❌ **Wrong**:
```yaml
active: "qwen3-vl-plus"  # This is the MODEL_ID, not the model name!
```

✅ **Correct**:
```yaml
active: "qwen"  # This is the model name from QWEN_* prefix
```

### Want a different model name?

Change the environment variable prefix in `.env`:

```bash
# If you want model name "qwen-vl"
QWENVL_API_BASE=...
QWENVL_MODEL_ID=qwen3-vl-plus
QWENVL_API_KEY=...
```

Then use:
```yaml
active: "qwen-vl"
```

## About parse_arguments()

The `parse_arguments()` function in `config_utils.py` is **LEGACY CODE** - it's no longer used.

✅ **Now**: All configuration via `config.yaml` + `.env`
❌ **Old**: Command-line arguments (deprecated)

You can safely ignore it. It's kept only for backward compatibility.
