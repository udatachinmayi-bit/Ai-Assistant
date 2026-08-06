"""App Manager for Chinu AI.

Handles all application-related actions, such as opening, closing, and managing applications.
"""

import os
import subprocess

from chinu.logging_system.logger import get_logger

logger = get_logger("app_manager")


class AppManager:
    """Manages all application-related actions."""

    def __init__(self) -> None:
        """Initialize the AppManager."""
        self.apps = {
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
            ],
            "vscode": [
                r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
            ],
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "cmd": "cmd",
            "powershell": "powershell",
            "explorer": "explorer",
            "spotify": [
                r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
            ],
            "discord": [
                r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe --processStart Discord.exe",
            ],
            "telegram": [
                r"C:\Users\%USERNAME%\AppData\Roaming\Telegram Desktop\Telegram.exe",
            ],
            "whatsapp": [
                r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe",
            ],
        }
        logger.info("✅ AppManager initialized")

    def open_application(self, app_name: str) -> bool:
        """
        Opens the specified application.

        Args:
            app_name: The name of the application to open.

        Returns:
            True if the application was opened successfully, False otherwise.
        """
        app_name = app_name.lower()
        if app_name not in self.apps:
            logger.warning(f"Application '{app_name}' not found.")
            return False

        target = self.apps[app_name]
        try:
            if isinstance(target, str):
                subprocess.Popen(target, shell=True)
            else:
                launched = False
                for path in target:
                    expanded_path = os.path.expandvars(path)
                    if " " in expanded_path and not expanded_path.startswith('"'):
                        parts = expanded_path.split(" ", 1)
                        executable = parts[0]
                        args = parts[1] if len(parts) > 1 else ""
                        if os.path.exists(executable):
                            subprocess.Popen(f'"{executable}" {args}', shell=True)
                            launched = True
                            break
                    elif os.path.exists(expanded_path):
                        subprocess.Popen(expanded_path, shell=True)
                        launched = True
                        break

                if not launched:
                    logger.warning(f"Application '{app_name}' not found at any specified path.")
                    return False

            logger.info(f"Application '{app_name}' opened successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to open application '{app_name}': {e}", exc_info=True)
            return False