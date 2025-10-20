# Code Review Engine — README

## Overview
`code-review-engine` analyzes a codebase, scores issues, and synthesizes a phased improvement plan. Optionally, it asks an AI provider to draft patches, then re-analyzes only the diffs to converge quickly.

## Quickstart

### 1) Prereqs
- Python 3.10+
- Git installed and repo initialized
- If using AI:
  - **OpenAI**: set `OPENAI_API_KEY`
  - **Anthropic**: set `ANTHROPIC_API_KEY`
  - **Google Gemini**: set `GOOGLE_GENAI_API_KEY`

### 2) Install
```bash
python -m venv .venv
. .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 3) Configure
```bash
cp .env.example .env
$EDITOR config/engine.yaml
```

### 4) Run
```bash
# Full pass (no AI)
python -m src.cli run --repo . --outputs ./outputs

# Full pass with AI (OpenAI example)
python -m src.cli run --repo . --outputs ./outputs --ai openai

# Delta-only re-review after commits
python -m src.cli delta --repo . --outputs ./outputs
```

### 5) Artifacts
- See `outputs/040_recommendations.md` and `outputs/050_phased_plan.md` for the human-readable results; JSON files provide machine-readable details.
