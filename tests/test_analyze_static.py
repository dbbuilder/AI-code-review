"""Unit tests for analyze_static.py - Static analysis tool adapters."""
import json
from pathlib import Path
from unittest.mock import Mock, patch
import subprocess

import pytest

from crengine.analyze_static import run_flake8, run_bandit, run_semgrep
from crengine.model_schemas import Finding


class TestRunFlake8:
    """Tests for run_flake8 function."""

    @patch("crengine.analyze_static.run_tool")
    def test_run_flake8_basic(self, mock_run_tool, mock_repo, config_files):
        """Test flake8 adapter with basic output."""
        mock_result = Mock()
        mock_result.stdout = "src/main.py::10::5::E501::line too long\nsrc/utils.py::3::1::F401::unused import"
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_flake8(mock_repo, config_files / "flake8.cfg")

        assert len(findings) == 2
        assert all(isinstance(f, Finding) for f in findings)
        assert findings[0].tool == "flake8"
        assert findings[0].rule_id == "E501"
        assert findings[0].severity == "INFO"
        assert findings[0].file == "src/main.py"
        assert findings[0].line == 10
        assert findings[0].col == 5

    @patch("crengine.analyze_static.run_tool")
    def test_run_flake8_no_findings(self, mock_run_tool, mock_repo, config_files):
        """Test flake8 with no issues found."""
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_flake8(mock_repo, config_files / "flake8.cfg")

        assert len(findings) == 0

    @patch("crengine.analyze_static.run_tool")
    def test_run_flake8_malformed_output(self, mock_run_tool, mock_repo, config_files):
        """Test flake8 gracefully handles malformed output."""
        mock_result = Mock()
        mock_result.stdout = "malformed line\nsrc/test.py::10::E501::msg"  # Missing column
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_flake8(mock_repo, config_files / "flake8.cfg")

        # Should skip malformed lines but continue
        assert isinstance(findings, list)

    @patch("crengine.analyze_static.run_tool")
    def test_run_flake8_tags(self, mock_run_tool, mock_repo, config_files):
        """Test that flake8 findings are tagged as 'style'."""
        mock_result = Mock()
        mock_result.stdout = "file.py::1::1::E501::line too long"
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_flake8(mock_repo, config_files / "flake8.cfg")

        assert "style" in findings[0].tags


class TestRunBandit:
    """Tests for run_bandit function."""

    @patch("crengine.analyze_static.run_tool")
    def test_run_bandit_basic(self, mock_run_tool, mock_repo, config_files):
        """Test bandit adapter with basic JSON output."""
        bandit_output = {
            "results": [
                {
                    "test_id": "B001",
                    "issue_severity": "HIGH",
                    "issue_text": "Use of eval() detected",
                    "filename": "src/main.py",
                    "line_number": 10
                }
            ]
        }
        mock_result = Mock()
        mock_result.stdout = json.dumps(bandit_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_bandit(mock_repo, config_files / "bandit.yaml")

        assert len(findings) == 1
        assert findings[0].tool == "bandit"
        assert findings[0].rule_id == "B001"
        assert findings[0].severity == "HIGH"
        assert findings[0].message == "Use of eval() detected"
        assert findings[0].file == "src/main.py"
        assert findings[0].line == 10
        assert findings[0].col is None

    @patch("crengine.analyze_static.run_tool")
    def test_run_bandit_security_tags(self, mock_run_tool, mock_repo, config_files):
        """Test that bandit findings are tagged with security."""
        bandit_output = {
            "results": [
                {
                    "test_id": "B105",
                    "issue_severity": "MEDIUM",
                    "issue_text": "Hardcoded password",
                    "filename": "config.py",
                    "line_number": 5
                }
            ]
        }
        mock_result = Mock()
        mock_result.stdout = json.dumps(bandit_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_bandit(mock_repo, config_files / "bandit.yaml")

        assert "security" in findings[0].tags
        assert "sast" in findings[0].tags

    @patch("crengine.analyze_static.run_tool")
    def test_run_bandit_no_findings(self, mock_run_tool, mock_repo, config_files):
        """Test bandit with no issues found."""
        bandit_output = {"results": []}
        mock_result = Mock()
        mock_result.stdout = json.dumps(bandit_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_bandit(mock_repo, config_files / "bandit.yaml")

        assert len(findings) == 0

    @patch("crengine.analyze_static.run_tool")
    def test_run_bandit_invalid_json(self, mock_run_tool, mock_repo, config_files):
        """Test bandit gracefully handles invalid JSON."""
        mock_result = Mock()
        mock_result.stdout = "not valid json"
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_bandit(mock_repo, config_files / "bandit.yaml")

        assert len(findings) == 0  # Should return empty list on parse error

    @patch("crengine.analyze_static.run_tool")
    def test_run_bandit_multiple_findings(self, mock_run_tool, mock_repo, config_files):
        """Test bandit with multiple findings."""
        bandit_output = {
            "results": [
                {"test_id": "B001", "issue_severity": "HIGH", "issue_text": "eval",
                 "filename": "a.py", "line_number": 1},
                {"test_id": "B002", "issue_severity": "MEDIUM", "issue_text": "exec",
                 "filename": "b.py", "line_number": 2},
                {"test_id": "B003", "issue_severity": "LOW", "issue_text": "pickle",
                 "filename": "c.py", "line_number": 3},
            ]
        }
        mock_result = Mock()
        mock_result.stdout = json.dumps(bandit_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_bandit(mock_repo, config_files / "bandit.yaml")

        assert len(findings) == 3
        assert [f.rule_id for f in findings] == ["B001", "B002", "B003"]


class TestRunSemgrep:
    """Tests for run_semgrep function."""

    @patch("crengine.analyze_static.run_tool")
    def test_run_semgrep_basic(self, mock_run_tool, mock_repo, config_files):
        """Test semgrep adapter with basic JSON output."""
        semgrep_output = {
            "results": [
                {
                    "check_id": "no-eval-python",
                    "path": "src/main.py",
                    "start": {"line": 10, "col": 5},
                    "extra": {
                        "severity": "ERROR",
                        "message": "Use of eval() is dangerous"
                    }
                }
            ]
        }
        mock_result = Mock()
        mock_result.stdout = json.dumps(semgrep_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_semgrep(mock_repo, config_files / "semgrep" / "rules.yaml")

        assert len(findings) == 1
        assert findings[0].tool == "semgrep"
        assert findings[0].rule_id == "no-eval-python"
        assert findings[0].severity == "ERROR"
        assert findings[0].message == "Use of eval() is dangerous"
        assert findings[0].file == "src/main.py"
        assert findings[0].line == 10
        assert findings[0].col == 5

    @patch("crengine.analyze_static.run_tool")
    def test_run_semgrep_security_tagging(self, mock_run_tool, mock_repo, config_files):
        """Test that security rules are tagged correctly."""
        semgrep_output = {
            "results": [
                {
                    "check_id": "python.security.sql-injection",
                    "path": "db.py",
                    "start": {"line": 5, "col": 1},
                    "extra": {"severity": "HIGH", "message": "SQL injection"}
                }
            ]
        }
        mock_result = Mock()
        mock_result.stdout = json.dumps(semgrep_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_semgrep(mock_repo, config_files / "semgrep" / "rules.yaml")

        assert "security" in findings[0].tags
        assert "pattern" in findings[0].tags

    @patch("crengine.analyze_static.run_tool")
    def test_run_semgrep_non_security_rule(self, mock_run_tool, mock_repo, config_files):
        """Test non-security rules are tagged as pattern only."""
        semgrep_output = {
            "results": [
                {
                    "check_id": "python.best-practices.no-print",
                    "path": "main.py",
                    "start": {"line": 1, "col": 1},
                    "extra": {"severity": "INFO", "message": "Avoid print statements"}
                }
            ]
        }
        mock_result = Mock()
        mock_result.stdout = json.dumps(semgrep_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_semgrep(mock_repo, config_files / "semgrep" / "rules.yaml")

        assert "pattern" in findings[0].tags
        assert "security" not in findings[0].tags

    @patch("crengine.analyze_static.run_tool")
    def test_run_semgrep_no_findings(self, mock_run_tool, mock_repo, config_files):
        """Test semgrep with no results."""
        semgrep_output = {"results": []}
        mock_result = Mock()
        mock_result.stdout = json.dumps(semgrep_output)
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_semgrep(mock_repo, config_files / "semgrep" / "rules.yaml")

        assert len(findings) == 0

    @patch("crengine.analyze_static.run_tool")
    def test_run_semgrep_invalid_json(self, mock_run_tool, mock_repo, config_files):
        """Test semgrep gracefully handles invalid JSON."""
        mock_result = Mock()
        mock_result.stdout = "invalid json output"
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        findings = run_semgrep(mock_repo, config_files / "semgrep" / "rules.yaml")

        assert len(findings) == 0
