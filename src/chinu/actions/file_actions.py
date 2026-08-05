import os
import subprocess

from chinu.logging_system.logger import get_logger

logger = get_logger("file_actions")


class FileActions:

    def __init__(self):
        self.folders = {
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
            "videos": os.path.join(os.path.expanduser("~"), "Videos"),
            "music": os.path.join(os.path.expanduser("~"), "Music"),
        }

    def handle(self, command: str) -> bool:

        if not command.startswith("open"):
            return False

        folder = command.replace("open", "").strip()

        if folder not in self.folders:
            return False

        try:
            subprocess.Popen(["explorer", self.folders[folder]])
            logger.info(f"Opened {folder}")
            return True

        except Exception as e:
            logger.error(e)
            return False