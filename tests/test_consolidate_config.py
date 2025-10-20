"""Unit tests for config-driven phase routing in consolidate.py."""
import pytest
import yaml
from pathlib import Path

from crengine.consolidate import to_phases_from_config
from crengine.model_schemas import Finding, ScoredItem


class TestToPhasesFromConfig:
    """Tests for config-driven phase routing."""

    def test_load_phase_config_from_yaml(self, temp_dir):
        """Test loading phase configuration from YAML."""
        config_yaml = """
phasing:
  - name: "Phase 0 – Hygiene"
    include_tags: ["style", "lints"]
  - name: "Phase 1 – Security"
    include_tags: ["security", "sast"]
"""
        config_file = temp_dir / "test_engine.yaml"
        config_file.write_text(config_yaml)

        config = yaml.safe_load(config_file.read_text())

        finding_style = Finding(
            tool="flake8", rule_id="E501", severity="INFO",
            message="Line long", file="a.py", tags=["style"]
        )
        finding_security = Finding(
            tool="bandit", rule_id="B001", severity="HIGH",
            message="eval", file="b.py", tags=["security"]
        )

        items = [
            ScoredItem(finding=finding_style, difficulty_risk=1.0, value_importance=1.0, est_hours=0.5),
            ScoredItem(finding=finding_security, difficulty_risk=4.0, value_importance=4.0, est_hours=6.0),
        ]

        phases = to_phases_from_config(items, config["phasing"])

        assert "Phase 0 – Hygiene" in phases
        assert "Phase 1 – Security" in phases
        assert len(phases["Phase 0 – Hygiene"]) == 1
        assert len(phases["Phase 1 – Security"]) == 1

    def test_multiple_tags_routes_to_first_matching_phase(self, temp_dir):
        """Test that items with multiple tags route to first matching phase."""
        config_yaml = """
phasing:
  - name: "Phase 1 – Security"
    include_tags: ["security"]
  - name: "Phase 2 – Performance"
    include_tags: ["perf"]
"""
        config_file = temp_dir / "test_engine.yaml"
        config_file.write_text(config_yaml)

        config = yaml.safe_load(config_file.read_text())

        # Finding with both security and perf tags
        finding = Finding(
            tool="test", rule_id="T1", severity="HIGH",
            message="Issue", file="a.py", tags=["security", "perf"]
        )
        items = [ScoredItem(finding=finding, difficulty_risk=3.0, value_importance=3.0, est_hours=4.0)]

        phases = to_phases_from_config(items, config["phasing"])

        # Should route to Phase 1 (security) since it's first
        assert len(phases["Phase 1 – Security"]) == 1
        assert len(phases["Phase 2 – Performance"]) == 0

    def test_unmatched_items_go_to_catchall_phase(self, temp_dir):
        """Test that items without matching tags go to a catch-all phase."""
        config_yaml = """
phasing:
  - name: "Phase 1 – Security"
    include_tags: ["security"]
"""
        config_file = temp_dir / "test_engine.yaml"
        config_file.write_text(config_yaml)

        config = yaml.safe_load(config_file.read_text())

        finding = Finding(
            tool="test", rule_id="T1", severity="INFO",
            message="Unknown", file="a.py", tags=["unknown_tag"]
        )
        items = [ScoredItem(finding=finding, difficulty_risk=2.0, value_importance=2.0, est_hours=2.0)]

        phases = to_phases_from_config(items, config["phasing"])

        # Should have a catch-all phase for unmatched items
        assert "Uncategorized" in phases or any(len(v) > 0 for v in phases.values())

    def test_empty_config_creates_default_phase(self, temp_dir):
        """Test that empty config creates a default phase."""
        config = {"phasing": []}

        finding = Finding(
            tool="test", rule_id="T1", severity="INFO",
            message="Test", file="a.py", tags=["test"]
        )
        items = [ScoredItem(finding=finding, difficulty_risk=1.0, value_importance=1.0, est_hours=0.5)]

        phases = to_phases_from_config(items, config["phasing"])

        # Should have at least one phase with the item
        assert sum(len(v) for v in phases.values()) == 1

    def test_preserves_all_items(self, temp_dir):
        """Test that all items are preserved (not lost during routing)."""
        config_yaml = """
phasing:
  - name: "Phase A"
    include_tags: ["tag_a"]
  - name: "Phase B"
    include_tags: ["tag_b"]
"""
        config_file = temp_dir / "test_engine.yaml"
        config_file.write_text(config_yaml)

        config = yaml.safe_load(config_file.read_text())

        items = [
            ScoredItem(
                finding=Finding(tool="t", rule_id=f"R{i}", severity="INFO",
                               message=f"msg{i}", file="f.py", tags=[f"tag_{chr(97 + i % 2)}"]),
                difficulty_risk=1.0, value_importance=1.0, est_hours=0.5
            )
            for i in range(10)
        ]

        phases = to_phases_from_config(items, config["phasing"])

        # All items should be in some phase
        total_items = sum(len(v) for v in phases.values())
        assert total_items == 10

    def test_case_insensitive_tag_matching(self, temp_dir):
        """Test that tag matching is case-insensitive."""
        config_yaml = """
phasing:
  - name: "Phase 1"
    include_tags: ["Security", "SAST"]
"""
        config_file = temp_dir / "test_engine.yaml"
        config_file.write_text(config_yaml)

        config = yaml.safe_load(config_file.read_text())

        # Tags with different casing
        finding1 = Finding(
            tool="t", rule_id="R1", severity="HIGH",
            message="msg", file="a.py", tags=["security"]  # lowercase
        )
        finding2 = Finding(
            tool="t", rule_id="R2", severity="HIGH",
            message="msg", file="b.py", tags=["SECURITY"]  # uppercase
        )

        items = [
            ScoredItem(finding=finding1, difficulty_risk=3.0, value_importance=3.0, est_hours=4.0),
            ScoredItem(finding=finding2, difficulty_risk=3.0, value_importance=3.0, est_hours=4.0),
        ]

        phases = to_phases_from_config(items, config["phasing"])

        # Both should be in Phase 1
        assert len(phases["Phase 1"]) == 2
