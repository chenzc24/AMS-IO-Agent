# Model Configuration - Quick Reference

## ✅ New Secure Approach

All sensitive model configurations are now in `.env` (gitignored).
`config.yaml` is safe to commit to GitHub!

## How It Works

### 1. Models Auto-Discovered from `.env`

The system automatically finds models by looking for this pattern:

```bash
MODELNAME_API_BASE=https://api.example.com/v1
MODELNAME_MODEL_ID=model-id
MODELNAME_API_KEY=your_api_key
```

### 2. Use Any Model

Just set in `config.yaml`:

```yaml
model:
  active: "modelname"  # Use the lowercase model name
```

## Your Current Models

Based on your `.env` file, you have:

```
✅ claude       - Claude Sonnet 4 (laozhang.ai)
✅ gpt-4o       - GPT-4o (laozhang.ai)
✅ gpt-4        - GPT-4 (laozhang.ai)
✅ claude-4     - Claude Sonnet 4 (OpenRouter)
✅ deepseek     - DeepSeek Chat v3 (DeepSeek API)
✅ wandou       - GPT-4 (XHub)
✅ qwen         - Qwen3 VL Plus (Aliyun)
```

## Adding a New Model

**Example: Adding GPT-4 Turbo via OpenAI**

### Step 1: Add to `.env`

```bash
# =============================================================================
# GPT-4 TURBO MODEL CONFIGURATION (via OpenAI Official)
# =============================================================================
GPT4TURBO_API_BASE=https://api.openai.com/v1
GPT4TURBO_MODEL_ID=gpt-4-turbo
GPT4TURBO_API_KEY=sk-xxxxxxxxxxxxx
```

### Step 2: Use It

```yaml
# In config.yaml
model:
  active: "gpt-4turbo"  # System auto-converts GPT4TURBO -> gpt-4turbo
```

That's it! No need to edit config.yaml's model section.

## Name Conversion Rules

Environment variable prefix → Model name:

- `CLAUDE_*` → `claude`
- `GPT4O_*` → `gpt-4o` (special case)
- `GPT4_*` → `gpt-4` (special case)
- `CLAUDE4_*` → `claude-4` (special case)
- `WANDOU_*` → `wandou`
- `QWEN_*` → `qwen`
- `MYCUSTOM_*` → `mycustom`

## What's Safe to Commit?

### ✅ Safe (Commit to GitHub)
- `config.yaml` - No sensitive data
- `.env.example` - Template only
- `docs/` - Documentation

### ❌ Never Commit (Gitignored)
- `.env` - Contains ALL sensitive data:
  - API keys
  - API base URLs
  - Model IDs
  - All credentials

## Benefits

✅ **Security**: No secrets in version control
✅ **Simplicity**: Just edit `.env` to add models
✅ **Clean**: `config.yaml` has no sensitive data
✅ **Auto-discovery**: Models appear automatically
✅ **Team-friendly**: Each dev has their own `.env`

## Troubleshooting

### "Unknown model configuration: xxx"

**Cause**: Model not in `.env`

**Fix**: Add these 3 lines to `.env`:
```bash
XXX_API_BASE=https://...
XXX_MODEL_ID=model-name
XXX_API_KEY=your_key
```

### Model not showing up

**Checklist**:
1. ✅ All 3 variables defined? (_API_BASE, _MODEL_ID, _API_KEY)
2. ✅ No typos in variable names?
3. ✅ Restart terminal after editing `.env`?

### Want to see available models?

Run the agent - it shows all discovered models on startup:

```
✅ Configuration loaded:
   Model: claude
   Available models: claude, claude-4, deepseek, gpt-4, gpt-4o, qwen, wandou
```

## Migration from Old Config

If you have models in `config.yaml`, migrate to `.env`:

### Before (in config.yaml):
```yaml
models:
  my-model:
    type: "OpenAIServerModel"
    id: "model-id"
    api_base: "https://api.example.com/v1"
    api_key: "${MY_API_KEY}"
```

### After (in .env):
```bash
MYMODEL_API_BASE=https://api.example.com/v1
MYMODEL_MODEL_ID=model-id
MYMODEL_API_KEY=your_actual_key
```

Then remove from `config.yaml` - it auto-discovers!
