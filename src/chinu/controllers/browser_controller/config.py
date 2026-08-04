"""Configuration for the Browser Controller."""

from typing import Literal

from pydantic import BaseModel, Field


class BrowserConfig(BaseModel):
    """Configuration for the Browser Controller.

    Attributes:
        browser_type: The type of browser to control ('chrome' or 'edge').
    """

    browser_type: Literal["chrome", "edge"] = Field(
        default="chrome",
        description="The type of browser to control ('chrome' or 'edge').",
    )