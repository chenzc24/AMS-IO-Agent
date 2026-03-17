from __future__ import annotations

import json
from typing import Optional, Dict, Any

EVENT_START_MARKER = "<<<AMS_TOOL_EVENT_V1>>>"
EVENT_END_MARKER = "<<<AMS_TOOL_EVENT_END>>>"
EVENT_MARKER_VALUE = "AMS_TOOL_EVENT_V1"


def format_tool_name(tool_name: str) -> str:
    acronym_map = {
        "io": "IO",
        "json": "JSON",
        "il": "IL",
        "drc": "DRC",
        "lvs": "LVS",
        "pex": "PEX",
        "kb": "KB",
        "eda": "EDA",
    }

    parts = tool_name.split("_")
    formatted = []
    for part in parts:
        lower = part.lower()
        if lower in acronym_map:
            formatted.append(acronym_map[lower])
        else:
            formatted.append(part[:1].upper() + part[1:])
    return "_".join(formatted)


def build_tool_summary(result_text: str) -> str:
    if not result_text:
        return "Tool execution finished."

    stripped = result_text.strip()
    first_line = stripped.splitlines()[0].strip() if stripped else ""
    if first_line.startswith("✅"):
        return f"Step completed successfully: {first_line[1:].strip()}"
    if first_line.startswith("❌"):
        return f"Step failed: {first_line[1:].strip()}"
    return f"Step update: {first_line or 'Execution finished.'}"


def has_event_envelope(text: str) -> bool:
    if not isinstance(text, str):
        return False
    return EVENT_START_MARKER in text and EVENT_END_MARKER in text


def wrap_tool_output(
    tool_name: str,
    result_text: str,
    *,
    summary: Optional[str] = None,
    event_type: str = "tool_result",
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    if has_event_envelope(result_text):
        return result_text

    payload = {
        "marker": EVENT_MARKER_VALUE,
        "tool": format_tool_name(tool_name),
        "event_type": event_type,
        "status": "failed" if result_text.strip().startswith("❌") else "completed",
        "summary": summary or build_tool_summary(result_text),
    }

    merged_extra: Dict[str, Any] = {}
    if result_text:
        merged_extra["raw_output"] = result_text
    if extra:
        merged_extra.update(extra)
    if merged_extra:
        payload["extra"] = merged_extra

    event_json = json.dumps(payload, ensure_ascii=False)
    return (
        f"{result_text}\n\n"
        f"{EVENT_START_MARKER}\n"
        f"{event_json}\n"
        f"{EVENT_END_MARKER}"
    )
