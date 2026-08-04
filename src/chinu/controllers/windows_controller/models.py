"""Data models for Windows Controller responses."""

from typing import Optional

from pydantic import BaseModel


class ActionResponse(BaseModel):
    """A generic response model for Windows operations.

    Attributes:
        success: Whether the action was successful.
        message: A message describing the result of the action.
    """

    success: bool
    message: str


class ProcessResponse(ActionResponse):
    """Response model for process-related actions.

    Attributes:
        process_name: The name of the application or process.
        pid: The process ID, if applicable.
    """

    process_name: str
    pid: Optional[int] = None