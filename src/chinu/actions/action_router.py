"""Action Router for Chinu AI.

Routes voice commands to appropriate action handlers, including the Desktop Manager.
"""

import os
import webbrowser
from typing import List

from chinu.actions.app_actions import AppActions
from chinu.actions.browser_actions import BrowserActions
from chinu.actions.file_actions import FileActions
from chinu.actions.system_actions import SystemActions
from chinu.desktop.app_manager import AppManager
from chinu.desktop.automation import Automation
from chinu.desktop.process_manager import ProcessManager
from chinu.desktop.window_manager import WindowManager
from chinu.logging_system.logger import get_logger

logger = get_logger("action_router")


class ActionRouter:
    """Routes commands to appropriate action handlers."""

    def __init__(self) -> None:
        """Initialize the ActionRouter with all action handlers."""
        # Legacy handlers
        self.apps = AppActions()
        self.browser = BrowserActions()
        self.files = FileActions()
        self.system = SystemActions()

        # Desktop Manager modules
        self.app_manager = AppManager()
        self.window_manager = WindowManager()
        self.process_manager = ProcessManager()
        self.automation = Automation()

        logger.info("✅ ActionRouter initialized with all handlers, including Desktop Manager")

    def _clean_target(self, text: str, action: str = "") -> str:
        """Removes filler words and the action itself from the command target."""
        # Combine action with common filler words
        filler_words = ["please", "for me", "can you", "the", "a", "an", "window", "application", "app", action]
        
        # Remove all occurrences of filler words
        for word in filler_words:
            text = text.replace(word, "").strip()
            
        return text

    def _handle_web_commands(self, command: str) -> bool:
        """
        Handles commands related to opening websites and searching.
        Returns True if the command was recognized and handled, False otherwise.
        """
        # Direct URL mapping for simple "open" commands
        site_map = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "chatgpt": "https://chat.openai.com",
            "facebook": "https://facebook.com",
            "instagram": "https://instagram.com",
            "x": "https://x.com",
            "twitter": "https://x.com",  # twitter is now x
            "linkedin": "https://linkedin.com",
        }

        # Search command handling
        if command.startswith("search "):
            parts = command.split(" for ", 1)
            if len(parts) == 2:
                search_engine_part, query = parts
                # Clean up the search engine part to get the keyword
                search_engine = self._clean_target(search_engine_part, action="search").lower()
                
                search_urls = {
                    "youtube": "https://www.youtube.com/results?search_query=",
                    "google": "https://www.google.com/search?q=",
                }
                
                if search_engine in search_urls:
                    url = search_urls[search_engine] + query.replace(" ", "+")
                    logger.info(f"Executing: Search {search_engine.capitalize()} for '{query}'")
                    webbrowser.open(url)
                    logger.info(f"Success: Opened browser for search query.")
                    return True

        # Simple "open" commands for websites
        if command.startswith("open "):
            target = self._clean_target(command, action="open")
            if target in site_map:
                url = site_map[target]
                logger.info(f"Executing: Open Website '{target}'")
                webbrowser.open(url)
                logger.info(f"Success: Opened {url} in browser.")
                return True
        
        return False

    def _handle_desktop_commands(self, command: str) -> bool:
        """
        Handles commands related to the Desktop Manager.
        Returns True if the command was recognized and handled, False otherwise.
        """
        # Commands with targets (e.g., "open chrome")
        action_map = {
            "open": self.app_manager.open_application,
            "close": self.app_manager.close_application,
            "maximize": self.window_manager.maximize_window,
            "minimize": self.window_manager.minimize_window,
            "focus": self.window_manager.focus_window,
            "switch to": self.window_manager.focus_window,
        }

        for action, method in action_map.items():
            if command.startswith(action + " "):
                target = self._clean_target(command, action=action)
                if target:
                    logger.info(f"Executing: {action.capitalize()} '{target}'")
                    try:
                        success = method(target)
                        if success:
                            logger.info(f"Success: {action.capitalize()}d '{target}'.")
                        else:
                            logger.warning(f"Action '{action} {target}' did not succeed or was not applicable.")
                        return True
                    except Exception as e:
                        logger.error(f"Error executing '{action} {target}': {e}", exc_info=True)
                        return True

        # Commands without a separate target
        simple_actions = {
            "take screenshot": lambda: self.automation.take_screenshot(os.path.expanduser("~/Desktop/screenshot.png")),
            "cpu usage": self.process_manager.cpu_usage,
            "memory usage": self.process_manager.memory_usage,
            "list running apps": self.app_manager.list_running_apps,
            "what is running": self.app_manager.list_running_apps,
        }

        for phrase, func in simple_actions.items():
            if phrase in command:
                logger.info(f"Executing: {phrase.capitalize()}")
                try:
                    result = func()
                    logger.info(f"Success: {phrase.capitalize()} -> {result}")
                    return True
                except Exception as e:
                    logger.error(f"Error executing '{phrase}': {e}", exc_info=True)
                    return True

        return False

    def execute(self, command: str) -> bool:
        """
        Execute a command by routing it to the appropriate handler.
        """
        if not command or not command.strip():
            logger.warning("Empty command received")
            return False

        command = command.lower().strip()
        logger.info(f"🎯 Routing command: '{command}'")

        # Priority 1: Web commands (most specific)
        if self._handle_web_commands(command):
            return True

        # Priority 2: Desktop commands
        if self._handle_desktop_commands(command):
            return True

        # Priority 3: Fallback to legacy handlers
        logger.info("Command not handled by Web or Desktop Manager, trying legacy handlers...")
        handlers = [
            ("apps", self.apps),
            ("browser", self.browser),
            ("files", self.files),
            ("system", self.system),
        ]

        for handler_name, handler in handlers:
            try:
                if handler.handle(command):
                    logger.info(f"✅ Command handled by legacy handler: {handler_name}")
                    return True
            except Exception as e:
                logger.error(f"Error in legacy {handler_name} handler: {e}", exc_info=True)

        logger.warning(f"❌ No handler found for command: '{command}'")
        return False