from typing import List, Dict, Any
from .model_schemas import Finding, ScoredItem

def _severity_weight(sev: str) -> float:
    return {"CRITICAL": 1.0, "HIGH": 0.85, "MEDIUM": 0.6, "LOW": 0.35, "INFO": 0.2}.get(sev.upper(), 0.2)

def score_findings(findings: List[Finding]) -> List[ScoredItem]:
    out: List[ScoredItem] = []
    for f in findings:
        # naive heuristics; can be extended with complexity metrics, coverage, churn
        dr = 1.0 + 4.0 * _severity_weight(f.severity) * (1.0 if "security" in f.tags else 0.7)
        vi = 1.0 + 4.0 * (_severity_weight(f.severity) if ("security" in f.tags or "perf" in f.tags) else 0.5)
        est = 0.5 if vi < 2 else 2 if dr < 2.5 else 6
        out.append(ScoredItem(finding=f, difficulty_risk=round(dr,2), value_importance=round(vi,2), est_hours=est))
    return out


def score_findings_from_config(
    findings: List[Finding],
    scoring_config: Dict[str, Any]
) -> List[ScoredItem]:
    """
    Score findings using weights from configuration.

    Args:
        findings: List of findings to score
        scoring_config: Scoring configuration with difficulty_weights and value_weights

    Returns:
        List of scored items with difficulty/risk and value/importance scores (1-5 scale)
    """
    # Extract config with defaults
    difficulty_weights = scoring_config.get("difficulty_weights", {
        "code_complexity": 0.25,
        "coupling_blastradius": 0.25,
        "test_coverage_gap": 0.25,
        "tooling_fixability": 0.25
    })

    value_weights = scoring_config.get("value_weights", {
        "security_severity": 0.25,
        "reliability_perf": 0.25,
        "developer_experience": 0.25,
        "user_value": 0.25
    })

    scale = scoring_config.get("scale", "1-5")
    min_score, max_score = map(int, scale.split("-"))
    score_range = max_score - min_score

    out: List[ScoredItem] = []

    for f in findings:
        # Compute difficulty/risk components
        severity_factor = _severity_weight(f.severity)

        # Difficulty components (normalized 0-1)
        code_complexity = severity_factor  # Higher severity = more complex fix
        coupling_blastradius = 1.0 if "security" in f.tags else 0.7  # Security affects more
        test_coverage_gap = 0.8 if "tests" in f.tags else 0.5  # Test issues harder
        tooling_fixability = 0.3 if f.tool in ["flake8", "pylint"] else 0.7  # Linters easier

        # Weighted difficulty score
        difficulty_raw = (
            difficulty_weights.get("code_complexity", 0.25) * code_complexity +
            difficulty_weights.get("coupling_blastradius", 0.25) * coupling_blastradius +
            difficulty_weights.get("test_coverage_gap", 0.25) * test_coverage_gap +
            difficulty_weights.get("tooling_fixability", 0.25) * tooling_fixability
        )

        # Value/importance components (normalized 0-1)
        security_severity = severity_factor if "security" in f.tags else 0.2
        reliability_perf = severity_factor if "perf" in f.tags else 0.3
        developer_experience = 0.6 if any(tag in f.tags for tag in ["tests", "docs", "typing"]) else 0.3
        user_value = 0.7 if any(tag in f.tags for tag in ["ux", "api", "i18n"]) else 0.2

        # Weighted value score
        value_raw = (
            value_weights.get("security_severity", 0.25) * security_severity +
            value_weights.get("reliability_perf", 0.25) * reliability_perf +
            value_weights.get("developer_experience", 0.25) * developer_experience +
            value_weights.get("user_value", 0.25) * user_value
        )

        # Scale to configured range (default 1-5)
        difficulty_risk = min_score + (difficulty_raw * score_range)
        value_importance = min_score + (value_raw * score_range)

        # Estimate hours based on scores
        est_hours = _estimate_hours(difficulty_risk, value_importance)

        out.append(ScoredItem(
            finding=f,
            difficulty_risk=round(difficulty_risk, 2),
            value_importance=round(value_importance, 2),
            est_hours=est_hours
        ))

    return out


def _estimate_hours(difficulty: float, value: float) -> float:
    """Estimate person-hours based on difficulty and value scores."""
    avg_score = (difficulty + value) / 2

    if avg_score < 2.0:
        return 0.5
    elif avg_score < 3.0:
        return 2.0
    elif avg_score < 4.0:
        return 6.0
    else:
        return 12.0
