#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility exports for health-check tools."""

from src.utils.tools_adapters.health_check_tool import (
    check_virtuoso_connection,
    quick_diagnostic,
    run_health_check,
)

__all__ = ["run_health_check", "check_virtuoso_connection", "quick_diagnostic"]
