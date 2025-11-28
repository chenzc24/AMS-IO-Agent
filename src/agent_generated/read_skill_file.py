#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generated Python helper tool
Created: 2025-10-26 17:05:26
"""

from smolagents import tool

@tool
def read_skill_file(file_path: str) -> str:
    """
    Read SKILL file and return its content as a string
    
    Args:
        file_path (str): Description of file_path
        
    Returns:
        str: Result of the operation
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"
