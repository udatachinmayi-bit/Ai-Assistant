# Core Engine

Owns application lifecycle, the event bus, and the interface contracts (`interfaces/`) that every other module depends on. This is the only module every other module is allowed to import from. Must never import concrete implementations from other modules.
