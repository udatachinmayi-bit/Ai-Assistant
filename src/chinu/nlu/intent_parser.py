import re

class IntentParser:
    """
    Parses a natural language command into a structured intent.

    This class uses a series of regular expression patterns to identify the user's
    intent and extract relevant entities (e.g., application names, search queries).
    The patterns are ordered from most specific to most general to ensure correct
    matching.
    """

    def __init__(self):
        """
        Initializes the IntentParser.

        This compiles the regex patterns for all supported intents and defines
        known entities like websites. The order of `intent_patterns` is crucial
        for correct intent resolution.
        """
        # A set of known websites to differentiate `open_website` from `open_app`
        self.known_websites = {
            "youtube", "google", "github", "chatgpt", "gmail", "linkedin",
            "facebook", "twitter", "instagram", "wikipedia"
        }

        # Define synonyms for common actions to make the parser more flexible.
        open_verbs = r"(?:open|launch|start|run|execute)"
        search_verbs = r"(?:search|google|find|look up)"
        play_verbs = r"(?:play|youtube)"

        # A list of (pattern, handler) tuples.
        # The parser will iterate through this list and use the first matching pattern.
        # More specific patterns should be placed before more general ones.
        self.intent_patterns = [
            # 1. Browser Profile Intent
            # Example: "open chrome with ganesh", "start firefox using work", "launch edge guest"
            (re.compile(rf"^{open_verbs} (\w+) (?:with|using) (\w+)$"), self._parse_browser_profile),
            (re.compile(rf"^{open_verbs} (\w+) (guest)$"), self._parse_browser_profile),

            # 2. YouTube Play Intent
            # Example: "play believer", "youtube believer", "search believer on youtube"
            (re.compile(rf"^play (.+?)(?: on youtube)?$"), self._parse_youtube_play),
            (re.compile(rf"^youtube (.+)$"), self._parse_youtube_play),
            (re.compile(rf"^search (.+) on youtube$"), self._parse_youtube_play),

            # 3. Google Search Intent
            # Example: "google ai", "find ai", "search ai on google", "search ai"
            (re.compile(rf"^{search_verbs} (.+)$"), self._parse_google_search),
            (re.compile(rf"^search (.+) on google$"), self._parse_google_search),

            # 4. Open App/Website Intent (a general "open" command)
            # Example: "open chrome", "launch youtube"
            (re.compile(rf"^{open_verbs} (.+)$"), self._parse_open),

            # 5. Windows Commands (simple, direct matches)
            (re.compile(r"^lock computer$"), lambda m: {"intent": "lock_pc"}),
            (re.compile(r"^shutdown(?: pc)?$"), lambda m: {"intent": "shutdown_pc"}),
            (re.compile(r"^restart(?: pc)?$"), lambda m: {"intent": "restart_pc"}),
            (re.compile(r"^sleep computer$"), lambda m: {"intent": "sleep_pc"}),
            (re.compile(r"^take screenshot$"), lambda m: {"intent": "screenshot"}),
        ]

    def _normalize_command(self, command: str) -> str:
        """
        Normalizes the command string for easier parsing.

        Normalization includes:
        1. Converting to lowercase.
        2. Removing punctuation.
        3. Collapsing multiple whitespace characters into a single space.

        Args:
            command: The raw command string.

        Returns:
            The normalized command string.
        """
        text = command.lower()
        # Remove all characters that are not letters, numbers, or whitespace
        text = re.sub(r"[^\w\s]", "", text)
        # Replace multiple spaces with a single space and trim leading/trailing spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _parse_browser_profile(self, match: re.Match) -> dict:
        """Handler for parsing the 'browser_profile' intent."""
        return {"intent": "browser_profile", "browser": match.group(1), "profile": match.group(2)}

    def _parse_youtube_play(self, match: re.Match) -> dict:
        """Handler for parsing the 'youtube_play' intent."""
        return {"intent": "youtube_play", "query": match.group(1)}

    def _parse_google_search(self, match: re.Match) -> dict:
        """Handler for parsing the 'google_search' intent."""
        return {"intent": "google_search", "query": match.group(1)}

    def _parse_open(self, match: re.Match) -> dict:
        """
        Handler for parsing the 'open' intent.

        It distinguishes between opening a known website and opening a generic app.
        """
        target = match.group(1).strip()
        if target in self.known_websites:
            return {"intent": "open_website", "site": target}
        else:
            return {"intent": "open_app", "app": target}

    def parse(self, command: str) -> dict:
        """
        Parses the given command string to determine the user's intent.

        It first normalizes the command, then iterates through the predefined
        intent patterns. If a match is found, it returns the structured intent.
        If no patterns match, it returns an 'unknown' intent.

        Args:
            command: The raw command string from the user.

        Returns:
            A dictionary containing the parsed intent and entities,
            or an 'unknown' intent if no pattern matches.
        """
        # Normalize the command to handle variations in user input
        normalized_command = self._normalize_command(command)

        # Iterate through the patterns and try to find a match
        for pattern, handler in self.intent_patterns:
            match = pattern.match(normalized_command)
            if match:
                # If a match is found, call its handler and return the result
                return handler(match)

        # If no intent is matched after checking all patterns, return 'unknown'
        # Include the original, unmodified command text for context.
        return {"intent": "unknown", "text": command}