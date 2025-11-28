# Python Helper Tools

This directory contains custom Python helper tools created during conversations to avoid repetitive code.

## Purpose

When you find yourself writing the same code repeatedly (e.g., reading IL files, parsing data), you can create a reusable helper tool instead.

## Directory Structure

```
skill_tools/python_helpers/
├── README.md                    # This file
├── read_il_file_content.py     # Example: Read IL file as string
├── parse_il_comments.py        # Example: Extract comments from IL
└── ...                         # Your custom helpers
```

## Creating Helpers

### Via Agent Conversation

Simply tell the Agent:

```
"I keep reading IL files. Create a helper tool to read IL file content as a string."
```

The Agent will use `create_python_helper()` to create the tool.

### Manually

Use the `create_python_helper()` function:

```python
create_python_helper(
    tool_name="read_il_file_content",
    description="Read IL file and return its content as a string",
    function_body='''
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
return content
''',
    parameters='{"file_path": "str"}',
    return_type="str"
)
```

## Using Helpers

After creation, helpers are immediately available:

```python
# Read IL file
content = read_il_file_content("path/to/file.il")

# Parse comments
comments = parse_il_comments("path/to/file.il")
```

## Managing Helpers

### List all helpers
```python
list_python_helpers()
```

### View helper code
```python
view_python_helper_code("read_il_file_content")
```

### Update helper
```python
update_python_helper(
    "read_il_file_content",
    '''
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
# Add error handling
if not content:
    return "Empty file"
return content
'''
)
```

### Delete helper
```python
delete_python_helper("read_il_file_content")
```

## Best Practices

### ✅ Good Use Cases
- File I/O operations (reading, writing, parsing)
- Data transformation (formatting, conversion)
- Simple calculations
- String manipulation
- Path operations

### ❌ Not Suitable For
- Complex business logic (use regular tools in `src/tools/`)
- SKILL execution (use `skill_tools/` instead)
- Operations requiring Agent context
- One-time use code

## Examples

### Example 1: Read IL File
```python
create_python_helper(
    tool_name="read_il_file_content",
    description="Read IL file and return its content as a string",
    function_body='''
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
return content
''',
    parameters='{"file_path": "str"}',
    return_type="str"
)
```

### Example 2: Count Lines in File
```python
create_python_helper(
    tool_name="count_file_lines",
    description="Count number of lines in a file",
    function_body='''
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
return str(len(lines))
''',
    parameters='{"file_path": "str"}',
    return_type="str"
)
```

### Example 3: Extract Function Names from IL
```python
create_python_helper(
    tool_name="extract_il_functions",
    description="Extract all function definitions from IL file",
    function_body='''
import re
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Match: procedure(functionName ...)
functions = re.findall(r'procedure\\s*\\(\\s*(\\w+)', content)
return ', '.join(functions)
''',
    parameters='{"file_path": "str"}',
    return_type="str"
)
```

## Hot-Reload

All helpers support hot-reload:
- **Create**: Available immediately after creation
- **Update**: Changes take effect on next call
- **Delete**: Removed immediately

No need to restart the Agent!

## Notes

- Helpers are stored as individual `.py` files
- Each helper is a standalone `@tool` decorated function
- Helpers are automatically loaded on Agent startup
- Helpers persist across sessions (saved to disk)

