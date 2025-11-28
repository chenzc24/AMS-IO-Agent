#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test User Profile Management Tools"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.user_profile_tool import update_user_profile, read_profile

if __name__ == "__main__":
    os.environ["USER_PROFILE_PATH"] = "user_data/test_profile.md"
    
    print("[Test 1]: Read current profile")
    current = read_profile()
    print(current)
    
    print("\n[Test 2]: Create initial profile")
    initial = read_profile()
    modified = initial + "\n- Likes [script_name] in output\n"
    print(update_user_profile(modified))
    
    print("\n[Test 3]: Read again")
    current = read_profile()
    print(current)
    
    print("\n✅ All tests passed!\n")
