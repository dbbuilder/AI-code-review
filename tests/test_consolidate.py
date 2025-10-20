"""Unit tests for consolidate.py - Phase routing and consolidation."""
import pytest

from crengine.consolidate import to_phases
from crengine.model_schemas import Finding, ScoredItem


class TestToPhases:
    """Tests for to_phases function."""

    def test_to_phases_security_routing(self):
        """Test that security findings route to Phase 1."""
        finding = Finding(
            tool="bandit", rule_id="B001", severity="HIGH",
            message="Security issue", file="a.py", tags=["security"]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=4.5,
            value_importance=4.8, est_hours=6.0
        )

        phases = to_phases([scored])

        assert len(phases["Phase 1 – Security & Safety"]) == 1
        assert phases["Phase 1 – Security & Safety"][0] == scored

    def test_to_phases_perf_routing(self):
        """Test that performance findings route to Phase 2."""
        finding = Finding(
            tool="pylint", rule_id="W001", severity="MEDIUM",
            message="Perf issue", file="b.py", tags=["perf"]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=3.0,
            value_importance=3.5, est_hours=4.0
        )

        phases = to_phases([scored])

        assert len(phases["Phase 2 – Reliability & Performance"]) == 1

    def test_to_phases_style_routing(self):
        """Test that style findings route to Phase 0."""
        finding = Finding(
            tool="flake8", rule_id="E501", severity="INFO",
            message="Line too long", file="c.py", tags=["style"]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=1.2,
            value_importance=1.5, est_hours=0.5
        )

        phases = to_phases([scored])

        assert len(phases["Phase 0 – Repo Hygiene"]) == 1

    def test_to_phases_default_routing(self):
        """Test that findings with no recognized tags route to Phase 3."""
        finding = Finding(
            tool="custom", rule_id="C001", severity="LOW",
            message="Generic issue", file="d.py", tags=["unknown"]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=2.0,
            value_importance=2.0, est_hours=2.0
        )

        phases = to_phases([scored])

        assert len(phases["Phase 3 – Developer Experience"]) == 1

    def test_to_phases_multiple_items(self):
        """Test routing multiple items to different phases."""
        items = [
            ScoredItem(
                finding=Finding(tool="bandit", rule_id="B001", severity="HIGH",
                              message="Security", file="a.py", tags=["security"]),
                difficulty_risk=4.0, value_importance=4.0, est_hours=6.0
            ),
            ScoredItem(
                finding=Finding(tool="flake8", rule_id="E501", severity="INFO",
                              message="Style", file="b.py", tags=["style"]),
                difficulty_risk=1.0, value_importance=1.0, est_hours=0.5
            ),
            ScoredItem(
                finding=Finding(tool="pylint", rule_id="W001", severity="MEDIUM",
                              message="Perf", file="c.py", tags=["perf"]),
                difficulty_risk=3.0, value_importance=3.0, est_hours=4.0
            ),
        ]

        phases = to_phases(items)

        assert len(phases["Phase 1 – Security & Safety"]) == 1
        assert len(phases["Phase 0 – Repo Hygiene"]) == 1
        assert len(phases["Phase 2 – Reliability & Performance"]) == 1

    def test_to_phases_all_phase_keys_present(self):
        """Test that all phase keys are present even when empty."""
        phases = to_phases([])

        expected_phases = [
            "Phase 0 – Repo Hygiene",
            "Phase 1 – Security & Safety",
            "Phase 2 – Reliability & Performance",
            "Phase 3 – Developer Experience",
            "Phase 4 – Product Polish"
        ]

        for phase_name in expected_phases:
            assert phase_name in phases
            assert isinstance(phases[phase_name], list)

    def test_to_phases_empty_list(self):
        """Test routing empty list."""
        phases = to_phases([])

        for phase_items in phases.values():
            assert len(phase_items) == 0

    def test_to_phases_priority_order(self):
        """Test that security tags take priority over other tags."""
        # Finding with both security and style tags
        finding = Finding(
            tool="semgrep", rule_id="S001", severity="HIGH",
            message="Issue", file="a.py", tags=["security", "style"]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=4.0,
            value_importance=4.0, est_hours=6.0
        )

        phases = to_phases([scored])

        # Should route to security phase (higher priority)
        assert len(phases["Phase 1 – Security & Safety"]) == 1
        assert len(phases["Phase 0 – Repo Hygiene"]) == 0

    def test_to_phases_perf_priority_over_style(self):
        """Test that perf tags take priority over style."""
        finding = Finding(
            tool="custom", rule_id="C001", severity="MEDIUM",
            message="Issue", file="a.py", tags=["perf", "style"]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=3.0,
            value_importance=3.0, est_hours=4.0
        )

        phases = to_phases([scored])

        assert len(phases["Phase 2 – Reliability & Performance"]) == 1
        assert len(phases["Phase 0 – Repo Hygiene"]) == 0

    def test_to_phases_no_tags_defaults_to_phase3(self):
        """Test that findings with empty tags go to Phase 3."""
        finding = Finding(
            tool="test", rule_id="T001", severity="MEDIUM",
            message="Issue", file="a.py", tags=[]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=2.0,
            value_importance=2.0, est_hours=2.0
        )

        phases = to_phases([scored])

        assert len(phases["Phase 3 – Developer Experience"]) == 1

    def test_to_phases_many_items_same_phase(self):
        """Test routing many items to the same phase."""
        items = [
            ScoredItem(
                finding=Finding(tool="bandit", rule_id=f"B00{i}", severity="HIGH",
                              message="Security", file=f"{i}.py", tags=["security"]),
                difficulty_risk=4.0, value_importance=4.0, est_hours=6.0
            )
            for i in range(10)
        ]

        phases = to_phases(items)

        assert len(phases["Phase 1 – Security & Safety"]) == 10

    def test_to_phases_preserves_scored_item_data(self):
        """Test that ScoredItem data is preserved during routing."""
        finding = Finding(
            tool="bandit", rule_id="B001", severity="HIGH",
            message="Security issue", file="test.py",
            line=42, col=10, tags=["security"]
        )
        scored = ScoredItem(
            finding=finding, difficulty_risk=4.5,
            value_importance=4.8, est_hours=6.0
        )

        phases = to_phases([scored])

        routed_item = phases["Phase 1 – Security & Safety"][0]
        assert routed_item.finding.line == 42
        assert routed_item.finding.col == 10
        assert routed_item.difficulty_risk == 4.5
        assert routed_item.value_importance == 4.8
        assert routed_item.est_hours == 6.0
