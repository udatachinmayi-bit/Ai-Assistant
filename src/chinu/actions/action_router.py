"""Action Router for Chinu AI.

Routes structured intents to appropriate action handlers.
"""

from chinu.desktop.browser_manager import BrowserManager
from chinu.desktop.desktop_manager import DesktopManager
from chinu.desktop.system_manager import SystemManager
from chinu.logging_system.logger import get_logger

logger = get_logger("action_router")


class ActionRouter:
    """Routes structured intents to appropriate action handlers."""

    def __init__(self) -> None:
        """Initialize the ActionRouter with all necessary managers."""
        self.desktop_manager = DesktopManager()
        self.browser_manager = BrowserManager()
        self.system_manager = SystemManager()
        logger.info("✅ ActionRouter initialized with all managers")

    def execute(self, intent_data: dict) -> bool:
        """
        Execute a command by routing a structured intent to the appropriate manager.

        Args:
            intent_data: A dictionary containing the intent and associated entities.

        Returns:
            True if the action was successfully executed, False otherwise.
        """
        intent = intent_data.get("intent")
        logger.info(f"Received Intent: {intent_data}")

        if not intent:
            logger.warning("No intent found in the provided data.")
            return False

        success = False
        try:
            match intent:
                case "open_app":
                    app = intent_data.get("app")
                    logger.info(f"Executing: open_app, Target: {app}")
                    success = self.desktop_manager.open_application(app)

                case "open_website":
                    site = intent_data.get("site")
                    logger.info(f"Executing: open_website, Target: {site}")
                    success = self.browser_manager.open_website(site)

                case "google_search":
                    query = intent_data.get("query")
                    logger.info(f"Executing: google_search, Query: {query}")
                    success = self.browser_manager.google_search(query)

                case "youtube_play":
                    query = intent_data.get("query")
                    logger.info(f"Executing: youtube_play, Query: {query}")
                    success = self.browser_manager.play_youtube(query)

                case "browser_profile":
                    browser = intent_data.get("browser")
                    profile = intent_data.get("profile")
                    logger.info(f"Executing: browser_profile, Browser: {browser}, Profile: {profile}")
                    success = self.browser_manager.open_browser_profile(browser, profile)

                case "shutdown_pc":
                    logger.info("Executing: shutdown_pc")
                    success = self.system_manager.shutdown()

                case "restart_pc":
                    logger.info("Executing: restart_pc")
                    success = self.system_manager.restart()

                case "lock_pc":
                    logger.info("Executing: lock_pc")
                    success = self.system_manager.lock()

                case "sleep_pc":
                    logger.info("Executing: sleep_pc")
                    success = self.system_manager.sleep()

                case "screenshot":
                    logger.info("Executing: screenshot")
                    success = self.desktop_manager.take_screenshot()

                case "unknown":
                    text = intent_data.get("text")
                    logger.warning(f"Cannot execute unknown intent for text: '{text}'")
                    success = False

                case _:
                    logger.error(f"No handler implemented for intent: '{intent}'")
                    success = False
        
        except Exception as e:
            logger.error(f"An error occurred while executing intent '{intent}': {e}", exc_info=True)
            success = False

        if success:
            logger.info(f"✅ Success for intent: '{intent}'")
        else:
            logger.error(f"❌ Failure for intent: '{intent}'")
            
        return success