#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generated Python helper tool
Created: 2025-11-22 15:38:42
"""

from smolagents import tool

@tool
def save_json_file(file_path: str, content: any) -> str:
    """
    Save JSON content to a file
    
    Args:
        file_path (str): Description of file_path
        content (any): Description of content
        
    Returns:
        str: Result of the operation
    """
    import json
    try:
        with open(file_path, 'w') as f:
            if isinstance(content, str):
                f.write(content)
            else:
                json.dump(content, f, indent=2)
        return f"File saved successfully: {file_path}"
    except Exception as e:
        return f"Error saving file: {e}"
