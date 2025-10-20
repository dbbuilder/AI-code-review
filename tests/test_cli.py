"""Unit tests for cli.py - Command-line interface."""
import sys
from unittest.mock import patch, Mock

import pytest

from cli import main


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""

    @patch("cli.run_full_pass")
    def test_run_command_basic(self, mock_run_full_pass):
        """Test basic run command."""
        with patch.object(sys, "argv", ["crengine", "run", "--repo", "/repo", "--outputs", "/outputs"]):
            main()

        mock_run_full_pass.assert_called_once_with("/repo", "/outputs", ai_override=None)

    @patch("cli.run_full_pass")
    def test_run_command_with_openai(self, mock_run_full_pass):
        """Test run command with OpenAI provider."""
        with patch.object(sys, "argv", [
            "crengine", "run", "--repo", "/repo", "--outputs", "/outputs", "--ai", "openai"
        ]):
            main()

        mock_run_full_pass.assert_called_once_with("/repo", "/outputs", ai_override="openai")

    @patch("cli.run_full_pass")
    def test_run_command_with_anthropic(self, mock_run_full_pass):
        """Test run command with Anthropic provider."""
        with patch.object(sys, "argv", [
            "crengine", "run", "--repo", "/repo", "--outputs", "/outputs", "--ai", "anthropic"
        ]):
            main()

        mock_run_full_pass.assert_called_once_with("/repo", "/outputs", ai_override="anthropic")

    @patch("cli.run_full_pass")
    def test_run_command_with_gemini(self, mock_run_full_pass):
        """Test run command with Gemini provider."""
        with patch.object(sys, "argv", [
            "crengine", "run", "--repo", "/repo", "--outputs", "/outputs", "--ai", "gemini"
        ]):
            main()

        mock_run_full_pass.assert_called_once_with("/repo", "/outputs", ai_override="gemini")

    @patch("cli.run_full_pass")
    def test_run_command_with_none_ai(self, mock_run_full_pass):
        """Test run command with explicit 'none' AI provider."""
        with patch.object(sys, "argv", [
            "crengine", "run", "--repo", "/repo", "--outputs", "/outputs", "--ai", "none"
        ]):
            main()

        mock_run_full_pass.assert_called_once_with("/repo", "/outputs", ai_override="none")

    @patch("cli.run_delta_pass")
    def test_delta_command_basic(self, mock_run_delta_pass):
        """Test basic delta command."""
        with patch.object(sys, "argv", ["crengine", "delta", "--repo", "/repo", "--outputs", "/outputs"]):
            main()

        mock_run_delta_pass.assert_called_once_with("/repo", "/outputs")

    def test_missing_command(self):
        """Test that missing command shows error."""
        with patch.object(sys, "argv", ["crengine"]):
            with pytest.raises(SystemExit):
                main()

    def test_run_missing_repo_argument(self):
        """Test that missing --repo argument shows error."""
        with patch.object(sys, "argv", ["crengine", "run", "--outputs", "/outputs"]):
            with pytest.raises(SystemExit):
                main()

    def test_run_missing_outputs_argument(self):
        """Test that missing --outputs argument shows error."""
        with patch.object(sys, "argv", ["crengine", "run", "--repo", "/repo"]):
            with pytest.raises(SystemExit):
                main()

    def test_delta_missing_repo_argument(self):
        """Test that delta missing --repo shows error."""
        with patch.object(sys, "argv", ["crengine", "delta", "--outputs", "/outputs"]):
            with pytest.raises(SystemExit):
                main()

    def test_delta_missing_outputs_argument(self):
        """Test that delta missing --outputs shows error."""
        with patch.object(sys, "argv", ["crengine", "delta", "--repo", "/repo"]):
            with pytest.raises(SystemExit):
                main()

    def test_invalid_ai_provider(self):
        """Test that invalid AI provider shows error."""
        with patch.object(sys, "argv", [
            "crengine", "run", "--repo", "/repo", "--outputs", "/outputs", "--ai", "invalid"
        ]):
            with pytest.raises(SystemExit):
                main()

    def test_unknown_command(self):
        """Test that unknown command shows error."""
        with patch.object(sys, "argv", ["crengine", "unknown", "--repo", "/repo", "--outputs", "/outputs"]):
            with pytest.raises(SystemExit):
                main()


class TestCLIExecution:
    """Tests for CLI command execution."""

    @patch("cli.run_full_pass")
    def test_run_executes_full_pass(self, mock_run_full_pass, mock_repo, temp_dir):
        """Test that run command executes run_full_pass."""
        with patch.object(sys, "argv", [
            "crengine", "run", "--repo", str(mock_repo), "--outputs", str(temp_dir)
        ]):
            main()

        assert mock_run_full_pass.called
        assert mock_run_full_pass.call_args[0][0] == str(mock_repo)
        assert mock_run_full_pass.call_args[0][1] == str(temp_dir)

    @patch("cli.run_delta_pass")
    def test_delta_executes_delta_pass(self, mock_run_delta_pass, mock_repo, temp_dir):
        """Test that delta command executes run_delta_pass."""
        with patch.object(sys, "argv", [
            "crengine", "delta", "--repo", str(mock_repo), "--outputs", str(temp_dir)
        ]):
            main()

        assert mock_run_delta_pass.called
        assert mock_run_delta_pass.call_args[0][0] == str(mock_repo)
        assert mock_run_delta_pass.call_args[0][1] == str(temp_dir)

    @patch("cli.run_full_pass")
    def test_run_with_relative_paths(self, mock_run_full_pass):
        """Test run command with relative paths."""
        with patch.object(sys, "argv", [
            "crengine", "run", "--repo", ".", "--outputs", "./outputs"
        ]):
            main()

        mock_run_full_pass.assert_called_once()
        # Paths should be passed as-is (main.py handles path resolution)
        assert mock_run_full_pass.call_args[0][0] == "."
        assert mock_run_full_pass.call_args[0][1] == "./outputs"

    @patch("cli.run_full_pass")
    def test_ai_override_parameter_passed(self, mock_run_full_pass):
        """Test that ai_override parameter is correctly passed."""
        test_cases = [
            (None, None),
            ("openai", "openai"),
            ("anthropic", "anthropic"),
            ("gemini", "gemini"),
            ("none", "none"),
        ]

        for ai_arg, expected_override in test_cases:
            mock_run_full_pass.reset_mock()

            argv = ["crengine", "run", "--repo", "/repo", "--outputs", "/out"]
            if ai_arg:
                argv.extend(["--ai", ai_arg])

            with patch.object(sys, "argv", argv):
                main()

            assert mock_run_full_pass.call_args[1]["ai_override"] == expected_override


class TestCLIEdgeCases:
    """Tests for CLI edge cases and error handling."""

    def test_help_flag(self):
        """Test --help flag."""
        with patch.object(sys, "argv", ["crengine", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0  # Help should exit with code 0

    def test_run_help(self):
        """Test run --help."""
        with patch.object(sys, "argv", ["crengine", "run", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_delta_help(self):
        """Test delta --help."""
        with patch.object(sys, "argv", ["crengine", "delta", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    @patch("cli.run_full_pass")
    def test_run_with_special_characters_in_paths(self, mock_run_full_pass):
        """Test handling paths with spaces and special characters."""
        with patch.object(sys, "argv", [
            "crengine", "run",
            "--repo", "/path/with spaces/repo",
            "--outputs", "/path/with-special_chars/outputs"
        ]):
            main()

        assert mock_run_full_pass.called
        assert mock_run_full_pass.call_args[0][0] == "/path/with spaces/repo"
        assert mock_run_full_pass.call_args[0][1] == "/path/with-special_chars/outputs"

    @patch("cli.run_full_pass")
    def test_arguments_order_independence(self, mock_run_full_pass):
        """Test that argument order doesn't matter."""
        # Test different argument orders
        orders = [
            ["crengine", "run", "--repo", "/r", "--outputs", "/o", "--ai", "openai"],
            ["crengine", "run", "--outputs", "/o", "--repo", "/r", "--ai", "openai"],
            ["crengine", "run", "--ai", "openai", "--repo", "/r", "--outputs", "/o"],
        ]

        for argv in orders:
            mock_run_full_pass.reset_mock()
            with patch.object(sys, "argv", argv):
                main()

            assert mock_run_full_pass.called
            assert mock_run_full_pass.call_args[0][0] == "/r"
            assert mock_run_full_pass.call_args[0][1] == "/o"
            assert mock_run_full_pass.call_args[1]["ai_override"] == "openai"
