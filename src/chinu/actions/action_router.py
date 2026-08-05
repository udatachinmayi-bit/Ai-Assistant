from chinu.logging_system.logger import get_logger

logger = get_logger("action_router")

class ActionRouter:
    def __init__(self):
        pass

    async def execute(self, command: str):
        logger.info(f"Executing command: {command}")