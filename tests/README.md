# Tests

Mirrors `src/chinu/` 1:1:
- `unit/` — isolated tests per module, mirroring `src/chinu/<module>` structure. External dependencies (hardware, network, OS) are mocked via the interfaces in `core/interfaces`.
- `integration/` — multi-module flow tests (e.g. wake word → STT → intent → automation).
- `fixtures/` — shared test fixtures/sample data (sample audio clips, mock config files, etc.).

Run with `pytest` from the project root once dependencies are installed.
