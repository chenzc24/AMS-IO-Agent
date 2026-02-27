import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Any
import threading
import queue
import builtins
import time

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil
import uuid

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
# Input Manager & Event Definitions
# ==========================================

class InputRequest:
    """Event triggered when Agent requests user input"""
    def __init__(self, prompt: str = ""):
        self.prompt = prompt

class ThreadSafeInputManager:
    """Manages input requests between Agent (Thread) and WebUI (Async)"""
    def __init__(self):
        self.input_event = threading.Event()
        self.input_value = None
        self.pending_prompt = None
        self.is_waiting = False
        # Queue to communicate back to the SSE generator
        # Note: This limits us to one active agent run globally for now
        self.response_queue = None 

    def set_response_queue(self, q: queue.Queue):
        self.response_queue = q

    def request_input(self, prompt=""):
        """Called by the agent (via patched input())"""
        logger.info(f"Agent requested input with prompt: {prompt}")
        self.is_waiting = True
        self.pending_prompt = prompt
        
        # Notify Frontend via SSE
        if self.response_queue:
            self.response_queue.put(InputRequest(prompt))
        
        # Wait for API to provide input
        self.input_event.wait()
        
        # Reset
        self.input_event.clear()
        self.is_waiting = False
        value = self.input_value
        self.input_value = None
        logger.info(f"Agent received input: {value}")
        return value

    def submit_input(self, value: str):
        """Called by FastAPI endpoint"""
        if not self.is_waiting:
            return False
        self.input_value = value
        self.input_event.set()
        return True

# Global Singletons
input_manager = ThreadSafeInputManager()
# Patched input function
original_input = builtins.input

def patched_input(prompt=""):
    return input_manager.request_input(prompt)


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

from src.app.layout.editor_confirm_merge import (
    build_confirmed_payload,
    normalize_editor_payload_for_confirm,
    resolve_source_intent_path,
)

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

# ==========================================
# New: File Upload & Static Routes
# ==========================================
# Directory for uploaded files
UPLOAD_DIR = os.path.join(project_root, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Directory for generated outputs
OUTPUT_DIR = os.path.join(project_root, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

@app.post("/api/agent/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the server and return its relative path."""
    try:
        # Generate a safe filename
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return path relative to project root or URL path
        # Assuming frontend serves from same domain or proxies
        return {
            "filename": file.filename,
            "filepath": f"uploads/{unique_filename}",
            "url": f"/uploads/{unique_filename}"
        }
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        return {"error": str(e)}


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

class InputSubmission(BaseModel):
    """Payload for submitting input to the paused agent"""
    value: str

# [ADDED] - PHASE 1: New Agent Chat Request Schema
class AgentChatRequest(BaseModel):
    prompt: str
    stream: bool = True
    reset_memory: bool = False
    files: List[str] = []  # List of file paths or contents if needed


class EditorConfirmRequest(BaseModel):
    source_path: str
    data: Any

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

# [ADDED] - PHASE 1: New SSE Formatter for structured events
def format_agent_event(event_type: str, data: Any) -> str:
    # Ensure data is JSON serializable
    payload = None
    if hasattr(data, "dict"):
        payload = data.dict()
    elif hasattr(data, "to_string"): # For AgentImage/AgentText
        payload = str(data.to_string())
    elif isinstance(data, (list, dict)):
        # Keep lists and dicts AS IS (so json.dumps handles them)
        payload = data
    else:
        # Fallback to string
        payload = str(data)
        
    packet = {
        "type": event_type,
        "content": payload,
        "timestamp": 0 # TODO: Add real timestamp
    }
    return f"event: agent_event\ndata: {json.dumps(packet)}\n\n"

# ==========================================
# Endpoints
# ==========================================
@app.post("/api/agent/submit_input")
async def submit_input(submission: InputSubmission):
    """Resume the paused agent with the provided input value"""
    if input_manager.submit_input(submission.value):
        logger.info(f"Input submitted: {submission.value}")
        return {"status": "success", "message": "Input received, agent resuming."}
    else:
        logger.warning("Received input submission but agent was not waiting.")
        raise HTTPException(status_code=400, detail="Agent is not waiting for input.")


@app.post("/api/agent/editor/confirm")
async def confirm_editor_layout(request: EditorConfirmRequest):
    """Persist IO editor data and trigger backend wait-loop continuation."""
    try:
        raw_path = (request.source_path or "").strip()
        if not raw_path:
            raise HTTPException(status_code=400, detail="source_path is required")

        normalized_path = raw_path.lstrip("/")
        if normalized_path.startswith("output/"):
            target_path = (project_root / normalized_path).resolve()
        elif normalized_path.startswith("turn_"):
            target_path = (Path(OUTPUT_DIR) / normalized_path).resolve()
        else:
            target_path = (Path(OUTPUT_DIR) / normalized_path).resolve()

        output_root = Path(OUTPUT_DIR).resolve()
        if not str(target_path).startswith(str(output_root)):
            raise HTTPException(status_code=400, detail="source_path must be inside output/")

        target_path.parent.mkdir(parents=True, exist_ok=True)

        source_intent_path = resolve_source_intent_path(target_path)
        source_payload = None
        if source_intent_path and source_intent_path.exists():
            with open(source_intent_path, "r", encoding="utf-8") as f:
                source_payload = json.load(f)

        normalized_payload = normalize_editor_payload_for_confirm(request.data)
        confirmed_payload = build_confirmed_payload(source_payload or {}, normalized_payload)

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(confirmed_payload, f, ensure_ascii=False, indent=2)

        written_paths = [str(target_path.relative_to(project_root))]

        # T28 compatibility: also emit *_confirmed.json (T180 still uses intermediate file mtime).
        if target_path.name.endswith("_intermediate_editor.json"):
            confirmed_path = target_path.with_name(
                target_path.name.replace("_intermediate_editor.json", "_confirmed.json")
            )
            with open(confirmed_path, "w", encoding="utf-8") as f:
                json.dump(confirmed_payload, f, ensure_ascii=False, indent=2)
            written_paths.append(str(confirmed_path.relative_to(project_root)))

        return {
            "ok": True,
            "written": written_paths,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to persist editor confirmation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        response_queue = queue.Queue()
        input_manager.set_response_queue(response_queue)
        
        # Define agent runner to execute in a separate thread
        def run_agent_worker():
            # Patch input
            builtins.input = patched_input
            try:
                # Run the agent (synchronous generator) matches smolagents API
                for step in agent_instance.run(query, stream=True):
                    response_queue.put(step)
                response_queue.put("DONE")
            except Exception as e:
                logger.error(f"Error in agent_runner: {e}")
                response_queue.put(e)
            finally:
                # Restore input
                builtins.input = original_input
                input_manager.set_response_queue(None)

        # Start agent thread
        agent_thread = threading.Thread(target=run_agent_worker)
        agent_thread.start()

        # Main SSE loop: consume from queue
        try:
            step_idx = 1
            while True:
                # Poll queue safely
                try:
                    # Non-blocking check or short timeout
                    item = await asyncio.to_thread(response_queue.get, timeout=0.1)
                except queue.Empty:
                    if not agent_thread.is_alive() and response_queue.empty():
                        break
                    # Keep yielding something (or nothing) to keep connection alive if needed
                    # But text/event-stream doesn't require constant data
                    await asyncio.sleep(0.05)
                    continue
                
                if item == "DONE":
                    break
                    
                if isinstance(item, Exception):
                    yield format_sse_event({
                        "completion": f"\n\n❌ An error occurred: {str(item)}",
                        "stop_reason": "error",
                        "model": "ams-io-agent"
                    })
                    break

                # Handle Input Request Event
                if isinstance(item, InputRequest):
                    yield f"event: input_request\ndata: {json.dumps({'prompt': item.prompt})}\n\n"
                    
                    # Yield a display message to the user as well
                    yield format_sse_event({
                        "completion": f"\n\n❓ **Input Requested**: {item.prompt}\n",
                        "stop_reason": None,
                        "model": "ams-io-agent"
                    })
                    continue
                
                # Check if it's a step object
                step = item
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

# ==========================================
# PHASE 1: New Structured Agent Endpoint
# ==========================================
@app.post("/api/agent/chat")
async def agent_chat(request: AgentChatRequest):
    logger.info(f"Received Agent Request: {request.prompt[:50]}...")
    
    if not agent_instance:
         # Initialize on demand if not ready (fallback)
         try:
             await startup_event()
         except:
             return {"error": "Agent not initialized"}
         
    # Create turn-specific working directory
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    turn_dir_name = f"turn_{timestamp}"
    turn_dir = os.path.join(OUTPUT_DIR, turn_dir_name)
    os.makedirs(turn_dir, exist_ok=True)
    relative_turn_dir = f"output/{turn_dir_name}"
    
    # Inject directory instruction into prompt
    # We append this instruction so the agent knows where to save files for this turn
    enhanced_prompt = f"{request.prompt}\n\n[SYSTEM INSTRUCTION: Save ALL generated files (images, code, reports) to the directory '{relative_turn_dir}'. Do not use 'output/' root.]"

    async def structured_event_generator():
        response_queue = queue.Queue()
        input_manager.set_response_queue(response_queue)
        
        # Track sent files to avoid duplicates
        sent_files = set()

        def scan_and_yield_files():
            files_to_send = []
            if os.path.exists(turn_dir):
                for root, dirs, files in os.walk(turn_dir):
                    for file in files:
                        file_abs_path = os.path.join(root, file)
                        # Check modification time or just existence? 
                        # Using abs path as ID for simplicity
                        if file_abs_path not in sent_files:
                            sent_files.add(file_abs_path)
                            file_rel_path = os.path.relpath(file_abs_path, project_root)
                            files_to_send.append({
                                "name": file,
                                "path": file_rel_path,
                                "url": f"/{file_rel_path}" 
                            })
            return files_to_send

        # Define agent runner to execute in a separate thread
        def run_agent_worker():
            # Patch input
            builtins.input = patched_input
            try:
                # 1. Yield an "ack" with directory info
                response_queue.put(format_agent_event("status", f"Starting Agent... (Output Dir: {turn_dir_name})"))
                
                # Check for existing files first (e.g. from previous turns or externally created)
                # But actually we are in a new turn dir, so it should be empty.
                pass 
                
                # 2. Run Agent
                for step in agent_instance.run(enhanced_prompt, stream=True, reset=request.reset_memory):
                    response_queue.put(step)
                    # Force yield a scan check after each step
                    response_queue.put("CHECK_FILES")
                
                response_queue.put("DONE")
            except Exception as e:
                logger.error(f"Error in agent_runner: {e}")
                response_queue.put(e)
            finally:
                # Restore input
                builtins.input = original_input
                input_manager.set_response_queue(None)

        # Start agent thread
        agent_thread = threading.Thread(target=run_agent_worker)
        agent_thread.start()

        try:
            while True:
                # Poll queue safely
                try:
                    # Non-blocking check or short timeout
                    item = await asyncio.to_thread(response_queue.get, timeout=0.1)
                except queue.Empty:
                    if not agent_thread.is_alive() and response_queue.empty():
                        break
                    
                    # [Polling] Scan for new files periodically during idle/slow moments
                    new_files = scan_and_yield_files()
                    if new_files:
                        yield format_agent_event("files_generated", new_files)

                    # Keep yielding something (or nothing) to keep connection alive if needed
                    await asyncio.sleep(0.05)
                    continue
                
                if item == "DONE":
                    break

                if item == "CHECK_FILES":
                    # Explicit signal to scan
                    new_files = scan_and_yield_files()
                    if new_files:
                        yield format_agent_event("files_generated", new_files)
                    continue
                    
                if isinstance(item, Exception):
                     yield format_agent_event("agent_error", str(item))
                     break
                     
                # Handle pre-formatted string (ack)
                if isinstance(item, str) and item.startswith("event:"):
                    yield item
                    continue

                # Handle Input Request Event
                if isinstance(item, InputRequest):
                    # [Pre-Input] Scan for any files generated just before asking
                    new_files = scan_and_yield_files()
                    if new_files:
                        yield format_agent_event("files_generated", new_files)
                        
                    yield format_agent_event("input_request", {"prompt": item.prompt})
                    continue

                # Process steps
                step = item
                
                # --- CASE A: Reasoning / Tool Plan (ActionStep) ---
                if isinstance(step, ActionStep):
                    # [Step-Bound] Scan for new files after each step execution finishes
                    # (Usually files are created during tool execution within the step)
                    
                    # A.1: The thought/plan
                    if hasattr(step, 'model_output') and step.model_output:
                        clean_thought = step.model_output.strip()
                        # [Fix] Ensure code blocks are closed if they look open
                        # If odd number of triple backticks, append one
                        triple_ticks = clean_thought.count("```")
                        if triple_ticks % 2 != 0:
                            clean_thought += "\n```"
                            
                        yield format_agent_event("agent_thought", clean_thought)
                    
                    # A.2: The tool call (if parsed/available separately)
                    if hasattr(step, 'tool_calls') and step.tool_calls:
                        for tc in step.tool_calls:
                            # Convert ToolCall object to dict safely
                            tc_dict = {
                                "name": getattr(tc, 'name', 'unknown'),
                                "arguments": getattr(tc, 'arguments', {})
                            }
                            yield format_agent_event("tool_call", tc_dict)

                    # A.3: The observation (Result)
                    if step.observations:
                        yield format_agent_event("tool_result", step.observations)
                        
                    if step.error:
                        yield format_agent_event("agent_error", str(step.error))

                # --- CASE B: Final Answer Stream (ChatMessageStreamDelta) ---
                elif isinstance(step, ChatMessageStreamDelta):
                    if step.content:
                        # Raw text chunks for the final answer
                        yield format_agent_event("final_answer_delta", step.content)

                # --- CASE C: Final Answer Complete (FinalAnswerStep) ---
                elif isinstance(step, FinalAnswerStep):
                    # Could send the whole final object if needed
                    yield format_agent_event("final_answer_done", str(step.output))

            # 3. Finish - One last scan
            try:
                # Save Memory
                log_path = project_root / "logs" / f"web_session_{os.getpid()}.json"
                save_agent_memory(agent_instance, log_path, None)
                
                new_files = scan_and_yield_files()
                if new_files:
                    yield format_agent_event("files_generated", new_files)
                    
            except Exception as e:
                logger.error(f"Post-processing failed: {e}")
                
            yield format_agent_event("status", "Finished")
            
        except Exception as e:
            logger.error(f"Agent Execution Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            yield format_agent_event("agent_error", str(e))

    return StreamingResponse(structured_event_generator(), media_type="text/event-stream")


# ==========================================
# File System API (New)
# ==========================================

class FileContentRequest(BaseModel):
    path: str
    content: Optional[str] = None

@app.get("/api/files")
async def list_files():
    """List project files recursively, respecting basic ignore rules."""
    ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'logs', 'site-packages'}
    ignore_files = {'.DS_Store'}
    
    file_list = []
    
    for root, dirs, files in os.walk(project_root):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file in ignore_files:
                continue
                
            full_path = Path(root) / file
            rel_path = full_path.relative_to(project_root)
            
            file_list.append({
                "path": str(rel_path),
                "name": file,
                "type": "file",
                "size": full_path.stat().st_size
            })
            
    return {"files": file_list}

@app.get("/api/files/content")
async def get_file_content(path: str):
    """Get the content of a file."""
    try:
        # Sanitize path to prevent traversal
        safe_path = (project_root / path).resolve()
        if not str(safe_path).startswith(str(project_root)):
             return {"error": "Access denied"}
             
        if not safe_path.exists():
            return {"error": "File not found"}
            
        return {"content": safe_path.read_text(encoding='utf-8', errors='replace')}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/files/content")
async def save_file_content(request: FileContentRequest):
    """Save content to a file."""
    try:
        safe_path = (project_root / request.path).resolve()
        # Allow creating new files within project root
        if not str(safe_path).startswith(str(project_root)):
             return {"error": "Access denied"}
             
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(request.content, encoding='utf-8')
        return {"status": "success", "path": str(request.path)}
    except Exception as e:
        return {"error": str(e)}

