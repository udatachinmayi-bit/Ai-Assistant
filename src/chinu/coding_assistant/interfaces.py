"""Interfaces for the Coding Assistant and its components."""

from abc import ABC, abstractmethod
from typing import List

from chinu.coding_assistant.models import (
    GeneratedCode,
    ImprovementSuggestion,
    ProjectAnalysis,
    RefactorSuggestion,
    CodeIssue,
)


class ICodeAnalyzer(ABC):
    """Interface for analyzing a project's structure."""

    @abstractmethod
    def analyze_project(self, project_path: str) -> ProjectAnalysis:
        """Analyze the entire project and return its structure."""
        pass


class ICodeExplainer(ABC):
    """Interface for explaining code."""

    @abstractmethod
    def explain_code(self, file_path: str, start_line: int, end_line: int) -> str:
        """Explain a specific piece of code."""
        pass


class IBugFinder(ABC):
    """Interface for finding bugs in code."""

    @abstractmethod
    def find_bugs(self, file_path: str) -> List[CodeIssue]:
        """Find potential bugs in a given file."""
        pass


class IImprovementSuggester(ABC):
    """Interface for suggesting code improvements."""

    @abstractmethod
    def suggest_improvements(self, file_path: str) -> List[ImprovementSuggestion]:
        """Suggest improvements for a given file."""
        pass


class ICodeGenerator(ABC):
    """Interface for generating new code."""

    @abstractmethod
    def generate_code(self, prompt: str, context: str) -> GeneratedCode:
        """Generate code based on a prompt and context."""
        pass


class ICodeRefactorer(ABC):
    """Interface for refactoring existing code."""

    @abstractmethod
    def refactor_code(
        self, file_path: str, start_line: int, end_line: int
    ) -> RefactorSuggestion:
        """Suggest a refactoring for a specific piece of code."""
        pass


class ICodingAssistant(
    ICodeAnalyzer,
    ICodeExplainer,
    IBugFinder,
    IImprovementSuggester,
    ICodeGenerator,
    ICodeRefactorer,
):
    """A comprehensive interface for the Coding Assistant."""

    pass