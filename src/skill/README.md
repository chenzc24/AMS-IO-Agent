# SKILL Tools

This directory contains reusable SKILL tool scripts for common operations.

## Available Tools

- `get_cellview_info.il` - Get current cellview information
- `clear_window.il` - Clear all components in current window  
- `print_hello.il` - Simple hello world example

## Usage

### From Python
```python
from src.tools.skill_tools_manager import run_skill_tool
run_skill_tool("get_cellview_info")
```

### From LLM Agent
```
list_skill_tools()           # List all tools
run_skill_tool("tool_name")  # Run specific tool
create_skill_tool("name", "code")  # Create new tool
update_skill_tool("name", "code") # Update existing tool
delete_skill_tool("name")    # Delete tool
```

## Adding New Tools

1. Create `.il` file in this directory
2. Use `create_skill_tool()` function
3. Or manually add to directory

## Tool Naming

- Use descriptive names
- No spaces, use underscores
- Keep names short but clear
