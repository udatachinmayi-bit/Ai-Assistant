import os
import subprocess
import webbrowser

from chinu.logging_system.logger import get_logger

logger = get_logger("app_actions")


class AppActions:

    def __init__(self):

        self.apps = {

            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],

            "vscode": [
                r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
            ],

            "notepad": "notepad",

            "calculator": "calc",

            "paint": "mspaint",

            "cmd": "cmd",

            "terminal": "wt",

            "explorer": "explorer",

            "spotify": [
                r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
            ],

            "whatsapp": [
                r"C:\Users\%USERNAME%\AppData\Local\WhatsApp\WhatsApp.exe",
            ],
        }

    def handle(self, command: str) -> bool:

        if not command.startswith("open"):
            return False

        app = command.replace("open", "").strip()

        if app not in self.apps:
            return False

        target = self.apps[app]

        try:

            if isinstance(target, str):

                subprocess.Popen(target)

            else:

                launched = False

                for path in target:

                    path = os.path.expandvars(path)

                    if os.path.exists(path):

                        subprocess.Popen(path)

                        launched = True

                        break

                if not launched:

                    logger.warning(f"{app} not found")

                    return False

            logger.info(f"{app} opened successfully")

            return True

        except Exception as e:

            logger.error(e)

            return False