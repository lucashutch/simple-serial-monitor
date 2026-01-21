"""
Embedded Cereal Bowl - A collection of lightweight Python utilities for
embedded development.

This package provides tools for serial monitoring, code formatting, time conversion,
and line ending checking, designed to simplify common embedded development tasks.
"""

__version__ = "0.1.0"
__author__ = "Lucas Hutch"

from . import monitor, formatter, timestamp, utils

__all__ = ["monitor", "formatter", "timestamp", "utils"]
