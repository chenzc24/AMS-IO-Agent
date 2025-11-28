import os
from smolagents import tool
from pathlib import Path
from typing import List, Dict, Union, Optional

# Get project root directory path
EXAMPLES_DIR = Path(__file__).parent.parent / "code_examples"

# Ensure examples directory exists
if not EXAMPLES_DIR.exists():
    EXAMPLES_DIR.mkdir(parents=True)

def list_examples() -> List[str]:
    """
    List all available example files
    
    Returns:
        List of example file paths
    """
    examples = []
    for ext in ['.py', '.il']:
        examples.extend([str(f) for f in EXAMPLES_DIR.glob(f"*{ext}")])
    return examples

def search_examples(
    query: str,
    file_type: Optional[str] = None
) -> List[Dict[str, Union[str, float]]]:
    """
    Search example files
    
    Args:
        query: Search keyword
        file_type: Optional file type filter (.py or .il)
        
    Returns:
        List of search results, each result is a dictionary containing file path (str) and relevance score (float)
    """
    if query is None:
        raise ValueError("Search keyword cannot be None")
        
    if file_type and file_type not in ['.py', '.il']:
        raise ValueError("Invalid file type, only .py and .il are supported")
    
    query = query.lower().strip()
    if not query:
        return []
    
    results = []
    for file_path in list_examples():
        # If file type is specified, skip non-matching files
        if file_type and not file_path.endswith(file_type):
            continue
            
        # Calculate relevance score
        relevance = 0.0
        file_name = os.path.basename(file_path).lower()
        
        # Filename matching
        if query in file_name:
            relevance += 0.5
            
        # Content matching
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if query in content:
                    relevance += 0.3
                    
                # Check comments and docstrings
                if f'"""{query}' in content or f"'''{query}" in content:
                    relevance += 0.2
                    
                # Check function and class names
                if f"def {query}" in content or f"class {query}" in content:
                    relevance += 0.4
        except Exception:
            continue
            
        if relevance > 0:
            results.append({
                "file": file_path,
                "relevance": min(1.0, relevance)  # Ensure score doesn't exceed 1.0
            })
    
    # Sort by relevance in descending order
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results

def get_example_description(file_name: str) -> str:
    """
    Get description information for example file
    
    Args:
        file_name: Example filename
        
    Returns:
        Description information for the example file
    """
    descriptions = {
        "layout_generation_example.py": """
This is a single-ring IO layout generator example, with the following characteristics:
1. Standard single-ring PAD layout
2. Clockwise PAD layout, please refer to this example for clockwise placement
3. Note the placement of corners, do not miss, note that there are only two types of corners and digital corners, no so-called isolated corners
4. Note the placement of fillers and PRCUTA_G, do not miss, note that two should be inserted between pads, one between pad and corner, and the type should be selected correctly, especially the insertion of PRCUTA_G. Note that the coordinates of the fill are related to clockwise and counterclockwise
5. Note the placement of digital IO features, do not miss, note that the main configuration line, sub-line, and pin should not be missed, brackets and the like should not be missed, need to be paired, especially in character matching scenarios

Applicable scenarios:
- Standard single-ring chip design
- Clockwise PAD layout
""",
        "dual_ring_layout_example.py": """
This is a dual-ring IO layout generator example, with the following characteristics:
1. Supports both inner and outer dual-ring PAD layouts, inner PAD placement does not need to move inward
2. Counterclockwise PAD layout, please refer to this example for counterclockwise placement
3. Enhanced fill strategy, handling spacing between inner and outer rings, inner 10, outer 20. Note that the coordinates of the fill are related to clockwise and counterclockwise, especially the insertion coordinates of the inner filler, which are counterclockwise offset 0 30, clockwise offset -10 20
4. Complex digital IO feature processing, supporting inner and outer ring signals
5. Advanced label placement system, ensuring correct placement of inner and outer ring labels
6. Supports special positioning and rotation of inner PADs

Applicable scenarios:
- Standard dual-ring chip design
- Counterclockwise PAD layout
"""
    }
    return descriptions.get(file_name, "")

@tool
def code_example_search(task_description: str) -> str:
    """
    Search for code examples related to the task description in the local library.
    For layout-related queries, always return single-ring and dual-ring examples.

    Args:
        task_description: A simple description of the task (e.g., 'layout', 'schematic', 'dual ring')

    Returns:
        Content of the relevant example file, or an error message if no match is found.
    """
    try:
        query = task_description.lower().strip()
        
        if not os.path.exists(EXAMPLES_DIR):
            return f"Error: Example directory not found at '{EXAMPLES_DIR}'"
            
        relevant_files = []
        
        # Determine which example files to return based on the query keyword
        if "layout" in query or "dual" in query:
            # Always return two layout examples
            relevant_files = ["layout_generation_example.py", "dual_ring_layout_example.py"]
        elif "schematic" in query:
            relevant_files.append("schematic_generation_example.py")

        if not relevant_files:
            return "No relevant code examples found. Please use 'layout' (layout) or 'schematic' (schematic)."

        result = []
        for target_file in relevant_files:
            file_path = os.path.join(EXAMPLES_DIR, target_file)
            if os.path.exists(file_path):
                # Add example description
                description = get_example_description(target_file)
                result.append(f"""
=== Code Example: {target_file} ===
{description}
--- Code content starts ---
{open(file_path, 'r', encoding='utf-8').read()}
--- Code content ends ---
""")
            else:
                result.append(f"Error: Example file '{target_file}' not found.")
        
        return "\n\n".join(result)

    except Exception as e:
        return f"code_example_search encountered an unexpected error: {e}" 