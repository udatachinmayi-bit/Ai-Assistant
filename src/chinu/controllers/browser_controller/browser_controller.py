"""Browser controller using Selenium for Chrome and Edge."""

from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from chinu.controllers.browser_controller.config import BrowserConfig
from chinu.controllers.browser_controller.models import ActionResponse, BrowserStatus
from chinu.logging_system.logger import get_logger

logger = get_logger("browser_controller")


class BrowserController:
    """Controls a web browser (Chrome or Edge) using Selenium."""

    def __init__(self, config: BrowserConfig) -> None:
        """Initialize the BrowserController."""
        self.config = config
        self.driver: Optional[webdriver.WebDriver] = None

    def _get_status(self) -> BrowserStatus:
        """Get the current status of the browser."""
        if not self.driver:
            return BrowserStatus(is_open=False)
        try:
            return BrowserStatus(
                is_open=True,
                current_url=self.driver.current_url,
                open_tabs=[handle for handle in self.driver.window_handles],
                active_tab_handle=self.driver.current_window_handle,
            )
        except Exception:
            # This can happen if the browser was closed manually
            self.driver = None
            return BrowserStatus(is_open=False)

    def open_browser(self) -> ActionResponse:
        """Open a new browser window."""
        if self.driver:
            return ActionResponse(
                success=False,
                message="Browser is already open.",
                status=self._get_status(),
            )
        try:
            if self.config.browser_type == "chrome":
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service)
            elif self.config.browser_type == "edge":
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service)
            else:
                raise ValueError(f"Unsupported browser: {self.config.browser_type}")

            logger.info(f"{self.config.browser_type.capitalize()} browser opened.")
            return ActionResponse(
                success=True,
                message=f"{self.config.browser_type.capitalize()} browser opened successfully.",
                status=self._get_status(),
            )
        except Exception as e:
            logger.error(f"Failed to open browser: {e}", exc_info=True)
            return ActionResponse(
                success=False, message=f"Failed to open browser: {e}", status=self._get_status()
            )

    def open_url(self, url: str) -> ActionResponse:
        """Navigate to a specific URL."""
        if not self.driver:
            self.open_browser()
        if not self.driver:
            return ActionResponse(
                success=False,
                message="Failed to open browser to navigate to URL.",
                status=self._get_status(),
            )

        try:
            self.driver.get(url)
            logger.info(f"Navigated to URL: {url}")
            return ActionResponse(
                success=True, message=f"Successfully navigated to {url}.", status=self._get_status()
            )
        except Exception as e:
            logger.error(f"Failed to open URL: {e}", exc_info=True)
            return ActionResponse(
                success=False, message=f"Failed to open URL: {e}", status=self._get_status()
            )

    def search_google(self, query: str) -> ActionResponse:
        """Perform a Google search."""
        url = f"https://www.google.com/search?q={query}"
        return self.open_url(url)

    def open_new_tab(self) -> ActionResponse:
        """Open a new, blank tab."""
        if not self.driver:
            return ActionResponse(
                success=False, message="Browser is not open.", status=self._get_status()
            )
        try:
            self.driver.switch_to.new_window("tab")
            logger.info("New tab opened.")
            return ActionResponse(
                success=True, message="New tab opened successfully.", status=self._get_status()
            )
        except Exception as e:
            logger.error(f"Failed to open new tab: {e}", exc_info=True)
            return ActionResponse(
                success=False, message=f"Failed to open new tab: {e}", status=self._get_status()
            )

    def close_browser(self) -> ActionResponse:
        """Close the browser and all its tabs."""
        if not self.driver:
            return ActionResponse(
                success=True, message="Browser was not open.", status=self._get_status()
            )
        try:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed.")
            return ActionResponse(
                success=True, message="Browser closed successfully.", status=self._get_status()
            )
        except Exception as e:
            logger.error(f"Failed to close browser: {e}", exc_info=True)
            # Even if it fails, the driver is likely unusable.
            self.driver = None
            return ActionResponse(
                success=False, message=f"Failed to close browser: {e}", status=self._get_status()
            )