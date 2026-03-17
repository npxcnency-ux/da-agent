"""
Security wrapper for file access operations.

This module provides a secure file access wrapper that enforces workspace-scoped
access and blocks access to sensitive files like .env, credentials, .ssh directories, etc.
"""

import os
from pathlib import Path
from typing import List, Optional


class SecurityError(Exception):
    """Raised when a security policy is violated."""
    pass


class SecureFileAccess:
    """
    Secure file access wrapper that enforces workspace-scoped access.

    All file operations are restricted to the workspace directory and
    forbidden patterns (e.g., .env files, credentials) are blocked.
    """

    # Patterns that are forbidden from access
    FORBIDDEN_PATTERNS = [
        ".env",  # Environment files
        ".env.local",
        ".env.development",
        ".env.production",
        "credentials",  # Credentials files (generic)
        "secrets",  # Secrets files (generic)
        ".ssh/",  # SSH directory
        ".aws/",  # AWS directory
        "id_rsa",  # SSH key file
        "id_dsa",  # SSH key file
        ".pem",  # Certificate files
    ]

    def __init__(self, workspace: str):
        """
        Initialize SecureFileAccess with a workspace directory.

        Args:
            workspace: Path to the workspace directory. Will be created if it doesn't exist.
        """
        self.workspace = Path(workspace).resolve()

        # Create workspace if it doesn't exist
        if not self.workspace.exists():
            self.workspace.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, path: str) -> Path:
        """
        Validate that a path is safe to access.

        Args:
            path: Path to validate (can be relative or absolute)

        Returns:
            Resolved absolute Path object

        Raises:
            SecurityError: If path is outside workspace or matches forbidden patterns
        """
        # Convert to Path and resolve (handles symlinks, .., etc.)
        if Path(path).is_absolute():
            resolved_path = Path(path).resolve()
        else:
            resolved_path = (self.workspace / path).resolve()

        # Check if path is within workspace
        try:
            resolved_path.relative_to(self.workspace)
        except ValueError:
            raise SecurityError(
                f"Access denied: Path '{path}' is outside workspace '{self.workspace}'"
            )

        # Check against forbidden patterns
        path_str = str(resolved_path)
        path_parts = resolved_path.parts

        for pattern in self.FORBIDDEN_PATTERNS:
            # Check if any part of the path matches forbidden patterns
            if pattern.endswith("/"):
                # Directory pattern (e.g., .ssh/, .aws/)
                if pattern.rstrip("/") in path_parts:
                    raise SecurityError(
                        f"Access denied: Path contains forbidden pattern '{pattern}'"
                    )
            elif pattern == ".pem":
                # File extension pattern specifically for .pem
                if resolved_path.suffix == pattern:
                    raise SecurityError(
                        f"Access denied: Path matches forbidden pattern '{pattern}'"
                    )
            else:
                # File/prefix pattern (e.g., .env, credentials, id_rsa)
                # Match exact name or name starting with pattern
                if resolved_path.name == pattern or resolved_path.name.startswith(pattern):
                    raise SecurityError(
                        f"Access denied: Path matches forbidden pattern '{pattern}'"
                    )

        return resolved_path

    def validate_path(self, file_path: str) -> Path:
        """
        Public method to validate that a path is safe to access.

        Args:
            file_path: Path to validate (can be relative or absolute)

        Returns:
            Resolved absolute Path object

        Raises:
            SecurityError: If path is outside workspace or matches forbidden patterns
        """
        return self._validate_path(file_path)

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        """
        Read a file from the workspace.

        Args:
            path: Path to the file (relative to workspace or absolute within workspace)
            encoding: File encoding (default: utf-8)

        Returns:
            File contents as string

        Raises:
            SecurityError: If path violates security policies
            FileNotFoundError: If file doesn't exist
        """
        validated_path = self._validate_path(path)

        if not validated_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return validated_path.read_text(encoding=encoding)

    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> None:
        """
        Write content to a file in the workspace.

        Args:
            path: Path to the file (relative to workspace or absolute within workspace)
            content: Content to write
            encoding: File encoding (default: utf-8)

        Raises:
            SecurityError: If path violates security policies
        """
        validated_path = self._validate_path(path)

        # Create parent directories if they don't exist
        validated_path.parent.mkdir(parents=True, exist_ok=True)

        validated_path.write_text(content, encoding=encoding)

    def delete_file(self, path: str) -> None:
        """
        Delete a file from the workspace.

        Args:
            path: Path to the file (relative to workspace or absolute within workspace)

        Raises:
            SecurityError: If path violates security policies
            FileNotFoundError: If file doesn't exist
        """
        validated_path = self._validate_path(path)

        if not validated_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        validated_path.unlink()

    def list_workspace_files(self, path: str = ".", include_hidden: bool = False) -> List[str]:
        """
        List files in a directory within the workspace.

        Args:
            path: Path to directory (relative to workspace or absolute within workspace)
            include_hidden: Whether to include hidden files (default: False)

        Returns:
            List of filenames (not full paths)

        Raises:
            SecurityError: If path violates security policies
        """
        validated_path = self._validate_path(path)

        if not validated_path.exists():
            return []

        if not validated_path.is_dir():
            return []

        files = []
        for item in validated_path.iterdir():
            if item.is_file():
                # Skip hidden files unless requested
                if not include_hidden and item.name.startswith("."):
                    continue
                files.append(item.name)

        return files

    def file_exists(self, path: str) -> bool:
        """
        Check if a file exists in the workspace.

        Args:
            path: Path to check (relative to workspace or absolute within workspace)

        Returns:
            True if file exists, False otherwise

        Raises:
            SecurityError: If path violates security policies
        """
        validated_path = self._validate_path(path)
        return validated_path.exists()
