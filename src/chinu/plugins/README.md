# Plugin System

The extensibility backbone of Chinu. `plugin_manager/` discovers, validates, and loads plugins at runtime. `interfaces/` defines the `IPlugin` contract every plugin implements. `installed/` is the drop-in folder for first- and third-party plugins — adding a plugin here must never require changes to core/brain/voice.
