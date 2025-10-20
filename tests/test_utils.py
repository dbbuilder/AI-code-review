"""Unit tests for utils.py - Utility functions."""
import json
import subprocess
from pathlib import Path

import pytest

from crengine.utils import sha256_file, run_tool, write_json, write_text


class TestSha256File:
    """Tests for sha256_file function."""

    def test_sha256_empty_file(self, temp_dir):
        """Test SHA256 hash of an empty file."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        # Known SHA256 hash of empty file
        expected_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert sha256_file(empty_file) == expected_hash

    def test_sha256_small_file(self, temp_dir):
        """Test SHA256 hash of a small file."""
        small_file = temp_dir / "small.txt"
        small_file.write_text("Hello, World!")

        hash_result = sha256_file(small_file)
        assert len(hash_result) == 64  # SHA256 is 64 hex characters
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_sha256_large_file(self, temp_dir):
        """Test SHA256 hash of a large file (tests chunking)."""
        large_file = temp_dir / "large.bin"
        # Create 2MB file
        large_file.write_bytes(b"x" * (2 * 1024 * 1024))

        hash_result = sha256_file(large_file)
        assert len(hash_result) == 64

    def test_sha256_consistency(self, temp_dir):
        """Test that same content produces same hash."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        content = "Consistent content"

        file1.write_text(content)
        file2.write_text(content)

        assert sha256_file(file1) == sha256_file(file2)

    def test_sha256_different_content(self, temp_dir):
        """Test that different content produces different hash."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"

        file1.write_text("Content A")
        file2.write_text("Content B")

        assert sha256_file(file1) != sha256_file(file2)


class TestRunTool:
    """Tests for run_tool function."""

    def test_run_tool_success(self):
        """Test running a successful command."""
        result = run_tool(["echo", "Hello"])
        assert result.returncode == 0
        assert "Hello" in result.stdout

    def test_run_tool_failure(self):
        """Test running a command that fails."""
        result = run_tool(["ls", "/nonexistent/path/xyz"])
        assert result.returncode != 0

    def test_run_tool_captures_stdout(self):
        """Test that stdout is captured."""
        result = run_tool(["echo", "test output"])
        assert "test output" in result.stdout
        assert isinstance(result.stdout, str)

    def test_run_tool_captures_stderr(self):
        """Test that stderr is captured."""
        # Python command that writes to stderr
        result = run_tool(["python", "-c", "import sys; sys.stderr.write('error msg')"])
        assert "error msg" in result.stderr

    def test_run_tool_with_arguments(self):
        """Test running command with multiple arguments."""
        result = run_tool(["python", "--version"])
        assert result.returncode == 0
        assert "Python" in result.stdout or "Python" in result.stderr

    def test_run_tool_no_shell_injection(self):
        """Test that shell injection is prevented (no shell=True)."""
        # This should NOT execute as a shell command
        result = run_tool(["echo", "test; ls"])
        # The semicolon should be treated as literal text, not command separator
        assert "test; ls" in result.stdout


class TestWriteJson:
    """Tests for write_json function."""

    def test_write_json_simple(self, temp_dir):
        """Test writing simple JSON object."""
        output_file = temp_dir / "output.json"
        data = {"key": "value", "number": 42}

        write_json(output_file, data)

        assert output_file.exists()
        loaded = json.loads(output_file.read_text())
        assert loaded["key"] == "value"
        assert loaded["number"] == 42

    def test_write_json_nested(self, temp_dir):
        """Test writing nested JSON structure."""
        output_file = temp_dir / "nested.json"
        data = {
            "findings": [
                {"tool": "bandit", "severity": "HIGH"},
                {"tool": "flake8", "severity": "INFO"}
            ]
        }

        write_json(output_file, data)

        loaded = json.loads(output_file.read_text())
        assert len(loaded["findings"]) == 2

    def test_write_json_creates_parent_dirs(self, temp_dir):
        """Test that parent directories are created automatically."""
        output_file = temp_dir / "subdir" / "nested" / "output.json"
        data = {"test": True}

        write_json(output_file, data)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_write_json_formatting(self, temp_dir):
        """Test that JSON is formatted with indentation."""
        output_file = temp_dir / "formatted.json"
        data = {"a": 1, "b": 2}

        write_json(output_file, data)

        content = output_file.read_text()
        assert "\n" in content  # Should be multi-line
        assert "  " in content  # Should have indentation

    def test_write_json_overwrites(self, temp_dir):
        """Test that write_json overwrites existing files."""
        output_file = temp_dir / "overwrite.json"

        write_json(output_file, {"version": 1})
        write_json(output_file, {"version": 2})

        loaded = json.loads(output_file.read_text())
        assert loaded["version"] == 2


class TestWriteText:
    """Tests for write_text function."""

    def test_write_text_simple(self, temp_dir):
        """Test writing simple text content."""
        output_file = temp_dir / "output.txt"
        content = "Hello, World!"

        write_text(output_file, content)

        assert output_file.exists()
        assert output_file.read_text() == content

    def test_write_text_multiline(self, temp_dir):
        """Test writing multiline text."""
        output_file = temp_dir / "multiline.txt"
        content = "Line 1\nLine 2\nLine 3"

        write_text(output_file, content)

        assert output_file.read_text() == content

    def test_write_text_creates_parent_dirs(self, temp_dir):
        """Test that parent directories are created."""
        output_file = temp_dir / "deep" / "nested" / "path" / "file.txt"
        content = "Test"

        write_text(output_file, content)

        assert output_file.exists()

    def test_write_text_unicode(self, temp_dir):
        """Test writing Unicode content."""
        output_file = temp_dir / "unicode.txt"
        content = "Hello 世界 🌍"

        write_text(output_file, content)

        assert output_file.read_text(encoding="utf-8") == content

    def test_write_text_overwrites(self, temp_dir):
        """Test that write_text overwrites existing files."""
        output_file = temp_dir / "overwrite.txt"

        write_text(output_file, "Version 1")
        write_text(output_file, "Version 2")

        assert output_file.read_text() == "Version 2"

    def test_write_text_markdown(self, temp_dir):
        """Test writing markdown content."""
        output_file = temp_dir / "README.md"
        content = "# Title\n\n## Subtitle\n\n- Item 1\n- Item 2"

        write_text(output_file, content)

        assert output_file.read_text() == content
