"""
AI Reasoner for Chinu AI.

This module provides a class that takes a structured intent and refines it
before it is passed to the ActionRouter. It normalizes entity names and can
be extended to include more advanced reasoning capabilities.
"""

from chinu.logging_system.logger import get_logger

logger = get_logger("ai_reasoner")


class AIReasoner:
    """
    The AIReasoner class processes structured intents to refine and normalize them.
    It acts as a bridge between the IntentParser and the ActionRouter.
    """

    def __init__(self):
        """Initializes the AIReasoner with normalization maps."""
        # Normalization map for application names
        self.app_normalization_map = {
            "browser": "chrome",
            "internet": "chrome",
            "visual studio": "vscode",
            "terminal": "cmd",
            "file explorer": "explorer",
            "calculator": "calc",
        }

        # Normalization map for website names
        self.site_normalization_map = {
            "yt": "youtube",
            "mail": "gmail",
            "docs": "google docs",
            "calendar": "google calendar",
            "drive": "google drive",
            "music": "spotify",
            "chat gpt": "chatgpt",
        }
        logger.info("✅ AIReasoner initialized")

    def _normalize_app(self, app_name: str) -> str:
        """Normalizes an application name using the mapping."""
        return self.app_normalization_map.get(app_name.lower(), app_name)

    def _normalize_site(self, site_name: str) -> str:
        """Normalizes a website name using the mapping."""
        return self.site_normalization_map.get(site_name.lower(), site_name)

    def reason(self, intent_data: dict) -> dict:
        """
        Analyzes and refines a structured intent.

        This method takes an intent dictionary, normalizes its entities (like app
        and site names), and returns the improved intent. In the future, this
        could be expanded to include LLM-based reasoning.

        Args:
            intent_data: The structured intent from the IntentParser.

        Returns:
            The refined and normalized intent dictionary.
        """
        logger.info(f"Received intent: {intent_data}")
        
        intent = intent_data.get("intent")
        if not intent:
            logger.warning("Intent data does not contain an 'intent' key.")
            return intent_data

        # Create a copy to avoid modifying the original dictionary
        refined_intent = intent_data.copy()
        reasoning_log = []

        # --- Intent-specific reasoning and normalization ---
        if intent == "open_app":
            app = refined_intent.get("app")
            if app:
                normalized_app = self._normalize_app(app)
                if normalized_app != app:
                    refined_intent["app"] = normalized_app
                    reasoning_log.append(f"Normalized app '{app}' to '{normalized_app}'.")

        elif intent == "open_website":
            site = refined_intent.get("site")
            if site:
                normalized_site = self._normalize_site(site)
                if normalized_site != site:
                    refined_intent["site"] = normalized_site
                    reasoning_log.append(f"Normalized site '{site}' to '{normalized_site}'.")

        # --- Confidence-based clarification (Placeholder) ---
        # In a future version, if confidence from an LLM is low, we could
        # return a clarification intent.
        # Example:
        # if intent_data.get("confidence", 1.0) < 0.7:
        #     logger.info("Confidence is low, asking for clarification.")
        #     return {
        #         "intent": "clarification",
        #         "message": "I'm not sure what you mean. Could you be more specific?"
        #     }

        if reasoning_log:
            logger.info(f"Reasoning applied: {' '.join(reasoning_log)}")
        else:
            logger.info("No normalization needed for this intent.")

        logger.info(f"Improved intent: {refined_intent}")
        return refined_intent