"""Tests for enhanced AI prompt generation with context."""
import pytest
from pathlib import Path
from crengine.prompt_generation import (
    load_prompt_templates,
    extract_file_context,
    generate_patch_prompt,
    select_template_for_finding
)
from crengine.model_schemas import Finding, ScoredItem


class TestLoadPromptTemplates:
    """Test loading prompt templates from YAML."""

    def test_load_prompt_templates_success(self):
        """Test loading templates from config file."""
        templates = load_prompt_templates()

        assert templates is not None
        assert 'system_prompt' in templates
        assert 'patch_template' in templates
        assert 'context_lines' in templates
        assert templates['context_lines'] == 5

    def test_load_prompt_templates_has_security_template(self):
        """Test that security-specific template exists."""
        templates = load_prompt_templates()

        assert 'security_patch_template' in templates
        assert 'SECURITY' in templates['security_patch_template']

    def test_load_prompt_templates_has_performance_template(self):
        """Test that performance-specific template exists."""
        templates = load_prompt_templates()

        assert 'performance_patch_template' in templates
        assert 'PERFORMANCE' in templates['performance_patch_template']


class TestExtractFileContext:
    """Test extracting surrounding lines from source files."""

    def test_extract_context_simple_file(self, temp_dir):
        """Test extracting context from a simple file."""
        test_file = temp_dir / "simple.py"
        test_file.write_text("""line 1
line 2
line 3
line 4
line 5
line 6
line 7
line 8
line 9
line 10""")

        # Extract context around line 5
        context = extract_file_context(test_file, line_num=5, context_lines=2)

        assert context['target_line'] == 'line 5'
        assert len(context['before']) == 2
        assert context['before'] == ['line 3', 'line 4']
        assert len(context['after']) == 2
        assert context['after'] == ['line 6', 'line 7']

    def test_extract_context_beginning_of_file(self, temp_dir):
        """Test extracting context at beginning of file."""
        test_file = temp_dir / "begin.py"
        test_file.write_text("""line 1
line 2
line 3
line 4
line 5""")

        context = extract_file_context(test_file, line_num=1, context_lines=3)

        assert context['target_line'] == 'line 1'
        assert context['before'] == []  # No lines before first line
        assert len(context['after']) == 3
        assert context['after'] == ['line 2', 'line 3', 'line 4']

    def test_extract_context_end_of_file(self, temp_dir):
        """Test extracting context at end of file."""
        test_file = temp_dir / "end.py"
        test_file.write_text("""line 1
line 2
line 3
line 4
line 5""")

        context = extract_file_context(test_file, line_num=5, context_lines=3)

        assert context['target_line'] == 'line 5'
        assert len(context['before']) == 3
        assert context['before'] == ['line 2', 'line 3', 'line 4']
        assert context['after'] == []  # No lines after last line

    def test_extract_context_with_line_numbers(self, temp_dir):
        """Test that context includes line numbers."""
        test_file = temp_dir / "numbered.py"
        test_file.write_text("""def foo():
    x = 1
    y = 2
    return x + y""")

        context = extract_file_context(test_file, line_num=2, context_lines=1, include_line_numbers=True)

        # Check full context includes line numbers (format is "   1  def foo():")
        full_context = context['full_context']
        assert '1' in full_context  # Line number present
        assert 'def foo()' in full_context
        assert '→' in full_context  # Target line marker

    def test_extract_context_nonexistent_file(self, temp_dir):
        """Test handling of nonexistent file."""
        nonexistent = temp_dir / "does_not_exist.py"

        context = extract_file_context(nonexistent, line_num=1, context_lines=3)

        assert context['target_line'] == ''
        assert context['before'] == []
        assert context['after'] == []
        assert 'File not found' in context['full_context']


class TestSelectTemplateForFinding:
    """Test template selection based on finding properties."""

    def test_select_security_template(self):
        """Test that security findings get security template."""
        finding = Finding(
            tool="bandit",
            rule_id="B602",
            severity="HIGH",
            message="subprocess with shell=True",
            file="test.py",
            line=10,
            tags=["security"]
        )

        templates = load_prompt_templates()
        selected = select_template_for_finding(finding, templates)

        assert 'SECURITY' in selected
        assert 'vulnerability' in selected.lower()

    def test_select_performance_template(self):
        """Test that performance findings get performance template."""
        finding = Finding(
            tool="pylint",
            rule_id="W0101",
            severity="MEDIUM",
            message="Inefficient loop",
            file="test.py",
            line=20,
            tags=["perf"]
        )

        templates = load_prompt_templates()
        selected = select_template_for_finding(finding, templates)

        assert 'PERFORMANCE' in selected
        assert 'optimize' in selected.lower() or 'optimization' in selected.lower()

    def test_select_default_template(self):
        """Test that non-specific findings get default template."""
        finding = Finding(
            tool="flake8",
            rule_id="E501",
            severity="INFO",
            message="Line too long",
            file="test.py",
            line=30,
            tags=["style"]
        )

        templates = load_prompt_templates()
        selected = select_template_for_finding(finding, templates)

        # Should get patch_template (default)
        assert 'Fix the following code quality issue' in selected


class TestGeneratePatchPrompt:
    """Test complete prompt generation."""

    def test_generate_basic_prompt(self, temp_dir):
        """Test generating a basic patch prompt."""
        # Create test file
        test_file = temp_dir / "example.py"
        test_file.write_text("""import os
import sys

def bad_function():
    eval("print('unsafe')")
    return True""")

        finding = Finding(
            tool="bandit",
            rule_id="B307",
            severity="HIGH",
            message="Use of eval() is dangerous",
            file=str(test_file),
            line=5,
            tags=["security"]
        )

        prompt = generate_patch_prompt(finding, context_lines=2)

        # Check prompt contains key elements
        assert 'example.py' in prompt
        assert 'B307' in prompt
        assert 'eval() is dangerous' in prompt
        assert 'def bad_function()' in prompt  # Context
        assert 'eval("print' in prompt  # Target line
        assert 'unified diff' in prompt.lower()

    def test_generate_prompt_with_scored_item(self, temp_dir):
        """Test generating prompt with ScoredItem (includes value/difficulty scores)."""
        test_file = temp_dir / "scored.py"
        test_file.write_text("""x = 1
y = 2
result = x+y  # No spaces
print(result)""")

        finding = Finding(
            tool="flake8",
            rule_id="E226",
            severity="INFO",
            message="Missing whitespace around operator",
            file=str(test_file),
            line=3,
            tags=["style"]
        )

        scored = ScoredItem(
            finding=finding,
            difficulty_risk=1.5,
            value_importance=2.0,
            est_hours=0.1
        )

        prompt = generate_patch_prompt(scored.finding, context_lines=1)

        assert 'E226' in prompt
        assert 'whitespace' in prompt.lower()
        assert 'x+y' in prompt

    def test_generate_prompt_includes_system_prompt(self, temp_dir):
        """Test that generated prompts include system-level instructions."""
        test_file = temp_dir / "sys.py"
        test_file.write_text("x = 1\n")

        finding = Finding(
            tool="test", rule_id="T1", severity="LOW",
            message="test", file=str(test_file), line=1, tags=[]
        )

        prompt = generate_patch_prompt(finding, include_system_prompt=True)

        assert 'expert code reviewer' in prompt.lower()
        assert 'preserve existing behavior' in prompt.lower()

    def test_generate_prompt_without_system_prompt(self, temp_dir):
        """Test generating prompt without system instructions."""
        test_file = temp_dir / "nosys.py"
        test_file.write_text("x = 1\n")

        finding = Finding(
            tool="test", rule_id="T1", severity="LOW",
            message="test", file=str(test_file), line=1, tags=[]
        )

        prompt = generate_patch_prompt(finding, include_system_prompt=False)

        # Should NOT include system prompt
        assert 'expert code reviewer' not in prompt.lower()
        # But should still have the main prompt
        assert 'Fix the following' in prompt

    def test_generate_prompt_handles_missing_file(self):
        """Test that prompt generation handles missing source files gracefully."""
        finding = Finding(
            tool="test",
            rule_id="T1",
            severity="MEDIUM",
            message="Test issue",
            file="/nonexistent/file.py",
            line=10,
            tags=[]
        )

        prompt = generate_patch_prompt(finding, context_lines=3)

        # Should still generate a prompt
        assert 'nonexistent/file.py' in prompt
        assert 'T1' in prompt
        # Should indicate file not available
        assert 'not found' in prompt.lower() or 'not available' in prompt.lower()


class TestPromptVariableSubstitution:
    """Test that template variables are properly substituted."""

    def test_all_variables_substituted(self, temp_dir):
        """Test that all template variables get substituted."""
        test_file = temp_dir / "vars.py"
        test_file.write_text("""line 1
line 2
line 3
line 4
line 5""")

        finding = Finding(
            tool="test_tool",
            rule_id="TEST123",
            severity="HIGH",
            message="Test message",
            file=str(test_file),
            line=3,
            tags=["test"]
        )

        prompt = generate_patch_prompt(finding, context_lines=1)

        # Check all variables were replaced
        assert '{file}' not in prompt
        assert '{line}' not in prompt
        assert '{tool}' not in prompt
        assert '{rule_id}' not in prompt
        assert '{message}' not in prompt
        assert '{severity}' not in prompt

        # Check actual values present
        assert 'vars.py' in prompt
        assert '3' in prompt
        assert 'test_tool' in prompt
        assert 'TEST123' in prompt
        assert 'Test message' in prompt
        assert 'HIGH' in prompt
