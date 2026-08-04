"""Data models for File Controller responses."""

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class FileContent(BaseModel):
    """Represents the content of a file.

    Attributes:
        path: The absolute path to the file.
        content: The text content of the file.
        file_type: The detected file type.
    """

    path: str
    content: str
    file_type: str


class SearchResult(BaseModel):
    """Represents a single search result within a file.

    Attributes:
        path: The path to the file where the match was found.
        line_number: The line number of the match.
        line_content: The content of the line containing the match.
    """

    path: str
    line_number: int
    line_content: str


class ActionResponse(BaseModel):
    """A generic response model for file operations.

    Attributes:
        success: Whether the action was successful.
        message: A message describing the result of the action.
        path: The primary path involved in the operation.
        new_path: The new path, if applicable (for move/rename).
    """

    success: bool
    message: str
    path: Optional[str] = None
    new_path: Optional[str] = None