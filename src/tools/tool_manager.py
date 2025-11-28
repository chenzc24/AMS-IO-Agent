"""
Dynamic Tool Management System
Allows runtime addition/removal of agent tools
"""

from smolagents import tool
from typing import Optional
import json
from datetime import datetime
from pathlib import Path

# Global reference to the agent instance
# Will be set by main.py after agent creation
_agent_instance = None

def set_agent_instance(agent):
    """Set the global agent instance for tool management"""
    global _agent_instance
    _agent_instance = agent

@tool
def list_registered_tools() -> str:
    """
    List all currently registered tools in the agent.
    
    Returns:
        String containing all tool names and their descriptions
    """
    if _agent_instance is None:
        return "❌ Agent instance not initialized"
    
    tools = _agent_instance.tools
    result = f"📋 Currently registered tools ({len(tools)}):\n\n"
    
    # Group by category (based on naming convention)
    categories = {
        'Knowledge': [],
        'Virtuoso': [],
        'Verification': [],
        'IO Ring': [],
        'System': []
    }
    
    for tool_name, tool_obj in tools.items():
        desc = tool_obj.description if hasattr(tool_obj, 'description') else "No description"
        
        # Categorize
        if 'knowledge' in tool_name or 'scan' in tool_name or 'search' in tool_name or 'load' in tool_name:
            categories['Knowledge'].append((tool_name, desc))
        elif 'il' in tool_name or 'screenshot' in tool_name or 'cell' in tool_name or 'clear' in tool_name:
            categories['Virtuoso'].append((tool_name, desc))
        elif 'drc' in tool_name or 'lvs' in tool_name or 'pex' in tool_name:
            categories['Verification'].append((tool_name, desc))
        elif 'io_ring' in tool_name:
            categories['IO Ring'].append((tool_name, desc))
        else:
            categories['System'].append((tool_name, desc))
    
    # Format output
    for category, tool_list in categories.items():
        if tool_list:
            result += f"## {category} ({len(tool_list)})\n"
            for name, desc in sorted(tool_list):
                result += f"  • {name}\n"
                if desc and desc != "No description":
                    result += f"    └─ {desc[:80]}...\n" if len(desc) > 80 else f"    └─ {desc}\n"
            result += "\n"
    
    return result


@tool
def get_tool_info(tool_name: str) -> str:
    """
    Get detailed information about a specific tool.
    
    Args:
        tool_name: Name of the tool to inspect
        
    Returns:
        Detailed information about the tool including description and parameters
    """
    if _agent_instance is None:
        return "❌ Agent instance not initialized"
    
    tools = _agent_instance.tools
    
    if tool_name not in tools:
        available = ", ".join(list(tools.keys())[:10])
        return f"❌ Tool '{tool_name}' not found. Available tools: {available}..."
    
    tool_obj = tools[tool_name]
    
    result = f"🔧 Tool: {tool_name}\n\n"
    result += f"Description:\n{tool_obj.description if hasattr(tool_obj, 'description') else 'No description'}\n\n"
    
    # Get input schema if available
    if hasattr(tool_obj, 'inputs'):
        result += "Parameters:\n"
        for param_name, param_info in tool_obj.inputs.items():
            param_type = param_info.get('type', 'unknown')
            param_desc = param_info.get('description', 'No description')
            result += f"  • {param_name} ({param_type}): {param_desc}\n"
    
    # Get output schema if available
    if hasattr(tool_obj, 'output_type'):
        result += f"\nReturn Type: {tool_obj.output_type}\n"
    
    return result


@tool
def check_tool_availability(tool_name: str) -> str:
    """
    Check if a specific tool is currently available.
    
    Args:
        tool_name: Name of the tool to check
        
    Returns:
        Availability status
    """
    if _agent_instance is None:
        return "❌ Agent instance not initialized"
    
    if tool_name in _agent_instance.tools:
        return f"✅ Tool '{tool_name}' is available"
    else:
        return f"❌ Tool '{tool_name}' is not available"


@tool
def export_tools_snapshot(output_path: str = "output/logs/tools_snapshot.json") -> str:
    """
    Export current tool registry to JSON file for inspection.
    
    Args:
        output_path: Path to save the JSON snapshot (default: logs/tools_snapshot.json)
        
    Returns:
        Success message with file path
    """
    if _agent_instance is None:
        return "❌ Agent instance not initialized"
    
    try:
        # Prepare output directory
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Gather tool information
        tools_data = {
            "metadata": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(_agent_instance.tools),
                "agent_type": type(_agent_instance).__name__
            },
            "tools": {}
        }
        
        # Categorize tools
        categories = {
            'tool_management': [],
            'knowledge_loading': [],
            'virtuoso_execution': [],
            'verification': [],
            'io_ring': [],
            'system': []
        }
        
        for tool_name, tool_obj in _agent_instance.tools.items():
            tool_info = {
                "name": tool_name,
                "description": getattr(tool_obj, 'description', 'No description'),
                "type": type(tool_obj).__name__
            }
            
            # Get input schema if available
            if hasattr(tool_obj, 'inputs'):
                tool_info["inputs"] = {
                    param_name: {
                        "type": param_info.get('type', 'unknown'),
                        "description": param_info.get('description', 'No description')
                    }
                    for param_name, param_info in tool_obj.inputs.items()
                }
            
            # Categorize
            if 'tool' in tool_name and ('list' in tool_name or 'get' in tool_name or 'check' in tool_name):
                category = 'tool_management'
            elif 'knowledge' in tool_name or 'scan' in tool_name or 'search' in tool_name or 'load' in tool_name:
                category = 'knowledge_loading'
            elif 'il' in tool_name or 'screenshot' in tool_name or 'cell' in tool_name or 'clear' in tool_name:
                category = 'virtuoso_execution'
            elif 'drc' in tool_name or 'lvs' in tool_name or 'pex' in tool_name:
                category = 'verification'
            elif 'io_ring' in tool_name:
                category = 'io_ring'
            else:
                category = 'system'
            
            tool_info["category"] = category
            categories[category].append(tool_name)
            tools_data["tools"][tool_name] = tool_info
        
        # Add category summary
        tools_data["categories"] = {
            cat: len(tools) for cat, tools in categories.items() if tools
        }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tools_data, f, ensure_ascii=False, indent=2)
        
        abs_path = output_file.resolve()
        return f"✅ Tool snapshot exported to: {abs_path}\n📊 Total tools: {len(_agent_instance.tools)}"
        
    except Exception as e:
        return f"❌ Failed to export tools snapshot: {e}"


@tool
def get_tools_summary() -> str:
    """
    Get a quick summary of tool categories and counts.
    
    Returns:
        JSON string with tool statistics
    """
    if _agent_instance is None:
        return json.dumps({"error": "Agent instance not initialized"})
    
    categories = {
        'tool_management': 0,
        'knowledge_loading': 0,
        'virtuoso_execution': 0,
        'verification': 0,
        'io_ring': 0,
        'system': 0
    }
    
    for tool_name in _agent_instance.tools.keys():
        if 'tool' in tool_name and ('list' in tool_name or 'get' in tool_name or 'check' in tool_name):
            categories['tool_management'] += 1
        elif 'knowledge' in tool_name or 'scan' in tool_name or 'search' in tool_name or 'load' in tool_name:
            categories['knowledge_loading'] += 1
        elif 'il' in tool_name or 'screenshot' in tool_name or 'cell' in tool_name or 'clear' in tool_name:
            categories['virtuoso_execution'] += 1
        elif 'drc' in tool_name or 'lvs' in tool_name or 'pex' in tool_name:
            categories['verification'] += 1
        elif 'io_ring' in tool_name:
            categories['io_ring'] += 1
        else:
            categories['system'] += 1
    
    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tools": len(_agent_instance.tools),
        "by_category": {k: v for k, v in categories.items() if v > 0}
    }
    
    return json.dumps(summary, ensure_ascii=False, indent=2)


# Advanced: Tool hot-swapping (use with caution)
def add_tool_to_agent(tool_obj, overwrite: bool = False) -> str:
    """
    Dynamically add a tool to the running agent (administrative function).
    
    Args:
        tool_obj: Tool instance to add
        overwrite: If True, overwrite existing tool with same name
        
    Returns:
        Success/failure message
    """
    if _agent_instance is None:
        return "❌ Agent instance not initialized"
    
    tool_name = tool_obj.name
    
    if tool_name in _agent_instance.tools and not overwrite:
        return f"❌ Tool '{tool_name}' already exists. Use overwrite=True to replace."
    
    _agent_instance.tools[tool_name] = tool_obj
    return f"✅ Tool '{tool_name}' added successfully"


def remove_tool_from_agent(tool_name: str) -> str:
    """
    Dynamically remove a tool from the running agent (administrative function).
    
    Args:
        tool_name: Name of the tool to remove
        
    Returns:
        Success/failure message
    """
    if _agent_instance is None:
        return "❌ Agent instance not initialized"
    
    if tool_name not in _agent_instance.tools:
        return f"❌ Tool '{tool_name}' not found"
    
    # Don't allow removal of critical tools
    critical_tools = ['final_answer', 'list_registered_tools', 'get_tool_info']
    if tool_name in critical_tools:
        return f"❌ Cannot remove critical tool '{tool_name}'"
    
    del _agent_instance.tools[tool_name]
    return f"✅ Tool '{tool_name}' removed successfully"

