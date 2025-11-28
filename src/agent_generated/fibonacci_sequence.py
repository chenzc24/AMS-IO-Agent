#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generated Python helper tool
Created: 2025-11-16 15:41:48
"""

from smolagents import tool

@tool
def fibonacci_sequence(n: int) -> list:
    """
    Generate Fibonacci sequence up to n terms
    
    Args:
        n (int): Description of n
        
    Returns:
        list: Result of the operation
    """
    # Simple Fibonacci sequence generator
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]

    sequence = [0, 1]
    for i in range(2, n):
        next_num = sequence[i-1] + sequence[i-2]
        sequence.append(next_num)

    return sequence
