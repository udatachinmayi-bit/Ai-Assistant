# Chinu AI — Architecture

This document is the source of truth for the project structure. It explains **what each folder is for**,
**what it must never do**, and **how it talks to the rest of the system**. Nothing in this document is
implemented yet — this is the contract the implementation must follow.

---

## 1. Architectural Style

Chinu follows **Clean Architecture** with a **plugin-based capability system**:

```
┌─────────────────────────────────────────────────────────────┐
│                        Plugins / Skills                       │  ← outermost, most volatile
│  (windows_controller, browser_controller, file_controller,    │
│   coding_assistant, vision, and any future third-party skill) │
├─────────────────────────────────────────────────────────────┤
│                     Application Services                      │
│        (automation engine, memory system, dashboard)          │
├─────────────────────────────────────────────────────────────┤
│                          AI Brain                              │
│        (intent recognition, reasoning, context building)      │
├─────────────────────────────────────────────────────────────┤
│                         Core Engine                            │
│   (event bus, lifecycle, plugin manager, interface contracts) │  ← innermost, most stable
└─────────────────────────────────────────────────────────────┘
```

Rules:
- **Dependencies point inward only.** The Core Engine never imports from `voice/`, `controllers/`, or `plugins/`.
- **Outer layers depend on inner-layer interfaces, never on inner-layer concrete classes.**
- **Every module exchanges data via plain data contracts (DTOs) defined in `core/interfaces`,** not by importing another module's internal classes.
- **Cross-module communication happens over the Event Bus** (publish/subscribe) or through explicit interface injection — never through direct singleton access.

---

## 2. Top-Level Folders

| Folder | Purpose |
|---|---|
| `src/chinu/` | The installable Python package. All application code lives here. |
| `installer/` | Windows-specific packaging: auto-start registration, service wrapper, build scripts for a distributable installer (e.g. via PyInstaller/NSIS). Not part of the importable package. |
| `models/` | Local model artifacts (weights, tokenizer files, ONNX/GGUF models) for LLM, STT, TTS, wake word, and vision. Gitignored except for `.gitkeep`/manifest files — models are downloaded, not committed. |
| `assets/` | Static, non-code resources: notification sounds, tray icons, images used by the dashboard or TTS "earcons". |
| `data/` | Runtime-generated data: SQLite/vector DB files, cached memory. Gitignored. |
| `logs/` | Runtime log output files. Gitignored. |
| `tests/` | Automated tests. Mirrors the `src/chinu` package structure 1:1 so every module has a corresponding test module. |
| `scripts/` | One-off developer scripts (env setup, model download helpers, formatting/lint runners). Not shipped to end users. |
| `docs/` | Architecture diagrams, API references, and the plugin development guide for third-party contributors. |
| `main.py` | Single entry point. Responsible only for bootstrapping `chinu.core.engine` — contains no business logic. |

---

## 3. `src/chinu/` Module Responsibilities

### 3.1 `core/` — Core Engine
The heart of the system. Owns:
- **`engine.py`** — application lifecycle: startup sequence, shutdown/cleanup, top-level orchestration loop.
- **`event_bus.py`** — the publish/subscribe backbone all modules use to communicate (e.g. `wake_word.detected`, `stt.transcript_ready`, `brain.intent_resolved`).
- **`lifecycle.py`** — defines startup/shutdown hooks that other modules can register against, so modules can initialize/dispose resources in a controlled order.
- **`interfaces/`** — abstract base classes / protocols that define contracts every other module must implement (e.g. `IWakeWordEngine`, `ISTTEngine`, `ITTSEngine`, `IMemoryStore`, `IController`, `IPlugin`). This is the only folder every other module is allowed to depend on.

**Must never:** import a concrete implementation from `voice/`, `brain/`, `controllers/`, or `plugins/`.

### 3.2 `brain/` — AI Brain
Turns transcribed text + context into an understood, actionable intent.
- **`llm/`** — adapters to LLM backends (local model runner, or cloud API client), all implementing a common `ILLMProvider` interface so the backend is swappable.
- **`intent/`** — intent classification/parsing: maps free-form text to a structured `Intent` object (name + parameters).
- **`context/`** — builds the working context window sent to the LLM (recent conversation, relevant memories, active plugin capabilities).
- **`reasoning/`** — higher-level decision logic: multi-step planning, tool/plugin selection, chaining.

### 3.3 `voice/` — Voice System
Everything audio-related, split by concern:
- **`wake_word/`** — always-listening wake word detector (e.g. "Hey Chinu"); publishes a `wake_word.detected` event and nothing else — it does not know what happens after.
- **`stt/`** — Speech-to-Text engine adapters (e.g. Whisper, Vosk); converts audio buffers to text.
- **`tts/`** — Text-to-Speech engine adapters; converts text responses to natural speech output.
- **`audio_io/`** — low-level microphone capture and speaker playback, shared by wake word/STT/TTS so audio device handling isn't duplicated three times.

### 3.4 `memory/` — Memory System
Persistent and working memory, so Chinu "remembers" things across sessions.
- **`short_term/`** — in-session conversational memory (recent turns, scratch state).
- **`long_term/`** — durable facts/preferences the user has told Chinu, persisted via `database/`.
- **`vector_store/`** — embeddings-based semantic memory for retrieval-augmented recall.

### 3.5 `automation/` — Automation Engine
Turns a resolved intent into a safe, executed action.
- **`tasks/`** — atomic, single-purpose task definitions (the unit of automation).
- **`scheduler/`** — time/event-based triggers ("every morning at 8am…", "when I open Chrome…").
- **`workflows/`** — multi-step task chains composed from individual tasks.

This layer is also where a future **permission/policy gate** will live, so no controller executes a
destructive action without an explicit safety check — that gate is designed for, but not implemented, in this step.

### 3.6 `controllers/` — System Controllers
Concrete "hands" of the assistant, each isolated so one can be disabled/replaced without affecting the others:
- **`windows_controller/`** — OS-level actions (apps, windows, system settings, shell commands).
- **`browser_controller/`** — browser automation/control.
- **`file_controller/`** — filesystem read/write/organize operations.

### 3.7 `coding_assistant/`
An isolated capability module for code-related help (reading/writing/refactoring code on request), with its own `analyzers/` and `generators/` sub-concerns so it can evolve independently of the rest of the assistant.

### 3.8 `vision/`
Screen/camera perception capability (e.g. "what's on my screen", OCR, object/window detection), split into `detectors/` and `ocr/`.

### 3.9 `plugins/` — Plugin System
The extensibility backbone:
- **`plugin_manager/`** — discovers, loads, validates, enables/disables plugins at runtime.
- **`interfaces/`** — the `IPlugin` contract (metadata, capability declaration, execute method) every plugin must implement.
- **`installed/`** — drop-in folder for first- and third-party plugins; each plugin is self-contained here and registers itself with the Plugin Manager. Nothing in `core/`, `brain/`, or `voice/` should ever need to change to add a new plugin here.

### 3.10 `config/` — Configuration
Centralized, environment-aware settings (YAML/`.env`-driven), with a single `config_loader.py` that every other module reads from — no module reads environment variables or config files directly on its own.

### 3.11 `logging_system/` — Logging
Centralized structured logging setup (console + rotating file handlers), used uniformly across every module so log format/level is controlled in one place. Named `logging_system` (not `logging`) to avoid shadowing Python's standard library module.

### 3.12 `dashboard/` — Dashboard
A local UI (backend API + frontend) for observing/controlling Chinu: conversation history, plugin status, logs, settings — split into `backend/` and `frontend/` so the UI layer can be swapped (e.g. web app vs. desktop tray app) without touching assistant logic.

### 3.13 `database/` — Database
Data persistence layer:
- **`models/`** — ORM/schema definitions.
- **`migrations/`** — schema version migrations.
Consumed by `memory/long_term`, `automation/scheduler`, and `dashboard/backend` — but they only talk to it through a repository interface, never with raw queries scattered across the codebase.

### 3.14 `utils/`
Small, generic, dependency-free helper functions shared across modules (no business logic lives here).

---

## 4. `tests/`
Mirrors `src/chinu/` 1:1: `tests/unit/<module>/...` and `tests/integration/...`. Every module ships with
its own tests so it can be verified in isolation — consistent with "every module should be replaceable
without affecting others."

---

## 5. Cross-Cutting Rules (SOLID in practice)

- **Single Responsibility** — one module = one reason to change (STT only transcribes; it never decides what to do with the text).
- **Open/Closed** — new capabilities are added via new plugins/adapters, not by editing existing module internals.
- **Liskov Substitution** — any concrete engine (e.g. `WhisperSTT`, `AzureSTT`) must be fully substitutable behind `ISTTEngine` with no surprises.
- **Interface Segregation** — interfaces in `core/interfaces` are small and capability-specific (`ISTTEngine`, `ITTSEngine`) rather than one giant `IEngine`.
- **Dependency Inversion** — high-level modules (`brain`, `automation`) depend on interfaces, and concrete implementations are wired together at startup in `core/engine.py` (composition root), not imported ad hoc throughout the codebase.

---

## 6. Data Flow Example (illustrative only — not implemented)

```
Mic Audio
   → voice/audio_io (capture)
   → voice/wake_word (detects "Hey Chinu")        → event: wake_word.detected
   → voice/stt (transcribes command)               → event: stt.transcript_ready
   → brain/intent (parses intent)                  → event: brain.intent_resolved
   → brain/context + memory (adds relevant context)
   → automation (selects task/workflow/plugin)
   → controllers/plugins (executes the action)
   → brain (formulates natural language response)
   → voice/tts (speaks the response)
   → logging_system + dashboard (observe the whole flow)
```

---

## 7. Recommended Python Packages (for future implementation)

Grouped by module — final choices may change during implementation; these are the leading candidates.

| Area | Candidates |
|---|---|
| Core / Async runtime | `asyncio`, `anyio`, `pydantic` (v2, for interface/data contracts) |
| Wake Word | `openwakeword`, `pvporcupine` |
| Speech-to-Text | `faster-whisper`, `openai-whisper`, `vosk` |
| Text-to-Speech | `edge-tts`, `pyttsx3`, `coqui-tts`, `elevenlabs` (cloud, optional) |
| Audio I/O | `sounddevice`, `pyaudio`, `numpy` |
| AI Brain / LLM | `anthropic`, `openai`, `llama-cpp-python`, `ollama` (local models) |
| Memory / Vector Store | `chromadb`, `faiss-cpu`, `sqlite-vec` |
| Database / ORM | `sqlalchemy`, `alembic` |
| Automation / Windows control | `pyautogui`, `pywin32`, `psutil`, `pygetwindow` |
| Browser control | `playwright`, `selenium` |
| File control | `watchdog`, `pathlib` (stdlib) |
| Vision | `opencv-python`, `pytesseract`, `mss` (screen capture), `pillow` |
| Plugin system | `pluggy`, `importlib.metadata` (stdlib), `stevedore` |
| Config | `pydantic-settings`, `python-dotenv`, `pyyaml` |
| Logging | `structlog`, `loguru`, `rich` (console formatting) |
| Dashboard backend | `fastapi`, `uvicorn`, `websockets` |
| Dashboard frontend | React or plain HTML/JS served by FastAPI (decided during implementation) |
| Scheduling | `apscheduler` |
| Windows service / auto-start | `pywin32` (`win32serviceutil`), Windows Task Scheduler / Startup folder shortcut |
| Installer packaging | `pyinstaller`, NSIS/Inno Setup |
| Testing | `pytest`, `pytest-asyncio`, `pytest-mock`, `pytest-cov` |
| Lint / Format / Type-check | `ruff`, `black`, `mypy`, `pre-commit` |

---

## 8. Coding Standards

See [`CODING_STANDARDS.md`](./CODING_STANDARDS.md).
