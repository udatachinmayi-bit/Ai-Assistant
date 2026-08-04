"""Controller for handling file system operations."""

import shutil
from pathlib import Path
from typing import List, Union

from chinu.controllers.file_controller.models import (
    ActionResponse,
    FileContent,
    SearchResult,
)
from chinu.controllers.file_controller.readers import get_reader
from chinu.logging_system.logger import get_logger

logger = get_logger("file_controller")


class FileController:
    """Manages file operations like read, write, search, and manipulation."""

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolve a string or Path to an absolute Path object."""
        return Path(path).resolve()

    def read_file(self, path: str) -> Union[FileContent, ActionResponse]:
        """Read the content of a supported file."""
        p = self._resolve_path(path)
        if not p.is_file():
            return ActionResponse(success=False, message=f"File not found: {p}", path=str(p))

        reader = get_reader(p.suffix)
        if not reader:
            return ActionResponse(
                success=False, message=f"Unsupported file type: {p.suffix}", path=str(p)
            )

        try:
            content = reader(p)
            logger.info(f"Read file: {p}")
            return FileContent(path=str(p), content=content, file_type=p.suffix)
        except Exception as e:
            logger.error(f"Failed to read file {p}: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Error reading file: {e}", path=str(p))

    def write_file(self, path: str, content: str) -> ActionResponse:
        """Write content to a file, overwriting if it exists."""
        p = self._resolve_path(path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Wrote to file: {p}")
            return ActionResponse(success=True, message="File written successfully.", path=str(p))
        except Exception as e:
            logger.error(f"Failed to write file {p}: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Error writing file: {e}", path=str(p))

    def search_in_file(self, path: str, query: str) -> Union[List[SearchResult], ActionResponse]:
        """Search for a string within a single file."""
        read_result = self.read_file(path)
        if isinstance(read_result, ActionResponse):
            return read_result

        results = []
        for i, line in enumerate(read_result.content.splitlines(), 1):
            if query in line:
                results.append(
                    SearchResult(path=path, line_number=i, line_content=line.strip())
                )
        return results

    def rename_file(self, path: str, new_name: str) -> ActionResponse:
        """Rename a file."""
        p = self._resolve_path(path)
        if not p.exists():
            return ActionResponse(success=False, message="Source path does not exist.", path=str(p))

        new_p = p.parent / new_name
        try:
            p.rename(new_p)
            logger.info(f"Renamed {p} to {new_p}")
            return ActionResponse(
                success=True,
                message="File renamed successfully.",
                path=str(p),
                new_path=str(new_p),
            )
        except Exception as e:
            logger.error(f"Failed to rename {p}: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Error renaming file: {e}", path=str(p))

    def delete_file(self, path: str) -> ActionResponse:
        """Delete a file."""
        p = self._resolve_path(path)
        if not p.is_file():
            return ActionResponse(success=False, message="File not found.", path=str(p))
        try:
            p.unlink()
            logger.info(f"Deleted file: {p}")
            return ActionResponse(success=True, message="File deleted successfully.", path=str(p))
        except Exception as e:
            logger.error(f"Failed to delete {p}: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Error deleting file: {e}", path=str(p))

    def move_file(self, source_path: str, dest_path: str) -> ActionResponse:
        """Move a file to a new destination."""
        src = self._resolve_path(source_path)
        dest = self._resolve_path(dest_path)
        if not src.is_file():
            return ActionResponse(success=False, message="Source file not found.", path=str(src))
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            logger.info(f"Moved {src} to {dest}")
            return ActionResponse(
                success=True,
                message="File moved successfully.",
                path=str(src),
                new_path=str(dest),
            )
        except Exception as e:
            logger.error(f"Failed to move {src}: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Error moving file: {e}", path=str(src))

    def copy_file(self, source_path: str, dest_path: str) -> ActionResponse:
        """Copy a file to a new destination."""
        src = self._resolve_path(source_path)
        dest = self._resolve_path(dest_path)
        if not src.is_file():
            return ActionResponse(success=False, message="Source file not found.", path=str(src))
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dest))
            logger.info(f"Copied {src} to {dest}")
            return ActionResponse(
                success=True,
                message="File copied successfully.",
                path=str(src),
                new_path=str(dest),
            )
        except Exception as e:
            logger.error(f"Failed to copy {src}: {e}", exc_info=True)
            return ActionResponse(success=False, message=f"Error copying file: {e}", path=str(src))