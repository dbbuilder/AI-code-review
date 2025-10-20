# TODO — Code Review Engine Development Plan

This document outlines the phased plan to complete the **code-review-engine** as a production-ready terminal-accessible tool.

## Current Status

**Completed**:
- ✅ Basic project structure with `src/crengine/` modules
- ✅ Pydantic models for data schemas
- ✅ CLI entry point with `run` and `delta` subcommands
- ✅ Configuration system (YAML-based)
- ✅ Basic static analysis adapters (Flake8, Bandit, Semgrep)
- ✅ **Config-driven scoring with weighted dimensions** (Phase 1)
- ✅ **Config-driven phase routing** (Phase 1)
- ✅ AI provider stubs (OpenAI, Anthropic, Gemini)
- ✅ Git diff scanning for delta reviews
- ✅ Output artifact generation (JSON/MD)
- ✅ **Comprehensive test suite: 156 tests, 90.16% coverage** (Phase 0)

**In Progress**:
- ⏳ Enhanced recommendation formatting with rationale (Phase 1)
- ⏳ Error handling and user feedback (Phase 1)

**Remaining**:
- ❌ No Tree-sitter integration for structural parsing
- ❌ AI integration not tested/verified with real providers
- ❌ Missing advanced features: code complexity metrics, churn analysis, coverage detection
- ❌ No PyPI packaging or distribution setup
- ❌ No CI/CD pipeline
- ❌ Missing comprehensive documentation

---

## Phase 0 — Foundation & Testing (Core Stability) ✅ COMPLETED

**Goal**: Ensure existing code works correctly with comprehensive test coverage.

### Tasks

#### 0.1 Test Infrastructure ✅
- [x] Add `pytest.ini` configuration
- [x] Add `conftest.py` with fixtures for:
  - Mock repository with sample files
  - Sample findings, scored items, manifests
  - Temporary output directories
- [x] Add `pytest-cov` for coverage reporting
- [x] Set coverage target: 80% minimum

#### 0.2 Unit Tests
- [x] **`tests/test_model_schemas.py`**
  - Validate Pydantic models: serialization, validation, edge cases
  - Test optional fields and defaults

- [x] **`tests/test_utils.py`**
  - Test `sha256_file()` with various file sizes
  - Test `run_tool()` with successful/failing commands
  - Test `write_json()` and `write_text()` path creation

- [x] **`tests/test_discover.py`**
  - Test manifest generation with include/exclude patterns
  - Test language detection for all supported extensions
  - Test with non-git repositories (should fail gracefully)

- [x] **`tests/test_analyze_static.py`**
  - Test Flake8 adapter with real/mocked output
  - Test Bandit adapter with JSON parsing
  - Test Semgrep adapter with various rule formats
  - Test error handling for tool failures

- [x] **`tests/test_score.py`**
  - Expand beyond basic test
  - Test all severity levels
  - Test tag combinations (security, perf, style)
  - Test edge cases (missing severity, empty tags)

- [x] **`tests/test_consolidate.py`**
  - Test phase routing with all tag types
  - Test items with multiple tags
  - Test empty input

- [x] **`tests/test_diffscan.py`**
  - Test changed file detection
  - Test hunk extraction
  - Test with no changes, many changes

- [x] **`tests/test_ai_apply.py`**
  - Mock AI provider responses
  - Test retry logic with tenacity
  - Test all three providers (OpenAI, Anthropic, Gemini)
  - Test error handling

#### 0.3 Integration Tests
- [x] **`tests/test_integration.py`**
  - Test full `run_full_pass()` end-to-end
  - Test `run_delta_pass()` with real git commits
  - Verify all output artifacts are created
  - Test with minimal repository

#### 0.4 CLI Tests
- [x] **`tests/test_cli.py`**
  - Test argument parsing
  - Test `run` and `delta` subcommands
  - Test `--ai` flag with all providers
  - Test error messages for missing args

**Deliverable**: ≥80% test coverage, all tests passing

---

## Phase 1 — Core Feature Completion (Production-Ready Analysis)

**Goal**: Implement missing core features for robust code analysis.

### Tasks

#### 1.1 Tree-sitter Integration
- [ ] Add Tree-sitter language parsers to dependencies
- [ ] Implement `src/crengine/parse_tree.py`:
  - [ ] Parse source files into AST
  - [ ] Extract structural metrics (function count, class count, nesting depth)
  - [ ] Detect common patterns (framework usage, imports)
  - [ ] Add to `Manifest` output
- [ ] Update `discover.py` to call Tree-sitter parser
- [ ] Add tests for Tree-sitter parsing

#### 1.2 Config-Driven Scoring ✅
- [ ] Implement **Code Complexity**:
  - [ ] Cyclomatic complexity via Tree-sitter or radon
  - [ ] Cognitive complexity
  - [ ] Nesting depth

- [ ] Implement **Coupling/Blast Radius**:
  - [ ] Import graph analysis
  - [ ] Shared resource usage (DB, files)
  - [ ] Call graph depth

- [ ] Implement **Churn Analysis**:
  - [ ] Git history: commits per file in last 90 days
  - [ ] Author count
  - [ ] Lines changed

- [ ] Implement **Test Coverage Detection**:
  - [ ] Detect presence of test files for each module
  - [ ] Parse coverage reports if available (`.coverage`, `coverage.xml`)

- [x] Update `score.py` to use `config/engine.yaml` weights:
  - [x] Load `scoring.difficulty_weights` and `scoring.value_weights`
  - [x] Compute weighted scores dynamically
  - [x] Remove hardcoded heuristics

#### 1.3 Config-Driven Phase Routing ✅
- [x] Update `consolidate.py` to load `phasing` from `config/engine.yaml`
- [x] Implement tag-based routing per phase definition
- [x] Support items with multiple tags (route to highest priority phase)
- [x] Add phase priority ordering

#### 1.4 Enhanced Recommendations
- [ ] Expand recommendation templates in `consolidate.py`:
  - [ ] Add rationale (why fix this?)
  - [ ] Add trade-offs (effort vs. impact)
  - [ ] Add best practice references (OWASP, Google Code Review)
  - [ ] Add actionable steps
- [ ] Format recommendations with rich markdown tables
- [ ] Sort by composite score (value × difficulty)

#### 1.5 Error Handling & User Feedback
- [ ] Add CLI argument validation (check repo exists, is git repo)
- [ ] Add progress bars for long operations (rich.progress)
- [ ] Add structured logging (rich.logging or loguru)
- [ ] Gracefully handle tool installation issues (flake8, bandit not found)
- [ ] Add `--verbose` and `--quiet` flags

**Deliverable**: Production-ready analysis engine with advanced metrics

---

## Phase 2 — AI Integration & Delta Optimization (Intelligent Automation)

**Goal**: Fully integrate AI providers and optimize delta re-review workflow.

### Tasks

#### 2.1 AI Provider Verification
- [ ] Test with real API keys:
  - [ ] OpenAI GPT-4 (update model name from fictitious `gpt-5.1`)
  - [ ] Anthropic Claude (update from fictitious `claude-3.7`)
  - [ ] Google Gemini (update from fictitious `gemini-2.5-pro-exp`)
- [ ] Verify API response formats
- [ ] Update adapters for actual API structure
- [ ] Add rate limiting per provider (use `rate_limit_rps` from config)
- [ ] Add token budget enforcement (`max_output_tokens`)
- [ ] Add cost estimation logging

#### 2.2 Enhanced AI Prompting
- [ ] Improve patch generation prompts:
  - [ ] Include surrounding context (before/after lines)
  - [ ] Specify diff format (unified diff)
  - [ ] Add constraints (preserve tests, no breaking changes)
- [ ] Add AI-based recommendation generation:
  - [ ] Generate rationale for each finding
  - [ ] Suggest trade-offs
- [ ] Add prompt templates in `config/prompts/`

#### 2.3 Delta Re-Review Enhancements
- [ ] Improve `diffscan.py`:
  - [ ] Parse unified diffs correctly (current implementation is brittle)
  - [ ] Extract exact line ranges per hunk
  - [ ] Re-run static analysis on changed regions only
  - [ ] Merge new findings with previous results
- [ ] Add `--base` flag to `delta` command for custom base ref
- [ ] Cache previous findings (avoid full re-scan)

#### 2.4 Patch Application Workflow
- [ ] Add `apply` subcommand to CLI:
  - [ ] Read `060_ai_patch_suggestions.md`
  - [ ] Parse unified diffs
  - [ ] Apply patches with `git apply` or similar
  - [ ] Create commits per patch
- [ ] Add interactive mode (ask user before each patch)
- [ ] Add dry-run mode

**Deliverable**: Fully functional AI-assisted review-apply-delta loop

---

## Phase 3 — Multi-Language Support (Cross-Platform Analysis)

**Goal**: Extend beyond Python to support JavaScript, TypeScript, C#, Java, Go, Rust, C/C++.

### Tasks

#### 3.1 Language-Specific Analyzers
- [ ] **JavaScript/TypeScript**:
  - [ ] Add ESLint adapter
  - [ ] Add TypeScript compiler checks
  - [ ] Detect Node.js/React/Vue frameworks

- [ ] **C#**:
  - [ ] Add Roslyn analyzer adapter
  - [ ] Add StyleCop/FxCop integration
  - [ ] Detect .NET framework versions

- [ ] **Java**:
  - [ ] Add SpotBugs/PMD adapter
  - [ ] Add Checkstyle integration
  - [ ] Detect Spring/Hibernate frameworks

- [ ] **Go**:
  - [ ] Add `go vet` and `golangci-lint` adapter
  - [ ] Detect Go modules

- [ ] **Rust**:
  - [ ] Add Clippy adapter
  - [ ] Add `cargo check` integration

- [ ] **C/C++**:
  - [ ] Add Clang-Tidy adapter
  - [ ] Add cppcheck integration

#### 3.2 Language Detection Enhancements
- [ ] Expand `LANG_BY_EXT` in `discover.py`
- [ ] Add shebang detection for scripts
- [ ] Add framework detection (requirements.txt, package.json, etc.)

#### 3.3 Cross-Language Semgrep Rules
- [ ] Add language-specific Semgrep rule packs in `config/semgrep/`:
  - [ ] Python security rules
  - [ ] JavaScript/TypeScript rules
  - [ ] C# rules
  - [ ] Java rules
  - [ ] Go rules
  - [ ] Rust rules

**Deliverable**: Multi-language analysis support for top 8 languages

---

## Phase 4 — Packaging & Distribution (Production Deployment)

**Goal**: Make the tool easily installable and distributable.

### Tasks

#### 4.1 PyPI Packaging
- [ ] Update `pyproject.toml` metadata:
  - [ ] Add real author info, license, URLs
  - [ ] Add keywords, classifiers
  - [ ] Pin dependency versions
- [ ] Add `README.md` content to `long_description`
- [ ] Add `LICENSE` file (MIT or Apache 2.0)
- [ ] Test local build: `python -m build`
- [ ] Test installation from wheel
- [ ] Publish to TestPyPI
- [ ] Publish to PyPI

#### 4.2 CLI Distribution
- [ ] Verify `crengine` script entry point works globally
- [ ] Add shell completions (bash, zsh, fish)
- [ ] Add man page generation

#### 4.3 Docker Containerization
- [ ] Create `Dockerfile`:
  - [ ] Base image: python:3.10-slim
  - [ ] Install all static analysis tools
  - [ ] Copy source code
  - [ ] Set `crengine` as entrypoint
- [ ] Add `docker-compose.yml` for local testing
- [ ] Publish to Docker Hub or GHCR

#### 4.4 GitHub Actions CI/CD
- [ ] Add `.github/workflows/test.yml`:
  - [ ] Run tests on push/PR
  - [ ] Matrix: Python 3.10, 3.11, 3.12
  - [ ] Upload coverage to Codecov

- [ ] Add `.github/workflows/publish.yml`:
  - [ ] Build and publish to PyPI on release tag
  - [ ] Build and publish Docker image

**Deliverable**: Installable via `pip install code-review-engine`

---

## Phase 5 — Documentation & Polish (User Experience)

**Goal**: Comprehensive documentation and UX improvements.

### Tasks

#### 5.1 User Documentation
- [ ] Expand `README.md`:
  - [ ] Add badges (build status, coverage, PyPI version)
  - [ ] Add screenshots of output
  - [ ] Add comparison with alternatives (SonarQube, CodeClimate)

- [ ] Create `docs/` directory:
  - [ ] `docs/installation.md`
  - [ ] `docs/configuration.md`
  - [ ] `docs/usage.md`
  - [ ] `docs/extending.md` (add new tools/providers)
  - [ ] `docs/architecture.md` (deep dive)

- [ ] Add Sphinx or MkDocs for generated docs
- [ ] Host docs on Read the Docs or GitHub Pages

#### 5.2 Developer Documentation
- [ ] Add `CONTRIBUTING.md`:
  - [ ] Development setup
  - [ ] Running tests
  - [ ] Code style guide
  - [ ] PR process

- [ ] Add inline docstrings to all modules/functions
- [ ] Generate API docs with Sphinx autodoc

#### 5.3 UX Enhancements
- [ ] Add colorized terminal output (rich.console)
- [ ] Add progress bars for long operations
- [ ] Add summary statistics at end (total findings, top issues)
- [ ] Add `--format` flag for output (json, markdown, html)
- [ ] Add interactive mode for patch application

#### 5.4 Examples & Tutorials
- [ ] Add `examples/` directory:
  - [ ] Sample Python project with known issues
  - [ ] Sample JavaScript project
  - [ ] Sample multi-language project

- [ ] Add tutorial videos or GIFs

**Deliverable**: Comprehensive documentation and polished UX

---

## Phase 6 — Advanced Features (Enterprise-Ready)

**Goal**: Add enterprise features for large-scale adoption.

### Tasks

#### 6.1 Performance Optimization
- [ ] Parallelize static analysis runs (multiprocessing)
- [ ] Cache tool outputs (keyed by file hash)
- [ ] Incremental analysis (skip unchanged files)
- [ ] Add `--workers` flag for parallelism

#### 6.2 Reporting & Dashboards
- [ ] Add HTML report generation:
  - [ ] Interactive dashboard with charts (Chart.js or Plotly)
  - [ ] Drill-down by phase, severity, file
- [ ] Add SARIF output format (for GitHub Code Scanning)
- [ ] Add JSON Schema for outputs (for tool integrations)

#### 6.3 CI/CD Integration Guides
- [ ] Add GitHub Actions example workflows
- [ ] Add GitLab CI example
- [ ] Add Jenkins example
- [ ] Add Azure Pipelines example

#### 6.4 Plugin System
- [ ] Define plugin interface for custom analyzers
- [ ] Add plugin discovery mechanism
- [ ] Add example plugin

#### 6.5 Enterprise Features
- [ ] Add RBAC for multi-team usage
- [ ] Add audit logging
- [ ] Add webhook notifications (Slack, Teams)
- [ ] Add database backend for findings history

**Deliverable**: Enterprise-grade code review platform

---

## Success Criteria

### Minimum Viable Product (MVP) — After Phase 2
- ✅ Analyze Python codebases with 5+ static analysis tools
- ✅ Generate scored, phased improvement plans
- ✅ AI-assisted patch generation (optional)
- ✅ Delta re-review for rapid iteration
- ✅ 80%+ test coverage
- ✅ Installable via `pip`

### Production-Ready — After Phase 4
- ✅ Multi-language support (8+ languages)
- ✅ PyPI package published
- ✅ Docker image available
- ✅ CI/CD pipeline active
- ✅ Comprehensive documentation

### Enterprise-Ready — After Phase 6
- ✅ Performance optimized for large repos (10k+ files)
- ✅ Plugin system for extensibility
- ✅ HTML dashboards and SARIF output
- ✅ CI/CD integration examples

---

## Estimated Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Phase 0 — Foundation & Testing | 1-2 weeks | Core stability |
| Phase 1 — Core Features | 2-3 weeks | Production-ready analysis |
| Phase 2 — AI & Delta | 1-2 weeks | Intelligent automation |
| Phase 3 — Multi-Language | 2-3 weeks | Cross-platform support |
| Phase 4 — Packaging | 1 week | Public release |
| Phase 5 — Documentation | 1-2 weeks | User adoption |
| Phase 6 — Advanced Features | 3-4 weeks | Enterprise-ready |

**Total**: ~11-17 weeks for full completion

**MVP**: ~4-7 weeks (Phases 0-2)

---

## Next Steps

1. **Start with Phase 0**: Build comprehensive test suite
2. **Validate assumptions**: Test with real AI providers, verify tool integrations
3. **Iterate**: Use delta re-review on this codebase to dogfood the tool
4. **Gather feedback**: Share early versions with users for UX input
5. **Document as you go**: Keep CLAUDE.md and docs updated

---

**Last Updated**: 2025-10-19
**Status**: Planning Phase → Ready to execute Phase 0

---

## Phase 7 — Web Platform & SaaS (Cloud-Based Service)

**Goal**: Transform the CLI tool into a web-based SaaS platform with GitHub integration.

### Overview

Build a web application that allows users to:
- Sign up via GitHub OAuth
- Point to their GitHub repositories
- Run automated code reviews in the cloud
- View results in a beautiful web dashboard
- Open findings directly in GitHub Codespaces

### Architecture

```
┌─────────────────┐
│   Frontend      │ Next.js/React + Tailwind CSS
│   (Vercel)      │ Landing page, dashboard, auth
└────────┬────────┘
         │
┌────────▼────────┐
│   Backend API   │ FastAPI/Python
│   (Cloud Run)   │ GitHub webhooks, job queue
└────────┬────────┘
         │
┌────────▼────────┐
│   Worker Pool   │ Celery/Redis
│   (Cloud Run)   │ Run crengine on repos
└────────┬────────┘
         │
┌────────▼────────┐
│   Database      │ PostgreSQL (Cloud SQL)
│   + Storage     │ Store results, user data
└─────────────────┘
```

### Tasks

#### 7.1 Landing Page & Marketing Site
- [ ] **Frontend Setup**:
  - [ ] Initialize Next.js 14 project with TypeScript
  - [ ] Setup Tailwind CSS + shadcn/ui components
  - [ ] Configure React Query for data fetching
  
- [ ] **Landing Page Components**:
  - [ ] Hero section with product value prop
  - [ ] Features showcase (config-driven, AI-powered, multi-language)
  - [ ] Pricing tiers (Free, Pro, Enterprise)
  - [ ] Live demo/playground section
  - [ ] Testimonials/social proof
  - [ ] FAQ section
  - [ ] Footer with links

- [ ] **Marketing Copy**:
  - [ ] "Intelligent Code Review, Automated" tagline
  - [ ] Feature highlights:
    - "Config-driven scoring with weighted dimensions"
    - "AI-powered patch suggestions"
    - "Enhanced recommendations with rationale & best practices"
    - "GitHub integration with Codespaces support"
  - [ ] Call-to-action: "Sign up with GitHub"

#### 7.2 GitHub OAuth Authentication
- [ ] **OAuth Flow**:
  - [ ] Register GitHub OAuth App
  - [ ] Implement OAuth callback handler
  - [ ] Store access tokens securely (encrypted)
  - [ ] Refresh token management
  
- [ ] **User Management**:
  - [ ] User model: id, github_id, email, username, avatar_url
  - [ ] Session management with JWT
  - [ ] Role-based access control (free, pro, enterprise)
  - [ ] Account settings page

- [ ] **GitHub API Integration**:
  - [ ] Fetch user repositories
  - [ ] Repository permissions check
  - [ ] Install GitHub App for webhook access

#### 7.3 Repository Selection & Analysis Trigger
- [ ] **Repository Browser**:
  - [ ] List user's accessible GitHub repositories
  - [ ] Search/filter repositories
  - [ ] Repository metadata (stars, language, last commit)
  - [ ] "Analyze Now" button per repo
  
- [ ] **Analysis Configuration**:
  - [ ] Select config preset (Security-focused, Performance, Comprehensive)
  - [ ] Custom config editor (YAML)
  - [ ] Branch selection
  - [ ] Schedule options (on-demand, on-push, daily)
  
- [ ] **GitHub Webhooks**:
  - [ ] Register webhook for push events
  - [ ] Webhook handler endpoint
  - [ ] Trigger analysis on push (optional)

#### 7.4 Backend API (FastAPI)
- [ ] **API Routes**:
  - [ ] `POST /api/auth/github/callback` - OAuth callback
  - [ ] `GET /api/user/repos` - List repositories
  - [ ] `POST /api/analysis/start` - Trigger analysis
  - [ ] `GET /api/analysis/{id}` - Get analysis status
  - [ ] `GET /api/analysis/{id}/results` - Get results
  - [ ] `POST /api/analysis/{id}/codespaces` - Open in Codespaces
  
- [ ] **Database Models** (PostgreSQL):
  ```python
  User: id, github_id, email, username, tier, created_at
  Repository: id, user_id, github_repo_id, name, url
  Analysis: id, repo_id, status, config, started_at, completed_at
  Finding: id, analysis_id, file, line, severity, message, score
  Recommendation: id, analysis_id, priority, rationale, steps
  ```

- [ ] **Background Job Queue**:
  - [ ] Setup Celery + Redis
  - [ ] Task: `run_code_review(repo_url, config)`
  - [ ] Task status tracking
  - [ ] Error handling & retries

#### 7.5 Code Review Worker
- [ ] **Worker Implementation**:
  - [ ] Clone GitHub repo (using access token)
  - [ ] Run `crengine run --repo . --outputs /tmp/results`
  - [ ] Parse output artifacts (JSON/MD)
  - [ ] Store results in database
  - [ ] Cleanup temporary files
  
- [ ] **Performance Optimization**:
  - [ ] Parallel analysis for large repos
  - [ ] Incremental/delta analysis for repeat runs
  - [ ] Caching of static analysis results
  - [ ] Timeout handling (max 15 minutes)

- [ ] **Resource Limits**:
  - [ ] Max repo size: 500MB (free), 2GB (pro)
  - [ ] Max analysis time: 5min (free), 15min (pro)
  - [ ] Rate limiting per user tier

#### 7.6 Results Dashboard
- [ ] **Overview Page**:
  - [ ] Summary statistics (total findings, effort estimate)
  - [ ] Severity breakdown chart (Critical/High/Medium/Low)
  - [ ] Top 10 high-priority issues
  - [ ] Phase distribution chart
  - [ ] Trend graph (if multiple analyses)

- [ ] **Findings Table**:
  - [ ] Sortable/filterable table (by severity, file, tool)
  - [ ] Pagination (20 per page)
  - [ ] File preview with syntax highlighting
  - [ ] Click to expand full recommendation

- [ ] **Enhanced Recommendation Cards**:
  - [ ] Display rationale, trade-offs, references
  - [ ] Actionable steps checklist
  - [ ] "Open in Codespaces" button
  - [ ] "Mark as resolved" action
  - [ ] Share finding permalink

- [ ] **Phased Plan View**:
  - [ ] Collapsible phase sections
  - [ ] Drag-and-drop to reorder priorities
  - [ ] Export as markdown
  - [ ] Export as GitHub Issues

#### 7.7 GitHub Codespaces Integration
- [ ] **Codespaces Deep Linking**:
  - [ ] Generate Codespaces URL: `https://github.dev/owner/repo/blob/main/file.py#L42`
  - [ ] Pre-populate search with finding location
  - [ ] Optional: Create `.devcontainer.json` with auto-linters
  
- [ ] **One-Click Fix Flow**:
  - [ ] Button: "Open in Codespaces & Navigate to Issue"
  - [ ] Opens Codespaces with file at exact line
  - [ ] Shows AI-suggested patch in sidebar (if available)

#### 7.8 GitHub Issues Export
- [ ] **Bulk Export**:
  - [ ] "Create GitHub Issues" button
  - [ ] Generate issues for top N findings
  - [ ] Issue template:
    ```markdown
    ## [Severity] Finding Title
    
    **File**: `src/example.py:42`
    **Tool**: bandit (B602)
    **Message**: subprocess call with shell=True identified
    
    ### Rationale
    [Auto-populated from recommendation]
    
    ### Actionable Steps
    - [ ] Step 1
    - [ ] Step 2
    
    **Estimated Effort**: ~6h
    **References**: [OWASP](...)
    ```
  
- [ ] **Issue Labels**:
  - [ ] Auto-create labels: `code-quality`, `security`, `performance`
  - [ ] Severity labels: `critical`, `high`, `medium`, `low`

#### 7.9 Deployment & Infrastructure
- [ ] **Frontend (Vercel)**:
  - [ ] Deploy Next.js to Vercel
  - [ ] Custom domain: `codereview.ai` or similar
  - [ ] Environment variables for API URL
  
- [ ] **Backend (Google Cloud Run)**:
  - [ ] Deploy FastAPI to Cloud Run
  - [ ] Auto-scaling configuration
  - [ ] Secret Manager for tokens/keys
  
- [ ] **Worker (Cloud Run Jobs)**:
  - [ ] Deploy worker as Cloud Run Job
  - [ ] Triggered by Pub/Sub or Cloud Tasks
  - [ ] Separate job pool for free vs paid users
  
- [ ] **Database (Cloud SQL)**:
  - [ ] PostgreSQL 15 instance
  - [ ] Automated backups
  - [ ] Connection pooling (PgBouncer)
  
- [ ] **Storage (Cloud Storage)**:
  - [ ] Store analysis artifacts (JSON/MD)
  - [ ] Signed URLs for temporary access
  - [ ] Lifecycle policy (delete after 90 days for free tier)

#### 7.10 Pricing & Monetization
- [ ] **Pricing Tiers**:
  ```
  Free Tier:
  - 5 analyses per month
  - Public repositories only
  - Max repo size: 500MB
  - Basic recommendations
  
  Pro Tier ($29/month):
  - Unlimited analyses
  - Private repositories
  - Max repo size: 2GB
  - AI-powered patch suggestions
  - Priority support
  - GitHub Issues export
  
  Enterprise ($499/month):
  - Self-hosted option
  - Custom config presets
  - Dedicated support
  - SLA guarantees
  - Audit logs
  ```
  
- [ ] **Stripe Integration**:
  - [ ] Subscription management
  - [ ] Webhook handlers for payment events
  - [ ] Usage tracking & billing

#### 7.11 Analytics & Monitoring
- [ ] **User Analytics**:
  - [ ] Plausible or PostHog for privacy-focused analytics
  - [ ] Track: signups, analyses triggered, tier conversions
  
- [ ] **Application Monitoring**:
  - [ ] Sentry for error tracking
  - [ ] Cloud Monitoring for performance
  - [ ] Uptime monitoring (UptimeRobot)
  
- [ ] **Cost Tracking**:
  - [ ] Cloud billing alerts
  - [ ] Per-user cost attribution

**Deliverable**: Fully functional SaaS platform with GitHub integration and Codespaces support

**Estimated Duration**: 6-8 weeks

**Tech Stack**:
- Frontend: Next.js 14, React, TypeScript, Tailwind CSS, shadcn/ui
- Backend: FastAPI, Python 3.12
- Worker: Celery, Redis
- Database: PostgreSQL 15
- Cloud: Google Cloud Platform (Cloud Run, Cloud SQL, Cloud Storage)
- Auth: GitHub OAuth
- Payments: Stripe
- Monitoring: Sentry, Cloud Monitoring

---

## Updated Timeline with Web Platform

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Phase 0 — Foundation & Testing | ✅ COMPLETE | Core stability |
| Phase 1 — Core Features | ✅ COMPLETE | Production-ready analysis |
| Phase 2 — AI & Delta | 1-2 weeks | Intelligent automation |
| Phase 3 — Multi-Language | 2-3 weeks | Cross-platform support |
| Phase 4 — Packaging | 1 week | Public CLI release |
| Phase 5 — Documentation | 1-2 weeks | User adoption |
| Phase 6 — Advanced Features | 3-4 weeks | Enterprise CLI |
| **Phase 7 — Web Platform** | **6-8 weeks** | **SaaS Launch** |

**Total**: ~17-25 weeks for full completion (including SaaS)

**MVP SaaS**: ~12-16 weeks (Phases 0-2 + Phase 7 basic)

---

**Last Updated**: 2025-10-19
**Status**: Phase 1 Complete ✅ → Planning Phase 2 & Phase 7
