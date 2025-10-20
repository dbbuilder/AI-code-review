"""Unit tests for config-driven scoring in score.py."""
import pytest
import yaml

from crengine.score import score_findings_from_config, _severity_weight
from crengine.model_schemas import Finding


class TestScoreFindingsFromConfig:
    """Tests for config-driven scoring."""

    def test_score_with_custom_weights(self, temp_dir):
        """Test scoring with custom weight configuration."""
        config_yaml = """
scoring:
  difficulty_weights:
    code_complexity: 0.25
    coupling_blastradius: 0.25
    test_coverage_gap: 0.25
    tooling_fixability: 0.25
  value_weights:
    security_severity: 0.50
    reliability_perf: 0.30
    developer_experience: 0.10
    user_value: 0.10
  scale: 1-5
"""
        config_file = temp_dir / "scoring_config.yaml"
        config_file.write_text(config_yaml)
        config = yaml.safe_load(config_file.read_text())

        finding = Finding(
            tool="bandit", rule_id="B001", severity="HIGH",
            message="Security issue", file="a.py", tags=["security"]
        )

        scored = score_findings_from_config([finding], config["scoring"])

        assert len(scored) == 1
        assert scored[0].difficulty_risk >= 1.0
        assert scored[0].value_importance >= 1.0
        assert scored[0].est_hours > 0

    def test_security_findings_get_higher_value(self, temp_dir):
        """Test that security findings get higher value scores."""
        config_yaml = """
scoring:
  difficulty_weights:
    code_complexity: 0.25
    coupling_blastradius: 0.25
    test_coverage_gap: 0.25
    tooling_fixability: 0.25
  value_weights:
    security_severity: 0.70
    reliability_perf: 0.15
    developer_experience: 0.10
    user_value: 0.05
  scale: 1-5
"""
        config = yaml.safe_load(config_yaml)

        security_finding = Finding(
            tool="bandit", rule_id="B001", severity="HIGH",
            message="eval", file="a.py", tags=["security"]
        )
        style_finding = Finding(
            tool="flake8", rule_id="E501", severity="INFO",
            message="line long", file="b.py", tags=["style"]
        )

        scored = score_findings_from_config(
            [security_finding, style_finding],
            config["scoring"]
        )

        security_score = next(s for s in scored if "security" in s.finding.tags)
        style_score = next(s for s in scored if "style" in s.finding.tags)

        # Security should have higher value due to higher weight
        assert security_score.value_importance > style_score.value_importance

    def test_scores_within_configured_scale(self, temp_dir):
        """Test that scores respect the configured scale (1-5)."""
        config_yaml = """
scoring:
  difficulty_weights:
    code_complexity: 0.25
    coupling_blastradius: 0.25
    test_coverage_gap: 0.25
    tooling_fixability: 0.25
  value_weights:
    security_severity: 0.25
    reliability_perf: 0.25
    developer_experience: 0.25
    user_value: 0.25
  scale: 1-5
"""
        config = yaml.safe_load(config_yaml)

        findings = [
            Finding(tool="test", rule_id=f"T{i}", severity=sev, message="msg",
                   file="f.py", tags=["test"])
            for i, sev in enumerate(["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"])
        ]

        scored = score_findings_from_config(findings, config["scoring"])

        for item in scored:
            assert 1.0 <= item.difficulty_risk <= 5.0
            assert 1.0 <= item.value_importance <= 5.0

    def test_weights_sum_validation(self, temp_dir):
        """Test that weights should sum to 1.0 (warning if not)."""
        config_yaml = """
scoring:
  difficulty_weights:
    code_complexity: 0.50
    coupling_blastradius: 0.30
    test_coverage_gap: 0.10
    tooling_fixability: 0.05  # Sums to 0.95, not 1.0
  value_weights:
    security_severity: 0.25
    reliability_perf: 0.25
    developer_experience: 0.25
    user_value: 0.25
  scale: 1-5
"""
        config = yaml.safe_load(config_yaml)

        finding = Finding(
            tool="test", rule_id="T1", severity="MEDIUM",
            message="msg", file="a.py", tags=["test"]
        )

        # Should still work, but might log warning
        scored = score_findings_from_config([finding], config["scoring"])
        assert len(scored) == 1

    def test_severity_impact_on_scores(self, temp_dir):
        """Test that severity levels impact scores appropriately."""
        config_yaml = """
scoring:
  difficulty_weights:
    code_complexity: 0.25
    coupling_blastradius: 0.25
    test_coverage_gap: 0.25
    tooling_fixability: 0.25
  value_weights:
    security_severity: 0.40
    reliability_perf: 0.30
    developer_experience: 0.20
    user_value: 0.10
  scale: 1-5
"""
        config = yaml.safe_load(config_yaml)

        critical = Finding(
            tool="t", rule_id="T1", severity="CRITICAL",
            message="msg", file="a.py", tags=["security"]
        )
        info = Finding(
            tool="t", rule_id="T2", severity="INFO",
            message="msg", file="b.py", tags=["security"]
        )

        scored = score_findings_from_config([critical, info], config["scoring"])

        critical_score = next(s for s in scored if s.finding.severity == "CRITICAL")
        info_score = next(s for s in scored if s.finding.severity == "INFO")

        # CRITICAL should score higher than INFO
        assert critical_score.difficulty_risk > info_score.difficulty_risk
        assert critical_score.value_importance > info_score.value_importance

    def test_estimation_based_on_scores(self, temp_dir):
        """Test that hour estimates are based on scores."""
        config_yaml = """
scoring:
  difficulty_weights:
    code_complexity: 0.25
    coupling_blastradius: 0.25
    test_coverage_gap: 0.25
    tooling_fixability: 0.25
  value_weights:
    security_severity: 0.40
    reliability_perf: 0.30
    developer_experience: 0.20
    user_value: 0.10
  scale: 1-5
"""
        config = yaml.safe_load(config_yaml)

        # High severity = more hours
        high_sev = Finding(
            tool="t", rule_id="T1", severity="CRITICAL",
            message="msg", file="a.py", tags=["security"]
        )
        # Low severity = fewer hours
        low_sev = Finding(
            tool="t", rule_id="T2", severity="INFO",
            message="msg", file="b.py", tags=["style"]
        )

        scored = score_findings_from_config([high_sev, low_sev], config["scoring"])

        high_score = next(s for s in scored if s.finding.severity == "CRITICAL")
        low_score = next(s for s in scored if s.finding.severity == "INFO")

        # Higher scores should generally mean more hours
        assert high_score.est_hours >= low_score.est_hours

    def test_tag_based_value_adjustment(self, temp_dir):
        """Test that different tags affect value scores differently."""
        config_yaml = """
scoring:
  difficulty_weights:
    code_complexity: 0.25
    coupling_blastradius: 0.25
    test_coverage_gap: 0.25
    tooling_fixability: 0.25
  value_weights:
    security_severity: 0.60
    reliability_perf: 0.25
    developer_experience: 0.10
    user_value: 0.05
  scale: 1-5
"""
        config = yaml.safe_load(config_yaml)

        security = Finding(
            tool="t", rule_id="T1", severity="MEDIUM",
            message="msg", file="a.py", tags=["security"]
        )
        perf = Finding(
            tool="t", rule_id="T2", severity="MEDIUM",
            message="msg", file="b.py", tags=["perf"]
        )
        style = Finding(
            tool="t", rule_id="T3", severity="MEDIUM",
            message="msg", file="c.py", tags=["style"]
        )

        scored = score_findings_from_config([security, perf, style], config["scoring"])

        sec_score = next(s for s in scored if "security" in s.finding.tags)
        perf_score = next(s for s in scored if "perf" in s.finding.tags)
        style_score = next(s for s in scored if "style" in s.finding.tags)

        # With security_severity weight at 0.60, security should score highest
        assert sec_score.value_importance >= perf_score.value_importance
        assert perf_score.value_importance >= style_score.value_importance

    def test_empty_config_uses_defaults(self, temp_dir):
        """Test that empty config uses sensible defaults."""
        config = {"scoring": {}}

        finding = Finding(
            tool="test", rule_id="T1", severity="MEDIUM",
            message="msg", file="a.py", tags=["test"]
        )

        scored = score_findings_from_config([finding], config["scoring"])

        assert len(scored) == 1
        assert 1.0 <= scored[0].difficulty_risk <= 5.0
        assert 1.0 <= scored[0].value_importance <= 5.0
