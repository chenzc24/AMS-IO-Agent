"""
CDAC (Capacitor Digital-to-Analog Converter) Analysis Module

This module provides intelligent analysis of CDAC capacitor arrays from Excel files.
"""

from .cdac_agent import (
    ObserveExcelTool,
    create_intelligent_agent,
    main as cdac_main
)

__all__ = [
    'ObserveExcelTool',
    'create_intelligent_agent',
    'cdac_main'
]

