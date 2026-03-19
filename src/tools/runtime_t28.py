#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runtime implementations for T28/T180 IO-ring tools without smolagents."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any, Dict, Optional, Tuple

from src.utils.bridge_utils import (
    execute_csh_script,
    ge_open_window,
    load_script_and_take_screenshot,
    open_cell_view_by_type,
    rb_exec,
    save_current_cellview,
    ui_redraw,
    ui_zoom_absolute_scale,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_output_root() -> Path:
    """Resolve unified output root for generated reports/artifacts.

    Priority:
    1) AMS_OUTPUT_ROOT env var (explicit override)
    2) Workspace-level output next to AMS-IO-Agent
    3) Legacy AMS-IO-Agent/output
    """
    env_root = os.environ.get("AMS_OUTPUT_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve(strict=False)

    workspace_output = PROJECT_ROOT.parent / "output"
    if workspace_output.exists() or PROJECT_ROOT.parent.exists():
        return workspace_output.resolve(strict=False)

    return (PROJECT_ROOT / "output").resolve(strict=False)


def _resolve_summary_file(subdir: str, filename: str) -> Path:
    """Resolve summary file path with backward-compatible fallback.

    Calibre summary files may still be written into legacy AMS-IO-Agent/output.
    """
    preferred = _resolve_output_root() / subdir / filename
    if preferred.exists():
        return preferred

    legacy = PROJECT_ROOT / "output" / subdir / filename
    if legacy.exists():
        return legacy

    return preferred


def _format_exception(error: Exception) -> str:
    message = f"{type(error).__name__}: {error}"
    causes = []
    current = error.__cause__ or error.__context__
    while current and len(causes) < 3:
        causes.append(f"{type(current).__name__}: {current}")
        current = current.__cause__ or current.__context__
    if causes:
        message += " | caused by: " + " -> ".join(causes)
    return message


def normalize_process_node(process_node: str) -> str:
    from src.core.layout.device_classifier import _normalize_process_node
    from src.core.layout.process_node_config import list_supported_process_nodes

    normalized = _normalize_process_node(process_node)
    supported = list_supported_process_nodes()
    if normalized not in supported:
        raise ValueError(f"Unsupported process node '{normalized}'. Supported nodes: {', '.join(supported)}")
    return normalized


def _resolve_confirmed_config_path(config_path: Path, process_node: str, consume_confirmed_only: bool) -> Path:
    if not consume_confirmed_only:
        return config_path

    if config_path.name.endswith("_confirmed.json"):
        return config_path

    expected_confirmed = config_path.with_name(f"{config_path.stem}_confirmed.json")
    if expected_confirmed.exists():
        return expected_confirmed

    from src.core.layout.T180.confirmed_config_builder import (
        build_confirmed_config_from_io_config as build_confirmed_t180,
    )
    from src.core.layout.T28.confirmed_config_builder import (
        build_confirmed_config_from_io_config as build_confirmed_t28,
    )

    if process_node == "T180":
        generated = Path(build_confirmed_t180(str(config_path)))
    else:
        generated = Path(build_confirmed_t28(str(config_path)))

    if generated.exists():
        return generated

    raise ValueError(
        "Editor-confirmed config required. "
        f"Expected: {expected_confirmed}. "
        "Please run build_io_ring_confirmed_config first."
    )


def validate_intent_graph(config_file_path: str) -> str:
    from src.core.intent_graph.json_validator import validate_config, get_config_statistics

    config_path = Path(config_file_path)
    if not config_path.exists():
        return f"❌ Error: File not found: {config_file_path}"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        return f"❌ Error: Failed to load JSON: {_format_exception(e)}"

    is_valid = bool(validate_config(config))
    if not is_valid:
        return "❌ Intent graph validation failed"

    stats = get_config_statistics(config)
    return (
        "✅ Intent graph validation passed\n"
        f"- Process: {stats.get('process_node', 'N/A')}\n"
        f"- Pads: {stats.get('total_pads', 'N/A')}\n"
        f"- Corners: {stats.get('total_corners', 'N/A')}\n"
        f"- Instances: {stats.get('total_instances', 'N/A')}"
    )


def build_io_ring_confirmed_config(
    config_file_path: str,
    confirmed_output_path: Optional[str] = None,
    process_node: str = "T28",
    skip_editor_confirmation: bool = False,
) -> str:
    from src.core.layout.T180.confirmed_config_builder import (
        build_confirmed_config_from_io_config as build_confirmed_t180,
    )
    from src.core.layout.T28.confirmed_config_builder import (
        build_confirmed_config_from_io_config as build_confirmed_t28,
    )

    config_path = Path(config_file_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Intent graph file does not exist: {config_path}")
    if config_path.suffix.lower() != ".json":
        raise ValueError(f"File is not a JSON file: {config_path}")

    node = normalize_process_node(process_node)
    if node == "T180":
        confirmed_path = build_confirmed_t180(
            source_json_path=str(config_path),
            confirmed_output_path=confirmed_output_path,
            skip_editor_confirmation=skip_editor_confirmation,
        )
    else:
        confirmed_path = build_confirmed_t28(
            source_json_path=str(config_path),
            confirmed_output_path=confirmed_output_path,
            skip_editor_confirmation=skip_editor_confirmation,
        )

    return (
        f"✅ Confirmed IO config generated successfully: {confirmed_path}\n"
        "💡 This file is ready for downstream layout/schematic generation."
    )


def generate_io_ring_schematic(
    config_file_path: str,
    output_file_path: Optional[str] = None,
    process_node: str = "T28",
    consume_confirmed_only: bool = True,
) -> str:
    from src.core.intent_graph.json_validator import convert_config_to_list
    from src.core.layout.device_classifier import _normalize_process_node
    from src.core.layout.process_node_config import get_template_file_paths
    from src.core.schematic.schematic_generator_T180 import generate_multi_device_schematic as gen_t180
    from src.core.schematic.schematic_generator_T28 import generate_multi_device_schematic as gen_t28

    config_path = Path(config_file_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Intent graph file does not exist: {config_path}")
    if config_path.suffix.lower() != ".json":
        raise ValueError(f"File is not a JSON file: {config_path}")

    node = normalize_process_node(process_node)
    config_path = _resolve_confirmed_config_path(config_path, node, consume_confirmed_only)

    template_file_names = get_template_file_paths(node)
    # Backward-compatible fallback names used by older generators/config packs.
    if node == "T180":
        template_file_names = list(dict.fromkeys(template_file_names + ["IO_device_info_T180.json"]))
    elif node == "T28":
        template_file_names = list(dict.fromkeys(template_file_names + ["IO_device_info_T28.json", "device_templates.json"]))
    possible_paths = []
    for name in template_file_names:
        possible_paths.extend(
            [
                PROJECT_ROOT / "src" / "core" / "schematic" / name,
                PROJECT_ROOT / "src" / "app" / "schematic" / name,
                PROJECT_ROOT / "src" / "schematic" / name,
                PROJECT_ROOT / "src" / "scripts" / "devices" / name,
                PROJECT_ROOT / name,
            ]
        )
    template_file = next((p for p in possible_paths if p.exists()), None)
    if template_file is None:
        expected = ", ".join(template_file_names)
        raise FileNotFoundError(f"Device template file not found for process node {node}. Expected: {expected}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if isinstance(config, dict) and isinstance(config.get("ring_config"), dict):
        config_node = config["ring_config"].get("process_node")
        if config_node:
            node = _normalize_process_node(config_node)

    config_list = convert_config_to_list(config)
    if output_file_path is None:
        output_dir = PROJECT_ROOT / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{config_path.stem}_generated.il"
    else:
        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.suffix.lower() != ".il":
            output_path = output_path.with_suffix(".il")

    if node == "T180":
        gen_t180(config_list, str(output_path))
    else:
        gen_t28(config_list, str(output_path))

    device_instances = [item for item in config_list if isinstance(item, dict) and "device" in item]
    device_count = len(device_instances)
    device_types = sorted({item["device"] for item in device_instances if item.get("device")})

    lines = [f"✅ Successfully generated schematic file: {output_path}", "📊 Statistics:", f"  - Device instance count: {device_count}"]
    if device_types:
        lines.append(f"  - Device types used: {', '.join(device_types)}")
    return "\n".join(lines)


def generate_io_ring_layout(
    config_file_path: str,
    output_file_path: Optional[str] = None,
    process_node: str = "T28",
    consume_confirmed_only: bool = True,
) -> str:
    from src.core.layout.T180.layout_visualizer import visualize_layout_T180
    from src.core.layout.T28.layout_visualizer import visualize_layout
    from src.core.layout.layout_generator_factory import generate_layout_from_json

    config_path = Path(config_file_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Intent graph file does not exist: {config_path}")
    if config_path.suffix.lower() != ".json":
        raise ValueError(f"File is not a JSON file: {config_path}")

    node = normalize_process_node(process_node)
    config_path = _resolve_confirmed_config_path(config_path, node, consume_confirmed_only)

    if output_file_path is None:
        output_dir = PROJECT_ROOT / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{config_path.stem}_layout.il"
    else:
        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.suffix.lower() != ".il":
            output_path = output_path.with_suffix(".il")

    generate_layout_from_json(str(config_path), str(output_path), node)

    vis_path = output_path.parent / f"{output_path.stem}_visualization.png"
    try:
        if node == "T180":
            visualize_layout_T180(str(output_path), str(vis_path))
        else:
            visualize_layout(str(output_path), str(vis_path))
    except Exception:
        vis_path = None

    if vis_path and vis_path.exists():
        return (
            f"✅ Successfully generated layout file: {output_path}\n"
            f"📊 Layout visualization generated: {vis_path}\n"
            "💡 Tip: Review the visualization image to verify the layout arrangement."
        )
    return f"✅ Successfully generated layout file: {output_path}"


def _parse_drc_summary(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        start_idx = None
        for i, line in enumerate(lines):
            if "RULECHECK RESULTS STATISTICS (BY CELL)" in line:
                start_idx = i
                break
        if start_idx is None:
            return "DRC statistics section (BY CELL) not found."
        return "\nDRC original statistics content excerpt:\n" + "".join(lines[start_idx:])
    except Exception as e:
        return f"Failed to extract DRC statistics content: {e}"


def _parse_lvs_summary(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        overall_results = ""
        cell_summary = ""
        summary_section = ""
        in_overall = False
        in_cell = False
        in_summary = False

        for i, line in enumerate(lines):
            if "OVERALL COMPARISON RESULTS" in line:
                in_overall = True
                overall_results += line
                continue
            if in_overall:
                overall_results += line
                if "CELL  SUMMARY" in line or "LVS PARAMETERS" in line:
                    in_overall = False

            if "CELL  SUMMARY" in line:
                in_cell = True
                cell_summary += line
                continue
            if in_cell:
                cell_summary += line
                if "LVS PARAMETERS" in line or "SUMMARY" in line:
                    in_cell = False

            if "SUMMARY" in line and (i + 1 < len(lines) and "Total CPU Time" in lines[i + 1]):
                in_summary = True
                summary_section += line
                continue
            if in_summary:
                summary_section += line
                if "Total Elapsed Time" in line:
                    in_summary = False

        result = ["LVS check result summary:", "=" * 50, ""]
        if overall_results:
            result.extend(["Overall comparison results:", overall_results, ""])
        if cell_summary:
            result.extend(["Cell summary:", cell_summary, ""])
        if summary_section:
            result.extend(["Execution summary:", summary_section, ""])

        if not overall_results and not cell_summary and not summary_section:
            return "LVS original summary content (first 100 lines):\n" + "=" * 50 + "\n" + "".join(lines[:100])
        return "\n".join(result)
    except Exception as e:
        return f"Failed to parse LVS summary file: {e}"


def _write_report(title: str, content: str, output_file: str) -> Tuple[bool, str]:
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{title}\n")
            f.write("=" * 50 + "\n\n")
            f.write(content)
        return True, f"Report generated: {output_file}"
    except Exception as e:
        return False, f"Error generating report: {e}"


def run_drc(lib: str, cell: str, view: str = "layout", tech_node: str = "T28") -> str:
    node = normalize_process_node(tech_node)
    script_path = PROJECT_ROOT / "src" / "scripts" / "calibre" / "run_drc.csh"
    if not script_path.exists():
        raise FileNotFoundError(f"DRC script file not found: {script_path}")

    script_path.chmod(0o755)
    ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="r", timeout=30)
    if not ok:
        raise RuntimeError(f"Failed to open cellView {lib}/{cell}/{view}")
    ui_redraw(timeout=5)

    result = execute_csh_script(str(script_path), lib, cell, view, node, timeout=300)
    if not result or str(result).startswith("Remote csh execution failed"):
        return "❌ DRC check failed"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = _resolve_output_root()
    summary_file = str(_resolve_summary_file("drc", f"{cell}.drc.summary"))
    report_file = str(output_root / f"{cell}_drc_report_{timestamp}.txt")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)

    parsed = _parse_drc_summary(summary_file)
    success, msg = _write_report("DRC report", parsed, report_file)
    if not success:
        return f"✅ DRC check completed, but report generation failed: {msg}"

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report_content = f.read()
        return "\n".join(
            [
                "✅ DRC check completed!",
                f"\nReport location: {report_file}",
                "\nReport content:",
                "=" * 50,
                report_content,
                "=" * 50,
            ]
        )
    except Exception as e:
        return f"✅ DRC check completed!\n{msg}\nNote: Cannot read report content: {e}"


def run_lvs(lib: str, cell: str, view: str = "layout", tech_node: str = "T28") -> str:
    node = normalize_process_node(tech_node)
    script_path = PROJECT_ROOT / "src" / "scripts" / "calibre" / "run_lvs.csh"
    if not script_path.exists():
        raise FileNotFoundError(f"LVS script file not found: {script_path}")

    script_path.chmod(0o755)
    ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="r", timeout=30)
    if not ok:
        raise RuntimeError(f"Failed to open cellView {lib}/{cell}/{view}")
    ui_redraw(timeout=5)

    result = execute_csh_script(str(script_path), lib, cell, view, node, timeout=300)
    if not result or str(result).startswith("Remote csh execution failed"):
        return "❌ LVS check failed"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = _resolve_output_root()
    summary_file = str(_resolve_summary_file("lvs", f"{cell}.lvs.summary"))
    report_file = str(output_root / f"{cell}_lvs_report_{timestamp}.txt")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)

    parsed = _parse_lvs_summary(summary_file)
    success, msg = _write_report("LVS report", parsed, report_file)
    if not success:
        return f"✅ LVS check completed, but report generation failed: {msg}"

    try:
        with open(report_file, "r", encoding="utf-8") as f:
            report_content = f.read()
        return "\n".join(
            [
                "✅ LVS check completed!",
                f"\nReport location: {report_file}",
                "\nReport content:",
                "=" * 50,
                report_content,
                "=" * 50,
            ]
        )
    except Exception as e:
        return f"✅ LVS check completed!\n{msg}\nNote: Cannot read report content: {e}"


def run_il_file(il_file_path: str, lib: str, cell: str, view: str = "layout", save: bool = False) -> str:
    ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="w", timeout=30)
    if not ok:
        return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"

    window_ok = ge_open_window(lib, cell, view=view, view_type=None, mode="a", timeout=30)
    if not window_ok:
        return f"❌ Error: Failed to open window for {lib}/{cell}/{view}"

    ui_redraw(timeout=10)
    sleep(0.5)
    rb_exec("cv = geGetEditCellView()", timeout=10)

    skill_path = Path(il_file_path)
    if not skill_path.exists():
        candidate = PROJECT_ROOT / "output" / skill_path.name
        if candidate.exists():
            skill_path = candidate
        else:
            return f"❌ Error: File {il_file_path} does not exist"

    if skill_path.suffix.lower() not in [".il", ".skill"]:
        return f"❌ Error: File {skill_path} is not a valid il/skill file"

    escaped_path = str(skill_path.resolve()).replace("\\", "\\\\").replace('"', '\\"')
    load_result = rb_exec(f'load("{escaped_path}")', timeout=60)
    if load_result and load_result.strip().lower() in {"t", "t\n", ""}:
        if save:
            if save_current_cellview(timeout=30):
                return f"✅ il file {skill_path.name} executed and saved successfully"
            return f"✅ il file {skill_path.name} executed successfully but save failed"
        return f"✅ il file {skill_path.name} executed successfully"

    safe_error = str(load_result).replace("\n", " ").replace("\r", " ").strip() if load_result else ""
    if safe_error and safe_error.lower() not in {"nil", "none"}:
        return f"❌ il file {skill_path.name} execution failed\n[Error Details]: {safe_error}"
    return f"❌ il file {skill_path.name} execution failed"


def list_il_files(directory: str = "output") -> str:
    dir_path = Path(directory)
    if not dir_path.is_absolute():
        dir_path = PROJECT_ROOT / dir_path
    if not dir_path.exists():
        return f"❌ Error: Directory {dir_path} does not exist"

    il_files = list(dir_path.glob("*.il")) + list(dir_path.glob("*.skill"))
    if not il_files:
        return f"No il files found in directory {dir_path}"

    files = sorted(il_files, key=lambda p: p.stat().st_mtime)
    lines = [f"Found the following il files in directory {dir_path}:"]
    for i, file_path in enumerate(files, 1):
        t = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"{i}. {file_path.name} [Timestamp: {t}]")
    return "\n".join(lines)


def run_il_with_screenshot(
    il_file_path: str,
    lib: str,
    cell: str,
    screenshot_path: Optional[str] = None,
    view: str = "layout",
) -> str:
    result_dict: Dict[str, Any] = {
        "status": "error",
        "message": "",
        "screenshot_path": None,
        "observations": [],
    }

    try:
        run_result = run_il_file(il_file_path=il_file_path, lib=lib, cell=cell, view=view, save=True)
        if not run_result.startswith("✅"):
            result_dict["message"] = run_result
            return json.dumps(result_dict, ensure_ascii=False)

        ui_redraw(timeout=10)
        ui_zoom_absolute_scale(0.9, timeout=10)
        sleep(2.0)

        if screenshot_path:
            save_path_obj = Path(screenshot_path).expanduser().resolve(strict=False)
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            save_path = str(save_path_obj)
        else:
            save_dir = PROJECT_ROOT / "output" / "screenshots"
            save_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = str((save_dir / f"virtuoso_{Path(il_file_path).stem}_{stamp}.png").resolve())

        screenshot_script = str((PROJECT_ROOT / "src" / "skill" / "screenshot.il").resolve(strict=False))
        if load_script_and_take_screenshot(screenshot_script, save_path, timeout=20):
            result_dict["status"] = "success"
            result_dict["message"] = run_result
            result_dict["screenshot_path"] = save_path
            result_dict["observations"].append(f"Screenshot saved: {save_path}")
        else:
            result_dict["message"] = "❌ Screenshot failed"
    except Exception as e:
        result_dict["message"] = f"❌ Error occurred while running il file: {_format_exception(e)}"

    return json.dumps(result_dict, ensure_ascii=False)


def check_virtuoso_connection(timeout: int = 5) -> Tuple[bool, str]:
    result = rb_exec('sprintf(nil "test")', timeout=timeout)
    if result and "error" not in result.lower():
        return True, result
    return False, result
