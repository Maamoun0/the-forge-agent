"""
File Tool — Safe file operations for agents.
Includes syntax validation guard to prevent broken code from being written.
"""
import os
import ast
import json
import logging
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger("forge.tools.file")


class FileTool:
    """
    Provides safe, sandboxed file operations.
    All paths are validated to stay within the project workspace.
    """

    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, relative_path: str) -> Path:
        """Ensure the path stays within the workspace (security guard)."""
        full_path = (self.workspace / relative_path).resolve()
        if not str(full_path).startswith(str(self.workspace)):
            raise PermissionError(f"Path traversal blocked: {relative_path}")
        return full_path

    def _check_syntax(self, content: str, file_path: str) -> tuple[bool, str]:
        """
        Validate syntax before writing. Returns (is_valid, error_message).
        Currently supports Python and JSON.
        """
        ext = Path(file_path).suffix.lower()

        if ext == ".py":
            try:
                ast.parse(content)
                return True, ""
            except SyntaxError as e:
                return False, f"Python syntax error at line {e.lineno}: {e.msg}"

        elif ext == ".json":
            try:
                json.loads(content)
                return True, ""
            except json.JSONDecodeError as e:
                return False, f"JSON syntax error: {e.msg} at line {e.lineno}"

        # For other file types, allow writing without syntax check
        return True, ""

    def read_file(self, relative_path: str) -> Optional[str]:
        """Read a file from the workspace."""
        path = self._validate_path(relative_path)
        if not path.exists():
            logger.warning(f"File not found: {relative_path}")
            return None
        return path.read_text(encoding="utf-8")

    def write_file(self, relative_path: str, content: str, force: bool = False) -> dict:
        """
        Write content to a file. Validates syntax before writing.
        Returns a result dict with status and any error messages.
        """
        path = self._validate_path(relative_path)

        # Syntax guard (can be bypassed with force=True)
        if not force:
            is_valid, error = self._check_syntax(content, relative_path)
            if not is_valid:
                logger.error(f"Syntax check failed for {relative_path}: {error}")
                return {
                    "status": "rejected",
                    "file": relative_path,
                    "error": error,
                    "message": "File write rejected due to syntax error. Fix the code and try again.",
                }

        # Create parent directories
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        path.write_text(content, encoding="utf-8")
        logger.info(f"File written: {relative_path} ({len(content)} bytes)")

        return {
            "status": "success",
            "file": relative_path,
            "size": len(content),
        }

    def edit_file(self, relative_path: str, old_content: str, new_content: str) -> dict:
        """
        Edit a file by replacing a specific section.
        Uses multi-tier matching (exact → flexible → error).
        """
        current = self.read_file(relative_path)
        if current is None:
            return {"status": "error", "error": f"File not found: {relative_path}"}

        # Tier 1: Exact match
        if old_content in current:
            updated = current.replace(old_content, new_content, 1)
            return self.write_file(relative_path, updated)

        # Tier 2: Flexible match (strip whitespace)
        stripped_old = old_content.strip()
        if stripped_old in current:
            updated = current.replace(stripped_old, new_content.strip(), 1)
            return self.write_file(relative_path, updated)

        return {
            "status": "error",
            "error": f"Could not find the target content in {relative_path}",
        }

    def list_dir(self, relative_path: str = ".") -> list[dict]:
        """List contents of a directory in the workspace."""
        path = self._validate_path(relative_path)
        if not path.is_dir():
            return []

        items = []
        for item in sorted(path.iterdir()):
            rel = item.relative_to(self.workspace)
            items.append({
                "path": str(rel),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
            })
        return items

    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists in the workspace."""
        return self._validate_path(relative_path).exists()

    def get_project_tree(self, max_depth: int = 4) -> str:
        """Generate a visual tree of the project structure."""
        lines = []

        def _walk(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{entry.name}")
                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    _walk(entry, prefix + extension, depth + 1)

        lines.append(self.workspace.name + "/")
        _walk(self.workspace)
        return "\n".join(lines)

    def create_zip(self) -> str:
        """Create a zip archive of the workspace. Returns the path to the zip."""
        zip_path = self.workspace.parent / f"{self.workspace.name}.zip"
        shutil.make_archive(str(self.workspace.parent / self.workspace.name), 'zip', self.workspace)
        return str(zip_path)

