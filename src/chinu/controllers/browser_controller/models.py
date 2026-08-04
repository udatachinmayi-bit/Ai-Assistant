"""Data models for Browser Controller responses."""

from typing import List, Optional

from pydantic import BaseModel, Field


class BrowserStatus(BaseModel):
    """Represents the current status of the browser.

    Attributes:
        is_open: Whether the browser is currently open.
        current_url: The URL of the active tab.
        open_tabs: A list of all open tab URLs.
        active_tab_handle: The handle of the active tab.
    """

    is_open: bool
    current_url: Optional[str] = None
    open_tabs: List[str] = Field(default_factory=list)
    active_tab_handle: Optional[str] = None


class ActionResponse(BaseModel):
    """A generic response model for browser actions.

    Attributes:
        success: Whether the action was successful.
        message: A message describing the result of the action.
        status: The updated status of the browser after the action.
    """

    success: bool
    message: str
    status: BrowserStatus