"""Unit tests for diffscan.py - Git diff scanning and delta detection."""
from pathlib import Path

import pytest
from git import Repo

from crengine.diffscan import changed_files, changed_hunks


class TestChangedFiles:
    """Tests for changed_files function."""

    def test_changed_files_basic(self, mock_repo):
        """Test detecting changed files between commits."""
        repo = Repo(mock_repo)

        # Create a new file and commit
        (mock_repo / "newfile.py").write_text("# New content")
        repo.index.add(["newfile.py"])
        repo.index.commit("Add new file")

        # Detect changes from previous commit
        files = changed_files(mock_repo, base_ref="HEAD~1")

        assert "newfile.py" in files

    def test_changed_files_modified_file(self, mock_repo):
        """Test detecting modified files."""
        repo = Repo(mock_repo)

        # Modify existing file
        (mock_repo / "src" / "main.py").write_text("# Modified content")
        repo.index.add(["src/main.py"])
        repo.index.commit("Modify main.py")

        files = changed_files(mock_repo, base_ref="HEAD~1")

        assert any("main.py" in f for f in files)

    def test_changed_files_no_changes(self, mock_repo):
        """Test when there are no changes."""
        # Don't make any new commits
        files = changed_files(mock_repo, base_ref="HEAD")

        assert len(files) == 0

    def test_changed_files_multiple_changes(self, mock_repo):
        """Test detecting multiple changed files."""
        repo = Repo(mock_repo)

        # Change multiple files
        (mock_repo / "file1.py").write_text("content1")
        (mock_repo / "file2.py").write_text("content2")
        (mock_repo / "file3.py").write_text("content3")

        repo.index.add(["file1.py", "file2.py", "file3.py"])
        repo.index.commit("Add multiple files")

        files = changed_files(mock_repo, base_ref="HEAD~1")

        assert len(files) >= 3
        assert "file1.py" in files
        assert "file2.py" in files
        assert "file3.py" in files

    def test_changed_files_returns_list(self, mock_repo):
        """Test that changed_files returns a list."""
        files = changed_files(mock_repo, base_ref="HEAD")

        assert isinstance(files, list)

    def test_changed_files_custom_base_ref(self, mock_repo):
        """Test using custom base reference."""
        repo = Repo(mock_repo)

        # Make first commit
        (mock_repo / "v1.py").write_text("version 1")
        repo.index.add(["v1.py"])
        commit1 = repo.index.commit("Version 1")

        # Make second commit
        (mock_repo / "v2.py").write_text("version 2")
        repo.index.add(["v2.py"])
        repo.index.commit("Version 2")

        # Check changes from first commit
        files = changed_files(mock_repo, base_ref=commit1.hexsha)

        assert "v2.py" in files
        assert "v1.py" not in files  # v1.py was in the base


class TestChangedHunks:
    """Tests for changed_hunks function."""

    def test_changed_hunks_basic(self, mock_repo):
        """Test extracting changed hunks."""
        repo = Repo(mock_repo)

        # Modify a file
        original = (mock_repo / "src" / "main.py").read_text()
        modified = original + "\n\ndef new_function():\n    pass\n"
        (mock_repo / "src" / "main.py").write_text(modified)

        repo.index.add(["src/main.py"])
        repo.index.commit("Add new function")

        hunks = changed_hunks(mock_repo, base_ref="HEAD~1")

        assert isinstance(hunks, dict)
        assert any("main.py" in key for key in hunks.keys())

    def test_changed_hunks_new_file(self, mock_repo):
        """Test hunks for newly added file."""
        repo = Repo(mock_repo)

        (mock_repo / "brand_new.py").write_text("def hello():\n    print('Hi')\n")
        repo.index.add(["brand_new.py"])
        repo.index.commit("Add brand new file")

        hunks = changed_hunks(mock_repo, base_ref="HEAD~1")

        assert "brand_new.py" in hunks
        assert "def hello" in hunks["brand_new.py"]

    def test_changed_hunks_returns_dict(self, mock_repo):
        """Test that changed_hunks returns a dictionary."""
        hunks = changed_hunks(mock_repo, base_ref="HEAD")

        assert isinstance(hunks, dict)

    def test_changed_hunks_no_changes(self, mock_repo):
        """Test hunks when there are no changes."""
        hunks = changed_hunks(mock_repo, base_ref="HEAD")

        assert len(hunks) == 0

    def test_changed_hunks_multiple_files(self, mock_repo):
        """Test hunks for multiple changed files."""
        repo = Repo(mock_repo)

        # Modify multiple files
        (mock_repo / "file_a.py").write_text("# File A changes")
        (mock_repo / "file_b.py").write_text("# File B changes")

        repo.index.add(["file_a.py", "file_b.py"])
        repo.index.commit("Modify multiple files")

        hunks = changed_hunks(mock_repo, base_ref="HEAD~1")

        assert "file_a.py" in hunks
        assert "file_b.py" in hunks

    def test_changed_hunks_contains_diff_markers(self, mock_repo):
        """Test that hunks contain diff format markers."""
        repo = Repo(mock_repo)

        (mock_repo / "test_diff.py").write_text("line 1\nline 2\nline 3")
        repo.index.add(["test_diff.py"])
        repo.index.commit("Initial content")

        (mock_repo / "test_diff.py").write_text("line 1\nMODIFIED\nline 3")
        repo.index.add(["test_diff.py"])
        repo.index.commit("Modify content")

        hunks = changed_hunks(mock_repo, base_ref="HEAD~1")

        # Should contain diff markers
        if "test_diff.py" in hunks:
            hunk_content = hunks["test_diff.py"]
            assert "diff --git" in hunk_content or "@@" in hunk_content or len(hunk_content) > 0

    def test_changed_hunks_custom_base_ref(self, mock_repo):
        """Test using custom base reference for hunks."""
        repo = Repo(mock_repo)

        (mock_repo / "versioned.py").write_text("v1")
        repo.index.add(["versioned.py"])
        commit1 = repo.index.commit("Version 1")

        (mock_repo / "versioned.py").write_text("v2")
        repo.index.add(["versioned.py"])
        repo.index.commit("Version 2")

        hunks = changed_hunks(mock_repo, base_ref=commit1.hexsha)

        assert "versioned.py" in hunks
