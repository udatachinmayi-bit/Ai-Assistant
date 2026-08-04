# Chinu AI

**Chinu** is a production-grade, locally-running personal AI assistant for Windows — conceptually similar to JARVIS.
It boots automatically with Windows, listens for a wake word, understands voice commands, speaks naturally,
remembers context over time, and safely automates and controls your machine through a modular plugin system.

> **Status:** Architecture / scaffolding phase. No application logic has been implemented yet.
> This repository currently defines the structure, contracts, and conventions the project will be built on.

---

## Why this architecture?

Chinu is designed to grow to **hundreds of features** over time without turning into a ball of mud. To do that:

- Every capability (STT, TTS, wake word, memory, automation, etc.) lives in its **own isolated module**.
- Modules talk to each other only through **interfaces/contracts**, never through direct concrete imports.
- New capabilities are added as **plugins**, not by editing the core.
- The **Core Engine** knows nothing about *how* a module works internally — only its interface.
- Any module can be swapped (e.g. replace Whisper with a different STT engine) without touching anything else.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full breakdown of every folder and its responsibility,
and [`CODING_STANDARDS.md`](./CODING_STANDARDS.md) for how code should be written in this repo.

---

## High-Level System Map

```
                        ┌───────────────────────┐
                        │        Core Engine      │
                        │  (orchestration, events) │
                        └───────────┬───────────┘
                                    │
        ┌────────────┬─────────────┼─────────────┬─────────────┐
        │             │             │             │             │
   ┌────▼───┐   ┌─────▼────┐  ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
   │ Voice  │   │ AI Brain │  │  Memory   │ │ Automation│ │  Plugins  │
   │ System │   │ (LLM /   │  │  System   │ │  Engine   │ │  Manager  │
   │        │   │ Reasoning)│  │           │ │           │ │           │
   └────┬───┘   └─────┬────┘  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
        │             │             │             │             │
   Wake Word,    Intent/Context  Short/Long   Windows/Browser  3rd-party /
   STT, TTS,     Reasoning        Term +       /File            first-party
   Audio I/O                      Vector Store Controllers      capabilities
```

The **Dashboard** and **Logging** modules observe the whole system. The **Database** module persists
structured state. The **Config** module supplies settings to everything else. The **Installer** packages
Chinu as a native Windows auto-start application.

---

## Project Layout (top level)

```
Chinu-AI/
├── src/chinu/          # All application source code (the actual package)
├── installer/          # Windows packaging, service registration, auto-start
├── models/             # Local model weights/configs (LLM, STT, TTS, wake word, vision)
├── assets/             # Sounds, icons, images used by the assistant
├── data/               # Runtime data (databases, memory store) — gitignored
├── logs/               # Runtime logs — gitignored
├── tests/              # Unit + integration tests, mirrors src/chinu structure
├── scripts/            # Developer setup/utility scripts
├── docs/               # Architecture notes, API docs, plugin dev guide
├── main.py             # Application entry point
├── requirements.txt    # Runtime dependencies
├── requirements-dev.txt# Development/test dependencies
├── pyproject.toml      # Build system, tooling config (black, ruff, mypy, pytest)
├── .env.example        # Template for local environment variables/secrets
└── .gitignore
```

Full per-folder responsibilities are documented in [`ARCHITECTURE.md`](./ARCHITECTURE.md) and in a
`README.md` inside each module folder under `src/chinu/`.

---

## Getting Started (once implementation begins)

```powershell
# 1. Clone and enter the project
git clone <repo-url> Chinu-AI
cd Chinu-AI

# 2. Create and activate a virtual environment (Python 3.12+)
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 4. Copy environment template
copy .env.example .env

# 5. Run
python main.py
```

---

## Design Principles

1. **Clean Architecture** — dependencies point inward: `plugins/controllers → brain/automation → core`. The core never depends on concrete implementations.
2. **SOLID** — every module exposes an interface (`interfaces/` or `*_interface.py`); concrete engines (e.g. `WhisperSTT`, `PorcupineWakeWord`) implement those interfaces and are swapped via configuration/dependency injection.
3. **Plugin-first** — new skills (e.g. "control Spotify", "summarize my email") are written as isolated plugins registered with the Plugin Manager, not as changes to core modules.
4. **Fail-safe automation** — anything that controls the OS, files, or browser goes through a permission/policy layer before execution (defined later, in the Automation Engine).
5. **Observability by default** — every module logs through the shared Logging System; the Dashboard visualizes system state.
6. **Local-first** — designed to run fully on-device where possible; cloud AI (LLM APIs) is an interchangeable backend behind the Brain interface, not a hard dependency.

---

## Roadmap (high level, not yet implemented)

| Phase | Focus |
|-------|-------|
| 0 | ✅ Architecture & folder structure (this step) |
| 1 | Core Engine + Config + Logging + Plugin Manager skeleton |
| 2 | Voice System: Wake Word → STT → TTS pipeline |
| 3 | AI Brain: LLM integration, intent parsing, context |
| 4 | Memory System: short-term + long-term + vector store |
| 5 | Windows / File / Browser Controllers |
| 6 | Automation Engine + permissioning |
| 7 | Coding Assistant + Vision Module |
| 8 | Dashboard UI |
| 9 | Installer: auto-start, Windows service, packaging |

---

## License

TBD.
