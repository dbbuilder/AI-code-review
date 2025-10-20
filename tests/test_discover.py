"""Unit tests for discover.py - Repository discovery and manifest generation."""
from pathlib import Path

import pytest
from git import Repo

from crengine.discover import build_manifest, LANG_BY_EXT


class TestLanguageDetection:
    """Tests for LANG_BY_EXT constant."""

    def test_lang_by_ext_python(self):
        """Test Python file extension detection."""
        assert LANG_BY_EXT[".py"] == "python"

    def test_lang_by_ext_javascript(self):
        """Test JavaScript file extension detection."""
        assert LANG_BY_EXT[".js"] == "javascript"

    def test_lang_by_ext_typescript(self):
        """Test TypeScript file extension detection."""
        assert LANG_BY_EXT[".ts"] == "typescript"

    def test_lang_by_ext_coverage(self):
        """Test all expected languages are present."""
        expected_langs = {"python", "javascript", "typescript", "c_sharp",
                         "java", "go", "rust", "cpp", "c"}
        actual_langs = set(LANG_BY_EXT.values())
        assert expected_langs.issubset(actual_langs)


class TestBuildManifest:
    """Tests for build_manifest function."""

    def test_build_manifest_basic(self, mock_repo, config_files):
        """Test building manifest for a basic repository."""
        # Create include_exclude.yaml in mock_repo
        include_exclude_yaml = """
include:
  - "**/*.py"
exclude:
  - "**/.venv/**"
  - "**/test_*"
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        assert manifest.repo_root == str(mock_repo)
        assert len(manifest.commit) == 40  # Git SHA is 40 characters
        assert len(manifest.files) > 0

    def test_build_manifest_detects_python_files(self, mock_repo, config_files):
        """Test that Python files are detected and language is set."""
        include_exclude_yaml = """
include:
  - "**/*.py"
exclude:
  - "**/.venv/**"
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        python_files = [f for f in manifest.files if f.language == "python"]
        assert len(python_files) > 0

        # Check that specific files are found
        file_paths = [f.path for f in manifest.files]
        assert any("main.py" in p for p in file_paths)

    def test_build_manifest_excludes_patterns(self, mock_repo, temp_dir):
        """Test that exclude patterns are respected."""
        # Create a .venv directory with Python files
        venv_dir = mock_repo / ".venv"
        venv_dir.mkdir()
        (venv_dir / "excluded.py").write_text("# Should be excluded")

        include_exclude_yaml = """
include:
  - "**/*.py"
exclude:
  - "**/.venv/**"
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        file_paths = [f.path for f in manifest.files]
        assert not any(".venv" in p for p in file_paths)

    def test_build_manifest_file_sizes(self, mock_repo, config_files):
        """Test that file sizes are captured correctly."""
        include_exclude_yaml = """
include:
  - "**/*.py"
exclude: []
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        # All files should have size >= 0
        assert all(f.bytes >= 0 for f in manifest.files)

        # __init__.py should be empty or very small
        init_files = [f for f in manifest.files if "__init__.py" in f.path]
        if init_files:
            assert init_files[0].bytes == 0

    def test_build_manifest_sha256_hashes(self, mock_repo, config_files):
        """Test that SHA256 hashes are computed correctly."""
        include_exclude_yaml = """
include:
  - "**/*.py"
exclude: []
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        # All files should have a valid SHA256 hash (64 hex characters)
        for f in manifest.files:
            assert len(f.sha256) == 64
            assert all(c in "0123456789abcdef" for c in f.sha256)

    def test_build_manifest_multiple_languages(self, temp_dir):
        """Test manifest with multiple programming languages."""
        # Create a multi-language repo
        multi_repo = temp_dir / "multi_lang"
        multi_repo.mkdir()

        repo = Repo.init(multi_repo)

        (multi_repo / "script.py").write_text("print('Python')")
        (multi_repo / "app.js").write_text("console.log('JS');")
        (multi_repo / "main.ts").write_text("const x: number = 1;")
        (multi_repo / "Program.cs").write_text("class Program {}")

        repo.index.add(["script.py", "app.js", "main.ts", "Program.cs"])
        repo.index.commit("Multi-language commit")

        include_exclude_yaml = """
include:
  - "**/*"
exclude: []
"""
        config_dir = multi_repo / "config"
        config_dir.mkdir()
        (config_dir / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            multi_repo,
            config_dir / "include_exclude.yaml"
        )

        languages = {f.language for f in manifest.files if f.language}
        assert "python" in languages
        assert "javascript" in languages
        assert "typescript" in languages
        assert "c_sharp" in languages

    def test_build_manifest_unknown_extension(self, temp_dir):
        """Test files with unknown extensions have None language."""
        repo_path = temp_dir / "unknown_ext"
        repo_path.mkdir()

        repo = Repo.init(repo_path)

        (repo_path / "README.md").write_text("# README")
        (repo_path / "data.json").write_text('{"key": "value"}')

        repo.index.add(["README.md", "data.json"])
        repo.index.commit("Unknown extensions")

        include_exclude_yaml = """
include:
  - "**/*"
exclude: []
"""
        config_dir = repo_path / "config"
        config_dir.mkdir()
        (config_dir / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            repo_path,
            config_dir / "include_exclude.yaml"
        )

        md_file = [f for f in manifest.files if f.path.endswith(".md")][0]
        assert md_file.language is None

    def test_build_manifest_git_commit_tracking(self, mock_repo, config_files):
        """Test that git commit hash is tracked correctly."""
        include_exclude_yaml = """
include:
  - "**/*.py"
exclude: []
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest1 = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        # Make a new commit
        repo = Repo(mock_repo)
        (mock_repo / "new_file.py").write_text("# New file")
        repo.index.add(["new_file.py"])
        repo.index.commit("Add new file")

        manifest2 = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        # Commit hashes should be different
        assert manifest1.commit != manifest2.commit

    def test_build_manifest_empty_includes(self, mock_repo, temp_dir):
        """Test manifest with default includes when none specified."""
        include_exclude_yaml = """
exclude:
  - "**/.venv/**"
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        # Should default to ["**/*"] and include all files
        assert len(manifest.files) > 0

    def test_build_manifest_relative_paths(self, mock_repo, config_files):
        """Test that file paths are relative to repo root."""
        include_exclude_yaml = """
include:
  - "**/*.py"
exclude: []
"""
        (mock_repo / "config" / "include_exclude.yaml").write_text(include_exclude_yaml)

        manifest = build_manifest(
            mock_repo,
            mock_repo / "config" / "include_exclude.yaml"
        )

        # All paths should be relative (not absolute)
        for f in manifest.files:
            assert not f.path.startswith("/")
            assert not f.path.startswith(str(mock_repo))
