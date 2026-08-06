"""
BrowserManager for Chinu AI.

This module provides a class to manage all browser-related actions,
such as opening websites, performing searches, and managing profiles.
"""

import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

from chinu.logging_system.logger import get_logger

logger = get_logger("browser_manager")


class BrowserManager:
    """A class to manage browser-related actions."""

    def __init__(self):
        """Initializes the BrowserManager."""
        self.site_map = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "chatgpt": "https://chat.openai.com",
            "gmail": "https://mail.google.com",
            "linkedin": "https://www.linkedin.com",
            "stackoverflow": "https://stackoverflow.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "reddit": "https://www.reddit.com",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://www.spotify.com",
            "maps": "https://www.google.com/maps",
            "drive": "https://drive.google.com",
            "calendar": "https://calendar.google.com",
            "news": "https://news.google.com",
        }
        logger.info("✅ BrowserManager initialized")

    def open_url(self, url: str) -> bool:
        """
        Opens a given URL in the default web browser.

        Args:
            url: The URL to open.

        Returns:
            True if successful, False otherwise.
        """
        try:
            logger.info(f"Opening URL: {url}")
            webbrowser.open(url)
            return True
        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}", exc_info=True)
            return False

    def open_website(self, site: str) -> bool:
        """
        Opens a supported website by its short name.

        Args:
            site: The short name of the site (e.g., "google", "youtube").

        Returns:
            True if the site is supported and opened, False otherwise.
        """
        site_key = site.lower()
        if site_key in self.site_map:
            url = self.site_map[site_key]
            logger.info(f"Opening website: {site} -> {url}")
            return self.open_url(url)
        else:
            logger.warning(f"Website '{site}' is not supported.")
            return False

    def google_search(self, query: str) -> bool:
        """
        Performs a Google search for the given query.

        Args:
            query: The search query.

        Returns:
            True if the search is successful, False otherwise.
        """
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            logger.info(f"Performing Google search for: '{query}'")
            return self.open_url(search_url)
        except Exception as e:
            logger.error(f"Failed to perform Google search for '{query}': {e}", exc_info=True)
            return False

    def youtube_search(self, query: str) -> bool:
        """
        Performs a YouTube search for the given query.

        Args:
            query: The search query.

        Returns:
            True if the search is successful, False otherwise.
        """
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            logger.info(f"Performing YouTube search for: '{query}'")
            return self.open_url(search_url)
        except Exception as e:
            logger.error(f"Failed to perform YouTube search for '{query}': {e}", exc_info=True)
            return False

    def youtube_play(self, query: str) -> bool:
        """
        Searches YouTube and attempts to play the first video result.
        Falls back to a regular search if it cannot play directly.

        Note: Directly playing the first result is complex and often requires
        an API or web scraping. This is a simplified version.
        """
        logger.info(f"Attempting to play '{query}' on YouTube.")
        # For now, this will just perform a search. A more advanced implementation
        # would require a library like `youtube-search-python` or similar.
        return self.youtube_search(query)

    def open_browser_profile(self, browser: str, profile: str) -> bool:
        """
        Opens a specific browser with a given profile.

        Args:
            browser: The browser to open ("chrome" or "edge").
            profile: The name of the profile to use.

        Returns:
            True if successful, False otherwise.
        """
        browser_executables = {
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
        }
        browser_name = browser.lower()

        if browser_name not in browser_executables:
            logger.error(f"Browser '{browser}' is not supported for profile switching.")
            return False

        executable = browser_executables[browser_name]
        command = [executable, f'--profile-directory="{profile}"']

        try:
            logger.info(f"Opening {browser} with profile '{profile}' using command: {' '.join(command)}")
            subprocess.Popen(command)
            return True
        except FileNotFoundError:
            logger.error(f"Executable '{executable}' not found. Make sure {browser} is installed and in your PATH.")
            return False
        except Exception as e:
            logger.error(f"Failed to open {browser} with profile '{profile}': {e}", exc_info=True)
            return False

    def search_maps(self, location: str) -> bool:
        """
        Searches for a location on Google Maps.

        Args:
            location: The location to search for.

        Returns:
            True if successful, False otherwise.
        """
        try:
            maps_url = f"https://www.google.com/maps/search/{quote_plus(location)}"
            logger.info(f"Searching Google Maps for: '{location}'")
            return self.open_url(maps_url)
        except Exception as e:
            logger.error(f"Failed to search maps for '{location}': {e}", exc_info=True)
            return False

    def gmail_compose(self, email: str = "") -> bool:
        """
        Opens the Gmail compose window.

        Args:
            email: Optional email address to pre-fill.

        Returns:
            True if successful, False otherwise.
        """
        try:
            compose_url = "https://mail.google.com/mail/?view=cm&fs=1"
            if email:
                compose_url += f"&to={email}"
            logger.info("Opening Gmail compose window.")
            return self.open_url(compose_url)
        except Exception as e:
            logger.error(f"Failed to open Gmail compose window: {e}", exc_info=True)
            return False

    def calendar_today(self) -> bool:
        """Opens Google Calendar to the current day."""
        logger.info("Opening Google Calendar.")
        return self.open_website("calendar")

    def news(self) -> bool:
        """Opens Google News."""
        logger.info("Opening Google News.")
        return self.open_website("news")