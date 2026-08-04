# Installer

Windows packaging and deployment tooling. Not part of the importable `chinu` package — this is build/ops tooling only.

Planned contents (not yet implemented):
- `build_installer.py` — builds a distributable Windows installer (e.g. via PyInstaller + NSIS/Inno Setup).
- `windows_service.py` — wraps Chinu as a Windows service using `pywin32`, for headless/background operation.
- `startup_registration.py` — registers Chinu to auto-start with Windows (Startup folder shortcut or Task Scheduler entry), with a corresponding uninstall/unregister path.

The installer must remain fully decoupled from `src/chinu` — it only invokes the packaged application, it never contains business logic.
