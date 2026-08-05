import logging
import pygetwindow as gw
from pywinauto.application import Application
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindowManager:
    """
    Manages window operations such as focusing, maximizing, minimizing,
    and closing windows using pygetwindow and pywinauto.
    """

    def _get_window(self, title: str) -> Optional[gw.Win32Window]:
        """
        Finds a window by its title.

        Args:
            title (str): The title of the window to find.

        Returns:
            Optional[gw.Win32Window]: The window object if found, otherwise None.
        """
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                return windows[0]
            logger.warning(f"Window with title '{title}' not found.")
            return None
        except Exception as e:
            logger.error(f"An error occurred while searching for window '{title}': {e}", exc_info=True)
            return None

    def focus_window(self, title: str) -> bool:
        """
        Brings a window to the foreground.

        Args:
            title (str): The title of the window to focus.

        Returns:
            bool: True if the window was focused, False otherwise.
        """
        window = self._get_window(title)
        if window:
            try:
                window.activate()
                logger.info(f"Window '{title}' focused.")
                return True
            except Exception as e:
                logger.error(f"Failed to focus window '{title}': {e}", exc_info=True)
                return False
        return False

    def maximize_window(self, title: str) -> bool:
        """
        Maximizes a window.

        Args:
            title (str): The title of the window to maximize.

        Returns:
            bool: True if the window was maximized, False otherwise.
        """
        window = self._get_window(title)
        if window:
            try:
                window.maximize()
                logger.info(f"Window '{title}' maximized.")
                return True
            except Exception as e:
                logger.error(f"Failed to maximize window '{title}': {e}", exc_info=True)
                return False
        return False

    def minimize_window(self, title: str) -> bool:
        """
        Minimizes a window.

        Args:
            title (str): The title of the window to minimize.

        Returns:
            bool: True if the window was minimized, False otherwise.
        """
        window = self._get_window(title)
        if window:
            try:
                window.minimize()
                logger.info(f"Window '{title}' minimized.")
                return True
            except Exception as e:
                logger.error(f"Failed to minimize window '{title}': {e}", exc_info=True)
                return False
        return False

    def close_window(self, title: str) -> bool:
        """
        Closes a window.

        Args:
            title (str): The title of the window to close.

        Returns:
            bool: True if the window was closed, False otherwise.
        """
        window = self._get_window(title)
        if window:
            try:
                window.close()
                logger.info(f"Window '{title}' closed.")
                return True
            except Exception as e:
                logger.error(f"Failed to close window '{title}': {e}", exc_info=True)
                # Fallback for stubborn windows
                try:
                    app = Application().connect(title_re=f".*{title}.*")
                    app.kill()
                    logger.info(f"Used pywinauto to kill window '{title}'.")
                    return True
                except Exception as inner_e:
                    logger.error(f"Fallback kill failed for window '{title}': {inner_e}", exc_info=True)
                    return False
        return False

    def list_windows(self) -> List[str]:
        """
        Lists the titles of all open windows.

        Returns:
            List[str]: A list of window titles.
        """
        try:
            return [window.title for window in gw.getAllWindows() if window.title]
        except Exception as e:
            logger.error(f"Failed to list windows: {e}", exc_info=True)
            return []

if __name__ == '__main__':
    manager = WindowManager()

    # List all windows
    all_windows = manager.list_windows()
    print("Open Windows:", all_windows)

    # Example: Manipulate a window. Open Notepad manually first.
    notepad_title = "Untitled - Notepad"
    if notepad_title in all_windows:
        print(f"\n--- Testing on '{notepad_title}' ---")
        if manager.focus_window(notepad_title):
            print("Focused Notepad.")
        if manager.maximize_window(notepad_title):
            print("Maximized Notepad.")
        if manager.minimize_window(notepad_title):
            print("Minimized Notepad.")
        # Be careful with close, it will close the window.
        # if manager.close_window(notepad_title):
        #     print("Closed Notepad.")
    else:
        print(f"\n'{notepad_title}' not found. Please open Notepad to test window management functions.")