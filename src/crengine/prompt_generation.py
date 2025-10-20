"""Enhanced AI prompt generation with file context and templates."""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from .model_schemas import Finding


def load_prompt_templates(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load prompt templates from YAML configuration.

    Args:
        config_path: Path to prompts config file. Defaults to config/prompts/patch_generation.yaml

    Returns:
        Dictionary containing template strings and configuration
    """
    if config_path is None:
        # Default to config/prompts/patch_generation.yaml relative to repo root
        config_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "patch_generation.yaml"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        return templates
    except FileNotFoundError:
        # Return minimal defaults if config not found
        return {
            'system_prompt': 'You are an expert code reviewer.',
            'patch_template': 'Fix: {message}\nFile: {file}\nLine: {line}',
            'context_lines': 5
        }


def extract_file_context(
    file_path: Path,
    line_num: int,
    context_lines: int = 5,
    include_line_numbers: bool = True
) -> Dict[str, Any]:
    """
    Extract surrounding lines from a source file.

    Args:
        file_path: Path to source file
        line_num: Target line number (1-indexed)
        context_lines: Number of lines before/after to include
        include_line_numbers: Whether to include line numbers in output

    Returns:
        Dictionary with:
        - target_line: The line at line_num
        - before: List of lines before target
        - after: List of lines after target
        - full_context: Formatted string with all context
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {
            'target_line': '',
            'before': [],
            'after': [],
            'full_context': f'File not found: {file_path}'
        }
    except Exception as e:
        return {
            'target_line': '',
            'before': [],
            'after': [],
            'full_context': f'Error reading file: {e}'
        }

    # Convert to 0-indexed
    target_idx = line_num - 1

    if target_idx < 0 or target_idx >= len(lines):
        return {
            'target_line': '',
            'before': [],
            'after': [],
            'full_context': f'Line {line_num} out of range (file has {len(lines)} lines)'
        }

    # Extract target line (remove trailing newline)
    target_line = lines[target_idx].rstrip('\n')

    # Extract before/after context
    start_idx = max(0, target_idx - context_lines)
    end_idx = min(len(lines), target_idx + context_lines + 1)

    before_lines = [line.rstrip('\n') for line in lines[start_idx:target_idx]]
    after_lines = [line.rstrip('\n') for line in lines[target_idx + 1:end_idx]]

    # Build full context string
    if include_line_numbers:
        full_context_lines = []
        for i in range(start_idx, end_idx):
            line_content = lines[i].rstrip('\n')
            marker = '→' if i == target_idx else ' '
            full_context_lines.append(f"{i+1:4d}{marker} {line_content}")
        full_context = '\n'.join(full_context_lines)
    else:
        full_context = '\n'.join(lines[start_idx:end_idx])

    return {
        'target_line': target_line,
        'before': before_lines,
        'after': after_lines,
        'full_context': full_context
    }


def select_template_for_finding(finding: Finding, templates: Dict[str, Any]) -> str:
    """
    Select appropriate template based on finding properties.

    Args:
        finding: The code issue to fix
        templates: Loaded template dictionary

    Returns:
        Template string to use for this finding
    """
    tags = [tag.lower() for tag in finding.tags]

    # Security issues get special template
    if 'security' in tags or 'secrets' in tags or 'sast' in tags:
        if 'security_patch_template' in templates:
            return templates['security_patch_template']

    # Performance issues get optimization template
    if 'perf' in tags or 'performance' in tags:
        if 'performance_patch_template' in templates:
            return templates['performance_patch_template']

    # Default to general patch template
    return templates.get('patch_template', 'Fix: {message}')


def generate_patch_prompt(
    finding: Finding,
    context_lines: int = 5,
    include_system_prompt: bool = False,
    templates: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate enhanced patch prompt with file context.

    Args:
        finding: Code issue to fix
        context_lines: Number of context lines before/after
        include_system_prompt: Whether to prepend system-level instructions
        templates: Pre-loaded templates (loads default if None)

    Returns:
        Complete prompt string ready for AI model
    """
    if templates is None:
        templates = load_prompt_templates()

    # Get file context
    file_path = Path(finding.file)
    line_num = finding.line if finding.line else 1

    # Use configured context_lines if not overridden
    if context_lines is None:
        context_lines = templates.get('context_lines', 5)

    context = extract_file_context(file_path, line_num, context_lines, include_line_numbers=True)

    # Select appropriate template
    template = select_template_for_finding(finding, templates)

    # Substitute template variables
    prompt = template.format(
        file=finding.file,
        line=finding.line if finding.line else 'N/A',
        tool=finding.tool,
        rule_id=finding.rule_id,
        message=finding.message,
        severity=finding.severity,
        context_before='\n'.join(context['before']),
        context_after='\n'.join(context['after']),
        full_context=context['full_context']
    )

    # Optionally prepend system prompt
    if include_system_prompt and 'system_prompt' in templates:
        system_prompt = templates['system_prompt']
        prompt = f"{system_prompt}\n\n{prompt}"

    return prompt
