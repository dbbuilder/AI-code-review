"""
AI-Powered Code Reviewer
Provides thoughtful, context-aware code review feedback using LLMs
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import anthropic
import openai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class CodeReviewFinding:
    """A single code review finding"""
    file: str
    line_start: int
    line_end: int
    severity: str  # critical, high, medium, low, info
    category: str  # security, performance, maintainability, style, bug, design
    title: str
    description: str
    reasoning: str  # Why this matters
    suggestion: str  # How to fix it
    code_snippet: Optional[str] = None
    confidence: float = 0.8  # 0.0 to 1.0


REVIEW_SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering best practices, security, performance, and maintainability.

Your role is to provide thoughtful, actionable code review feedback that helps developers improve their code quality.

Guidelines for your reviews:
1. **Be Specific**: Point to exact lines and explain clearly what needs attention
2. **Be Constructive**: Always explain WHY something matters and HOW to improve it
3. **Prioritize**: Focus on issues that truly impact code quality, not nitpicks
4. **Be Contextual**: Consider the purpose and constraints of the code
5. **Be Respectful**: Assume competence and good intentions

Severity Levels:
- **critical**: Security vulnerabilities, data loss risks, crashes
- **high**: Bugs, performance issues, major design flaws
- **medium**: Code smells, maintainability issues, minor bugs
- **low**: Style inconsistencies, minor optimizations
- **info**: Suggestions, best practices, educational points

Categories:
- **security**: SQL injection, XSS, auth bypass, secrets in code
- **performance**: N+1 queries, memory leaks, inefficient algorithms
- **maintainability**: Complex functions, unclear names, lack of modularity
- **style**: Formatting, naming conventions, code organization
- **bug**: Logic errors, edge cases, incorrect assumptions
- **design**: Architecture, patterns, separation of concerns

Return your findings as a JSON array of objects with this structure:
{
  "file": "path/to/file.py",
  "line_start": 42,
  "line_end": 45,
  "severity": "high",
  "category": "security",
  "title": "Brief, clear title",
  "description": "Detailed explanation of the issue",
  "reasoning": "Why this matters and potential impact",
  "suggestion": "Concrete steps to fix, with code examples if helpful",
  "confidence": 0.9
}

Focus only on meaningful issues. Skip trivial style issues unless they impact readability."""


def create_review_prompt(file_path: str, code_content: str, language: str) -> str:
    """Create a focused review prompt for a single file"""
    return f"""Review this {language} code file for issues.

File: {file_path}

Code:
```{language}
{code_content}
```

Analyze for:
1. Security vulnerabilities (SQL injection, XSS, auth issues, secrets)
2. Bugs and logic errors
3. Performance problems (inefficient algorithms, memory issues)
4. Maintainability issues (complex functions, unclear code)
5. Design problems (tight coupling, missing abstractions)

Return ONLY a JSON array of findings. If the code is good, return an empty array [].
Do NOT include markdown formatting, just the raw JSON array."""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def review_with_anthropic(
    file_path: str,
    code_content: str,
    language: str,
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022"
) -> List[CodeReviewFinding]:
    """
    Review code using Anthropic Claude

    Uses retry logic for rate limiting
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = create_review_prompt(file_path, code_content, language)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.3,  # Lower temperature for more consistent analysis
            system=REVIEW_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract JSON from response
        content = response.content[0].text.strip()

        # Handle markdown code blocks if present
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1])  # Remove first and last line

        findings_data = json.loads(content)

        # Convert to CodeReviewFinding objects
        findings = []
        for finding in findings_data:
            findings.append(CodeReviewFinding(**finding))

        return findings

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response for {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error reviewing {file_path} with Anthropic: {e}")
        raise  # Let retry handle it


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def review_with_openai(
    file_path: str,
    code_content: str,
    language: str,
    api_key: str,
    model: str = "gpt-4o-mini"
) -> List[CodeReviewFinding]:
    """
    Review code using OpenAI GPT-4

    Uses retry logic for rate limiting
    """
    client = openai.OpenAI(api_key=api_key)

    prompt = create_review_prompt(file_path, code_content, language)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096
        )

        # Extract JSON from response
        content = response.choices[0].message.content.strip()

        # Handle markdown code blocks if present
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1])

        findings_data = json.loads(content)

        # Convert to CodeReviewFinding objects
        findings = []
        for finding in findings_data:
            findings.append(CodeReviewFinding(**finding))

        return findings

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response for {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error reviewing {file_path} with OpenAI: {e}")
        raise  # Let retry handle it


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def review_with_openrouter(
    file_path: str,
    code_content: str,
    language: str,
    api_key: str,
    model: str = "openai/gpt-4o-mini"
) -> List[CodeReviewFinding]:
    """
    Review code using OpenRouter (supports multiple models)

    OpenRouter provides access to many models:
    - openai/gpt-4o-mini (fast, cheap)
    - openai/gpt-4o (best quality)
    - anthropic/claude-3.5-sonnet
    - google/gemini-pro-1.5
    - meta-llama/llama-3.1-70b-instruct
    And many more...

    Uses retry logic for rate limiting
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    prompt = create_review_prompt(file_path, code_content, language)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096
        )

        # Extract JSON from response
        content = response.choices[0].message.content.strip()

        # Handle markdown code blocks if present
        if content.startswith('```'):
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1])

        findings_data = json.loads(content)

        # Convert to CodeReviewFinding objects
        findings = []
        for finding in findings_data:
            findings.append(CodeReviewFinding(**finding))

        return findings

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response for {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error reviewing {file_path} with OpenRouter: {e}")
        raise  # Let retry handle it


def review_file(
    file_path: Path,
    repo_root: Path,
    ai_provider: str,
    api_key: str,
    language: Optional[str] = None,
    model: Optional[str] = None
) -> List[CodeReviewFinding]:
    """
    Review a single file using AI

    Args:
        file_path: Path to the file
        repo_root: Repository root for relative paths
        ai_provider: 'openai', 'anthropic', or 'openrouter'
        api_key: API key for the provider
        language: Programming language (auto-detected if None)
        model: Specific model to use (optional, uses provider default)

    Returns:
        List of findings for this file
    """
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except (UnicodeDecodeError, IOError) as e:
        print(f"Could not read {file_path}: {e}")
        return []

    # Skip empty files
    if not code_content.strip():
        return []

    # Skip very large files (over 50KB - too much for AI context)
    if len(code_content) > 51200:
        print(f"Skipping {file_path}: too large for AI review")
        return []

    # Get relative path for display
    try:
        relative_path = str(file_path.relative_to(repo_root))
    except ValueError:
        relative_path = str(file_path)

    # Auto-detect language if not provided
    if not language:
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.cs': 'c#',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
        language = language_map.get(ext, 'unknown')

    # Call appropriate AI provider
    if ai_provider.lower() == 'anthropic':
        if model:
            return review_with_anthropic(relative_path, code_content, language, api_key, model)
        return review_with_anthropic(relative_path, code_content, language, api_key)
    elif ai_provider.lower() == 'openai':
        if model:
            return review_with_openai(relative_path, code_content, language, api_key, model)
        return review_with_openai(relative_path, code_content, language, api_key)
    elif ai_provider.lower() == 'openrouter':
        if model:
            return review_with_openrouter(relative_path, code_content, language, api_key, model)
        return review_with_openrouter(relative_path, code_content, language, api_key)
    else:
        raise ValueError(f"Unknown AI provider: {ai_provider}")


def review_repository(
    files: List[Path],
    repo_root: Path,
    ai_provider: str,
    api_key: str,
    max_files: int = 50
) -> List[CodeReviewFinding]:
    """
    Review multiple files in a repository

    Args:
        files: List of file paths to review
        repo_root: Repository root
        ai_provider: AI provider to use
        api_key: API key
        max_files: Maximum number of files to review (to control cost)

    Returns:
        Combined list of all findings
    """
    all_findings = []

    # Limit files to prevent excessive API costs
    files_to_review = files[:max_files]

    print(f"Reviewing {len(files_to_review)} files with {ai_provider}...")

    for i, file_path in enumerate(files_to_review):
        print(f"  [{i+1}/{len(files_to_review)}] Reviewing {file_path.name}...")

        findings = review_file(file_path, repo_root, ai_provider, api_key)
        all_findings.extend(findings)

        print(f"    Found {len(findings)} issues")

    print(f"\nTotal findings: {len(all_findings)}")

    return all_findings


def save_findings_json(findings: List[CodeReviewFinding], output_path: Path):
    """Save findings to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([asdict(f) for f in findings], f, indent=2)


def generate_markdown_report(findings: List[CodeReviewFinding], output_path: Path):
    """Generate a human-readable markdown report"""
    # Group by severity
    by_severity = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': [],
        'info': []
    }

    for finding in findings:
        by_severity[finding.severity].append(finding)

    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Code Review Report\n\n")

        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total Issues**: {len(findings)}\n")
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = len(by_severity[severity])
            if count > 0:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢', 'info': '🔵'}
                f.write(f"- **{severity.capitalize()}**: {count} {emoji[severity]}\n")
        f.write("\n---\n\n")

        # Findings by severity
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            issues = by_severity[severity]
            if not issues:
                continue

            f.write(f"## {severity.capitalize()} Issues\n\n")

            for finding in issues:
                f.write(f"### {finding.title}\n\n")
                f.write(f"**File**: `{finding.file}` (lines {finding.line_start}-{finding.line_end})  \n")
                f.write(f"**Category**: {finding.category}  \n")
                f.write(f"**Confidence**: {finding.confidence:.0%}\n\n")

                f.write(f"**Issue**: {finding.description}\n\n")
                f.write(f"**Why It Matters**: {finding.reasoning}\n\n")
                f.write(f"**How to Fix**: {finding.suggestion}\n\n")

                f.write("---\n\n")
