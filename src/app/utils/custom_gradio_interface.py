#!/usr/bin/env python
# coding=utf-8
import ast
import base64
import html
import json
import mimetypes
import os
from urllib.parse import quote
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Generator

import gradio as gr 
# Explicit import of gradio to ensure we have it

from smolagents.agent_types import AgentAudio, AgentImage, AgentText
from smolagents.agents import MultiStepAgent, PlanningStep
from smolagents.memory import ActionStep, FinalAnswerStep
from smolagents.models import ChatMessageStreamDelta, MessageRole, agglomerate_stream_deltas
from smolagents.utils import _is_package_available

from .visualization import get_io_ring_editor_html, get_file_preview_html

# ------------------------------------------------------------------------
# Helper Functions (Copied from smolagents/gradio_ui.py or custom user fork)
# ------------------------------------------------------------------------

def get_step_footnote_content(step_log: ActionStep | PlanningStep, step_name: str) -> str:
    """Get a footnote string for a step log with duration and token information"""
    step_footnote = f"**{step_name}**"
    if step_log.token_usage is not None:
        step_footnote += f" | Input tokens: {step_log.token_usage.input_tokens:,} | Output tokens: {step_log.token_usage.output_tokens:,}"
    step_footnote += f" | Duration: {round(float(step_log.timing.duration), 2)}s" if step_log.timing.duration else ""
    step_footnote_content = f"""<span style="color: #bbbbc2; font-size: 12px;">{step_footnote}</span> """
    return step_footnote_content


def _clean_model_output(model_output: str) -> str:
    if not model_output:
        return ""
    model_output = model_output.strip()
    model_output = re.sub(r"```\s*<end_code>", "```", model_output)
    model_output = re.sub(r"<end_code>\s*```", "```", model_output)
    model_output = re.sub(r"```\s*\n\s*<end_code>", "```", model_output)
    return model_output.strip()


_DICT_BLOCK_PATTERN = re.compile(r"\{[^{}]*\}", re.DOTALL)


def _format_code_content(content: str) -> str:
    content = content.strip()
    content = re.sub(r"```.*?\n", "", content)
    content = re.sub(r"\s*<end_code>\s*", "", content)
    content = content.strip()
    if not content.startswith("```python"):
        content = f"```python\n{content}\n```"
    return content


def _as_stream_payload(execution_log: str | None, full_log: str | None) -> dict[str, str]:
    return {
        "execution_log": (execution_log or "").strip(),
        "full_log": full_log or "",
    }


def _maybe_dict_from_string(payload) -> dict | None:
    if isinstance(payload, str):
        text = payload.strip()
        candidate = text
        if not (text.startswith("{") and text.endswith("}")):
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                candidate = None
            else:
                candidate = text[start : end + 1]
        if candidate:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                try:
                    return ast.literal_eval(candidate)
                except (ValueError, SyntaxError):
                    return None
    if isinstance(payload, dict):
        return payload
    return None


def _extract_execution_text(block: str) -> str:
    if not block:
        return ""
    text = block.strip()
    if not text:
        return ""

    direct_dict = _maybe_dict_from_string(text)
    if direct_dict and "execution_log" in direct_dict:
        exec_text = str(direct_dict.get("execution_log") or "").strip()
        if exec_text:
            return exec_text

    pieces: list[str] = []
    saw_dict = False
    cursor = 0
    for match in _DICT_BLOCK_PATTERN.finditer(text):
        saw_dict = True
        prefix = text[cursor:match.start()].strip()
        data = _maybe_dict_from_string(match.group(0))
        if data and "execution_log" in data:
            exec_text = str(data.get("execution_log") or "").strip()
            if exec_text:
                if prefix:
                    normalized = prefix.rstrip()
                    suffix = ":" if normalized.endswith(":") else ""
                    normalized = normalized[:-1].rstrip() if suffix else normalized
                    if normalized:
                        pieces.append(f"{normalized}:{exec_text}")
                    else:
                        pieces.append(exec_text)
                else:
                    pieces.append(exec_text)
        cursor = match.end()

    if pieces:
        return "\n\n".join(pieces).strip()

    if saw_dict:
        stripped = _DICT_BLOCK_PATTERN.sub("", text)
        stripped = re.sub(r"^Execution logs:\s*", "", stripped, flags=re.IGNORECASE).strip()
        return stripped

    cleaned = re.sub(r"^Execution logs:\s*", "", text, flags=re.IGNORECASE).strip()
    return cleaned


def _extract_tool_logs(action_output) -> tuple[str, str]:
    maybe_dict = _maybe_dict_from_string(action_output)
    if maybe_dict is not None and {"execution_log", "full_log"}.issubset(maybe_dict.keys()):
        exec_log = maybe_dict.get("execution_log") or ""
        full_log = maybe_dict.get("full_log") or ""
        return str(exec_log), str(full_log)
    if isinstance(action_output, dict) and {"execution_log", "full_log"}.issubset(action_output.keys()):
        exec_log = action_output.get("execution_log") or ""
        full_log = action_output.get("full_log") or ""
        return str(exec_log), str(full_log)
    if action_output is None:
        return "", ""
    return str(action_output), ""


def _render_final_answer_logs(step_log: FinalAnswerStep) -> tuple[str, str]:
    final_answer = step_log.output
    if isinstance(final_answer, AgentText):
        text = final_answer.to_string()
    elif isinstance(final_answer, (AgentImage, AgentAudio)):
        text = final_answer.to_string()
    else:
        text = str(final_answer)
    formatted = f"**Final answer:**\n{text}" if text else "Final answer provided."
    return formatted, formatted


def _step_to_full_markdown(step_log: ActionStep | PlanningStep | FinalAnswerStep) -> str:
    parts: list[str] = []

    if isinstance(step_log, ActionStep):
        step_number = f"Step {step_log.step_number}"
        parts.append(f"**{step_number}**")

        model_output = getattr(step_log, "model_output", "")
        if model_output:
            parts.append(_clean_model_output(model_output))

        tool_calls = getattr(step_log, "tool_calls", []) or []
        if tool_calls:
            first_tool_call = tool_calls[0]
            args = first_tool_call.arguments
            if isinstance(args, dict):
                content = str(args.get("answer", args))
            else:
                content = str(args).strip()

            if first_tool_call.name == "python_interpreter":
                content = _format_code_content(content)

            parts.append(f"**🛠️ Used tool `{first_tool_call.name}`**\n\n{content}")

        observations = getattr(step_log, "observations", "")
        if observations and observations.strip():
            log_content = re.sub(r"^Execution logs:\s*", "", observations.strip())
            parts.append(f"```bash\n{log_content}\n```")

        images = getattr(step_log, "observations_images", []) or []
        for image in images:
            path_image = AgentImage(image).to_string()
            parts.append(f"![Output image]({path_image})")

        if getattr(step_log, "error", None):
            parts.append(f"**Error:** {step_log.error}")

        parts.append(get_step_footnote_content(step_log, step_number))
        parts.append("-----")
        return "\n\n".join(part for part in parts if part).strip()

    if isinstance(step_log, PlanningStep):
        parts.append("**Planning step**")
        if step_log.plan:
            parts.append(step_log.plan)
        parts.append(get_step_footnote_content(step_log, "Planning step"))
        parts.append("-----")
        return "\n\n".join(part for part in parts if part).strip()

    if isinstance(step_log, FinalAnswerStep):
        _, full_log = _render_final_answer_logs(step_log)
        return full_log

    return ""


def _step_to_stream_payload(step_log: ActionStep | PlanningStep | FinalAnswerStep) -> dict[str, str]:
    full_markdown = _step_to_full_markdown(step_log)
    if isinstance(step_log, ActionStep):
        exec_log, tool_full = _extract_tool_logs(step_log.action_output)
        full_log_parts: list[str] = []
        if tool_full:
            full_log_parts.append(tool_full)
        if step_log.observations:
            full_log_parts.append(step_log.observations)
        if step_log.error:
            full_log_parts.append(f"Error: {step_log.error}")
        if not exec_log and step_log.observations:
            observations = step_log.observations.strip()
            execution_text = _extract_execution_text(observations)
            if execution_text:
                exec_log = execution_text
        if not exec_log and step_log.error:
            exec_log = f"Error: {step_log.error}"
        if not exec_log:
            exec_log = "Action step completed."
        full_log = "\n\n".join(part for part in full_log_parts if part)
        if not full_log:
            full_log = exec_log
        return _as_stream_payload(exec_log, full_markdown or full_log)
    if isinstance(step_log, PlanningStep):
        return _as_stream_payload("", full_markdown or step_log.plan)
    if isinstance(step_log, FinalAnswerStep):
        _, full_log = _render_final_answer_logs(step_log)
        return _as_stream_payload("", full_markdown or full_log)
    return _as_stream_payload("", "")


def stream_to_gradio(
    agent,
    task: str,
    task_images: list | None = None,
    reset_agent_memory: bool = False,
    additional_args: dict | None = None,
) -> Generator:
    accumulated_events: list[ChatMessageStreamDelta] = []
    last_stream_text = ""
    for event in agent.run(
        task, images=task_images, stream=True, reset=reset_agent_memory, additional_args=additional_args
    ):
        if isinstance(event, (ActionStep, PlanningStep, FinalAnswerStep)):
            yield _step_to_stream_payload(event)
            accumulated_events = []
            last_stream_text = ""
        elif isinstance(event, ChatMessageStreamDelta):
            accumulated_events.append(event)
            text = agglomerate_stream_deltas(accumulated_events).render_as_markdown()
            if not text:
                continue
            if last_stream_text and text.startswith(last_stream_text):
                new_piece = text[len(last_stream_text) :]
            else:
                new_piece = text
            if not new_piece:
                continue
            last_stream_text = text
            yield _as_stream_payload("", new_piece)


class IOAgentGradioUI:
    """
    Custom Gradio Interface for AMS-IO-Agent.
    Features:
    - Chat Interface
    - File Output Browser with Previews
    - Visual IO Ring Editor (Puzzle Module)
    """

    def __init__(
        self,
        agent: MultiStepAgent,
        file_upload_folder: str | None = None,
        reset_agent_memory: bool = False,
        allowed_file_types: list[str] | None = None,
        output_base_folders: list[str] | None = None,
    ):
        mimetypes.init()
        mimetypes.add_type("text/markdown", ".md")
        mimetypes.add_type("text/plain", ".log")
        mimetypes.add_type("application/json", ".json")

        self.agent = agent
        self.file_upload_folder = Path(file_upload_folder) if file_upload_folder is not None else None
        self.reset_agent_memory = reset_agent_memory
        self.name = getattr(agent, "name") or "AMS IO Agent"
        self.description = getattr(agent, "description", None)
        self.allowed_file_types = (
            [ft.lower() if ft.startswith(".") else f".{ft.lower().lstrip('.')}" for ft in allowed_file_types]
            if allowed_file_types
            else [".pdf", ".docx", ".txt", ".json", ".yaml"]
        )
        base_folders = output_base_folders if output_base_folders else ["output"]
        self.output_base_folders = [Path(folder) for folder in base_folders]
        self._chatbot_component = None

        if self.file_upload_folder:
            if not self.file_upload_folder.exists():
                self.file_upload_folder.mkdir(parents=True, exist_ok=True)
        for folder in self.output_base_folders:
            folder.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        sanitized_name = re.sub(r"[^\w\-.]", "_", os.path.basename(filename))
        return sanitized_name or "uploaded_file"

    def _extension_is_allowed(self, file_path: Path) -> bool:
        if not self.allowed_file_types:
            return True
        return file_path.suffix.lower() in self.allowed_file_types

    def _resolve_file_path(self, file_like) -> Path | None:
        if file_like is None:
            return None
        candidate = None
        if isinstance(file_like, (str, Path)):
            candidate = Path(file_like)
        elif isinstance(file_like, dict):
            for key in ("path", "name", "file"):
                value = file_like.get(key)
                if value:
                    candidate = Path(value)
                    break
        elif hasattr(file_like, "name") and getattr(file_like, "name"):
            candidate = Path(file_like.name)

        if candidate is None:
            return None
        return candidate if candidate.exists() else None

    def _copy_into_uploads(self, source_path: Path, session_folder_name: str | None = None) -> str:
        if self.file_upload_folder is None:
            raise ValueError("File uploads are disabled.")
        sanitized_name = self._sanitize_filename(source_path.name)
        if session_folder_name is None:
            session_folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = self.file_upload_folder / session_folder_name
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / sanitized_name
        counter = 1
        while destination.exists():
            destination = target_dir / f"{destination.stem}_{counter}{destination.suffix}"
            counter += 1
        shutil.copy(source_path, destination)
        return str(destination)

    def _chatbot_image_content(self, file_path: str):
        return (str(file_path), None)

    def _detect_output_type(self, file_path: Path) -> str:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith("image/"): return "image"
            if mime_type == "application/json": return "json"
            if mime_type.startswith("text/"): return "text"
        return "other"

    def load_latest_output_files(self, min_timestamp: float = 0) -> list[dict] | None:
        candidate_dirs: list[Path] = []
        for base in self.output_base_folders:
            if not base.exists(): continue
            for child in base.iterdir():
                if child.is_dir() and not child.name.startswith(".") and child.name not in ["drc", "lvs"]:
                    candidate_dirs.append(child)

        valid_dirs = [d for d in candidate_dirs if d.stat().st_mtime >= min_timestamp]
        if not valid_dirs: return None

        valid_dirs.sort(key=lambda folder: folder.stat().st_mtime, reverse=True)
        results = []
        for directory in valid_dirs:
            file_entries = []
            for child in sorted(directory.iterdir()):
                if not child.is_file() or child.name.startswith("."): continue
                file_type = self._detect_output_type(child)
                try:
                    file_path = os.path.relpath(str(child.resolve()), os.getcwd())
                except ValueError:
                    file_path = str(child.resolve())
                file_entries.append({"path": file_path, "name": child.name, "type": file_type})
            
            if file_entries:
                results.append({"folder": str(directory), "folder_name": directory.name, "files": file_entries})
        return results if results else None

    # [Truncated] _extract_prompt_and_files and log_user_message and interact_with_agent 
    # are almost identical to smolagents but adapted for our storage. 
    # For brevity, I'm reimplementing strict necessary logic based on previous read.
    
    def _extract_prompt_and_files(self, prompt_payload) -> tuple[str, list[str], list[str]]:
        # Simplified for robustness
        if not prompt_payload: return "", [], []
        session_folder = datetime.now().strftime("%Y%m%d_%H%M%S")
        text, saved, source = "", [], []
        
        def process_path(p):
            rp = self._resolve_file_path(p)
            if rp and self._extension_is_allowed(rp):
                saved_path = self._copy_into_uploads(rp, session_folder)
                saved.append(saved_path)
                source.append(str(rp))

        if isinstance(prompt_payload, dict):
             text = str(prompt_payload.get("text", "")).strip()
             for k in ["files"]:
                 files = prompt_payload.get(k, [])
                 if not isinstance(files, list): files = [files]
                 for f in files: process_path(f)
        else:
             text = str(prompt_payload).strip()
        
        return text.strip(), saved, source

    def log_user_message(self, prompt_payload, file_uploads_log, session_state):
        try:
            prompt_text, saved_files, temp_files = self._extract_prompt_and_files(prompt_payload)
        except ValueError as exc:
            raise gr.Error(str(exc))

        if not prompt_text and not saved_files:
            raise gr.Error("Empty message")
            
        session_state.setdefault("latest_files", [])
        session_state["latest_files"] = saved_files
        
        if saved_files:
            msg = f"<uploaded_files>\n" + "\n".join(saved_files) + "\n</uploaded_files>"
            prompt_text = f"{prompt_text}\n\n{msg}" if prompt_text else msg
            
        return prompt_text, gr.update(value=None, interactive=False), (file_uploads_log or []) + saved_files

    def interact_with_agent(self, prompt, messages, session_state):
        if "agent" not in session_state: session_state["agent"] = self.agent
        
        attached_files = session_state.get("latest_files", [])
        display_text = prompt or ""
        
        # UI Message
        messages.append(gr.ChatMessage(role="user", content=display_text, metadata={"status": "done"}))
        for fp in attached_files:
             if self._detect_output_type(Path(fp)) == "image":
                 messages.append(gr.ChatMessage(role="user", content=(fp, None), metadata={"status": "done"}))

        session_state["full_buffer"] = ""
        session_state["exec_buffer"] = ""
        session_state["step"] = 1

        exec_msg = gr.ChatMessage(role="assistant", content="", metadata={"type": "exec", "status": "pending"})
        messages.append(exec_msg)
        exec_index = len(messages) - 1

        def _full_reason_update():
            full_buffer = session_state.get("full_buffer", "")
            content = full_buffer or "_No reasoning yet._"
            return gr.update(value=content)

        yield messages, _full_reason_update()

        try:
            # Run Agent
            for msg in stream_to_gradio(session_state["agent"], task=prompt, reset_agent_memory=self.reset_agent_memory):
                if isinstance(msg, dict) and "execution_log" in msg:
                    exec_piece = msg.get("execution_log", "")
                    if exec_piece:
                        s = session_state["step"]
                        session_state["exec_buffer"] += f"### Step {s}\n{exec_piece}\n\n"
                        messages[exec_index].content = session_state["exec_buffer"].strip()
                        session_state["step"] = s + 1
                    session_state["full_buffer"] += msg.get("full_log", "")
                    yield messages, _full_reason_update()
                elif isinstance(msg, gr.ChatMessage):
                    messages.append(msg)
                    yield messages, _full_reason_update()
            
            messages[exec_index].metadata["status"] = "done"
            yield messages, _full_reason_update()

        except Exception as e:
            raise gr.Error(str(e))
        finally:
            session_state["latest_files"] = []

    def sync_puzzle_state(self, json_str):
        """Callback to handle JSON updates from the Puzzle Editor"""
        if not json_str: return
        try:
            print(f"[Puzzle Bridge] Received {len(json_str)} chars")
            # Save to a persistent location that the agent can read
            target_path = Path("io_ring_intent_graph.json")
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"[Puzzle Bridge] Saved to {target_path.absolute()}")
            gr.Info(f"Layout synced to backend: {target_path.name}")
        except Exception as e:
            print(f"[Puzzle Bridge] Error: {e}")
            gr.Warning(f"Sync failed: {e}")

    def create_app(self, allowed_paths: list[str] | None = None):
        import inspect
        blocks_kwargs = {"theme": "ocean", "fill_height": True, "title": "AMS IO Agent & Editor"}
        if allowed_paths and "allowed_paths" in inspect.signature(gr.Blocks).parameters:
            blocks_kwargs["allowed_paths"] = allowed_paths

        with gr.Blocks(**blocks_kwargs) as demo:
            session_state = gr.State({"start_time": datetime.now().timestamp()})
            stored_messages = gr.State("")
            file_uploads_log = gr.State([])
            output_refresh_state = gr.State(0)

            with gr.Sidebar():
                gr.Markdown(f"# {self.name}\n\n{self.description or ''}")
                
                # Output Files Section
                with gr.Accordion("📂 Output Files", open=False):
                    @gr.render(inputs=[session_state, output_refresh_state])
                    def render_output_files(state, _):
                        start_time = state.get("start_time", 0) if state else 0
                        payloads = self.load_latest_output_files(min_timestamp=start_time)
                        if not payloads:
                            gr.Markdown("_No files yet._")
                        else:
                            for entry in payloads:
                                with gr.Accordion(entry["folder_name"], open=False):
                                    file_output = gr.File(
                                        value=[f["path"] for f in entry["files"]],
                                        file_count="multiple",
                                        interactive=False,
                                        label=entry["folder_name"]
                                    )
                                    # Preview Logic
                                    file_map_state = gr.State({f["name"]: f for f in entry["files"]})
                                    modal_container = gr.HTML(visible=True)
                                    
                                    def on_select(evt: gr.SelectData, f_map):
                                        if not evt.value: return ""
                                        return get_file_preview_html(os.path.basename(evt.value), f_map)

                                    file_output.select(on_select, [file_map_state], [modal_container])

                    refresh_btn = gr.Button("🔄 Refresh Files", variant="secondary")
                    refresh_btn.click(lambda c: c+1, [output_refresh_state], [output_refresh_state])

            with gr.Tabs():
                # TAB 1: Main Chat Interface
                with gr.Tab("💬 Agent Chat"):
                    with gr.Column(scale=1):
                        chatbot = gr.Chatbot(
                            label="Conversation",
                            type="messages",
                            resizeable=False,
                            scale=1
                        )
                        with gr.Accordion("🔍 Inner Monologue", open=False):
                            full_reasoning_md = gr.Markdown("_No logs._")
                        
                        prompt_input = gr.MultimodalTextbox(
                            label="Message", 
                            placeholder="Type here or upload files...",
                            file_count="multiple"
                        )
                        
                        # Wiring
                        prompt_input.submit(
                            self.log_user_message, 
                            [prompt_input, file_uploads_log, session_state], 
                            [stored_messages, prompt_input, file_uploads_log]
                        ).then(
                            self.interact_with_agent,
                            [stored_messages, chatbot, session_state],
                            [chatbot, full_reasoning_md]
                        ).then(
                            lambda c: c+1, [output_refresh_state], [output_refresh_state]
                        )

                # TAB 2: Visual Puzzle Editor
                with gr.Tab("🧩 Layout Editor"):
                    gr.Markdown("Drag and drop IO pads to configure the ring. Click 'Sync to Agent' to save.")
                    
                    # The IFrame / HTML Editor
                    initial_data = None
                    
                    # 1. Try to load from output/generated/ (Latest Timestamped Folder)
                    try:
                        gen_dir = Path("output/generated")
                        if gen_dir.exists():
                            # Find all subdirectories
                            subdirs = [d for d in gen_dir.iterdir() if d.is_dir()]
                            if subdirs:
                                # Sort by modification time (or name) to get the latest folder
                                latest_dir = max(subdirs, key=lambda p: p.name)  # timestamp naming makes name sort valid
                                print(f"[Layout Editor] Checking latest folder: {latest_dir}")
                                
                                # Look for potential JSON config files in priority order
                                # We support both exact names and timestamped versions (e.g. io_ring_config_20230101.json)
                                candidate_patterns = ["io_ring_config*.json", "io_ring_config_corrected*.json", "io_ring_intent_graph*.json"]
                                target_file = None
                                
                                for pattern in candidate_patterns:
                                    # Use glob to find files matching the pattern
                                    matches = list(latest_dir.glob(pattern))
                                    if matches:
                                        # If multiple matches (e.g. multiple timestamps), pick the one with latest mtime
                                        target_file = max(matches, key=lambda p: p.stat().st_mtime)
                                        break
                                
                                if target_file:
                                    print(f"[Layout Editor] Loading file: {target_file}")
                                    with open(target_file, "r", encoding="utf-8") as f:
                                        initial_data = json.load(f)
                                else:
                                    print(f"[Layout Editor] No config JSON found in {latest_dir}")
                    except Exception as e:
                        print(f"[Layout Editor] Warning: Could not load from output/generated: {e}")

                    # 2. Fallback to root io_ring_intent_graph.json
                    if initial_data is None:
                        try:
                            if os.path.exists("io_ring_intent_graph.json"):
                                with open("io_ring_intent_graph.json", "r", encoding="utf-8") as f:
                                    initial_data = json.load(f)
                        except: pass
                    
                    editor_html = get_io_ring_editor_html(initial_data)
                    # Gradio version here does not support sanitize_html param; scripts are allowed by default
                    gr.HTML(editor_html, elem_id="io-editor-frame")
                    
                    # The Bridge
                    # 'io-ring-bridge' class must match what's in visualization.py JS
                    bridge_input = gr.Textbox(visible=False, elem_classes=["io-ring-bridge"])
                    bridge_input.change(self.sync_puzzle_state, inputs=[bridge_input])

        return demo

    def launch(self, share: bool = False, **kwargs):
        allowed = kwargs.pop("allowed_paths", [])
        allowed.extend([os.getcwd(), os.path.realpath(os.getcwd())])
        if self.file_upload_folder: allowed.append(str(self.file_upload_folder))
        
        app = self.create_app(allowed_paths=allowed)
        
        # Re-inject allowed_paths into kwargs for launch() in case Blocks didn't consume it
        kwargs["allowed_paths"] = allowed
        app.launch(share=share, **kwargs)
