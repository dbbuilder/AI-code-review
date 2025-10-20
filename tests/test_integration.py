"""Integration tests for the full code review pipeline."""
import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from crengine.main import run_full_pass, run_delta_pass


@pytest.mark.integration
class TestRunFullPass:
    """Integration tests for run_full_pass function."""

    @patch("crengine.main.run_flake8")
    @patch("crengine.main.run_bandit")
    @patch("crengine.main.run_semgrep")
    def test_run_full_pass_creates_all_outputs(
        self, mock_semgrep, mock_bandit, mock_flake8,
        mock_repo, config_files, temp_dir
    ):
        """Test that full pass creates all expected output files."""
        # Mock the static analysis tools to return empty findings
        mock_flake8.return_value = []
        mock_bandit.return_value = []
        mock_semgrep.return_value = []

        outputs_dir = temp_dir / "outputs"

        # Copy config files to mock_repo
        import shutil
        shutil.copytree(config_files, mock_repo / "config", dirs_exist_ok=True)

        run_full_pass(str(mock_repo), str(outputs_dir), ai_override="none")

        # Check that all expected outputs were created
        assert (outputs_dir / "000_manifest.json").exists()
        assert (outputs_dir / "010_static_findings.json").exists()
        assert (outputs_dir / "030_scores.json").exists()
        assert (outputs_dir / "040_recommendations.md").exists()
        assert (outputs_dir / "050_phased_plan.md").exists()

    @patch("crengine.main.run_flake8")
    @patch("crengine.main.run_bandit")
    @patch("crengine.main.run_semgrep")
    def test_run_full_pass_with_findings(
        self, mock_semgrep, mock_bandit, mock_flake8,
        mock_repo, config_files, temp_dir, sample_findings
    ):
        """Test full pass with actual findings."""
        # Mock tools to return sample findings
        mock_flake8.return_value = [sample_findings[1]]  # style finding
        mock_bandit.return_value = [sample_findings[0]]  # security finding
        mock_semgrep.return_value = [sample_findings[3]]  # security pattern

        outputs_dir = temp_dir / "outputs"

        # Copy config to mock_repo
        import shutil
        shutil.copytree(config_files, mock_repo / "config", dirs_exist_ok=True)

        run_full_pass(str(mock_repo), str(outputs_dir), ai_override="none")

        # Verify findings were processed
        findings_file = outputs_dir / "010_static_findings.json"
        findings_data = json.loads(findings_file.read_text())
        assert len(findings_data) == 3

        # Verify scores were generated
        scores_file = outputs_dir / "030_scores.json"
        scores_data = json.loads(scores_file.read_text())
        assert len(scores_data) == 3

    @patch("crengine.main.run_flake8")
    @patch("crengine.main.run_bandit")
    @patch("crengine.main.run_semgrep")
    def test_run_full_pass_manifest_content(
        self, mock_semgrep, mock_bandit, mock_flake8,
        mock_repo, config_files, temp_dir
    ):
        """Test that manifest contains expected repository info."""
        mock_flake8.return_value = []
        mock_bandit.return_value = []
        mock_semgrep.return_value = []

        outputs_dir = temp_dir / "outputs"

        import shutil
        shutil.copytree(config_files, mock_repo / "config", dirs_exist_ok=True)

        run_full_pass(str(mock_repo), str(outputs_dir), ai_override="none")

        manifest_file = outputs_dir / "000_manifest.json"
        manifest = json.loads(manifest_file.read_text())

        assert "repo_root" in manifest
        assert "commit" in manifest
        assert "files" in manifest
        assert len(manifest["commit"]) == 40  # Git SHA length

    @patch("crengine.main.run_flake8")
    @patch("crengine.main.run_bandit")
    @patch("crengine.main.run_semgrep")
    @patch("crengine.main.propose_patches")
    def test_run_full_pass_with_ai_provider(
        self, mock_propose, mock_semgrep, mock_bandit, mock_flake8,
        mock_repo, config_files, temp_dir, sample_findings
    ):
        """Test full pass with AI provider enabled."""
        mock_flake8.return_value = [sample_findings[0]]
        mock_bandit.return_value = []
        mock_semgrep.return_value = []
        mock_propose.return_value = ["patch suggestion 1"]

        outputs_dir = temp_dir / "outputs"

        import shutil
        shutil.copytree(config_files, mock_repo / "config", dirs_exist_ok=True)

        run_full_pass(str(mock_repo), str(outputs_dir), ai_override="openai")

        # Verify AI patch file was created
        ai_patches_file = outputs_dir / "060_ai_patch_suggestions.md"
        assert ai_patches_file.exists()

        content = ai_patches_file.read_text()
        assert "patch suggestion 1" in content

    @patch("crengine.main.run_flake8")
    @patch("crengine.main.run_bandit")
    @patch("crengine.main.run_semgrep")
    def test_run_full_pass_phased_plan_structure(
        self, mock_semgrep, mock_bandit, mock_flake8,
        mock_repo, config_files, temp_dir, sample_findings
    ):
        """Test that phased plan has correct structure."""
        mock_flake8.return_value = [sample_findings[1]]  # style
        mock_bandit.return_value = [sample_findings[0]]  # security
        mock_semgrep.return_value = []

        outputs_dir = temp_dir / "outputs"

        import shutil
        shutil.copytree(config_files, mock_repo / "config", dirs_exist_ok=True)

        run_full_pass(str(mock_repo), str(outputs_dir), ai_override="none")

        plan_file = outputs_dir / "050_phased_plan.md"
        content = plan_file.read_text()

        # Should contain phase headers
        assert "# Phased Improvement Plan" in content
        assert "Phase 0" in content or "Phase 1" in content


@pytest.mark.integration
class TestRunDeltaPass:
    """Integration tests for run_delta_pass function."""

    def test_run_delta_pass_creates_output(self, mock_repo, temp_dir):
        """Test that delta pass creates delta review output."""
        from git import Repo

        # Make a change
        repo = Repo(mock_repo)
        (mock_repo / "delta_test.py").write_text("# New change")
        repo.index.add(["delta_test.py"])
        repo.index.commit("Delta change")

        outputs_dir = temp_dir / "outputs"

        run_delta_pass(str(mock_repo), str(outputs_dir))

        # Verify delta output was created
        delta_file = outputs_dir / "070_delta_review.json"
        assert delta_file.exists()

        delta_data = json.loads(delta_file.read_text())
        assert "changed_files" in delta_data

    def test_run_delta_pass_detects_changes(self, mock_repo, temp_dir):
        """Test that delta pass detects file changes."""
        from git import Repo

        repo = Repo(mock_repo)
        test_file = mock_repo / "modified_file.py"
        test_file.write_text("original")
        repo.index.add(["modified_file.py"])
        repo.index.commit("Original")

        test_file.write_text("modified")
        repo.index.add(["modified_file.py"])
        repo.index.commit("Modified")

        outputs_dir = temp_dir / "outputs"

        run_delta_pass(str(mock_repo), str(outputs_dir))

        delta_file = outputs_dir / "070_delta_review.json"
        delta_data = json.loads(delta_file.read_text())

        assert "modified_file.py" in delta_data["changed_files"]


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndPipeline:
    """End-to-end tests simulating real usage."""

    @patch("crengine.analyze_static.run_tool")
    def test_end_to_end_no_issues(self, mock_run_tool, mock_repo, config_files, temp_dir):
        """Test complete pipeline with clean code (no issues)."""
        # Mock all tools to return no findings
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run_tool.return_value = mock_result

        outputs_dir = temp_dir / "outputs"

        import shutil
        shutil.copytree(config_files, mock_repo / "config", dirs_exist_ok=True)

        run_full_pass(str(mock_repo), str(outputs_dir), ai_override="none")

        # All files should exist
        assert (outputs_dir / "000_manifest.json").exists()
        assert (outputs_dir / "010_static_findings.json").exists()
        assert (outputs_dir / "030_scores.json").exists()
        assert (outputs_dir / "040_recommendations.md").exists()
        assert (outputs_dir / "050_phased_plan.md").exists()

        # Findings should be empty
        findings = json.loads((outputs_dir / "010_static_findings.json").read_text())
        assert len(findings) == 0

    @patch("crengine.analyze_static.run_tool")
    def test_end_to_end_with_issues(self, mock_run_tool, mock_repo, config_files, temp_dir):
        """Test complete pipeline with code issues."""
        # Mock flake8 to return a finding
        flake8_result = Mock()
        flake8_result.stdout = "src/main.py::10::5::E501::line too long"
        flake8_result.stderr = ""

        # Mock bandit to return a finding
        bandit_result = Mock()
        bandit_output = {
            "results": [{
                "test_id": "B001",
                "issue_severity": "HIGH",
                "issue_text": "eval() usage",
                "filename": "src/main.py",
                "line_number": 10
            }]
        }
        bandit_result.stdout = json.dumps(bandit_output)
        bandit_result.stderr = ""

        # Mock semgrep to return empty
        semgrep_result = Mock()
        semgrep_result.stdout = '{"results": []}'
        semgrep_result.stderr = ""

        # Return different results based on command
        def run_tool_side_effect(cmd):
            if "flake8" in cmd:
                return flake8_result
            elif "bandit" in cmd:
                return bandit_result
            elif "semgrep" in cmd:
                return semgrep_result
            return Mock(stdout="", stderr="")

        mock_run_tool.side_effect = run_tool_side_effect

        outputs_dir = temp_dir / "outputs"

        import shutil
        shutil.copytree(config_files, mock_repo / "config", dirs_exist_ok=True)

        run_full_pass(str(mock_repo), str(outputs_dir), ai_override="none")

        # Verify findings were detected
        findings = json.loads((outputs_dir / "010_static_findings.json").read_text())
        assert len(findings) >= 1

        # Verify scores were computed
        scores = json.loads((outputs_dir / "030_scores.json").read_text())
        assert len(scores) >= 1
        assert all("difficulty_risk" in s for s in scores)
        assert all("value_importance" in s for s in scores)
