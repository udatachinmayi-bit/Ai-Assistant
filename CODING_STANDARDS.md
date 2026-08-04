# Chinu AI — Coding Standards

These standards apply to all code written in this repository, starting from the first implementation PR.

## 1. Language & Tooling
- **Python 3.12+** everywhere. Use modern typing (`list[str]` not `List[str]`, `str | None` not `Optional[str]`).
- **Formatting:** `black`, line length 100.
- **Linting:** `ruff` (replaces flake8/isort/pyupgrade in one tool).
- **Type checking:** `mypy --strict` on `src/chinu`. All public functions/methods must be fully type-hinted.
- **Pre-commit hooks** run black, ruff, and mypy before every commit.

## 2. Project Structure Rules
- One module = one responsibility. If a file starts doing two unrelated things, split it.
- No module in `core/` may import from `voice/`, `brain/`, `controllers/`, `plugins/`, or `dashboard/`.
- Every module that other modules depend on must expose its contract as an interface (`Protocol` or `ABC`) in `core/interfaces/`.
- Concrete implementations are wired together only in the composition root (`core/engine.py` / `main.py`), never imported ad hoc deep inside another module.
- Plugins are the *only* sanctioned way to add a new "skill." If you're tempted to add a new `if intent == "..."` branch inside `brain/` or `automation/`, it should be a plugin instead.

## 3. Interfaces & Contracts
- Define interfaces with `typing.Protocol` where structural typing is sufficient; use `abc.ABC` when you need shared default behavior.
- Data passed between modules should be explicit, typed data classes (`pydantic.BaseModel` or `@dataclass`), not raw dicts.
- Every interface must be documented with a docstring describing its contract (inputs, outputs, side effects, error behavior).

## 4. Naming Conventions
- `snake_case` for functions, variables, modules.
- `PascalCase` for classes.
- `UPPER_SNAKE_CASE` for constants.
- Interfaces prefixed with `I` (e.g. `ISTTEngine`) to make dependency direction obvious at a glance.
- Event names on the event bus use dot notation: `<module>.<event>` (e.g. `wake_word.detected`, `stt.transcript_ready`).

## 5. Error Handling
- Never use bare `except:`. Catch specific exceptions.
- Define module-specific exception types (e.g. `STTTranscriptionError`) inheriting from a common `ChinuError` base, defined in `core/interfaces`.
- Any action that touches the OS, filesystem, or browser (`controllers/`) must fail loudly and safely — never silently swallow an automation error.

## 6. Logging
- All modules log through `logging_system`, never via `print()`.
- Use structured logging (key-value context) rather than free-form string concatenation.
- Log levels: `DEBUG` for internal flow, `INFO` for user-relevant events, `WARNING` for recoverable issues, `ERROR` for failures, `CRITICAL` for startup/shutdown failures.

## 7. Testing
- Every module in `src/chinu/<module>` has a mirrored test module in `tests/unit/<module>`.
- Integration tests (multi-module flows, e.g. "wake word → STT → intent") live in `tests/integration/`.
- Target minimum 80% coverage on `core/`, `brain/`, and `automation/` (the modules everything else depends on).
- External services/hardware (microphone, LLM APIs, OS calls) must be mockable via the interfaces defined in `core/interfaces` — tests never require real hardware or network access.

## 8. Documentation
- Every module folder has a `README.md` describing its responsibility, public interface, and configuration options (already scaffolded).
- Public classes and functions require docstrings (Google-style).
- Non-obvious architectural decisions go in `docs/architecture/` as short ADRs (Architecture Decision Records).

## 9. Git Workflow
- Conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- One feature/module per branch and PR where possible, to keep changes isolated (mirroring the module isolation itself).
- No secrets, API keys, model weights, or `data/`/`logs/` contents ever committed — see `.gitignore`.

## 10. Security & Safety
- Anything in `controllers/` or `automation/` that can modify the system, files, or send data externally must go through an explicit confirmation/policy check once that layer is implemented — no silent destructive actions.
- Secrets/config load from `.env` / environment variables via `config/`, never hardcoded.
