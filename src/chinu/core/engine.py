"""Engine alias module providing ChinuEngine interface."""

from chinu.core.application import Application

# Alias Application as ChinuEngine for architecture backwards compatibility
ChinuEngine = Application

__all__ = ["Application", "ChinuEngine"]
