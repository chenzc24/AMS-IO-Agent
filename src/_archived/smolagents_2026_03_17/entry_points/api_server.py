import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Any, Dict
import threading
import queue
import builtins
import time

from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
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
# Phase 6 hardening configuration
# ==========================================
CHAT_SESSIONS_RETENTION_DAYS = 0
CHAT_SESSIONS_DEFAULT_PAGE_SIZE = int(os.environ.get("CHAT_SESSIONS_DEFAULT_PAGE_SIZE", "50"))
CHAT_SESSIONS_MAX_PAGE_SIZE = int(os.environ.get("CHAT_SESSIONS_MAX_PAGE_SIZE", "200"))
CHAT_RECORD_MAX_TEXT_CHARS = int(os.environ.get("CHAT_RECORD_MAX_TEXT_CHARS", "120000"))
CHAT_RECORD_MAX_DETAIL_COUNT = int(os.environ.get("CHAT_RECORD_MAX_DETAIL_COUNT", "300"))
CHAT_RECORD_MAX_DETAIL_TEXT_CHARS = int(os.environ.get("CHAT_RECORD_MAX_DETAIL_TEXT_CHARS", "30000"))
CHAT_RECORD_MAX_ASSET_COUNT = int(os.environ.get("CHAT_RECORD_MAX_ASSET_COUNT", "300"))
CHAT_RECORD_MAX_ATTACHMENT_COUNT = int(os.environ.get("CHAT_RECORD_MAX_ATTACHMENT_COUNT", "100"))

chat_metrics_lock = threading.Lock()
chat_metrics = {
    "history_load_count": 0,
    "history_load_total_latency_ms": 0.0,
    "chat_write_success_count": 0,
    "chat_write_error_count": 0,
}

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


class RunControl:
    """Per-run pause/resume coordination for the streaming worker."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self._pause_requested = False
        self._is_paused = False
        self._resume_event = threading.Event()
        self._resume_value = ""
        self._lock = threading.Lock()

    def request_pause(self) -> bool:
        with self._lock:
            if self._is_paused:
                return False
            self._pause_requested = True
            return True

    def consume_pause_request(self) -> bool:
        with self._lock:
            should_pause = self._pause_requested
            if should_pause:
                self._pause_requested = False
                self._is_paused = True
                self._resume_value = ""
                self._resume_event.clear()
            return should_pause

    def wait_for_resume(self) -> str:
        self._resume_event.wait()
        with self._lock:
            value = self._resume_value
            self._resume_value = ""
            self._is_paused = False
            self._resume_event.clear()
            return value

    def resume(self, value: str) -> bool:
        with self._lock:
            if not self._is_paused:
                return False
            self._resume_value = value
            self._resume_event.set()
            return True

    def status(self) -> str:
        with self._lock:
            if self._is_paused:
                return "paused"
            if self._pause_requested:
                return "pause_requested"
            return "running"

# Global Singletons
input_manager = ThreadSafeInputManager()
run_controls = {}
run_controls_lock = threading.Lock()
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
    from src.app.utils.agent_factory import load_prompt_from_config
    from src.app.utils.agent_utils import save_agent_memory
    from src.app.utils.system_prompt_builder import load_system_prompt_with_profile
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
GENERATED_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "generated")
os.makedirs(GENERATED_OUTPUT_DIR, exist_ok=True)

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
runtime_config = None
active_model_name = None


def _clean_optional_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return str(value).strip()


def _get_config_prompt_defaults() -> tuple:
    """Read prompt defaults from loaded runtime config safely."""
    prompt_text = ""
    prompt_key = ""
    prompt_config_file = "user_prompt"

    if runtime_config and hasattr(runtime_config, "prompt"):
        prompt_text = _clean_optional_text(getattr(runtime_config.prompt, "text", ""))
        prompt_key = _clean_optional_text(getattr(runtime_config.prompt, "key", ""))
        configured_path = _clean_optional_text(getattr(runtime_config.prompt, "config_path", ""))
        if configured_path:
            prompt_config_file = configured_path

    return prompt_text, prompt_key, prompt_config_file


def resolve_effective_prompt(
    request_prompt: Optional[str] = None,
    request_prompt_text: Optional[str] = None,
    request_prompt_key: Optional[str] = None,
    request_prompt_config_file: Optional[str] = None,
) -> str:
    """
    Resolve prompt with priority aligned to main behavior, with API interactive fallback:
    1) PROMPT_TEXT env var
    2) Explicit request prompt (interactive payload)
    3) Request prompt_text
    4) Request prompt_key + prompt_config_file
    5) Config prompt.text
    6) Config prompt.key + config prompt_config_path
    """
    env_prompt = _clean_optional_text(os.environ.get("PROMPT_TEXT"))
    if env_prompt:
        return env_prompt

    direct_request_prompt = _clean_optional_text(request_prompt)
    if direct_request_prompt:
        return direct_request_prompt

    direct_prompt_text = _clean_optional_text(request_prompt_text)
    if direct_prompt_text:
        return direct_prompt_text

    request_prompt_key = _clean_optional_text(request_prompt_key)
    request_prompt_config_file = _clean_optional_text(request_prompt_config_file)
    if request_prompt_key:
        loaded = load_prompt_from_config(
            request_prompt_key,
            request_prompt_config_file or "user_prompt",
        )
        if loaded:
            return str(loaded).strip()

    config_prompt_text, config_prompt_key, config_prompt_config_file = _get_config_prompt_defaults()
    if config_prompt_text:
        return config_prompt_text

    if config_prompt_key:
        loaded = load_prompt_from_config(config_prompt_key, config_prompt_config_file)
        if loaded:
            return str(loaded).strip()

    return ""


def persist_session_memory(session_tag: str, first_user_input: Optional[str] = None) -> None:
    """Persist session memory with a stable per-session log directory."""
    if not agent_instance:
        return

    try:
        log_dir = project_root / "logs" / session_tag
        config_info = {
            "model_name": active_model_name,
            "first_user_input": first_user_input,
        }
        save_agent_memory(agent_instance, str(log_dir), config_info=config_info)
        logger.info(f"Session memory saved under: {log_dir}")
    except Exception as e:
        logger.error(f"Failed to save memory: {e}")

@app.on_event("startup")
async def startup_event():
    global agent_instance, runtime_config, active_model_name
    try:
        logger.info("loading configuration...")
        config_dict = load_config_from_yaml("config.yaml")
        # Ensure we're dealing with a dict mostly, but if using Config object wrapper:
        config = Config(config_dict)
        runtime_config = config
        
        # FIX: Explicitly resolve model name and get the dict config
        model_name = getattr(config.model, 'active', getattr(config.model, 'name', 'claude'))
        active_model_name = model_name
        logger.info(f"Resolved model name: {model_name}")
        
        # Fetch the actual model configuration dictionary using the utility
        model_config = get_model_config(model_name)
        
        logger.info(f"Initializing Agent with model config dict...")
        # Now passing the dictionary 'model_config' instead of the object 'config.model'
        # Explicitly pass the correct tools_config path from the config object or default
        tools_config_path = getattr(config.tools, 'config_path', "src/tools/tools_config.yaml")
        agent_instance = create_master_agent_with_workers(model_config, tools_config_path=tools_config_path)

        system_prompt = load_system_prompt_with_profile()
        if system_prompt:
            agent_instance.instructions = (
                f"{system_prompt}\n\n{agent_instance.instructions}"
            )

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


class RunResumeSubmission(BaseModel):
    value: str = ""

# [ADDED] - PHASE 1: New Agent Chat Request Schema
class AgentChatRequest(BaseModel):
    prompt: str = ""
    prompt_text: Optional[str] = None
    prompt_key: Optional[str] = None
    prompt_config_file: Optional[str] = None
    stream: bool = True
    reset_memory: bool = False
    files: List[str] = []  # List of file paths or contents if needed
    run_id: Optional[str] = None
    session_id: Optional[str] = None


# ==========================================
# PHASE 0: Chat Record Contract (Design Lock)
# ==========================================
class ChatRecordFileRefDTO(BaseModel):
    name: str
    path: str
    url: str


class ChatAttachmentDTO(BaseModel):
    id: str
    name: str
    path: str
    url: str
    mime_type: Optional[str] = Field(default=None, alias="mimeType")
    category: Optional[str] = None
    size: Optional[int] = None
    timestamp: int


class AssistantDetailBlockDTO(BaseModel):
    id: str
    type: str
    content: str
    files: List[ChatRecordFileRefDTO] = Field(default_factory=list)
    timestamp: int


class ChatAssetDTO(BaseModel):
    id: str
    name: str
    url: str
    type: str
    timestamp: int


class ChatMessageDTO(BaseModel):
    id: str
    role: str
    text: str
    main_text: Optional[str] = Field(default=None, alias="mainText")
    is_complete: Optional[bool] = Field(default=None, alias="isComplete")
    created_at: int = Field(alias="createdAt")
    sequence: int
    details: List[AssistantDetailBlockDTO] = Field(default_factory=list)
    assets: List[ChatAssetDTO] = Field(default_factory=list)
    attachments: List[ChatAttachmentDTO] = Field(default_factory=list)


class ChatSessionSummaryDTO(BaseModel):
    id: str
    name: str
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")
    message_count: int = Field(alias="messageCount")


class ChatSessionDetailDTO(BaseModel):
    id: str
    name: str
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")
    messages: List[ChatMessageDTO]


class CreateChatSessionRequest(BaseModel):
    id: str
    name: str = "New Chat"
    created_at: Optional[int] = Field(default=None, alias="createdAt")
    updated_at: Optional[int] = Field(default=None, alias="updatedAt")


class AppendChatMessagesRequest(BaseModel):
    messages: List[ChatMessageDTO] = Field(default_factory=list)


class UpdateChatSessionRequest(BaseModel):
    name: str


class AppendChatMessagesResponse(BaseModel):
    accepted: int
    skipped: int
    session: ChatSessionDetailDTO


class DeleteChatSessionResponse(BaseModel):
    status: str
    session_id: str = Field(alias="sessionId")


class ChatOpsMetricsResponse(BaseModel):
    history_load_count: int = Field(alias="historyLoadCount")
    history_load_avg_latency_ms: float = Field(alias="historyLoadAvgLatencyMs")
    chat_write_success_count: int = Field(alias="chatWriteSuccessCount")
    chat_write_error_count: int = Field(alias="chatWriteErrorCount")
    chat_write_error_rate: float = Field(alias="chatWriteErrorRate")


# Canonical ID mapping locked in Phase 0.
# frontend chatId == backend session_id
CHAT_RECORD_ID_MAPPING = "frontend.chatId == backend.session_id"

# Transition policy locked in Phase 0.
# During migration, backend is target source; frontend local cache is temporary fallback.
CHAT_RECORD_TRANSITION_POLICY = "local_fallback_during_migration"


def record_history_load_latency(latency_ms: float) -> None:
    with chat_metrics_lock:
        chat_metrics["history_load_count"] += 1
        chat_metrics["history_load_total_latency_ms"] += max(latency_ms, 0.0)


def record_chat_write_result(success: bool) -> None:
    with chat_metrics_lock:
        key = "chat_write_success_count" if success else "chat_write_error_count"
        chat_metrics[key] += 1


def build_chat_metrics_snapshot() -> ChatOpsMetricsResponse:
    with chat_metrics_lock:
        history_count = int(chat_metrics["history_load_count"])
        total_latency = float(chat_metrics["history_load_total_latency_ms"])
        write_success = int(chat_metrics["chat_write_success_count"])
        write_error = int(chat_metrics["chat_write_error_count"])

    write_total = write_success + write_error
    return ChatOpsMetricsResponse(
        historyLoadCount=history_count,
        historyLoadAvgLatencyMs=(total_latency / history_count) if history_count else 0.0,
        chatWriteSuccessCount=write_success,
        chatWriteErrorCount=write_error,
        chatWriteErrorRate=(write_error / write_total) if write_total else 0.0,
    )


class ChatSessionReadStore:
    """Phase 1/3 adapter for backend-loaded chat sessions (read + write)."""

    def __init__(self, store_path: Path):
        self.store_path = store_path
        self._lock = threading.Lock()
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_store(self) -> dict:
        if not self.store_path.exists():
            return {"sessions": []}

        try:
            payload = json.loads(self.store_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                sessions = payload.get("sessions", [])
                if isinstance(sessions, list):
                    return {"sessions": sessions}
        except Exception as exc:
            logger.warning(f"Failed to read chat session store: {exc}")

        return {"sessions": []}

    def _write_store(self, payload: Dict[str, Any]) -> None:
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        self.store_path.write_text(serialized, encoding="utf-8")

    def _apply_retention_policy_locked(self, payload: Dict[str, Any]) -> bool:
        # Retention cleanup intentionally disabled by requirement.
        void_payload = payload
        del void_payload
        return True

    @staticmethod
    def _model_to_dict(model: Any) -> dict:
        if hasattr(model, "model_dump"):
            return model.model_dump(by_alias=True)
        return model.dict(by_alias=True)

    @staticmethod
    def _truncate_text(value: Any, max_chars: int) -> str:
        text = str(value or "")
        if len(text) <= max_chars:
            return text

        reserve = 64
        keep = max(max_chars - reserve, 0)
        dropped = len(text) - keep
        return f"{text[:keep]}\n\n[Truncated {dropped} chars for persistence]"

    @classmethod
    def _normalize_message_dict(cls, raw_message: dict) -> dict:
        msg = dict(raw_message)
        msg["text"] = cls._truncate_text(msg.get("text") or "", CHAT_RECORD_MAX_TEXT_CHARS)

        if msg.get("mainText") is not None:
            msg["mainText"] = cls._truncate_text(
                msg.get("mainText") or "",
                CHAT_RECORD_MAX_TEXT_CHARS,
            )

        details = msg.get("details")
        normalized_details = []
        if isinstance(details, list):
            for detail in details[:CHAT_RECORD_MAX_DETAIL_COUNT]:
                if not isinstance(detail, dict):
                    continue
                normalized_detail = dict(detail)
                normalized_detail["content"] = cls._truncate_text(
                    normalized_detail.get("content") or "",
                    CHAT_RECORD_MAX_DETAIL_TEXT_CHARS,
                )
                files = normalized_detail.get("files")
                normalized_detail["files"] = files if isinstance(files, list) else []
                normalized_details.append(normalized_detail)
        msg["details"] = normalized_details

        assets = msg.get("assets")
        msg["assets"] = (
            [asset for asset in assets if isinstance(asset, dict)][:CHAT_RECORD_MAX_ASSET_COUNT]
            if isinstance(assets, list)
            else []
        )

        attachments = msg.get("attachments")
        msg["attachments"] = (
            [att for att in attachments if isinstance(att, dict)][:CHAT_RECORD_MAX_ATTACHMENT_COUNT]
            if isinstance(attachments, list)
            else []
        )

        is_complete = msg.get("isComplete")
        if isinstance(is_complete, bool):
            msg["isComplete"] = is_complete
        elif "isComplete" in msg:
            msg.pop("isComplete", None)

        return msg

    @staticmethod
    def _to_summary(session: dict) -> ChatSessionSummaryDTO:
        messages = session.get("messages") or []
        return ChatSessionSummaryDTO(
            id=str(session.get("id") or ""),
            name=str(session.get("name") or "New Chat"),
            createdAt=int(session.get("createdAt") or 0),
            updatedAt=int(session.get("updatedAt") or session.get("createdAt") or 0),
            messageCount=int(session.get("messageCount") or len(messages)),
        )

    @staticmethod
    def _to_detail(session: dict) -> ChatSessionDetailDTO:
        raw_messages = session.get("messages") or []
        messages: List[ChatMessageDTO] = []
        for index, msg in enumerate(raw_messages):
            if not isinstance(msg, dict):
                continue
            messages.append(
                ChatMessageDTO(
                    id=str(msg.get("id") or ""),
                    role=str(msg.get("role") or "Human"),
                    text=str(msg.get("text") or ""),
                    mainText=str(msg.get("mainText")) if msg.get("mainText") is not None else None,
                    isComplete=msg.get("isComplete") if isinstance(msg.get("isComplete"), bool) else None,
                    createdAt=int(msg.get("createdAt") or 0),
                    sequence=int(msg.get("sequence") or index),
                    details=msg.get("details") or [],
                    assets=msg.get("assets") or [],
                    attachments=msg.get("attachments") or [],
                )
            )

        return ChatSessionDetailDTO(
            id=str(session.get("id") or ""),
            name=str(session.get("name") or "New Chat"),
            createdAt=int(session.get("createdAt") or 0),
            updatedAt=int(session.get("updatedAt") or session.get("createdAt") or 0),
            messages=messages,
        )

    def list_sessions(
        self,
        page: int = 1,
        page_size: int = CHAT_SESSIONS_DEFAULT_PAGE_SIZE,
    ) -> tuple:
        with self._lock:
            payload = self._read_store()
            self._apply_retention_policy_locked(payload)
            sessions = payload.get("sessions", [])

            summaries = [
                self._to_summary(session)
                for session in sessions
                if isinstance(session, dict) and session.get("id")
            ]

        summaries.sort(key=lambda item: item.updated_at, reverse=True)
        total = len(summaries)

        safe_page = max(page, 1)
        safe_size = max(1, min(page_size, CHAT_SESSIONS_MAX_PAGE_SIZE))
        start = (safe_page - 1) * safe_size
        end = start + safe_size
        return summaries[start:end], total

    def get_session(self, session_id: str) -> Optional[ChatSessionDetailDTO]:
        with self._lock:
            payload = self._read_store()
            self._apply_retention_policy_locked(payload)
            for session in payload.get("sessions", []):
                if not isinstance(session, dict):
                    continue
                if str(session.get("id") or "") == session_id:
                    return self._to_detail(session)
        return None

    def create_session(
        self,
        session_id: str,
        name: str,
        created_at: Optional[int] = None,
        updated_at: Optional[int] = None,
    ) -> ChatSessionDetailDTO:
        now = int(time.time() * 1000)
        created_ms = int(created_at or now)
        updated_ms = int(updated_at or created_ms)

        with self._lock:
            payload = self._read_store()
            self._apply_retention_policy_locked(payload)
            sessions = payload.get("sessions", [])

            for session in sessions:
                if isinstance(session, dict) and str(session.get("id") or "") == session_id:
                    raise ValueError("Session already exists")

            session = {
                "id": session_id,
                "name": name or "New Chat",
                "createdAt": created_ms,
                "updatedAt": updated_ms,
                "messageCount": 0,
                "messages": [],
            }
            sessions.append(session)
            payload["sessions"] = sessions
            self._write_store(payload)

            return self._to_detail(session)

    def append_messages(
        self,
        session_id: str,
        messages: List[ChatMessageDTO],
    ) -> AppendChatMessagesResponse:
        now = int(time.time() * 1000)

        with self._lock:
            payload = self._read_store()
            self._apply_retention_policy_locked(payload)
            sessions = payload.get("sessions", [])

            target_session = None
            for session in sessions:
                if isinstance(session, dict) and str(session.get("id") or "") == session_id:
                    target_session = session
                    break

            if target_session is None:
                raise KeyError("Session not found")

            existing_messages = target_session.get("messages") or []
            existing_index_by_id = {}
            for index, msg in enumerate(existing_messages):
                if not isinstance(msg, dict):
                    continue
                msg_id = str(msg.get("id") or "")
                if msg_id:
                    existing_index_by_id[msg_id] = index

            def rebuild_signatures() -> set:
                return {
                    (
                        str(msg.get("role") or ""),
                        str(msg.get("text") or ""),
                        int(msg.get("sequence") or 0),
                    )
                    for msg in existing_messages
                    if isinstance(msg, dict)
                }

            existing_signatures = rebuild_signatures()

            accepted = 0
            skipped = 0

            for message in messages:
                msg_dict = self._normalize_message_dict(self._model_to_dict(message))
                msg_id = str(msg_dict.get("id") or "")
                role = str(msg_dict.get("role") or "Human")
                text = str(msg_dict.get("text") or "")
                sequence = int(msg_dict.get("sequence") or 0)
                signature = (role, text, sequence)

                if msg_id and msg_id in existing_index_by_id:
                    target_index = existing_index_by_id[msg_id]
                    previous = existing_messages[target_index]
                    if isinstance(previous, dict) and previous.get("createdAt"):
                        msg_dict["createdAt"] = int(previous.get("createdAt"))
                    elif not msg_dict.get("createdAt"):
                        msg_dict["createdAt"] = now

                    existing_messages[target_index] = msg_dict
                    existing_signatures = rebuild_signatures()
                    accepted += 1
                    continue

                if signature in existing_signatures:
                    skipped += 1
                    continue

                if not msg_dict.get("createdAt"):
                    msg_dict["createdAt"] = now

                existing_messages.append(msg_dict)
                if msg_id:
                    existing_index_by_id[msg_id] = len(existing_messages) - 1
                existing_signatures.add(signature)
                accepted += 1

            existing_messages.sort(key=lambda msg: int(msg.get("sequence") or 0))
            target_session["messages"] = existing_messages
            target_session["messageCount"] = len(existing_messages)
            target_session["updatedAt"] = now

            payload["sessions"] = sessions
            self._write_store(payload)

            return AppendChatMessagesResponse(
                accepted=accepted,
                skipped=skipped,
                session=self._to_detail(target_session),
            )

    def rename_session(self, session_id: str, name: str) -> ChatSessionDetailDTO:
        now = int(time.time() * 1000)
        with self._lock:
            payload = self._read_store()
            self._apply_retention_policy_locked(payload)
            sessions = payload.get("sessions", [])

            for session in sessions:
                if isinstance(session, dict) and str(session.get("id") or "") == session_id:
                    session["name"] = name or "New Chat"
                    session["updatedAt"] = now
                    self._write_store(payload)
                    return self._to_detail(session)

        raise KeyError("Session not found")

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            payload = self._read_store()
            self._apply_retention_policy_locked(payload)
            sessions = payload.get("sessions", [])
            remaining = [
                session
                for session in sessions
                if not (
                    isinstance(session, dict)
                    and str(session.get("id") or "") == session_id
                )
            ]

            if len(remaining) == len(sessions):
                return False

            payload["sessions"] = remaining
            self._write_store(payload)
            return True


CHAT_SESSION_STORE_PATH = project_root / "user_data" / "chat_sessions.json"
chat_session_store = ChatSessionReadStore(CHAT_SESSION_STORE_PATH)
chat_session_read_store = chat_session_store


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


@app.post("/api/agent/runs/{run_id}/pause")
async def pause_run(run_id: str):
    """Request pausing a running stream. Pause takes effect at the next safe step boundary."""
    with run_controls_lock:
        run_control = run_controls.get(run_id)

    if not run_control:
        raise HTTPException(status_code=404, detail="Run not found")

    run_control.request_pause()
    return {"status": "ok", "run_id": run_id, "state": run_control.status()}


@app.post("/api/agent/runs/{run_id}/resume")
async def resume_run(run_id: str, submission: RunResumeSubmission):
    """Resume a paused stream with optional user guidance text."""
    with run_controls_lock:
        run_control = run_controls.get(run_id)

    if not run_control:
        raise HTTPException(status_code=404, detail="Run not found")

    if not run_control.resume(submission.value):
        raise HTTPException(status_code=400, detail="Run is not paused")

    return {"status": "ok", "run_id": run_id}


@app.post("/api/agent/editor/confirm")
async def confirm_editor_layout(request: EditorConfirmRequest):
    """Persist IO editor confirmation and trigger backend wait-loop continuation."""
    try:
        raw_path = (request.source_path or "").strip()
        if not raw_path:
            raise HTTPException(status_code=400, detail="source_path is required")

        normalized_path = raw_path.lstrip("/")
        if normalized_path.startswith("output/generated/"):
            target_path = (project_root / normalized_path).resolve()
        else:
            raise HTTPException(status_code=400, detail="source_path must be inside output/generated/")

        generated_root = Path(GENERATED_OUTPUT_DIR).resolve()
        if not str(target_path).startswith(str(generated_root)):
            raise HTTPException(status_code=400, detail="source_path must be inside output/generated/")

        target_path.parent.mkdir(parents=True, exist_ok=True)

        source_intent_path = resolve_source_intent_path(target_path)
        source_payload = None
        if source_intent_path and source_intent_path.exists():
            with open(source_intent_path, "r", encoding="utf-8") as f:
                source_payload = json.load(f)

        normalized_payload = normalize_editor_payload_for_confirm(request.data)
        confirmed_payload = build_confirmed_payload(source_payload or {}, normalized_payload)

        write_path = target_path
        if target_path.name.endswith("_intermediate_editor.json"):
            # Keep intermediate export immutable after confirmation; persist only confirmed output.
            write_path = target_path.with_name(
                target_path.name.replace("_intermediate_editor.json", "_confirmed.json")
            )

        with open(write_path, "w", encoding="utf-8") as f:
            json.dump(confirmed_payload, f, ensure_ascii=False, indent=2)

        written_paths = [str(write_path.relative_to(project_root))]

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
    if not query.strip():
        query = resolve_effective_prompt()
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
        memory_saved = False
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
            persist_session_memory(f"web_session_{os.getpid()}", first_user_input=query)
            memory_saved = True

            yield format_sse_event({
                "completion": "",
                "stop_reason": "stop_sequence", 
                "model": "ams-io-agent"
            })
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            if not memory_saved:
                persist_session_memory(f"web_session_error_{os.getpid()}", first_user_input=query)
                
            yield format_sse_event({
                "completion": f"\n\n**Error**: {str(e)}", 
                "stop_reason": "stop_sequence",
                "model": "error"
            })

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
async def health():
    return {"status": "ok", "agent_initialized": agent_instance is not None}


@app.get("/api/chat/metrics", response_model=ChatOpsMetricsResponse)
async def get_chat_metrics():
    return build_chat_metrics_snapshot()


# ==========================================
# PHASE 1: Backend Read APIs (No Behavior Break)
# ==========================================
@app.get("/api/chat/sessions", response_model=List[ChatSessionSummaryDTO])
async def list_chat_sessions(
    response: Response,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=CHAT_SESSIONS_DEFAULT_PAGE_SIZE, ge=1, le=CHAT_SESSIONS_MAX_PAGE_SIZE),
):
    started = time.perf_counter()
    sessions, total = chat_session_store.list_sessions(page=page, page_size=page_size)
    latency_ms = (time.perf_counter() - started) * 1000.0
    record_history_load_latency(latency_ms)

    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page"] = str(page)
    response.headers["X-Page-Size"] = str(page_size)
    return sessions


@app.get("/api/chat/sessions/{session_id}", response_model=ChatSessionDetailDTO)
async def get_chat_session(session_id: str):
    started = time.perf_counter()
    session = chat_session_store.get_session(session_id)
    latency_ms = (time.perf_counter() - started) * 1000.0
    record_history_load_latency(latency_ms)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


# ==========================================
# PHASE 3: Backend Write APIs
# ==========================================
@app.post("/api/chat/sessions", response_model=ChatSessionDetailDTO)
async def create_chat_session(request: CreateChatSessionRequest):
    try:
        created = chat_session_store.create_session(
            session_id=request.id,
            name=request.name,
            created_at=request.created_at,
            updated_at=request.updated_at,
        )
        record_chat_write_result(True)
        return created
    except ValueError as exc:
        record_chat_write_result(False)
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post(
    "/api/chat/sessions/{session_id}/messages",
    response_model=AppendChatMessagesResponse,
)
async def append_chat_session_messages(
    session_id: str,
    request: AppendChatMessagesRequest,
):
    try:
        result = chat_session_store.append_messages(session_id, request.messages)
        record_chat_write_result(True)
        return result
    except KeyError as exc:
        record_chat_write_result(False)
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.patch("/api/chat/sessions/{session_id}", response_model=ChatSessionDetailDTO)
async def rename_chat_session(session_id: str, request: UpdateChatSessionRequest):
    try:
        session = chat_session_store.rename_session(session_id, request.name)
        record_chat_write_result(True)
        return session
    except KeyError as exc:
        record_chat_write_result(False)
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete(
    "/api/chat/sessions/{session_id}",
    response_model=DeleteChatSessionResponse,
)
async def delete_chat_session(session_id: str):
    deleted = chat_session_store.delete_session(session_id)
    if not deleted:
        record_chat_write_result(False)
        raise HTTPException(status_code=404, detail="Session not found")
    record_chat_write_result(True)
    return DeleteChatSessionResponse(status="ok", sessionId=session_id)

# ==========================================
# PHASE 1: New Structured Agent Endpoint
# ==========================================
@app.post("/api/agent/chat")
async def agent_chat(request: AgentChatRequest):
    resolved_prompt = resolve_effective_prompt(
        request_prompt=request.prompt,
        request_prompt_text=request.prompt_text,
        request_prompt_key=request.prompt_key,
        request_prompt_config_file=request.prompt_config_file,
    )

    logger.info(f"Received Agent Request: {resolved_prompt[:50]}...")
    if not resolved_prompt:
        raise HTTPException(status_code=400, detail="No prompt provided. Set prompt or configure prompt defaults.")
    
    if not agent_instance:
         # Initialize on demand if not ready (fallback)
         try:
             await startup_event()
         except:
             return {"error": "Agent not initialized"}
         
    run_id = (request.run_id or str(uuid.uuid4())).strip()
    session_id = (request.session_id or "").strip()
    memory_session_key = session_id or run_id
    run_control = RunControl(run_id)
    with run_controls_lock:
        run_controls[run_id] = run_control

    # Create timestamp-specific working directory under output/generated
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    generated_dir_name = timestamp
    generated_dir = os.path.join(GENERATED_OUTPUT_DIR, generated_dir_name)
    os.makedirs(generated_dir, exist_ok=True)
    relative_generated_dir = f"output/generated/{generated_dir_name}"
    
    # Inject directory instruction into prompt
    # We append this instruction so the agent knows where to save files for this turn
    enhanced_prompt = f"{resolved_prompt}\n\n[SYSTEM INSTRUCTION: Save ALL generated files (images, code, reports) to the directory '{relative_generated_dir}'. Do not use any other output path.]"

    async def structured_event_generator():
        response_queue = queue.Queue()
        input_manager.set_response_queue(response_queue)
        run_started_at = time.time()
        run_started_epoch_sec = int(run_started_at)

        # Track emitted file versions so updated files can be re-emitted.
        sent_file_versions = {}

        def scan_and_yield_files():
            files_to_send = []
            seen_abs_paths_in_scan = set()
            scan_roots = [generated_dir, GENERATED_OUTPUT_DIR]
            for scan_root in scan_roots:
                if not os.path.exists(scan_root):
                    continue

                for root, dirs, files in os.walk(scan_root):
                    for file in files:
                        file_abs_path = os.path.realpath(os.path.join(root, file))
                        if file_abs_path in seen_abs_paths_in_scan:
                            continue

                        seen_abs_paths_in_scan.add(file_abs_path)
                        try:
                            stat_result = os.stat(file_abs_path)
                            mtime = stat_result.st_mtime
                            mtime_ns = stat_result.st_mtime_ns
                            size = stat_result.st_size
                        except OSError:
                            continue

                        last_version = sent_file_versions.get(file_abs_path)
                        # Use nanosecond precision to catch rapid same-path rewrites.
                        current_version = (mtime_ns, size)
                        is_current_turn = os.path.commonpath([file_abs_path, generated_dir]) == generated_dir

                        # Skip old historical files on first sighting to avoid flooding events.
                        # Do not filter current-turn files, and use second-level boundary for
                        # non-current-turn paths to avoid same-second false negatives.
                        if (
                            last_version is None
                            and (not is_current_turn)
                            and mtime < run_started_epoch_sec
                        ):
                            continue

                        if last_version == current_version:
                            continue

                        sent_file_versions[file_abs_path] = current_version
                        file_rel_path = os.path.relpath(file_abs_path, project_root)
                        rel_parts = file_rel_path.split(os.sep)
                        detected_turn_dir = None
                        if len(rel_parts) >= 3 and rel_parts[0] == "output" and rel_parts[1] == "generated":
                            detected_turn_dir = "/".join(rel_parts[:3])

                        files_to_send.append({
                            "name": file,
                            "path": file_rel_path,
                            "url": f"/{file_rel_path}",
                            "mtime": mtime,
                            "mtime_ns": mtime_ns,
                            "size": size,
                            "event_id": str(uuid.uuid4()),
                            "source_turn_dir": detected_turn_dir,
                            "is_current_turn": is_current_turn,
                        })
            return files_to_send

        # Define agent runner to execute in a separate thread
        def run_agent_worker():
            # Patch input
            builtins.input = patched_input
            try:
                # 1. Yield run metadata so frontend can control pause/resume deterministically.
                response_queue.put(format_agent_event("run_started", {
                    "run_id": run_id,
                    "output_dir": relative_generated_dir,
                }))
                response_queue.put(format_agent_event("status", f"Starting Agent... (Output Dir: {relative_generated_dir})"))
                
                # Check for existing files first (e.g. from previous turns or externally created)
                # But actually we are in a new turn dir, so it should be empty.
                pass 
                
                # 2. Run Agent, support pause->resume continuation via follow-up prompt.
                current_prompt = enhanced_prompt
                reset_memory = request.reset_memory

                while True:
                    resume_prompt = None
                    for step in agent_instance.run(current_prompt, stream=True, reset=reset_memory):
                        response_queue.put(step)
                        # Force yield a scan check after each step
                        response_queue.put("CHECK_FILES")

                        if run_control.consume_pause_request():
                            response_queue.put(format_agent_event("paused", {"run_id": run_id}))
                            resume_prompt = run_control.wait_for_resume()
                            response_queue.put(format_agent_event("resumed", {"run_id": run_id}))
                            break

                    if resume_prompt is None:
                        break

                    current_prompt = resume_prompt
                    # After first run in a stream, follow-up runs should keep memory context.
                    reset_memory = False
                
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
                persist_session_memory(
                    f"web_session_{memory_session_key}",
                    first_user_input=resolved_prompt,
                )

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
        finally:
            with run_controls_lock:
                run_controls.pop(run_id, None)

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

