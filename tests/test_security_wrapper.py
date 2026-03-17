"""
Tests for SecureFileAccess wrapper.

This module tests the security wrapper that enforces workspace-scoped access
and blocks access to sensitive files.
"""

import os
import tempfile
from pathlib import Path

import pytest

from lib.security_wrapper import SecureFileAccess, SecurityError


class TestSecureFileAccessInitialization:
    """Test initialization and workspace setup."""

    def test_init_with_valid_workspace(self, tmp_path):
        """Should initialize with a valid workspace directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))

        assert sfa.workspace == workspace.resolve()
        assert sfa.workspace.exists()

    def test_init_creates_workspace_if_missing(self, tmp_path):
        """Should create workspace directory if it doesn't exist."""
        workspace = tmp_path / "new_workspace"

        sfa = SecureFileAccess(str(workspace))

        assert sfa.workspace.exists()
        assert sfa.workspace.is_dir()

    def test_init_normalizes_workspace_path(self, tmp_path):
        """Should normalize workspace path (resolve symlinks, .. etc)."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Use path with .. in it
        weird_path = tmp_path / "workspace" / ".." / "workspace"
        sfa = SecureFileAccess(str(weird_path))

        assert sfa.workspace == workspace.resolve()


class TestPathValidation:
    """Test path validation and security checks."""

    def test_public_validate_path(self, tmp_path):
        """Should provide public validate_path method."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "test.txt"
        test_file.write_text("content")

        sfa = SecureFileAccess(str(workspace))
        validated_path = sfa.validate_path("test.txt")

        assert validated_path == test_file.resolve()
        assert isinstance(validated_path, Path)

    def test_validate_allows_file_in_workspace(self, tmp_path):
        """Should allow access to files within workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "test.txt"
        test_file.write_text("content")

        sfa = SecureFileAccess(str(workspace))
        validated_path = sfa._validate_path(str(test_file))

        assert validated_path == test_file.resolve()

    def test_validate_allows_relative_path(self, tmp_path):
        """Should allow and resolve relative paths within workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "subdir" / "test.txt"
        test_file.parent.mkdir()
        test_file.write_text("content")

        sfa = SecureFileAccess(str(workspace))
        validated_path = sfa._validate_path("subdir/test.txt")

        assert validated_path == test_file.resolve()

    def test_validate_blocks_path_traversal_absolute(self, tmp_path):
        """Should block path traversal attempts using absolute paths."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("secret")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path(str(outside_file))

        assert "outside workspace" in str(exc_info.value).lower()

    def test_validate_blocks_path_traversal_relative(self, tmp_path):
        """Should block path traversal attempts using relative paths."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path("../../../etc/passwd")

        assert "outside workspace" in str(exc_info.value).lower()

    def test_validate_blocks_symlink_escape(self, tmp_path):
        """Should block symlinks that point outside workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("secret")

        # Create symlink inside workspace pointing outside
        symlink = workspace / "escape.txt"
        symlink.symlink_to(outside_file)

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path("escape.txt")

        assert "outside workspace" in str(exc_info.value).lower()

    def test_validate_blocks_env_file(self, tmp_path):
        """Should block access to .env files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        env_file = workspace / ".env"
        env_file.write_text("SECRET=123")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path(".env")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_blocks_env_files_in_subdirs(self, tmp_path):
        """Should block access to .env files in subdirectories."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        subdir = workspace / "config"
        subdir.mkdir()
        env_file = subdir / ".env.local"
        env_file.write_text("SECRET=123")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path("config/.env.local")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_blocks_ssh_directory(self, tmp_path):
        """Should block access to .ssh directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        ssh_dir = workspace / ".ssh"
        ssh_dir.mkdir()

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path(".ssh/id_rsa")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_blocks_credentials(self, tmp_path):
        """Should block access to credentials files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        creds = workspace / "credentials.json"
        creds.write_text("{}")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path("credentials.json")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_blocks_secrets(self, tmp_path):
        """Should block access to secrets files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        secrets = workspace / "secrets.yaml"
        secrets.write_text("api_key: secret")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path("secrets.yaml")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_blocks_aws_directory(self, tmp_path):
        """Should block access to .aws directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        aws_dir = workspace / ".aws"
        aws_dir.mkdir()

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path(".aws/credentials")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_blocks_ssh_keys(self, tmp_path):
        """Should block access to SSH key files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        ssh_key = workspace / "id_rsa"
        ssh_key.write_text("-----BEGIN RSA PRIVATE KEY-----")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path("id_rsa")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_blocks_pem_files(self, tmp_path):
        """Should block access to .pem certificate files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        pem_file = workspace / "certificate.pem"
        pem_file.write_text("-----BEGIN CERTIFICATE-----")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError) as exc_info:
            sfa._validate_path("certificate.pem")

        assert "forbidden" in str(exc_info.value).lower()

    def test_validate_allows_git_directory(self, tmp_path):
        """Should allow access to .git directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        git_dir = workspace / ".git"
        git_dir.mkdir()
        config_file = git_dir / "config"
        config_file.write_text("[core]")

        sfa = SecureFileAccess(str(workspace))
        validated_path = sfa._validate_path(".git/config")

        assert validated_path == config_file.resolve()


class TestReadFile:
    """Test read_file operation."""

    def test_read_file_success(self, tmp_path):
        """Should successfully read a valid file."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "test.txt"
        test_file.write_text("Hello, World!")

        sfa = SecureFileAccess(str(workspace))
        content = sfa.read_file("test.txt")

        assert content == "Hello, World!"

    def test_read_file_with_encoding(self, tmp_path):
        """Should read file with specified encoding."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "test.txt"
        test_file.write_text("Hello, 世界!", encoding="utf-8")

        sfa = SecureFileAccess(str(workspace))
        content = sfa.read_file("test.txt", encoding="utf-8")

        assert content == "Hello, 世界!"

    def test_read_file_blocks_forbidden(self, tmp_path):
        """Should block reading forbidden files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        env_file = workspace / ".env"
        env_file.write_text("SECRET=123")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError):
            sfa.read_file(".env")

    def test_read_file_nonexistent(self, tmp_path):
        """Should raise FileNotFoundError for nonexistent files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(FileNotFoundError):
            sfa.read_file("nonexistent.txt")


class TestWriteFile:
    """Test write_file operation."""

    def test_write_file_creates_new(self, tmp_path):
        """Should create and write to a new file."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))
        sfa.write_file("new.txt", "New content")

        assert (workspace / "new.txt").read_text() == "New content"

    def test_write_file_overwrites_existing(self, tmp_path):
        """Should overwrite existing file."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "test.txt"
        test_file.write_text("Old content")

        sfa = SecureFileAccess(str(workspace))
        sfa.write_file("test.txt", "New content")

        assert test_file.read_text() == "New content"

    def test_write_file_creates_subdirs(self, tmp_path):
        """Should create parent directories if they don't exist."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))
        sfa.write_file("subdir/nested/file.txt", "Content")

        assert (workspace / "subdir" / "nested" / "file.txt").read_text() == "Content"

    def test_write_file_blocks_forbidden(self, tmp_path):
        """Should block writing to forbidden files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError):
            sfa.write_file(".env", "SECRET=123")


class TestDeleteFile:
    """Test delete_file operation."""

    def test_delete_file_success(self, tmp_path):
        """Should successfully delete a file."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "test.txt"
        test_file.write_text("Content")

        sfa = SecureFileAccess(str(workspace))
        sfa.delete_file("test.txt")

        assert not test_file.exists()

    def test_delete_file_nonexistent(self, tmp_path):
        """Should raise FileNotFoundError for nonexistent files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(FileNotFoundError):
            sfa.delete_file("nonexistent.txt")

    def test_delete_file_blocks_forbidden(self, tmp_path):
        """Should block deleting forbidden files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        env_file = workspace / ".env"
        env_file.write_text("SECRET=123")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError):
            sfa.delete_file(".env")


class TestListWorkspaceFiles:
    """Test list_workspace_files operation."""

    def test_list_files_in_directory(self, tmp_path):
        """Should list all files in a directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "file1.txt").write_text("1")
        (workspace / "file2.txt").write_text("2")
        (workspace / "file3.py").write_text("3")

        sfa = SecureFileAccess(str(workspace))
        files = sfa.list_workspace_files(".")

        assert len(files) == 3
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "file3.py" in files

    def test_list_files_in_subdirectory(self, tmp_path):
        """Should list files in a subdirectory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        subdir = workspace / "subdir"
        subdir.mkdir()
        (subdir / "file1.txt").write_text("1")
        (subdir / "file2.txt").write_text("2")

        sfa = SecureFileAccess(str(workspace))
        files = sfa.list_workspace_files("subdir")

        assert len(files) == 2
        assert "file1.txt" in files
        assert "file2.txt" in files

    def test_list_files_excludes_hidden(self, tmp_path):
        """Should exclude hidden files by default."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "visible.txt").write_text("1")
        (workspace / ".hidden").write_text("2")

        sfa = SecureFileAccess(str(workspace))
        files = sfa.list_workspace_files(".")

        assert "visible.txt" in files
        assert ".hidden" not in files

    def test_list_files_includes_hidden_when_requested(self, tmp_path):
        """Should include hidden files when requested."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "visible.txt").write_text("1")
        (workspace / ".hidden").write_text("2")

        sfa = SecureFileAccess(str(workspace))
        files = sfa.list_workspace_files(".", include_hidden=True)

        assert "visible.txt" in files
        assert ".hidden" in files

    def test_list_files_blocks_outside_workspace(self, tmp_path):
        """Should block listing files outside workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError):
            sfa.list_workspace_files("../..")

    def test_list_files_empty_directory(self, tmp_path):
        """Should return empty list for empty directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))
        files = sfa.list_workspace_files(".")

        assert files == []


class TestFileExists:
    """Test file_exists operation."""

    def test_file_exists_returns_true(self, tmp_path):
        """Should return True for existing files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        test_file = workspace / "test.txt"
        test_file.write_text("Content")

        sfa = SecureFileAccess(str(workspace))

        assert sfa.file_exists("test.txt") is True

    def test_file_exists_returns_false(self, tmp_path):
        """Should return False for nonexistent files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        sfa = SecureFileAccess(str(workspace))

        assert sfa.file_exists("nonexistent.txt") is False

    def test_file_exists_blocks_forbidden(self, tmp_path):
        """Should block checking existence of forbidden files."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        env_file = workspace / ".env"
        env_file.write_text("SECRET=123")

        sfa = SecureFileAccess(str(workspace))

        with pytest.raises(SecurityError):
            sfa.file_exists(".env")
