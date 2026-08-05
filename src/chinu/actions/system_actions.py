import ctypes
import os
import subprocess

from chinu.logging_system.logger import get_logger

logger = get_logger("system_actions")


class SystemActions:

    def handle(self, command: str) -> bool:

        command = command.lower().strip()

        try:

            if command == "lock computer":
                ctypes.windll.user32.LockWorkStation()
                logger.info("Computer Locked")
                return True

            if command == "shutdown computer":
                subprocess.Popen("shutdown /s /t 5")
                logger.info("Shutdown Started")
                return True

            if command == "restart computer":
                subprocess.Popen("shutdown /r /t 5")
                logger.info("Restart Started")
                return True

            if command == "sleep computer":
                os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")
                logger.info("Sleep Mode")
                return True

        except Exception as e:

            logger.error(e)
            return False

        return False