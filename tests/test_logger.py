#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MinimalOutputLogger directly
"""

from pathlib import Path
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.app.utils.custom_logger import MinimalOutputLogger

# Create logger instance
logger = MinimalOutputLogger()

print("\n" + "=" * 70)
print("Testing MinimalOutputLogger")
print("=" * 70 + "\n")

# Test different log types
print("Test 1: Thought (should be CYAN)")
logger.log("Thought: The user is testing the logger functionality...")

print("\nTest 2: Final answer (should be GREEN)")
logger.log("Final answer: The logger is working correctly with colors!")

print("\nTest 3: Step timing (should be YELLOW)")
logger.log("[Step 1: Duration 5.23 seconds | Input tokens: 1,234 | Output tokens: 567]")

print("\nTest 4: Observation (should be default color)")
logger.log("Observation: Test completed successfully")

print("\nTest 5: Code execution (should be HIDDEN)")
logger.log("─ Executing parsed code:")

print("\n" + "=" * 70)
print("Test Complete")
print("=" * 70 + "\n")

