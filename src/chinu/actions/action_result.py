"""
This module defines the data structures for action results.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionResult:
    """A data class to hold the result of an action."""
    success: bool
    action: str
    target: Any = None
    query: str = ""
    message: str = ""
    data: dict = field(default_factory=dict)