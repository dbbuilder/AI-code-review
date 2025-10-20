# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**code-review-engine** is a deterministic, AI-optional code review pipeline that analyzes codebases, scores issues by difficulty/risk and value/importance, and synthesizes a phased improvement plan. It supports optional AI integration (OpenAI, Anthropic, Google Gemini) to draft patches, then re-analyzes only the diffs using Git history for rapid convergence.

### Core Design Principles

- **Repeatable & Auditable**: Every step emits timestamped JSON/MD files to `outputs/` for CI artifacts and audits
- **Deterministic**: Same commit hash + config = same results
- **Multi-language**: Uses Tree-sitter for parsing, Semgrep for cross-language rules
- **Security-first**: References OWASP guidance; no shell injection (subprocess uses argument lists); user paths validated
- **Delta-optimized**: Re-reviews only changed files/hunks via Git history

## Commands

### Installation & Setup
```bash
# Create virtual environment and install
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

# Install with AI support
pip install -e ".[ai]"

# Configure environment
cp .env.example .env
# Edit .env to add API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_GENAI_API_KEY
```

### Running Analysis

```bash
# Full pass (no AI)
python -m src.cli run --repo . --outputs ./outputs

# Full pass with OpenAI
python -m src.cli run --repo . --outputs ./outputs --ai openai

# Full pass with Anthropic Claude
python -m src.cli run --repo . --outputs ./outputs --ai anthropic

# Full pass with Google Gemini
python -m src.cli run --repo . --outputs ./outputs --ai gemini

# Delta-only re-review after commits (faster iteration)
python -m src.cli delta --repo . --outputs ./outputs

# Alternative: Use installed CLI script (after pip install -e .)
crengine run --repo . --outputs ./outputs
crengine run --repo . --outputs ./outputs --ai anthropic
crengine delta --repo . --outputs ./outputs
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_scoring.py

# Run with verbose output
pytest -v tests/
```

## Architecture

### Pipeline Stages (Sequential)

The engine executes in a strict sequence, with each stage producing artifacts:

1. **Discovery** (`src/crengine/discover.py`)
   - Enumerates files, detects languages via Tree-sitter
   - Produces: `outputs/000_manifest.json` (paths, sizes, hashes, detected frameworks)

2. **Static Analysis** (`src/crengine/analyze_static.py`)
   - Runs toolchain per language: Pylint/Flake8/Bandit (Python), Semgrep (cross-language)
   - Normalizes outputs to unified schema (file, line/col, rule/id, severity, message, tags)
   - Produces: `outputs/010_static_findings.json`

3. **Scoring** (`src/crengine/score.py`)
   - Assigns **Difficulty/Risk** (1-5) and **Value/Importance** (1-5) scores
   - Heuristics combine: code complexity, blast radius, churn, security severity, test coverage
   - Estimates person-hours per finding
   - Produces: `outputs/030_scores.json`

4. **Consolidation** (`src/crengine/consolidate.py`)
   - Transforms findings into human-readable recommendations with rationale, trade-offs, best practice references
   - Aggregates into **Phased Plan** (Phase 0-4: Hygiene → Safety → Reliability → DevEx → Polish)
   - Produces: `outputs/040_recommendations.md`, `outputs/050_phased_plan.md`

5. **AI Application** (Optional, `src/crengine/ai_apply.py`)
   - Invokes one provider (OpenAI/Anthropic/Gemini) to draft patches as unified diffs
   - Caps to top 20 findings by score to avoid token blowups
   - Produces: `outputs/060_ai_patch_suggestions.md`

6. **Delta Re-Review** (`src/crengine/diffscan.py`)
   - Detects changed files/hunks via Git; re-runs analysis only where needed
   - Produces: `outputs/070_delta_review.json`

### Key Modules

- **`src/cli.py`**: CLI entry point with `run` and `delta` subcommands
- **`src/crengine/main.py`**: Orchestrates `run_full_pass()` and `run_delta_pass()` flows
- **`src/crengine/model_schemas.py`**: Pydantic models for Manifest, Finding, ScoredItem, DeltaFinding
- **`src/crengine/utils.py`**: Shared utilities for file I/O, JSON/text writing

**Note**: The package structure uses `src/crengine/` on disk but imports as `from crengine.*` after installation. This is configured via setuptools in `pyproject.toml`, which exposes the `crengine` CLI script.

### Configuration System

All configuration lives in `config/`:

- **`config/engine.yaml`**: Master config for:
  - AI provider selection (`none|openai|anthropic|gemini`) and model names
  - Scoring weights (difficulty vs. value dimensions)
  - Phase definitions with tag-based routing
  - Tool paths (flake8, bandit, semgrep configs)

- **`config/include_exclude.yaml`**: Glob patterns for file filtering

- **`config/flake8.cfg`**: Flake8 linter settings

- **`config/bandit.yaml`**: Bandit security scanner settings

- **`config/semgrep/`**: Custom Semgrep rules for house style or security invariants

### Phased Plan Structure

Findings are automatically routed to phases based on tags:

- **Phase 0 – Repo Hygiene**: `dead_code`, `formatting`, `lints`, `duplicate`, `infra`
- **Phase 1 – Security & Safety**: `security`, `secrets`, `sast`, `auth`, `input_validation`
- **Phase 2 – Reliability & Performance**: `perf`, `db`, `io`, `concurrency`, `error_handling`
- **Phase 3 – Developer Experience**: `tests`, `typing`, `docs`, `build`, `logging`
- **Phase 4 – Product Polish**: `ux`, `api`, `observability`, `i18n`

### AI Integration Design

- **Single provider per run**: Specify via `--ai` flag (overrides `config/engine.yaml`)
- **Rate limiting**: Configured via `rate_limit_rps` in engine.yaml; uses `tenacity` for retries
- **Token budgets**: `max_output_tokens` and `temperature` configurable per provider
- **Model versions**: Centralized in `config/engine.yaml` (`ai.model.openai`, etc.)
- **Error handling**: AI failures logged but don't halt the pipeline (step skipped with warning)

### Delta Re-Review Mechanism

Uses `git.Repo` (GitPython) to:
- Detect changed files since last commit
- Extract hunks with line ranges
- Re-run static analysis only on changed regions
- Preserve previous findings for unchanged code

This enables **rapid iteration loops**: make changes → delta review → see only new issues.

## Development Workflow

### Adding a New Static Analysis Tool

1. Add tool to `pyproject.toml` dependencies
2. Create adapter function in `src/crengine/analyze_static.py` that:
   - Invokes tool via subprocess (argument list, no shell=True)
   - Parses output into `Finding` objects with normalized schema
   - Assigns appropriate tags for phase routing
3. Call adapter in `run_full_pass()` in `src/crengine/main.py`
4. Add tool config to `config/engine.yaml` → `tools` section
5. Write test in `tests/` to verify normalization

### Modifying Scoring Weights

Edit `config/engine.yaml` → `scoring` section:
- `difficulty_weights`: Adjust how complexity/coupling/testing gaps factor into risk
- `value_weights`: Adjust how security/reliability/DevEx factor into importance
- Weights must sum to 1.0 within each category
- Scale is always 1-5

### Adding Custom Semgrep Rules

1. Create `.yaml` rule file in `config/semgrep/`
2. Reference from `config/engine.yaml` → `tools.semgrep_rules`
3. Ensure rules emit tags matching phase definitions (e.g., `security`, `perf`)

### Extending AI Providers

1. Add SDK to `pyproject.toml` → `[project.optional-dependencies].ai`
2. Implement adapter function in `src/crengine/ai_apply.py`:
   - Follow pattern of `_call_openai()`, `_call_anthropic()`, `_call_gemini()`
   - Use `tenacity` for retries with exponential backoff
   - Return list of patch strings (unified diff format preferred)
3. Add provider to `--ai` choices in `src/cli.py`
4. Add model config to `config/engine.yaml` → `ai.model.<provider>`

## Output Artifacts

All outputs written to `--outputs` directory (typically `./outputs/`):

| File | Description |
|------|-------------|
| `000_manifest.json` | Repository file manifest with languages, sizes, hashes |
| `010_static_findings.json` | Raw findings from all static analysis tools |
| `030_scores.json` | Scored findings with difficulty/risk, value/importance, estimates |
| `040_recommendations.md` | Human-readable recommendations sorted by score |
| `050_phased_plan.md` | Findings grouped into 5 phases (Hygiene → Polish) |
| `060_ai_patch_suggestions.md` | AI-generated unified diffs (if `--ai` specified) |
| `070_delta_review.json` | Changed files and hunks (from `delta` command) |

## Important Constraints

- **No shell injection**: All `subprocess` calls use argument lists; never `shell=True`
- **Path validation**: User-supplied paths resolved and validated before use
- **Pinned dependencies**: All tool versions pinned in `pyproject.toml` for reproducibility
- **AI capping**: Max 20 findings sent to AI to prevent token/cost blowups
- **Git requirement**: Repository must be initialized (even if no commits); needed for delta tracking
- **Python 3.10+**: Uses modern type hints and Pydantic v2

## References

- **Google Code Review Practices**: Influences recommendation phrasing and rationale structure
- **OWASP Top 10 & Secure Coding Practices**: Security finding classification and severity mapping
- **Industry Guidance**: Not a replacement for human review; prioritizes and drafts changes for human validation
