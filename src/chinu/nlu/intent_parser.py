import re

class IntentParser:
    """
    Parses a natural language command into a structured intent.
    """

    def __init__(self):
        """
        Initializes the IntentParser, compiling regex patterns for intent matching.
        """
        # The order of patterns is important. More specific patterns should come first.
        self.intent_patterns = [
            (re.compile(r'^open (\w+) with (\w+) account$', re.IGNORECASE), self._parse_browser_profile),
            (re.compile(r'^search (.+) on google$', re.IGNORECASE), self._parse_google_search),
            (re.compile(r'^play (.+) on youtube$', re.IGNORECASE), self._parse_youtube_play),
            (re.compile(r'^open (\w+)$', re.IGNORECASE), self._parse_open),
            (re.compile(r'^shutdown computer$', re.IGNORECASE), lambda m: {"intent": "shutdown_pc"}),
            (re.compile(r'^restart computer$', re.IGNORECASE), lambda m: {"intent": "restart_pc"}),
            (re.compile(r'^take screenshot$', re.IGNORECASE), lambda m: {"intent": "screenshot"}),
        ]
        # A simple set of known websites to differentiate between opening a website and an app.
        self.known_websites = {"youtube", "google", "facebook", "twitter", "instagram", "wikipedia"}

    def _parse_browser_profile(self, match: re.Match) -> dict:
        """Parses the browser profile intent."""
        return {"intent": "browser_profile", "browser": match.group(1), "profile": match.group(2)}

    def _parse_google_search(self, match: re.Match) -> dict:
        """Parses the Google search intent."""
        return {"intent": "google_search", "query": match.group(1)}

    def _parse_youtube_play(self, match: re.Match) -> dict:
        """Parses the YouTube play intent."""
        return {"intent": "youtube_play", "query": match.group(1)}

    def _parse_open(self, match: re.Match) -> dict:
        """
        Parses the open intent, distinguishing between apps and websites.
        """
        target = match.group(1)
        if target in self.known_websites:
            return {"intent": "open_website", "site": target}
        else:
            return {"intent": "open_app", "app": target}

    def parse(self, command: str) -> dict:
        """
        Parses the given command string to determine the user's intent.

        Args:
            command: The raw command string from the user.

        Returns:
            A dictionary containing the parsed intent and any associated entities,
            or an 'unknown' intent if no pattern matches.
        """
        normalized_command = command.lower().strip()
        for pattern, handler in self.intent_patterns:
            match = pattern.match(normalized_command)
            if match:
                return handler(match)

        return {"intent": "unknown", "text": command}