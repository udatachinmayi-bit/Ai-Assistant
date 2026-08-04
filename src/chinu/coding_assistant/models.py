"""Data models for the Coding Assistant."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CodeElement(BaseModel):
    """A generic representation of an element in a code file."""

    name: str
    file_path: str
    start_line: int
    end_line: int


class FunctionElement(CodeElement):
    """Represents a function or method."""

    signature: str


class ClassElement(CodeElement):
    """Represents a class."""

    methods: List[FunctionElement] = Field(default_factory=list)


class ProjectAnalysis(BaseModel):
    """Represents a high-level analysis of a project."""

    files: List[str]
    classes: List[ClassElement] = Field(default_factory=list)
    functions: List[FunctionElement] = Field(default_factory=list)


class Severity(str, Enum):
    """Severity level for issues or suggestions."""

    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    CRITICAL = "Critical"


class CodeIssue(BaseModel):
    """Represents a potential bug or issue in the code."""

    file_path: str
    line_number: int
    description: str
    severity: Severity


class ImprovementSuggestion(BaseModel):
    """Represents a suggestion for improving a piece of code."""

    file_path: str
    start_line: int
    end_line: int
    suggestion: str
    description: Optional[str] = None


class GeneratedCode(BaseModel):
    """Represents a block of generated code."""

    file_path: Optional[str] = None  # Suggest a file or leave empty
    code: str
    description: Optional[str] = None


class RefactorSuggestion(BaseModel):
    """Represents a refactoring suggestion."""

    file_path: str
    start_line: int
    end_line: int
    original_code: str
    refactored_code: str
    description: str