#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import types
from pathlib import Path

if "smolagents" not in sys.modules:
    smolagents_stub = types.ModuleType("smolagents")

    def tool(func):
        return func

    smolagents_stub.tool = tool
    sys.modules["smolagents"] = smolagents_stub

import src.tools.io_ring_generator_tool as ring_tool


def test_order_constraints_for_fixed_orchestrator(monkeypatch, tmp_path):
    source = tmp_path / "intent_graph.json"
    source.write_text("{}", encoding="utf-8")

    calls = []

    def fake_build_confirmed_config_from_io_config(source_json_path, confirmed_output_path=None):
        calls.append("confirmed")
        confirmed = Path(confirmed_output_path) if confirmed_output_path else Path(source_json_path).with_name("intent_graph_confirmed.json")
        confirmed.write_text("{}", encoding="utf-8")
        return str(confirmed)

    def fake_generate_layout(config_file_path, output_file_path=None, process_node="T180", consume_confirmed_only=True):
        calls.append("layout")
        assert config_file_path.endswith("_confirmed.json")
        assert consume_confirmed_only is True
        return "✅ layout ok"

    def fake_generate_schematic(config_file_path, output_file_path=None, process_node="T180", consume_confirmed_only=True):
        calls.append("schematic")
        assert config_file_path.endswith("_confirmed.json")
        assert consume_confirmed_only is True
        return "✅ schematic ok"

    monkeypatch.setattr(ring_tool, "build_confirmed_config_from_io_config", fake_build_confirmed_config_from_io_config)
    monkeypatch.setattr(ring_tool, "generate_io_ring_layout", fake_generate_layout)
    monkeypatch.setattr(ring_tool, "generate_io_ring_schematic", fake_generate_schematic)
    monkeypatch.setattr(ring_tool, "_normalize_supported_process_node", lambda process_node: "T180")

    result = ring_tool.generate_io_ring_confirmed_artifacts(str(source), process_node="T180")

    assert result.startswith("✅")
    assert calls == ["confirmed", "layout", "schematic"]


def test_confirmed_consumption_for_layout_requires_confirmed_by_default(tmp_path):
    source = tmp_path / "intent_graph.json"
    source.write_text("{}", encoding="utf-8")

    result = ring_tool.generate_io_ring_layout(
        config_file_path=str(source),
        process_node="T28",
    )

    assert result.startswith("❌")
    assert "Editor-confirmed config required" in result


def test_confirmed_consumption_for_schematic_requires_confirmed_by_default(tmp_path):
    source = tmp_path / "intent_graph.json"
    source.write_text("{}", encoding="utf-8")

    result = ring_tool.generate_io_ring_schematic(
        config_file_path=str(source),
        process_node="T28",
    )

    assert result.startswith("❌")
    assert "Editor-confirmed config required" in result
