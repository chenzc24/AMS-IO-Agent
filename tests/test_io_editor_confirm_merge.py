#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for IO editor confirm merge logic (add/delete/move)."""

from src.app.layout import editor_confirm_merge as merge_logic


def _base_source_payload():
    return {
        "ring_config": {
            "process_node": "T180",
            "chip_width": 630,
            "chip_height": 630,
            "pad_spacing": 90,
            "pad_width": 80,
            "pad_height": 120,
            "corner_size": 130,
            "top_count": 4,
            "bottom_count": 4,
            "left_count": 4,
            "right_count": 4,
            "placement_order": "clockwise",
        },
        "instances": [
            {
                "id": "inst_a",
                "name": "RSTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "view_name": "layout",
                "pad_width": 80,
                "pad_height": 120,
                "position": "bottom_0",
            },
            {
                "id": "inst_b",
                "name": "DOTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "view_name": "layout",
                "pad_width": 80,
                "pad_height": 120,
                "position": "bottom_1",
            },
        ],
        "layout_data": [
            {
                "id": "inst_a",
                "name": "RSTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "view_name": "layout",
                "pad_width": 80,
                "pad_height": 120,
                "position": "bottom_0",
            },
            {
                "id": "inst_b",
                "name": "DOTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "view_name": "layout",
                "pad_width": 80,
                "pad_height": 120,
                "position": "bottom_1",
            },
        ],
    }


def test_move_instance_updates_position_and_strips_meta():
    source = _base_source_payload()
    editor_payload = {
        "ring_config": {
            "process_node": "T180",
            "chip_width": 630,
            "chip_height": 630,
            "pad_spacing": 90,
            "pad_width": 80,
            "pad_height": 120,
            "corner_size": 130,
            "top_count": 4,
            "bottom_count": 4,
            "left_count": 4,
            "right_count": 4,
            "placement_order": "clockwise",
        },
        "instances": [
            {
                "id": "inst_a",
                "name": "RSTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "side": "bottom",
                "order": 2,
                "position": [0, 0],
                "meta": {"_relative_position": "bottom_1"},
            },
            {
                "id": "inst_b",
                "name": "DOTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "side": "bottom",
                "order": 1,
                "position": [0, 0],
                "meta": {"_relative_position": "bottom_0"},
            },
        ],
    }

    merged = merge_logic.build_confirmed_payload(source, editor_payload)
    merged_by_id = {x["id"]: x for x in merged["instances"]}

    assert merged_by_id["inst_a"]["position"] == "bottom_1"
    assert merged_by_id["inst_b"]["position"] == "bottom_0"
    assert "meta" not in merged_by_id["inst_a"]
    assert "meta" not in merged_by_id["inst_b"]
    assert "side" not in merged_by_id["inst_a"]
    assert "order" not in merged_by_id["inst_a"]
    assert "_relative_position" not in merged_by_id["inst_a"]
    assert "position_str" not in merged_by_id["inst_a"]


def test_add_delete_and_dual_container_sync():
    source = _base_source_payload()

    # Remove inst_b, keep inst_a, and add a new analog pad
    editor_payload = {
        "ring_config": source["ring_config"],
        "instances": [
            {
                "id": "inst_a",
                "name": "RSTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "position": "bottom_0",
            },
            {
                "id": "inst_new",
                "name": "MCLK",
                "device": "PVDD1ANA",
                "type": "pad",
                "side": "right",
                "order": 3,
                "position": [0, 0],
                "meta": {"_relative_position": "right_2"},
            },
        ],
    }

    merged = merge_logic.build_confirmed_payload(source, editor_payload)
    ids = [x.get("id") for x in merged["instances"]]

    assert "inst_a" in ids
    assert "inst_b" not in ids
    assert "inst_new" in ids

    new_item = next(x for x in merged["instances"] if x.get("id") == "inst_new")
    assert new_item.get("position") == "right_2"
    assert new_item.get("view_name") == "layout"
    assert new_item.get("pad_width") == 80
    assert new_item.get("pad_height") == 120
    assert "meta" not in new_item
    assert "side" not in new_item
    assert "order" not in new_item
    assert "_relative_position" not in new_item

    # dual-container sync invariant
    assert merged.get("layout_data") == merged.get("instances")


def test_merge_keeps_source_ring_config_shape_only():
    source = {
        "ring_config": {
            "process_node": "T180",
            "chip_width": 630,
            "chip_height": 630,
            "top_count": 4,
            "bottom_count": 4,
            "left_count": 4,
            "right_count": 4,
        },
        "instances": [],
    }
    editor_payload = {
        "ring_config": {
            "process_node": "T180",
            "chip_width": 720,
            "chip_height": 720,
            "width": 8,
            "height": 8,
            "top_count": 8,
            "bottom_count": 8,
            "left_count": 8,
            "right_count": 8,
        },
        "instances": [],
    }

    merged = merge_logic.build_confirmed_payload(source, editor_payload)
    # width/height are not in source shape, so they should not be introduced by merge.
    assert "width" not in merged["ring_config"]
    assert "height" not in merged["ring_config"]
    assert merged["ring_config"]["top_count"] == 8
    assert merged["ring_config"]["chip_width"] == 720


def test_blank_uses_blank_template_with_filler_dimensions():
    source = _base_source_payload()
    editor_payload = {
        "ring_config": source["ring_config"],
        "instances": [
            {
                "id": "inst_a",
                "name": "RSTM",
                "device": "PDDW0412SCDG",
                "type": "pad",
                "position": "bottom_0",
            },
            {
                "id": "inst_blank",
                "name": "blank_gap_0",
                "device": "BLANK",
                "type": "blank",
                "side": "bottom",
                "order": 3,
                "position": [0, 0],
                "meta": {"_relative_position": "bottom_2"},
            },
        ],
    }

    merged = merge_logic.build_confirmed_payload(source, editor_payload)
    blank = next(x for x in merged["instances"] if x.get("id") == "inst_blank")

    assert blank.get("type") == "blank"
    assert blank.get("position") == "bottom_2"
    assert blank.get("pad_width") == 10
    assert blank.get("pad_height") == 120
    assert blank.get("filler_width") == 10
    assert blank.get("filler_height") == 120
    assert "side" not in blank
    assert "order" not in blank
    assert "_relative_position" not in blank


def test_duplicate_name_device_type_kept_by_position():
    source = {
        "ring_config": {
            "process_node": "T180",
            "chip_width": 1350,
            "chip_height": 1350,
            "pad_width": 80,
            "pad_height": 120,
            "corner_size": 130,
            "placement_order": "clockwise",
        },
        "instances": [
            {
                "name": "GIOHD",
                "device": "PVSS2CDG",
                "type": "pad",
                "position": "bottom_13",
                "view_name": "layout",
                "pad_width": 80,
                "pad_height": 120,
            },
            {
                "name": "GIOHD",
                "device": "PVSS2CDG",
                "type": "pad",
                "position": "top_3",
                "view_name": "layout",
                "pad_width": 80,
                "pad_height": 120,
            },
        ],
    }

    editor_payload = {
        "ring_config": source["ring_config"],
        "instances": [
            {
                "name": "GIOHD",
                "device": "PVSS2CDG",
                "type": "pad",
                "position": "bottom_13",
            },
            {
                "name": "GIOHD",
                "device": "PVSS2CDG",
                "type": "pad",
                "position": "top_3",
            },
        ],
    }

    merged = merge_logic.build_confirmed_payload(source, editor_payload)
    gi = [x for x in merged["instances"] if x.get("name") == "GIOHD" and x.get("device") == "PVSS2CDG"]

    assert len(gi) == 2
    assert {x.get("position") for x in gi} == {"bottom_13", "top_3"}
