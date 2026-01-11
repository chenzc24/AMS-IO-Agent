#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Factory - IO Ring Design Agent
Specialized for IO Ring generation and EDA workflows
"""

import sys
from pathlib import Path
from smolagents import CodeAgent, ToolCallingAgent
import json

# Import existing factory functions
from .agent_factory import create_model, get_tools_for_agent
from .agent_utils import TokenLimitedCodeAgent
from .custom_logger import MinimalOutputLogger

# Import default tools from smolagents
try:
    from smolagents.default_tools import UserInputTool
except ImportError:
    # Fallback if default_tools is not available
    UserInputTool = None


# CDAC worker agent removed - this version focuses on IO Ring design only
# If you need CDAC functionality, please restore from git history


def create_master_agent_with_workers(model_config, tools_config_path="config/tools_config.yaml"):
    """
    Create IO Ring design agent with standard EDA tools.
    
    This agent is specialized for IO Ring generation and verification workflows.
    
    Args:
        model_config: Model configuration
        tools_config_path: Path to tools configuration
        
    Returns:
        IO Ring design agent with full EDA toolset
    """
    # Load standard tools for IO agent
    standard_tools = get_tools_for_agent(tools_config_path)
    
    # Add default tools from smolagents (like user_input)
    if UserInputTool is not None:
        standard_tools.append(UserInputTool())
    
    # Create model for agent
    model = create_model(model_config)
    
    # IO agent system prompt
    io_agent_instructions = """
You are an AI agent specialized in IO Ring design for integrated circuits.

You have access to comprehensive EDA tools for:
- **IO Ring Generation**: Automated schematic and layout generation for IO pad rings
- **Virtuoso Integration**: Execute SKILL scripts in Cadence Virtuoso
- **Verification**: DRC, LVS, and PEX workflows
- **Knowledge Base**: Access to design rules, technology parameters, and best practices

**YOUR CAPABILITIES**:

1. **IO Ring Design**:
   - Parse user requirements for IO ring specifications
   - Generate JSON intent graphs for pad placement
   - Create schematic and layout SKILL code
   - Handle single/double ring topologies
   - Support multiple voltage domains
   - Manage corner cells and filler placement

2. **EDA Tool Integration**:
   - Execute SKILL scripts in Virtuoso
   - Run DRC verification
   - Run LVS verification
   - Perform parasitic extraction (PEX)
   - Manage design libraries and cellviews

3. **Knowledge Management**:
   - Load relevant knowledge modules on-demand
   - Access technology-specific design rules
   - Reference IO pad libraries and specifications
   - Learn from error patterns and solutions

**WORKFLOW GUIDELINES**:

1. **Understand Requirements**: Parse user input to extract IO ring specifications.
2. **Clarify Design Context**:
   - **ASK the user** for the target Library, Cell, and View names before execution.
   - If not provided, ask for permission to use default names (e.g., IO_RING_LIB / io_ring_design).
   - If defaults fail or user prefers, fallback to executing in the currently open Virtuoso window.
3. **Generate Design**: Create intent graph and SKILL code for implementation.
4. **Execute in Virtuoso**: Run generated SKILL scripts via il_runner tool.
   - Prefer passing explicit lib/cell/view if known and valid.
   - Omit lib/cell arguments to run in the current active window if specific targets are invalid or unspecified.
5. **Verify**: Run DRC, LVS, and PEX to validate the design.
6. **Iterate**: Fix errors and regenerate if verification fails.
7. **Document**: Save results and provide clear feedback to user.

**BEST PRACTICES**:
- **Robust Execution**: Do not assume libraries exist. Try to create them, or ask the user, or fallback to current window.
- Use knowledge base for technology-specific parameters
- Provide clear error messages and suggestions
- Save intermediate results for debugging
- Document design decisions and rationale

Focus on delivering high-quality, verified IO ring designs that meet user specifications.
"""
    
    # Create IO agent without managed_agents (simplified architecture)
    io_agent = TokenLimitedCodeAgent(
        tools=standard_tools,
        model=model,
        instructions=io_agent_instructions,
        stream_outputs=True,
        additional_authorized_imports=[
            'os', 'pathlib', 'io', 'sys', 'subprocess', 
            'typing', 'posixpath', 'ntpath', 'importlib', 'glob', 'json', 'ast'
        ],
        executor_kwargs={
            "additional_functions": {
                "open": open, 
                "exec": exec,
                "locals": locals,
                "globals": globals,
                "vars": vars
            }
        },
        max_steps=100
    )
    
    # Set agent instance for tool management
    from src.tools.tool_manager import set_agent_instance
    set_agent_instance(io_agent)
    
    # Load all existing Python helper tools (hot-reload support)
    try:
        from src.tools.python_tool_creator import load_all_python_helpers
        load_all_python_helpers()
    except Exception as e:
        print(f"Warning: Failed to load Python helpers: {e}")
    
    return io_agent


def create_multi_agent_system(model_config, tools_config_path="config/tools_config.yaml"):
    """
    Create IO Ring design system (legacy compatibility function)
    
    Args:
        model_config: Model configuration
        tools_config_path: Tools configuration path
        
    Returns:
        dict with IO agent
    """
    io_agent = create_master_agent_with_workers(model_config, tools_config_path)
    
    return {
        'master': io_agent,
        'workers': {}  # No workers in IO-only version
    }


