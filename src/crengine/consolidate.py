from typing import List, Dict, Any, Optional
from .model_schemas import ScoredItem


def to_phases(items: List[ScoredItem]) -> Dict[str, List[ScoredItem]]:
    """Legacy function - routes items using hardcoded rules."""
    phases = {
        "Phase 0 – Repo Hygiene": [],
        "Phase 1 – Security & Safety": [],
        "Phase 2 – Reliability & Performance": [],
        "Phase 3 – Developer Experience": [],
        "Phase 4 – Product Polish": []
    }
    for it in items:
        if "security" in it.finding.tags:
            phases["Phase 1 – Security & Safety"].append(it)
        elif "perf" in it.finding.tags:
            phases["Phase 2 – Reliability & Performance"].append(it)
        elif "style" in it.finding.tags:
            phases["Phase 0 – Repo Hygiene"].append(it)
        else:
            phases["Phase 3 – Developer Experience"].append(it)
    return phases


def to_phases_from_config(
    items: List[ScoredItem],
    phase_config: List[Dict[str, Any]]
) -> Dict[str, List[ScoredItem]]:
    """
    Route items to phases based on config.

    Args:
        items: List of scored findings to route
        phase_config: List of phase definitions from config/engine.yaml
                     Each entry should have 'name' and 'include_tags' keys

    Returns:
        Dictionary mapping phase names to lists of items
    """
    # Initialize phases from config
    phases: Dict[str, List[ScoredItem]] = {}
    for phase_def in phase_config:
        phase_name = phase_def["name"]
        phases[phase_name] = []

    # Add catch-all phase for unmatched items
    phases["Uncategorized"] = []

    # Normalize tags in config for case-insensitive matching
    normalized_config = []
    for phase_def in phase_config:
        normalized_tags = [tag.lower() for tag in phase_def["include_tags"]]
        normalized_config.append({
            "name": phase_def["name"],
            "include_tags": normalized_tags
        })

    # Route each item to first matching phase
    for item in items:
        item_tags = [tag.lower() for tag in item.finding.tags]
        matched = False

        for phase_def in normalized_config:
            phase_name = phase_def["name"]
            phase_tags = phase_def["include_tags"]

            # Check if any of the item's tags match this phase
            if any(tag in phase_tags for tag in item_tags):
                phases[phase_name].append(item)
                matched = True
                break

        # If no match, put in catch-all
        if not matched:
            phases["Uncategorized"].append(item)

    return phases


def generate_enhanced_recommendation(item: ScoredItem) -> str:
    """
    Generate enhanced recommendation with rationale, trade-offs, and best practices.

    Args:
        item: Scored finding to generate recommendation for

    Returns:
        Formatted markdown recommendation with rationale and actionable steps
    """
    finding = item.finding

    # Build header with scores
    header = f"### [{item.value_importance:.1f}/5 Value × {item.difficulty_risk:.1f}/5 Risk] {finding.file}:{finding.line or 'N/A'}\n"

    # Issue summary
    summary = f"**Issue**: `{finding.rule_id}` from {finding.tool}\n"
    summary += f"**Message**: {finding.message}\n"
    summary += f"**Severity**: {finding.severity} | **Tags**: {', '.join(finding.tags) if finding.tags else 'none'}\n"

    # Rationale - why fix this?
    rationale = _generate_rationale(item)

    # Trade-offs - effort vs impact
    tradeoffs = _generate_tradeoffs(item)

    # Best practice references
    references = _generate_references(item)

    # Actionable steps
    steps = _generate_actionable_steps(item)

    # Assemble recommendation
    recommendation = header + "\n"
    recommendation += summary + "\n"
    recommendation += f"**Rationale**:\n{rationale}\n\n"
    recommendation += f"**Trade-offs**:\n{tradeoffs}\n\n"
    if references:
        recommendation += f"**References**:\n{references}\n\n"
    recommendation += f"**Actionable Steps**:\n{steps}\n\n"
    recommendation += f"**Estimated Effort**: ~{item.est_hours}h\n"
    recommendation += "\n---\n\n"

    return recommendation


def _generate_rationale(item: ScoredItem) -> str:
    """Generate rationale for why this finding should be fixed."""
    finding = item.finding

    # Tag-based rationale
    if "security" in finding.tags:
        return (f"Security issues can expose the application to attacks and data breaches. "
                f"With a severity of {finding.severity}, this finding represents a potential "
                f"vulnerability that should be addressed to maintain system integrity.")
    elif "perf" in finding.tags:
        return (f"Performance issues can degrade user experience and increase infrastructure costs. "
                f"Addressing this {finding.severity} severity performance concern will improve "
                f"application responsiveness and resource utilization.")
    elif "tests" in finding.tags:
        return (f"Test coverage gaps reduce confidence in code changes and increase the risk of "
                f"regressions. Adding tests for this code will improve maintainability and "
                f"enable safer refactoring.")
    elif "style" in finding.tags:
        return (f"Code style consistency improves readability and maintainability. While lower "
                f"priority than functional issues, addressing style violations helps maintain "
                f"code quality standards across the team.")
    else:
        return (f"This {finding.severity} severity issue should be addressed to maintain code "
                f"quality and prevent potential problems in production.")


def _generate_tradeoffs(item: ScoredItem) -> str:
    """Generate trade-off analysis (effort vs. impact)."""
    value = item.value_importance
    difficulty = item.difficulty_risk

    # Categorize by value/difficulty matrix
    if value >= 4.0 and difficulty <= 2.0:
        return (f"**High Value, Low Effort** (Quick Win): This issue offers significant value "
                f"({value:.1f}/5) with relatively low complexity ({difficulty:.1f}/5). "
                f"Prioritize for immediate fix.")
    elif value >= 4.0 and difficulty >= 4.0:
        return (f"**High Value, High Effort** (Major Project): This is a critical issue "
                f"({value:.1f}/5 value) but requires substantial effort ({difficulty:.1f}/5 complexity). "
                f"Plan dedicated time and resources.")
    elif value <= 2.0 and difficulty <= 2.0:
        return (f"**Low Value, Low Effort** (Nice to Have): While easy to fix ({difficulty:.1f}/5), "
                f"the impact is modest ({value:.1f}/5). Address during cleanup sprints.")
    elif value <= 2.0 and difficulty >= 4.0:
        return (f"**Low Value, High Effort** (Low Priority): This requires significant work "
                f"({difficulty:.1f}/5) for limited benefit ({value:.1f}/5). Consider deferring.")
    else:
        return (f"**Balanced Trade-off**: Value ({value:.1f}/5) and complexity ({difficulty:.1f}/5) "
                f"are moderate. Prioritize based on current sprint capacity.")


def _generate_references(item: ScoredItem) -> Optional[str]:
    """Generate best practice references based on finding tags."""
    finding = item.finding
    refs = []

    if "security" in finding.tags:
        refs.append("- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Web application security risks")
        refs.append("- [CWE Top 25](https://cwe.mitre.org/top25/) - Most dangerous software weaknesses")

    if "perf" in finding.tags:
        refs.append("- [Google Web Vitals](https://web.dev/vitals/) - Performance best practices")

    if "tests" in finding.tags:
        refs.append("- [Google Testing Blog](https://testing.googleblog.com/) - Testing strategies")
        refs.append("- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) - Balanced test suite")

    if "style" in finding.tags:
        refs.append("- [PEP 8](https://pep8.org/) - Python style guide" if finding.file.endswith(".py") else None)

    # Filter out None values
    refs = [r for r in refs if r]

    return "\n".join(refs) if refs else None


def _generate_actionable_steps(item: ScoredItem) -> str:
    """Generate actionable steps to resolve the finding."""
    finding = item.finding

    # Generic steps based on tool
    if finding.tool == "flake8":
        return (f"1. Review the style violation at {finding.file}:{finding.line}\n"
                f"2. Apply automated fixes with `autopep8` or `black` if applicable\n"
                f"3. Manually adjust code to comply with PEP 8 standards\n"
                f"4. Run `flake8` to verify resolution")
    elif finding.tool == "bandit":
        return (f"1. Review the security issue at {finding.file}:{finding.line}\n"
                f"2. Consult Bandit documentation for rule `{finding.rule_id}`\n"
                f"3. Implement secure alternative (e.g., use `subprocess` with argument lists, not shell)\n"
                f"4. Add security tests to prevent regression\n"
                f"5. Re-run `bandit` to confirm fix")
    elif finding.tool == "semgrep":
        return (f"1. Examine the pattern match at {finding.file}:{finding.line}\n"
                f"2. Review Semgrep rule: `{finding.rule_id}`\n"
                f"3. Refactor code to avoid the anti-pattern\n"
                f"4. Validate with `semgrep --config <rule>`")
    else:
        return (f"1. Locate the issue in {finding.file}:{finding.line or 'N/A'}\n"
                f"2. Read tool documentation for `{finding.rule_id}`\n"
                f"3. Implement the recommended fix\n"
                f"4. Add tests to verify resolution\n"
                f"5. Re-run static analysis to confirm")
