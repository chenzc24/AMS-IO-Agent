#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generated Python helper tool
Created: 2025-11-22 16:05:59
"""

from smolagents import tool

@tool
def create_text_file(file_path: str, content: str) -> str:
    """
    Create a text file with the specified content
    
    Args:
        file_path (str): Description of file_path
        content (str): Description of content
        
    Returns:
        str: Result of the operation
    """
    def create_text_file(file_path, content):
        """Create a text file with the specified content"""
        try:
            # Extract directory from file path
            import os
            directory = os.path.dirname(file_path)

            # Create directory if it doesn't exist
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"[INFO] Created directory: {directory}")

            # Save text content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully saved text file to: {file_path}"
        except Exception as e:
            return f"Error saving text file: {str(e)}"
