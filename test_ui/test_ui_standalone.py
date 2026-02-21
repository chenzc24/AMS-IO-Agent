
import sys
import os
import shutil
import time
from pathlib import Path
from typing import Generator

# Add paths to ensure imports work
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "AMS-IO-Agent"))

try:
    from src.app.utils.custom_gradio_interface import IOAgentGradioUI
    from smolagents.memory import ActionStep, FinalAnswerStep
    from smolagents.agent_types import AgentText
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# -------------------------------------------------------------------------
# Mock Agent for UI Testing
# -------------------------------------------------------------------------
class MockAgent:
    def __init__(self):
        self.name = "Mock IO Agent"
        self.description = "A standalone mock agent for UI testing. It echoes your input and pretends to think."
        self.memory = MockMemory()
        self.model = MockModel()

    def run(self, task: str, images=None, stream=False, reset=False, additional_args=None) -> Generator:
        """Simulates the agent thinking and running tools"""
        
        # yield a fake thought
        yield f"**Thinking...**\nReceived task: `{task}`. I will verify the IO Ring layout."
        time.sleep(0.5)

        # yield a fake action step (Tool Call)
        # Note: In real smolagents, this yields ActionStep objects. 
        # We need to mock minimal structure if stream_to_gradio expects it.
        # But stream_to_gradio handles ActionStep, PlanningStep, etc.
        # Let's just yield simple text logs for the mock to verify Chat interface works.
        # If we want to test step rendering, we need to construct ActionStep.
        
        yield "**Plan:**\n1. Check layout file.\n2. Confirm sync.\n"
        
        # Simulate output
        yield f"Confirmed. The IO layout currently loaded has {len(task)} chars in description."
        
        # Yield final answer
        yield FinalAnswerStep(output=AgentText(f"I have received your update. You can continue editing in the Layout Editor tab."))

class MockMemory:
    def reset(self):
        pass

class MockModel:
    flatten_messages_as_text = True


# -------------------------------------------------------------------------
# Setup Test Data
# -------------------------------------------------------------------------
def setup_test_data():
    target_file = Path("io_ring_intent_graph.json")
    
    # Use the specific test file mentioned by user
    source_file = Path("AMS-IO-Agent/user_data/io_ring_12x12/io_ring_intent_graph.json")
    
    if source_file.exists():
        print(f"Copying test data from {source_file} to {target_file}...")
        shutil.copy(source_file, target_file)
    else:
        print(f"Warning: Test source file {source_file} not found. Using default empty JSON.")
        with open(target_file, "w") as f:
            f.write('{"ring_config": {}, "instances": []}')

    # Important: To ensure the UI uses this fallback file, we might need to 
    # warn the user if `output/generated` has newer files.
    gen_dir = Path("output/generated")
    if gen_dir.exists():
        latest = None
        try:
             subdirs = [d for d in gen_dir.iterdir() if d.is_dir()]
             if subdirs:
                 latest = max(subdirs, key=lambda p: p.name)
        except: pass
        
        if latest:
            print("---------------------------------------------------------------")
            print(f"NOTE: A generated folder exists at {latest}")
            print("The UI prefers loading from output/generated/ if available.")
            print("To verify YOUR test_json, please ensure the UI falls back to")
            print("io_ring_intent_graph.json or check the console logs to see which file loaded.")
            print("---------------------------------------------------------------")

# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------
if __name__ == "__main__":
    setup_test_data()
    
    print("Initializing Mock Agent...")
    agent = MockAgent()
    
    print("Launching Standalone Gradio UI...")
    ui = IOAgentGradioUI(agent=agent, file_upload_folder="uploads")
    
    # Launch with share=False for local test, debug=True
    ui.launch(share=False, debug=True, allowed_paths=[os.getcwd()])
