import logging
import os
import subprocess
import platform
from typing import Dict, Optional, List

from .process_manager import ProcessManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppManager:
    """
    Manages desktop applications, including opening, closing, and checking their status.
    It attempts to locate installed applications automatically.
    """

    def __init__(self):
        self.process_manager = ProcessManager()
        self._app_paths = self._initialize_app_paths()

    def _initialize_app_paths(self) -> Dict[str, str]:
        """
        Initializes the paths for supported applications.
        This is a placeholder for a more robust discovery mechanism.
        """
        paths = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # 👈 UPDATED FULL PATH
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "vscode": "Code.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "spotify": "Spotify.exe",
            "whatsapp": "WhatsApp.exe",
            "discord": "Discord.exe",
            "telegram": "Telegram.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
        }
        return paths

    def _get_app_executable(self, app_name: str) -> Optional[str]:
        """
        Gets the executable name for a given application.

        Args:
            app_name (str): The simplified name of the application.

        Returns:
            Optional[str]: The executable name or None if not supported.
        """
        return self._app_paths.get(app_name.lower())

    def open_application(self, app_name: str) -> bool:
        """
        Opens an application.

        Args:
            app_name (str): The name of the application to open.

        Returns:
            bool: True if the application was opened successfully, False otherwise.
        """
        executable = self._get_app_executable(app_name)
        
        if not executable:
            logger.error(f"Application '{app_name}' is not supported or configured.")
            return False

        try:
            # 👇 ADDED THESE TWO LINES
            logger.info(f"Executable Path: {executable}")
            logger.info(f"Exists: {os.path.exists(executable)}")
            
            # 👇 CHANGED THIS - removed creationflags for better compatibility
            subprocess.Popen([executable])
            
            logger.info(f"'{app_name}' opened successfully.")
            return True

        except FileNotFoundError:
            logger.error(f"Executable '{executable}' not found.")
            return False

        except Exception as e:
            logger.error(f"Error opening '{app_name}': {e}", exc_info=True)
            return False

    def close_application(self, app_name: str) -> bool:
        """
        Closes an application by terminating its process.

        Args:
            app_name (str): The name of the application to close.

        Returns:
            bool: True if the application process was terminated, False otherwise.
        """
        executable = self._get_app_executable(app_name)
        if not executable:
            logger.error(f"Application '{app_name}' is not supported or configured.")
            return False

        logger.info(f"Attempting to close '{app_name}' by killing process '{executable}'")
        return self.process_manager.kill_process(executable)

    def restart_application(self, app_name: str) -> bool:
        """
        Restarts an application by closing and then reopening it.

        Args:
            app_name (str): The name of the application to restart.

        Returns:
            bool: True if the restart process was successful, False otherwise.
        """
        logger.info(f"Attempting to restart '{app_name}'.")
        self.close_application(app_name)
        # A small delay might be necessary for the process to terminate completely
        import time
        time.sleep(2)
        return self.open_application(app_name)

    def is_running(self, app_name: str) -> bool:
        """
        Checks if an application is currently running.

        Args:
            app_name (str): The name of the application to check.

        Returns:
            bool: True if the application is running, False otherwise.
        """
        executable = self._get_app_executable(app_name)
        if not executable:
            logger.warning(f"Cannot check status for unsupported application '{app_name}'.")
            return False

        processes = self.process_manager.find_process(executable)
        return processes is not None and len(processes) > 0

    def list_running_apps(self) -> List[str]:
        """
        Lists all supported applications that are currently running.

        Returns:
            List[str]: A list of names of running applications.
        """
        running_apps = []
        for app_name in self._app_paths.keys():
            if self.is_running(app_name):
                running_apps.append(app_name)
        logger.info(f"Currently running supported apps: {running_apps}")
        return running_apps


if __name__ == '__main__':
    manager = AppManager()

    print("--- App Manager Test ---")

    # List running applications from the supported list
    print("Running supported apps:", manager.list_running_apps())

    # Test opening an application
    app_to_test = "chrome"
    print(f"\nAttempting to open {app_to_test}...")
    if manager.open_application(app_to_test):
        print(f"{app_to_test} opened.")
        import time
        time.sleep(3)  # Wait for app to be fully open

        # Check if it's running
        if manager.is_running(app_to_test):
            print(f"{app_to_test} is confirmed to be running.")
        else:
            print(f"Could not confirm if {app_to_test} is running.")

        # Test closing the application
        print(f"Attempting to close {app_to_test}...")
        if manager.close_application(app_to_test):
            print(f"{app_to_test} closed.")
        else:
            print(f"Failed to close {app_to_test}.")
    else:
        print(f"Failed to open {app_to_test}.")

    # Test a non-existent app
    print("\nTesting a non-supported app...")
    manager.open_application("MyFakeApp")