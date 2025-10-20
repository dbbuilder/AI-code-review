# Code Review Engine — REQUIREMENTS

## Purpose
This project provides a **repeatable, auditable code-review engine** to understand an unfamiliar codebase, produce actionable findings, score them by **difficulty/risk** and **value/importance**, and consolidate those into a **phased improvement plan**. It optionally **invokes an AI model** (OpenAI, Anthropic, or Gemini) to propose or apply changes, then **re-reviews only the delta** using Git history.

## Scope
- Multi-language discovery and structural parsing (Tree-sitter).
- Static analysis (style, correctness, security) via Pylint/Flake8/Bandit for Python and Semgrep for cross-language rules.
- Configurable scoring and prioritization.
- Phase planning (Foundational → Safety/SecOps → Performance → UX/API polish).
- AI adapters to draft patches and rationale.
- Iterative loop: **review → apply → re-review (delta)**.

## Non-Goals
- Replacing human review; rather, we prioritize and draft changes consistent with industry guidance (Google code review practices; OWASP Top-10 & Secure Coding Practices).

## Functional Requirements
1. **Repository Discovery**
   - Enumerate files, identify languages, build a manifest (paths, sizes, hashes).
   - Produce `outputs/000_manifest.json` with summaries and detected frameworks.

2. **Static Analysis**
   - Run toolchain(s) per language; normalize outputs to a single schema with:
     - file, line/col, rule/id, severity, message, suggested fix (if available).

3. **Rule Extensions**
   - Load optional Semgrep rules from `config/semgrep/` to enforce house style or security invariants.

4. **Scoring**
   - Assign a **Difficulty/Risk** score (1–5) and **Value/Importance** score (1–5).
   - Default heuristics combine complexity, blast radius, churn, security severity, and test coverage presence.
   - Output `outputs/030_scores.json`.

5. **Recommendations**
   - Transform findings into human-readable recommendations with rationale, trade-offs, references to best practices, and estimated person-hours.
   - Output `outputs/040_recommendations.md`.

6. **Phased Plan**
   - Aggregate recommendations into a sequenced **phased plan**: Phase 0 (Repo Hygiene), Phase 1 (Safety & Security), Phase 2 (Reliability/Perf), Phase 3 (Developer Experience), Phase 4 (Product polish).
   - Output `outputs/050_phased_plan.md`.

7. **AI Application (Optional)**
   - Invoke one provider per run (OpenAI Responses API, Anthropic Claude API, or Gemini GenAI SDK) to draft patches in-place or as unified diffs; store diffs and rationale in `outputs/060_ai_patch_suggestions.md`.

8. **Delta-Only Re-Review**
   - Detect changed files and hunks via Git; re-run analyses only where needed; produce `outputs/070_delta_review.json`.

## Quality & Compliance Requirements
- All external tool invocations are pinned in `pyproject.toml`.
- Engine runs are deterministic given the same commit hash and config.
- No shell injection—subprocess calls use argument lists; user-supplied paths validated.
- Security guidance references OWASP; security rule packs maintained in repo.

## Configuration
- `config/engine.yaml` governs weights for scoring, severity mappings, AI provider, token budgets, and rate-limits.
- `config/include_exclude.yaml` for glob patterns (include/exclude).

## Outputs & Auditability
- Every step emits a timestamped JSON/MD file to `outputs/` to support audits and CI artifacts.
