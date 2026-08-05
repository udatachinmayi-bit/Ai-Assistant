import webbrowser
from urllib.parse import quote

from chinu.logging_system.logger import get_logger

logger = get_logger("browser_actions")


class BrowserActions:

    def handle(self, command: str) -> bool:

        command = command.lower().strip()

        try:

            # Open YouTube
            if command == "open youtube":
                webbrowser.open("https://www.youtube.com")
                logger.info("Opened YouTube")
                return True

            # Open Google
            if command == "open google":
                webbrowser.open("https://www.google.com")
                logger.info("Opened Google")
                return True

            # Open Gmail
            if command == "open gmail":
                webbrowser.open("https://mail.google.com")
                logger.info("Opened Gmail")
                return True

            # Search Google
            if command.startswith("search google for"):

                query = command.replace(
                    "search google for",
                    ""
                ).strip()

                webbrowser.open(
                    f"https://www.google.com/search?q={quote(query)}"
                )

                logger.info(f"Searching Google : {query}")

                return True

            # Search YouTube
            if command.startswith("search youtube for"):

                query = command.replace(
                    "search youtube for",
                    ""
                ).strip()

                webbrowser.open(
                    f"https://www.youtube.com/results?search_query={quote(query)}"
                )

                logger.info(f"Searching YouTube : {query}")

                return True

        except Exception as e:

            logger.error(e)

            return False

        return False