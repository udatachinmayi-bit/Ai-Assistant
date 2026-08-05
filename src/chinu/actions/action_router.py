"""Action Router for Chinu AI.

Routes voice commands to appropriate action handlers.
"""

from chinu.actions.app_actions import AppActions
from chinu.actions.browser_actions import BrowserActions
from chinu.actions.file_actions import FileActions
from chinu.actions.system_actions import SystemActions
from chinu.logging_system.logger import get_logger

logger = get_logger("action_router")


class ActionRouter:
    """Routes commands to appropriate action handlers."""

    def __init__(self) -> None:
        """Initialize the ActionRouter with all action handlers."""
        self.apps = AppActions()
        self.browser = BrowserActions()
        self.files = FileActions()
        self.system = SystemActions()
        logger.info("✅ ActionRouter initialized with all handlers")

    def execute(self, command: str) -> bool:
        """
        Execute a command by routing it to the appropriate handler.
        
        Args:
            command: The command text to execute (e.g., "open chrome", "lock computer")
            
        Returns:
            bool: True if command was executed successfully, False otherwise
        """
        if not command or not command.strip():
            logger.warning("Empty command received")
            return False

        command = command.lower().strip()
        logger.info(f"🎯 Routing command: '{command}'")

        # Try each handler in priority order
        handlers = [
            ("apps", self.apps),
            ("browser", self.browser),
            ("files", self.files),
            ("system", self.system),
        ]

        for handler_name, handler in handlers:
            try:
                # All handlers are synchronous - just call them directly
                result = handler.handle(command)
                
                if result:
                    logger.info(f"✅ Command handled by {handler_name}")
                    return True
            except Exception as e:
                logger.error(f"Error in {handler_name} handler: {e}")

        logger.warning(f"❌ No handler found for command: '{command}'")
        return False