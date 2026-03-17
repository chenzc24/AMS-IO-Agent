from __future__ import annotations

import json
from functools import wraps
from typing import Any, Callable

from smolagents import tool as smol_tool


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except TypeError:
        return str(value)


def format_tool_logs(execution_log: Any = "", full_log: Any | None = None, extra_fields: dict[str, Any] | None = None) -> dict[str, Any]:
    exec_text = _stringify(execution_log)
    full_text = _stringify(full_log) if full_log is not None else exec_text
    result: dict[str, Any] = {"execution_log": exec_text, "full_log": full_text}
    if extra_fields:
        result.update(extra_fields)
    return result


def dual_stream_tool(func: Callable | None = None):
    def decorator(inner: Callable):
        @wraps(inner)
        def wrapper(*args, **kwargs):
            result = inner(*args, **kwargs)
            if isinstance(result, dict) and {"execution_log", "full_log"}.issubset(result.keys()):
                return result
            if isinstance(result, tuple):
                if len(result) == 3:
                    return format_tool_logs(result[0], result[1], result[2])
                if len(result) == 2:
                    return format_tool_logs(result[0], result[1])
            return format_tool_logs(result)

        return smol_tool(wrapper)

    if func is None:
        return decorator
    return decorator(func)
