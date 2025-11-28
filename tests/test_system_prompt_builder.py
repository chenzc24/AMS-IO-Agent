from pathlib import Path
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.app.utils.system_prompt_builder import load_system_prompt_with_profile

# Build and display system prompt
prompt = load_system_prompt_with_profile()
print(f"{'=' * 80}\n{prompt}\n{'=' * 80}\nTotal: {len(prompt)} chars")
