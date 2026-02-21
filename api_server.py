import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Any

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api_server")

# ==========================================
# Path Setup
# ==========================================
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))
os.chdir(project_root)

load_dotenv()

# ==========================================
# Agent Imports
# ==========================================
try:
    from src.app.utils.config_utils import load_config_from_yaml, Config, get_model_config
    from src.app.utils.multi_agent_factory import create_master_agent_with_workers
    from src.app.utils.agent_utils import save_agent_memory
    from smolagents.memory import ActionStep, FinalAnswerStep
    from smolagents.models import ChatMessageStreamDelta
    logger.info("✅ Agent components imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import agent components: {e}")
    sys.exit(1)

# ==========================================
# Initialize FastAPI
# ==========================================
app = FastAPI(title="AMS IO Agent Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Agent Instance
agent_instance = None

@app.on_event("startup")
async def startup_event():
    global agent_instance
    try:
        logger.info("loading configuration...")
        config_dict = load_config_from_yaml("config.yaml")
        # Ensure we're dealing with a dict mostly, but if using Config object wrapper:
        config = Config(config_dict)
        
        # FIX: Explicitly resolve model name and get the dict config
        model_name = getattr(config.model, 'active', getattr(config.model, 'name', 'claude'))
        logger.info(f"Resolved model name: {model_name}")
        
        # Fetch the actual model configuration dictionary using the utility
        model_config = get_model_config(model_name)
        
        logger.info(f"Initializing Agent with model config dict...")
        # Now passing the dictionary 'model_config' instead of the object 'config.model'
        # Explicitly pass the correct tools_config path from the config object or default
        tools_config_path = getattr(config.tools, 'config_path', "src/tools/tools_config.yaml")
        agent_instance = create_master_agent_with_workers(model_config, tools_config_path=tools_config_path)
        logger.info("🤖 Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing agent: {e}")
        # Continue to allow app to start, but requests will fail if agent is None

# ==========================================
# Models
# ==========================================
class AnthropicCompletionRequest(BaseModel):
    prompt: str
    model: str = "claude-2.1"
    max_tokens_to_sample: int = 4000
    stop_sequences: List[str] = []
    stream: bool = True
    temperature: float = 0.7
    top_k: int = -1
    top_p: int = -1

# ==========================================
# Helpers
# ==========================================
def extract_last_user_message(full_prompt: str) -> str:
    """
    Parses the Anthropic prompt format into a contextual task description.
    Instead of just taking the last message, it reconstructs the conversation history
    so the Agent can understand cross-turn context (e.g., "Use that file" -> refers to previous file).
    """
    if not full_prompt:
        return ""
    
    # Check if there is history (more than one "Human:" marker)
    human_marker = "\n\nHuman:"
    if full_prompt.count(human_marker) <= 1:
        # Fallback to simple extraction for single-turn or raw prompts
        clean_prompt = full_prompt.strip()
        if clean_prompt.endswith("Assistant:"):
            clean_prompt = clean_prompt[:-10].strip()
        
        if human_marker in clean_prompt:
            return clean_prompt.split(human_marker)[-1].strip()
        elif "Human:" in clean_prompt: # Handling edge cases with different spacing
             return clean_prompt.rsplit("Human:", 1)[-1].strip()
        return clean_prompt

    # Multi-turn context injection
    logger.info("Detected multi-turn conversation. Constructing contextual prompt...")
    
    # Split raw string into turns. Typical structure:
    # "Human: Msg1\n\nAssistant: Ans1\n\nHuman: Msg2\n\nAssistant:"
    
    # 1. Remove the trailing empty Assistant prompt
    clean_prompt = full_prompt.strip() 
    if clean_prompt.endswith("Assistant:"):
        clean_prompt = clean_prompt[:-10].strip()
        
    # 2. Split by Human marker
    # The first element might be empty or system prompt.
    fragments = clean_prompt.split(human_marker)
    
    context_str = "You are an intelligent agent interacting with a user. Here is the conversation history for context:\n\n"
    
    current_request = ""
    
    for i, fragment in enumerate(fragments):
        fragment = fragment.strip()
        if not fragment:
            continue
            
        if "\n\nAssistant:" in fragment:
            # This turns contains User query + AI reply
            parts = fragment.split("\n\nAssistant:")
            user_msg = parts[0].strip()
            ai_msg = parts[1].strip() if len(parts) > 1 else ""
            
            context_str += f"[User]: {user_msg}\n"
            if ai_msg:
                context_str += f"[AI]: {ai_msg}\n"
        else:
            # This is likely the LAST fragment (Current Request) 
            # OR a fragment where AI hasn't replied yet (rare in this format but possible)
            if i == len(fragments) - 1:
                current_request = fragment
            else:
                context_str += f"[User]: {fragment}\n"
    
    # Construct the final "Task" for the agent
    final_task = f"""{context_str}
    
=========================================
[Current User Request]:
{current_request}
=========================================
Based on the history above and the current request, please proceed with the necessary actions.
"""
    return final_task

def format_sse_event(data_dict: dict) -> str:
    return f"event: completion\ndata: {json.dumps(data_dict)}\n\n"

# ==========================================
# Endpoints
# ==========================================
@app.post("/anthropic/v1/complete")
async def complete(request: AnthropicCompletionRequest):
    logger.info(f"DEBUG: Raw received prompt: {repr(request.prompt)}")
    query = extract_last_user_message(request.prompt)
    logger.info(f"Received query length: {len(query)}")
    logger.info(f"DEBUG: Extracted query: {repr(query)}")
    
    # [FIX] Handle empty query from frontend keep-alive or malformed requests
    if not query.strip():
        logger.warning("Empty query received. Returning default prompt request.")
        async def empty_response_generator():
            yield format_sse_event({
                "completion": " 收到空指令，请问有什么可以帮您？",
                "stop_reason": "stop_sequence",
                "model": "ams-io-agent"
            })
        return StreamingResponse(empty_response_generator(), media_type="text/event-stream")

    if not agent_instance:
         return {"error": "Agent not initialized"}

    async def event_generator():
        try:
            step_idx = 1
            # Run the agent (synchronous generator) matches smolagents API
            for step in agent_instance.run(query, stream=True):
                output_chunk = ""
                
                if isinstance(step, ActionStep):
                    # Format Action Step (Thought + Tool)
                    output_chunk += f"\n\n> **Step {step_idx}**\n"
                    
                    # [Check 1] The LLM's raw thought and code generation
                    # For CodeAgent, this contains the "Thought: ..." and the "Code: ```python...```"
                    if hasattr(step, 'model_output') and step.model_output:
                        output_chunk += f"{step.model_output.strip()}\n"
                    
                    # [Check 2] Explicit Tool Calls (if separate from model_output)
                    if hasattr(step, 'tool_calls') and step.tool_calls:
                        for tool_call in step.tool_calls:
                            t_name = getattr(tool_call, 'name', 'tool')
                            # Check arguments
                            t_args = getattr(tool_call, 'arguments', None)
                            
                            # Only print if not redundant (CodeAgent usually puts code in model_output)
                            # But if arguments are parsed separately, showing them is helpful.
                            if t_name != 'python_interpreter': # Avoid double printing code
                                output_chunk += f"> *Tool Call*: `{t_name}`\n"
                                if t_args:
                                    output_chunk += f"> *Args*: `{t_args}`\n"

                    # Observations/Results
                    if step.observations:
                        obs = str(step.observations).strip()
                        # Force flush full observation to log for debug
                        logger.info(f"Step {step_idx} Observation: {obs}")
                        
                        if len(obs) > 2000: # Increased limit
                            obs = obs[:2000] + "... (truncated)"
                        output_chunk += f"\n> *Observation*: \n{obs}\n"
                    
                    step_idx += 1
                    output_chunk += "\n"

                elif isinstance(step, ChatMessageStreamDelta):
                    # Final answer streaming
                    if step.content:
                        output_chunk += step.content

                elif isinstance(step, FinalAnswerStep):
                    pass

                if output_chunk:
                    yield format_sse_event({
                        "completion": output_chunk,
                        "stop_reason": None,
                        "model": "ams-io-agent"
                    })
                    
            # Final Event when done
            # [ADDED] Force save memory to disk for debugging and history tracking
            try:
                # Mock an args object if needed by save_agent_memory, or just pass None if it allows
                # Assuming save_agent_memory(agent, log_file, start_time) structure
                # We'll create a dummy log path
                log_path = project_root / "logs" / f"web_session_{os.getpid()}.json"
                save_agent_memory(agent_instance, log_path, None)
                logger.info(f"Session memory saved to {log_path}")
            except Exception as mem_err:
                 logger.error(f"Failed to save memory: {mem_err}")

            yield format_sse_event({
                "completion": "",
                "stop_reason": "stop_sequence", 
                "model": "ams-io-agent"
            })
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            # Still try to save memory on error
            try:
                log_path = project_root / "logs" / f"web_session_error_{os.getpid()}.json"
                save_agent_memory(agent_instance, log_path, None)
            except: 
                pass
                
            yield format_sse_event({
                "completion": f"\n\n**Error**: {str(e)}", 
                "stop_reason": "stop_sequence",
                "model": "error"
            })

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
async def health():
    return {"status": "ok", "agent_initialized": agent_instance is not None}
