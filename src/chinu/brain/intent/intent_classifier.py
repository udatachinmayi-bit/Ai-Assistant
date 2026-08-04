"""A keyword-based intent classifier independent of any LLM."""

from enum import Enum, auto
from typing import Dict, List, Optional


class Intent(Enum):
    """Enumeration of possible user intents."""

    OPEN_APP = auto()
    CLOSE_APP = auto()
    SEARCH_WEB = auto()
    CHAT = auto()
    CODE = auto()
    REMEMBER = auto()
    FORGET = auto()
    FILE_OPERATION = auto()
    UNKNOWN = auto()


class IntentClassifier:
    """A simple, keyword-based intent classifier."""

    def __init__(self) -> None:
        """Initialize the intent classifier with keywords for each intent."""
        self._intent_keywords: Dict[Intent, List[str]] = {
            Intent.OPEN_APP: ["open", "launch", "start", "run"],
            Intent.CLOSE_APP: ["close", "exit", "quit", "terminate", "shut down"],
            Intent.SEARCH_WEB: ["search", "google", "find", "look up", "browse"],
            Intent.CODE: ["code", "write", "develop", "program", "script"],
            Intent.REMEMBER: ["remember", "save", "store", "recall", "note"],
            Intent.FORGET: ["forget", "delete", "remove", "erase"],
            Intent.FILE_OPERATION: ["file", "folder", "directory", "create", "copy", "move"],
            Intent.CHAT: ["chat", "talk", "speak", "ask", "tell me"],
        }

    def classify(self, text: str) -> Intent:
        """Classify the user's intent based on the input text.

        Args:
            text: The user's input text.

        Returns:
            The most likely Intent, or UNKNOWN if no keywords match.
        """
        text_lower = text.lower()
        scores: Dict[Intent, int] = {intent: 0 for intent in self._intent_keywords}

        for intent, keywords in self._intent_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[intent] += 1

        # Find the intent with the highest score
        highest_score = 0
        best_intent = Intent.UNKNOWN
        for intent, score in scores.items():
            if score > highest_score:
                highest_score = score
                best_intent = intent

        # A simple tie-breaking rule: if multiple intents have the same highest score,
        # we might default to a general intent like CHAT or UNKNOWN.
        # For now, we'll just take the first one we find with the highest score.
        if highest_score > 0:
            return best_intent

        # If no keywords were found, but the text is not empty, default to CHAT.
        if text.strip():
            return Intent.CHAT

        return Intent.UNKNOWN