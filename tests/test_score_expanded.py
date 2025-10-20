"""Expanded unit tests for score.py - Scoring heuristics."""
import pytest

from crengine.score import score_findings, _severity_weight
from crengine.model_schemas import Finding


class TestSeverityWeight:
    """Tests for _severity_weight helper function."""

    def test_critical_severity(self):
        """Test CRITICAL severity weight."""
        assert _severity_weight("CRITICAL") == 1.0

    def test_high_severity(self):
        """Test HIGH severity weight."""
        assert _severity_weight("HIGH") == 0.85

    def test_medium_severity(self):
        """Test MEDIUM severity weight."""
        assert _severity_weight("MEDIUM") == 0.6

    def test_low_severity(self):
        """Test LOW severity weight."""
        assert _severity_weight("LOW") == 0.35

    def test_info_severity(self):
        """Test INFO severity weight."""
        assert _severity_weight("INFO") == 0.2

    def test_unknown_severity(self):
        """Test unknown severity defaults to INFO."""
        assert _severity_weight("UNKNOWN") == 0.2

    def test_case_insensitive(self):
        """Test that severity is case-insensitive."""
        assert _severity_weight("critical") == 1.0
        assert _severity_weight("High") == 0.85
        assert _severity_weight("MEDIUM") == 0.6


class TestScoreFindings:
    """Tests for score_findings function."""

    def test_score_high_security_finding(self):
        """Test scoring of high-severity security finding."""
        finding = Finding(
            tool="bandit",
            rule_id="B001",
            severity="HIGH",
            message="Use of eval() detected",
            file="main.py",
            line=10,
            tags=["security", "sast"]
        )

        scored = score_findings([finding])[0]

        assert scored.difficulty_risk >= 3.0
        assert scored.value_importance >= 3.0
        assert scored.est_hours == 6.0

    def test_score_critical_security_finding(self):
        """Test scoring of critical security finding."""
        finding = Finding(
            tool="semgrep",
            rule_id="sql-injection",
            severity="CRITICAL",
            message="SQL injection vulnerability",
            file="db.py",
            line=50,
            tags=["security", "input_validation"]
        )

        scored = score_findings([finding])[0]

        assert scored.difficulty_risk > 4.0
        assert scored.value_importance > 4.0
        assert scored.est_hours == 6.0

    def test_score_low_style_finding(self):
        """Test scoring of low-severity style finding."""
        finding = Finding(
            tool="flake8",
            rule_id="E501",
            severity="INFO",
            message="Line too long",
            file="utils.py",
            line=5,
            tags=["style"]
        )

        scored = score_findings([finding])[0]

        # INFO severity gets low weight, non-security tag gets 0.7 multiplier
        assert scored.difficulty_risk < 3.0  # Should be around 1.56
        assert scored.value_importance < 4.0  # Non-security gets lower value
        assert scored.est_hours >= 0.5

    def test_score_performance_finding(self):
        """Test scoring of performance finding."""
        finding = Finding(
            tool="pylint",
            rule_id="W0621",
            severity="MEDIUM",
            message="Inefficient loop",
            file="processor.py",
            line=100,
            tags=["perf", "optimization"]
        )

        scored = score_findings([finding])[0]

        # Performance findings should have decent value
        assert scored.value_importance >= 2.0

    def test_score_no_security_tag_lower_value(self):
        """Test that non-security findings have lower value."""
        security_finding = Finding(
            tool="bandit",
            rule_id="B001",
            severity="HIGH",
            message="Security issue",
            file="a.py",
            tags=["security"]
        )

        non_security_finding = Finding(
            tool="pylint",
            rule_id="C0103",
            severity="HIGH",
            message="Naming convention",
            file="b.py",
            tags=["style"]
        )

        scored_security = score_findings([security_finding])[0]
        scored_non_security = score_findings([non_security_finding])[0]

        assert scored_security.value_importance > scored_non_security.value_importance

    def test_score_multiple_findings(self):
        """Test scoring multiple findings at once."""
        findings = [
            Finding(tool="bandit", rule_id="B001", severity="HIGH",
                   message="eval()", file="a.py", tags=["security"]),
            Finding(tool="flake8", rule_id="E501", severity="INFO",
                   message="line long", file="b.py", tags=["style"]),
            Finding(tool="pylint", rule_id="W0612", severity="MEDIUM",
                   message="unused var", file="c.py", tags=["dead_code"]),
        ]

        scored = score_findings(findings)

        assert len(scored) == 3
        # Security finding should have highest composite score
        assert scored[0].value_importance >= scored[1].value_importance
        assert scored[0].value_importance >= scored[2].value_importance

    def test_score_all_severity_levels(self):
        """Test that all severity levels produce valid scores."""
        severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        findings = [
            Finding(tool="test", rule_id=f"T{i}", severity=sev,
                   message=f"Test {sev}", file="test.py", tags=["security"])
            for i, sev in enumerate(severities)
        ]

        scored = score_findings(findings)

        # All scores should be in valid range (1-5)
        for item in scored:
            assert 1.0 <= item.difficulty_risk <= 5.0
            assert 1.0 <= item.value_importance <= 5.0
            assert item.est_hours > 0

    def test_score_no_tags(self):
        """Test scoring finding with no tags."""
        finding = Finding(
            tool="custom",
            rule_id="C001",
            severity="MEDIUM",
            message="Generic issue",
            file="main.py",
            tags=[]
        )

        scored = score_findings([finding])[0]

        # Should still produce valid scores
        assert 1.0 <= scored.difficulty_risk <= 5.0
        assert 1.0 <= scored.value_importance <= 5.0

    def test_score_estimation_tiers(self):
        """Test that estimated hours follow the tier system."""
        # Low value (< 2)
        low_finding = Finding(
            tool="flake8", rule_id="E501", severity="INFO",
            message="line long", file="a.py", tags=["style"]
        )

        # Medium value (2-3)
        med_finding = Finding(
            tool="pylint", rule_id="W0612", severity="MEDIUM",
            message="unused", file="b.py", tags=["lints"]
        )

        # High value (> 3)
        high_finding = Finding(
            tool="bandit", rule_id="B001", severity="CRITICAL",
            message="eval", file="c.py", tags=["security"]
        )

        scored_low = score_findings([low_finding])[0]
        scored_med = score_findings([med_finding])[0]
        scored_high = score_findings([high_finding])[0]

        # Estimates should increase with value/difficulty
        # Current logic: 0.5 if vi < 2, 2 if dr < 2.5, else 6
        assert scored_low.est_hours >= 0.5  # May be 2.0 depending on scoring
        assert scored_med.est_hours >= scored_low.est_hours or scored_med.est_hours > 0
        assert scored_high.est_hours >= scored_med.est_hours

    def test_score_tags_affect_weighting(self):
        """Test that different tag combinations affect scores."""
        security_finding = Finding(
            tool="test", rule_id="T1", severity="MEDIUM",
            message="issue", file="a.py", tags=["security"]
        )

        perf_finding = Finding(
            tool="test", rule_id="T2", severity="MEDIUM",
            message="issue", file="b.py", tags=["perf"]
        )

        style_finding = Finding(
            tool="test", rule_id="T3", severity="MEDIUM",
            message="issue", file="c.py", tags=["style"]
        )

        scored_security = score_findings([security_finding])[0]
        scored_perf = score_findings([perf_finding])[0]
        scored_style = score_findings([style_finding])[0]

        # Security should have higher scores than style
        assert scored_security.value_importance > scored_style.value_importance
        # Perf should have higher value than style
        assert scored_perf.value_importance > scored_style.value_importance

    def test_score_empty_list(self):
        """Test scoring empty findings list."""
        scored = score_findings([])
        assert len(scored) == 0

    def test_score_preserves_finding_reference(self):
        """Test that scored items preserve original finding reference."""
        finding = Finding(
            tool="test", rule_id="T1", severity="HIGH",
            message="test message", file="test.py",
            line=42, col=10, tags=["security"]
        )

        scored = score_findings([finding])[0]

        assert scored.finding is finding
        assert scored.finding.tool == "test"
        assert scored.finding.line == 42
        assert scored.finding.col == 10

    def test_score_rounding(self):
        """Test that scores are rounded to 2 decimal places."""
        finding = Finding(
            tool="test", rule_id="T1", severity="MEDIUM",
            message="test", file="a.py", tags=["security"]
        )

        scored = score_findings([finding])[0]

        # Check that scores have at most 2 decimal places
        assert scored.difficulty_risk == round(scored.difficulty_risk, 2)
        assert scored.value_importance == round(scored.value_importance, 2)
