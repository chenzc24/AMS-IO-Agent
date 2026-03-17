#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Logger for Agent Output Filtering
Allows selective display of Thought, Code, and Observations
"""

import sys
from smolagents import AgentLogger
from typing import Any, Optional


class CustomAgentLogger(AgentLogger):
    """
    Custom logger that filters out "Executing parsed code" blocks
    while keeping Thought and Observation.
    """
    
    def __init__(
        self,
        show_thought: bool = True,
        show_code_execution: bool = False,  # Set to False to hide "Executing parsed code"
        show_observation: bool = True,
        show_final_answer: bool = True,
    ):
        super().__init__()
        self.show_thought = show_thought
        self.show_code_execution = show_code_execution
        self.show_observation = show_observation
        self.show_final_answer = show_final_answer
        self._in_code_block = False
    
    def log(self, log: str, level: str = "info", **kwargs: Any):
        """Override log method to filter outputs"""
        
        # Convert Panel to string if needed
        log_str = str(log)
        
        # Detect code execution blocks
        if "Executing parsed code:" in log_str or "─────" in log_str:
            if not self.show_code_execution:
                self._in_code_block = not self._in_code_block
                return  # Skip this line
        
        # Skip content inside code blocks if code execution is disabled
        if self._in_code_block and not self.show_code_execution:
            # Check if this is the closing separator
            if "─────" in log_str:
                self._in_code_block = False
            return
        
        # Filter by content type
        if "Thought:" in log_str and not self.show_thought:
            return
        
        if "Observation:" in log_str and not self.show_observation:
            return
        
        if "Final answer:" in log_str and not self.show_final_answer:
            return
        
        # Print allowed content
        super().log(log, level, **kwargs)


class MinimalOutputLogger(AgentLogger):
    """
    Minimal logger that only shows Thought and Final answer with colors.
    Hides all code execution details.
    """
    
    # ANSI color codes
    CYAN = '\033[36m'     # Thought
    GREEN = '\033[32m'    # Final answer
    YELLOW = '\033[93m'   # Step timing
    RESET = '\033[0m'
    
    def log(self, log: str, level: str = "info", **kwargs: Any):
        """Only show Thought and Final answer with colors"""
        
        # Convert to string for checking
        log_str = str(log)
        
        # Skip code execution blocks entirely
        if any(marker in log_str for marker in [
            "─ Executing parsed code:",
            "──────────────────",
            "Code:",
            "print(",
            "final_answer(",
            "return "
        ]):
            return
        
        # Determine if we should show this content and what color
        should_show = False
        color = ""
        
        if "Thought:" in log_str:
            should_show = True
            color = self.CYAN
        elif "Final answer:" in log_str:
            should_show = True
            color = self.GREEN
        elif "[Step " in log_str:
            should_show = True
            color = self.YELLOW
        elif "Observation:" in log_str:
            should_show = True
            color = ""  # No color
        
        if should_show:
            # Apply color by printing directly
            if color:
                print(f"{color}{log_str}{self.RESET}")
            else:
                print(log_str)


class SilentLogger(AgentLogger):
    """Logger that only shows final answer, nothing else."""
    
    def log(self, log: str, level: str = "info", **kwargs: Any):
        """Only show final answer"""
        log_str = str(log)
        if "Final answer:" in log_str or ("Agent:" in log_str and "Final answer" not in log_str):
            super().log(log, level, **kwargs)

