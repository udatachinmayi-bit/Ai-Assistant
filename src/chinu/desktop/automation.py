import logging
import pyautogui
from typing import Tuple, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Automation:
    """
    Provides a high-level interface for GUI automation tasks
    using pyautogui, such as mouse and keyboard control.
    """

    def click(self, x: int, y: int, button: str = 'left') -> None:
        """
        Performs a mouse click at the specified coordinates.

        Args:
            x (int): The x-coordinate for the click.
            y (int): The y-coordinate for the click.
            button (str): The mouse button to use ('left', 'right', 'middle').
        """
        try:
            pyautogui.click(x, y, button=button)
            logger.info(f"Clicked {button} button at ({x}, {y}).")
        except Exception as e:
            logger.error(f"Failed to perform {button} click at ({x}, {y}): {e}", exc_info=True)

    def double_click(self, x: int, y: int) -> None:
        """
        Performs a double-click at the specified coordinates.

        Args:
            x (int): The x-coordinate for the double-click.
            y (int): The y-coordinate for the double-click.
        """
        try:
            pyautogui.doubleClick(x, y)
            logger.info(f"Double-clicked at ({x}, {y}).")
        except Exception as e:
            logger.error(f"Failed to perform double-click at ({x}, {y}): {e}", exc_info=True)

    def right_click(self, x: int, y: int) -> None:
        """
        Performs a right-click at the specified coordinates.

        Args:
            x (int): The x-coordinate for the right-click.
            y (int): The y-coordinate for the right-click.
        """
        self.click(x, y, button='right')

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> None:
        """
        Moves the mouse to the specified coordinates.

        Args:
            x (int): The target x-coordinate.
            y (int): The target y-coordinate.
            duration (float): The time in seconds to move the mouse.
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y}).")
        except Exception as e:
            logger.error(f"Failed to move mouse to ({x}, {y}): {e}", exc_info=True)

    def scroll(self, amount: int) -> None:
        """
        Scrolls the mouse wheel.

        Args:
            amount (int): The number of units to scroll.
                          Positive for up, negative for down.
        """
        try:
            pyautogui.scroll(amount)
            direction = "up" if amount > 0 else "down"
            logger.info(f"Scrolled {abs(amount)} units {direction}.")
        except Exception as e:
            logger.error(f"Failed to scroll: {e}", exc_info=True)

    def write(self, text: str, interval: float = 0.05) -> None:
        """
        Types a string of text.

        Args:
            text (str): The text to type.
            interval (float): The time in seconds between each keypress.
        """
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: '{text}'")
        except Exception as e:
            logger.error(f"Failed to type text '{text}': {e}", exc_info=True)

    def press(self, key: str) -> None:
        """
        Presses a single keyboard key.

        Args:
            key (str): The key to press (e.g., 'enter', 'f1', 'a').
        """
        try:
            pyautogui.press(key)
            logger.info(f"Pressed key: '{key}'")
        except Exception as e:
            logger.error(f"Failed to press key '{key}': {e}", exc_info=True)

    def hotkey(self, keys: List[str]) -> None:
        """
        Presses a combination of keys simultaneously (a hotkey).

        Args:
            keys (List[str]): A list of keys to press together (e.g., ['ctrl', 'c']).
        """
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"Pressed hotkey: {keys}")
        except Exception as e:
            logger.error(f"Failed to press hotkey {keys}: {e}", exc_info=True)

    def take_screenshot(self, path: str) -> bool:
        """
        Takes a screenshot and saves it to a file.

        Args:
            path (str): The file path to save the screenshot.

        Returns:
            bool: True if the screenshot was taken successfully, False otherwise.
        """
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            logger.info(f"Screenshot saved to '{path}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot and save to '{path}': {e}", exc_info=True)
            return False

if __name__ == '__main__':
    import time
    auto = Automation()

    print("--- Automation Test ---")
    print("Note: This will take control of your mouse and keyboard.")
    print("Starting in 3 seconds...")
    time.sleep(3)

    # Get screen size
    width, height = pyautogui.size()
    center_x, center_y = width // 2, height // 2

    # Move mouse
    auto.move_mouse(center_x, center_y)
    time.sleep(1)
    auto.move_mouse(center_x + 100, center_y)
    time.sleep(1)

    # Click
    # auto.click(center_x, center_y) # Be careful where you click!

    # Scroll
    auto.scroll(-10) # Scroll down
    time.sleep(1)
    auto.scroll(10) # Scroll up

    # Write (e.g., in an open text editor)
    # auto.write("Hello from Chinu AI!")
    # time.sleep(1)

    # Press key
    # auto.press('enter')

    # Hotkey (e.g., to copy)
    # auto.hotkey(['ctrl', 'a'])
    # auto.hotkey(['ctrl', 'c'])

    # Screenshot
    screenshot_path = "chinu_ai_screenshot.png"
    if auto.take_screenshot(screenshot_path):
        print(f"Screenshot test successful. Image saved to {screenshot_path}")
    else:
        print("Screenshot test failed.")

    print("\nAutomation test finished.")