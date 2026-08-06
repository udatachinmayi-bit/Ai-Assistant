"""Action Router for Chinu AI.

Routes structured intents to appropriate action handlers and executes them.
"""

from chinu.app.app_manager import AppManager
from chinu.browser.browser_manager import BrowserManager
from chinu.desktop.desktop_manager import DesktopManager
from chinu.system.system_manager import SystemManager
from chinu.logging_system.logger import get_logger
from chinu.actions.action_result import ActionResult

logger = get_logger("action_router")


class ActionRouter:
    """Routes structured intents to appropriate action handlers and executes them."""

    def __init__(self) -> None:
        """Initialize the ActionRouter with all necessary managers."""
        self.app_manager = AppManager()
        self.browser_manager = BrowserManager()
        self.system_manager = SystemManager()
        self.desktop_manager = DesktopManager()
        logger.info("✅ ActionRouter initialized with all managers")

    def execute(self, intent_data: dict) -> ActionResult:
        """
        Executes an action by routing a structured intent to the appropriate manager.

        Args:
            intent_data: A dictionary containing the intent and associated entities.

        Returns:
            An ActionResult object indicating the outcome of the execution.
        """
        intent = intent_data.get("intent")
        logger.info(f"Executing action for intent: {intent_data}")

        if not intent:
            logger.warning("No intent found in the provided data.")
            return ActionResult(success=False, action="error", message="No intent provided.")

        try:
            success = False
            action_result = ActionResult(success=False, action=intent)

            match intent:
                case "open_app":
                    app = intent_data.get("app")
                    action_result.target = app
                    if app:
                        success = self.app_manager.open_application(app)
                
                case "open_website":
                    site = intent_data.get("site")
                    action_result.target = site
                    if site:
                        success = self.browser_manager.open_website(site)

                case "google_search":
                    query = intent_data.get("query")
                    action_result.query = query
                    if query:
                        success = self.browser_manager.google_search(query)

                case "youtube_play":
                    query = intent_data.get("query")
                    action_result.query = query
                    if query:
                        success = self.browser_manager.play_youtube(query)

                case "browser_profile":
                    browser = intent_data.get("browser")
                    profile = intent_data.get("profile")
                    if browser and profile:
                        success = self.browser_manager.open_browser_profile(browser, profile)
                        action_result.data = {"browser": browser, "profile": profile}

                case "shutdown_pc":
                    success = self.system_manager.shutdown()

                case "restart_pc":
                    success = self.system_manager.restart()

                case "lock_pc":
                    success = self.system_manager.lock()

                case "sleep_pc":
                    success = self.system_manager.sleep()

                case "screenshot":
                    success = self.desktop_manager.take_screenshot()

                case "get_capabilities":
                    # This is handled in VoiceService, but we can return success here
                    success = True

                case "unknown":
                    text = intent_data.get("text")
                    action_result.message = f"Unknown intent for text: '{text}'"
                    success = False

                case _:
                    action_result.message = f"No handler for intent: '{intent}'"
                    success = False
            
            action_result.success = success
            return action_result

        except Exception as e:
            logger.error(f"An error occurred while executing intent '{intent}': {e}", exc_info=True)
            return ActionResult(success=False, action="error", message=str(e))