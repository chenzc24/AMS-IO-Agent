#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple IL File Runner using RAMIC Bridge

NOTE: This script uses RAMIC Bridge, NOT skillbridge.
It requires the RAMIC system to be properly configured.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.il_runner_tool import run_il_file

def main():
    # Test 1: Simple return value
    result1 = run_il_file("/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/test_return.il")    
    print(f"[Test 1 - Simple Return]: {result1}\n")
    
    # Test 2: Get cellview info (may return nil if no cellview is open)
    result2 = run_il_file("/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/get_cellview_info.il")    
    print(f"[Test 2 - Cellview Info]: {result2}\n")
    
    # Test 3: Simple test from output folder
    result3 = run_il_file("/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/simple_test.il")    
    print(f"[Test 3 - Simple Test]: {result3}")

if __name__ == "__main__":
    main()
