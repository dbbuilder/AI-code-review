"""Pytest configuration and shared fixtures for code-review-engine tests."""
import json
import shutil
import tempfile
from pathlib import Path
from typing import List

import pytest
from git import Repo

from crengine.model_schemas import Finding, ScoredItem, Manifest, FileEntry


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    tmpdir = Path(tempfile.mkdtemp())
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def mock_repo(temp_dir):
    """Create a mock git repository with sample files."""
    repo_path = temp_dir / "mock_repo"
    repo_path.mkdir()

    # Initialize git repo
    repo = Repo.init(repo_path)

    # Create sample Python files
    (repo_path / "src").mkdir()
    (repo_path / "src" / "__init__.py").write_text("")
    (repo_path / "src" / "main.py").write_text("""
def hello(name):
    eval("print('dangerous')")  # Intentional security issue
    return f"Hello {name}"

def unused_function():  # Dead code
    pass
""")

    (repo_path / "src" / "utils.py").write_text("""
def add(a, b):
    return a + b

def very_long_line_that_exceeds_flake8_limits_and_should_trigger_a_warning_about_line_length_in_the_static_analysis():
    pass
""")

    # Create test file
    (repo_path / "tests").mkdir()
    (repo_path / "tests" / "test_main.py").write_text("""
from src.main import hello

def test_hello():
    assert hello("World") == "Hello World"
""")

    # Create config directory
    (repo_path / "config").mkdir()

    # Commit initial files
    repo.index.add(["src", "tests"])
    repo.index.commit("Initial commit")

    yield repo_path


@pytest.fixture
def sample_findings() -> List[Finding]:
    """Sample findings for testing."""
    return [
        Finding(
            tool="bandit",
            rule_id="B001",
            severity="HIGH",
            message="Use of eval() detected",
            file="src/main.py",
            line=3,
            col=5,
            tags=["security", "sast"]
        ),
        Finding(
            tool="flake8",
            rule_id="E501",
            severity="INFO",
            message="line too long (120 > 79 characters)",
            file="src/utils.py",
            line=5,
            col=80,
            tags=["style"]
        ),
        Finding(
            tool="pylint",
            rule_id="W0612",
            severity="MEDIUM",
            message="Unused function 'unused_function'",
            file="src/main.py",
            line=7,
            tags=["dead_code", "lints"]
        ),
        Finding(
            tool="semgrep",
            rule_id="no-eval-python",
            severity="CRITICAL",
            message="Use of eval() is dangerous; avoid or sanitize inputs.",
            file="src/main.py",
            line=3,
            tags=["security", "pattern"]
        ),
    ]


@pytest.fixture
def sample_scored_items(sample_findings) -> List[ScoredItem]:
    """Sample scored items for testing."""
    return [
        ScoredItem(
            finding=sample_findings[0],
            difficulty_risk=4.5,
            value_importance=4.8,
            est_hours=6.0
        ),
        ScoredItem(
            finding=sample_findings[1],
            difficulty_risk=1.2,
            value_importance=1.5,
            est_hours=0.5
        ),
        ScoredItem(
            finding=sample_findings[2],
            difficulty_risk=2.0,
            value_importance=2.5,
            est_hours=2.0
        ),
        ScoredItem(
            finding=sample_findings[3],
            difficulty_risk=4.8,
            value_importance=5.0,
            est_hours=6.0
        ),
    ]


@pytest.fixture
def sample_manifest(mock_repo) -> Manifest:
    """Sample manifest for testing."""
    repo = Repo(mock_repo)
    return Manifest(
        repo_root=str(mock_repo),
        commit=repo.head.commit.hexsha,
        files=[
            FileEntry(
                path="src/__init__.py",
                language="python",
                bytes=0,
                sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            ),
            FileEntry(
                path="src/main.py",
                language="python",
                bytes=150,
                sha256="abc123def456"
            ),
            FileEntry(
                path="src/utils.py",
                language="python",
                bytes=100,
                sha256="def456ghi789"
            ),
        ]
    )


@pytest.fixture
def config_files(temp_dir):
    """Create sample config files for testing."""
    config_dir = temp_dir / "config"
    config_dir.mkdir()

    # engine.yaml
    engine_yaml = """
ai:
  provider: none
  model:
    openai: "gpt-4"
    anthropic: "claude-3-5-sonnet-20241022"
    gemini: "gemini-1.5-pro"
  max_output_tokens: 2000
  temperature: 0.2
  rate_limit_rps: 1.0

scoring:
  difficulty_weights:
    code_complexity: 0.30
    coupling_blastradius: 0.30
    test_coverage_gap: 0.20
    tooling_fixability: 0.20
  value_weights:
    security_severity: 0.40
    reliability_perf: 0.25
    developer_experience: 0.20
    user_value: 0.15
  scale: 1-5

phasing:
  - name: "Phase 0 – Repo Hygiene"
    include_tags: ["dead_code","formatting","lints","duplicate","infra"]
  - name: "Phase 1 – Security & Safety"
    include_tags: ["security","secrets","sast","auth","input_validation"]
  - name: "Phase 2 – Reliability & Performance"
    include_tags: ["perf","db","io","concurrency","error_handling"]
  - name: "Phase 3 – Developer Experience"
    include_tags: ["tests","typing","docs","build","logging"]
  - name: "Phase 4 – Product Polish"
    include_tags: ["ux","api","observability","i18n"]

tools:
  flake8_config: "config/flake8.cfg"
  bandit_config: "config/bandit.yaml"
  semgrep_rules: "config/semgrep/rules.yaml"

include_exclude: "config/include_exclude.yaml"
"""
    (config_dir / "engine.yaml").write_text(engine_yaml)

    # include_exclude.yaml
    include_exclude_yaml = """
include:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"
exclude:
  - "**/.venv/**"
  - "**/node_modules/**"
  - "**/test_*"
"""
    (config_dir / "include_exclude.yaml").write_text(include_exclude_yaml)

    # flake8.cfg
    flake8_cfg = """
[flake8]
max-line-length = 120
exclude = .venv,dist,build
"""
    (config_dir / "flake8.cfg").write_text(flake8_cfg)

    # bandit.yaml
    (config_dir / "bandit.yaml").write_text('skips: ["B101"]')

    # semgrep rules
    semgrep_dir = config_dir / "semgrep"
    semgrep_dir.mkdir()
    semgrep_rules = """
rules:
  - id: no-eval-python
    patterns:
      - pattern: eval(...)
    message: "Use of eval() is dangerous"
    severity: ERROR
    languages: [python]
"""
    (semgrep_dir / "rules.yaml").write_text(semgrep_rules)

    yield config_dir
