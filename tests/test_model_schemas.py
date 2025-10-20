"""Unit tests for model_schemas.py - Pydantic models validation."""
import pytest
from pydantic import ValidationError

from crengine.model_schemas import (
    FileEntry,
    Manifest,
    Finding,
    ScoredItem,
    PhaseItem,
    DeltaFinding,
)


class TestFileEntry:
    """Tests for FileEntry model."""

    def test_file_entry_valid(self):
        """Test creating a valid FileEntry."""
        entry = FileEntry(
            path="src/main.py",
            language="python",
            bytes=1024,
            sha256="abc123def456"
        )
        assert entry.path == "src/main.py"
        assert entry.language == "python"
        assert entry.bytes == 1024
        assert entry.sha256 == "abc123def456"

    def test_file_entry_optional_language(self):
        """Test FileEntry with optional language field."""
        entry = FileEntry(
            path="README.md",
            language=None,
            bytes=512,
            sha256="xyz789"
        )
        assert entry.language is None

    def test_file_entry_serialization(self):
        """Test FileEntry serialization to dict."""
        entry = FileEntry(
            path="test.py",
            language="python",
            bytes=100,
            sha256="hash123"
        )
        data = entry.model_dump()
        assert data["path"] == "test.py"
        assert data["language"] == "python"

    def test_file_entry_missing_required_field(self):
        """Test FileEntry fails without required fields."""
        with pytest.raises(ValidationError):
            FileEntry(path="test.py")  # Missing bytes and sha256


class TestManifest:
    """Tests for Manifest model."""

    def test_manifest_valid(self):
        """Test creating a valid Manifest."""
        manifest = Manifest(
            repo_root="/path/to/repo",
            commit="abc123",
            files=[
                FileEntry(path="a.py", language="python", bytes=100, sha256="hash1"),
                FileEntry(path="b.js", language="javascript", bytes=200, sha256="hash2"),
            ]
        )
        assert manifest.repo_root == "/path/to/repo"
        assert manifest.commit == "abc123"
        assert len(manifest.files) == 2

    def test_manifest_empty_files(self):
        """Test Manifest with empty file list."""
        manifest = Manifest(
            repo_root="/repo",
            commit="abc",
            files=[]
        )
        assert len(manifest.files) == 0

    def test_manifest_serialization(self):
        """Test Manifest serialization."""
        manifest = Manifest(
            repo_root="/repo",
            commit="abc",
            files=[FileEntry(path="x.py", bytes=50, sha256="h1")]
        )
        data = manifest.model_dump()
        assert data["repo_root"] == "/repo"
        assert len(data["files"]) == 1


class TestFinding:
    """Tests for Finding model."""

    def test_finding_valid(self):
        """Test creating a valid Finding."""
        finding = Finding(
            tool="bandit",
            rule_id="B001",
            severity="HIGH",
            message="Security issue detected",
            file="main.py",
            line=10,
            col=5,
            suggestion="Use safer alternative",
            tags=["security", "sast"]
        )
        assert finding.tool == "bandit"
        assert finding.rule_id == "B001"
        assert finding.severity == "HIGH"
        assert finding.line == 10
        assert finding.col == 5
        assert "security" in finding.tags

    def test_finding_optional_fields(self):
        """Test Finding with optional fields as None."""
        finding = Finding(
            tool="flake8",
            rule_id="E501",
            severity="INFO",
            message="Line too long",
            file="test.py"
        )
        assert finding.line is None
        assert finding.col is None
        assert finding.suggestion is None
        assert finding.tags == []

    def test_finding_default_tags(self):
        """Test Finding defaults to empty tags list."""
        finding = Finding(
            tool="test",
            rule_id="T001",
            severity="LOW",
            message="Test",
            file="a.py"
        )
        assert isinstance(finding.tags, list)
        assert len(finding.tags) == 0


class TestScoredItem:
    """Tests for ScoredItem model."""

    def test_scored_item_valid(self):
        """Test creating a valid ScoredItem."""
        finding = Finding(
            tool="bandit",
            rule_id="B001",
            severity="HIGH",
            message="Issue",
            file="main.py",
            tags=["security"]
        )
        scored = ScoredItem(
            finding=finding,
            difficulty_risk=4.5,
            value_importance=4.8,
            est_hours=6.0
        )
        assert scored.difficulty_risk == 4.5
        assert scored.value_importance == 4.8
        assert scored.est_hours == 6.0
        assert scored.finding.tool == "bandit"

    def test_scored_item_nested_serialization(self):
        """Test ScoredItem serialization with nested Finding."""
        finding = Finding(
            tool="test",
            rule_id="T1",
            severity="LOW",
            message="msg",
            file="f.py"
        )
        scored = ScoredItem(
            finding=finding,
            difficulty_risk=2.0,
            value_importance=3.0,
            est_hours=1.5
        )
        data = scored.model_dump()
        assert "finding" in data
        assert data["finding"]["tool"] == "test"


class TestPhaseItem:
    """Tests for PhaseItem model."""

    def test_phase_item_valid(self):
        """Test creating a valid PhaseItem."""
        finding = Finding(
            tool="test",
            rule_id="T1",
            severity="INFO",
            message="msg",
            file="a.py"
        )
        scored = ScoredItem(
            finding=finding,
            difficulty_risk=1.0,
            value_importance=1.0,
            est_hours=0.5
        )
        phase = PhaseItem(
            phase="Phase 0 – Repo Hygiene",
            items=[scored]
        )
        assert phase.phase == "Phase 0 – Repo Hygiene"
        assert len(phase.items) == 1


class TestDeltaFinding:
    """Tests for DeltaFinding model."""

    def test_delta_finding_valid(self):
        """Test creating a valid DeltaFinding."""
        finding = Finding(
            tool="test",
            rule_id="T1",
            severity="INFO",
            message="msg",
            file="changed.py"
        )
        delta = DeltaFinding(
            file="changed.py",
            hunks=[{"start": 10, "end": 20}],
            findings=[finding]
        )
        assert delta.file == "changed.py"
        assert len(delta.hunks) == 1
        assert len(delta.findings) == 1

    def test_delta_finding_empty_findings(self):
        """Test DeltaFinding with no findings."""
        delta = DeltaFinding(
            file="clean.py",
            hunks=[],
            findings=[]
        )
        assert len(delta.findings) == 0
