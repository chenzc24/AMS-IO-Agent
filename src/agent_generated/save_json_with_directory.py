#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generated Python helper tool
Created: 2025-11-22 15:58:11
"""

from smolagents import tool

@tool
def save_json_with_directory(file_path: str, content: object) -> str:
    """
    Create directory if needed and save JSON content to file
    
    Args:
        file_path (str): Description of file_path
        content (object): Description of content
        
    Returns:
        str: Result of the operation
    """
    import os
    import json

    def create_directory_and_save_json(file_path, content):
        """Create directory if needed and save JSON content to file"""
        try:
            # Extract directory from file path
            directory = os.path.dirname(file_path)

            # Create directory if it doesn't exist
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"[INFO] Created directory: {directory}")

            # Save JSON content
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)

            return f"Successfully saved JSON file to: {file_path}"
        except Exception as e:
            return f"Error saving file: {str(e)}"
