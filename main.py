"""Chinu AI — application entry point.

Composition root for bootstrapping and running the Chinu AI engine.
"""

from chinu.core.engine import ChinuEngine


def main() -> None:
    """Entry point for running Chinu AI engine."""
    engine = ChinuEngine()
    engine.run()


if __name__ == "__main__":
    main()

