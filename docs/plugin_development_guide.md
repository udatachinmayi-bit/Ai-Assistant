# Plugin Development Guide (Draft)

> This guide will be fully written once the Plugin Manager and `IPlugin` interface are implemented.
> It's included now as a placeholder so the intended developer experience is documented from day one.

## Intent

Anyone should be able to add a new capability to Chinu by dropping a self-contained folder into
`src/chinu/plugins/installed/` — without editing `core/`, `brain/`, or `voice/`.

## Planned Plugin Contract

Every plugin will implement the `IPlugin` interface (to be defined in `src/chinu/plugins/interfaces/`):

- `name: str` — unique plugin identifier.
- `description: str` — human-readable summary.
- `capabilities: list[str]` — intents/actions this plugin can handle.
- `execute(intent, context) -> PluginResult` — the entry point invoked by the Automation Engine.
- `setup()` / `teardown()` — lifecycle hooks for resource acquisition/cleanup.

## Planned Folder Shape for a Plugin

```
plugins/installed/<plugin_name>/
├── __init__.py
├── plugin.py        # IPlugin implementation
├── README.md         # what it does, required config/permissions
└── tests/
```

## Planned Safety Rules

- A plugin declares the permissions it needs (filesystem, browser, OS control, network) up front.
- The Automation Engine's policy layer approves/denies plugin actions at runtime based on those declared permissions.
- Plugins never get direct access to other plugins' state — only to the shared context passed in by the Automation Engine.

Full documentation, examples, and a plugin scaffolding CLI will be added when this module is implemented.
