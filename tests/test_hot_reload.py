#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test hot-reload functionality of SKILL tools
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.skill_tools_manager import (
    list_skill_tools, 
    create_skill_tool, 
    run_skill_tool,
    update_skill_tool,
    delete_skill_tool
)

def test_hot_reload():
    """Test creating, running, updating, and deleting a tool without restart"""
    
    print("=" * 60)
    print("Testing SKILL Tools Hot-Reload Functionality")
    print("=" * 60)
    
    # Step 1: List current tools
    print("\n[Step 1] List current tools:")
    print(list_skill_tools())
    
    # Step 2: Create a new tool
    print("\n[Step 2] Create a new tool 'test_hot_reload':")
    tool_code = ''';; Test hot reload functionality
printf("Hot reload test - Version 1\\n")
"Version 1"
'''
    result = create_skill_tool("test_hot_reload", tool_code)
    print(result)
    
    # Step 3: Run the new tool immediately (without restart!)
    print("\n[Step 3] Run the new tool immediately:")
    result = run_skill_tool("test_hot_reload")
    print(result)
    
    # Step 4: Update the tool
    print("\n[Step 4] Update the tool:")
    updated_code = ''';; Test hot reload functionality - UPDATED
printf("Hot reload test - Version 2 (UPDATED)\\n")
"Version 2 - UPDATED"
'''
    result = update_skill_tool("test_hot_reload", updated_code)
    print(result)
    
    # Step 5: Run the updated tool (changes take effect immediately!)
    print("\n[Step 5] Run the updated tool:")
    result = run_skill_tool("test_hot_reload")
    print(result)
    
    # Step 6: Delete the test tool
    print("\n[Step 6] Delete the test tool:")
    result = delete_skill_tool("test_hot_reload")
    print(result)
    
    # Step 7: Verify deletion
    print("\n[Step 7] Verify tool is deleted:")
    result = run_skill_tool("test_hot_reload")
    print(result)
    
    print("\n" + "=" * 60)
    print("✅ Hot-reload test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_hot_reload()

