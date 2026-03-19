#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IL execution tool entrypoints without smolagents wrappers."""

from .runtime_t28 import list_il_files, run_il_file, run_il_with_screenshot


def run_il_file_with_save(il_file_path: str, lib: str, cell: str, view: str = "layout") -> str:
    return run_il_file(il_file_path=il_file_path, lib=lib, cell=cell, view=view, save=True)


__all__ = [
    "list_il_files",
    "run_il_file",
    "run_il_file_with_save",
    "run_il_with_screenshot",
]
