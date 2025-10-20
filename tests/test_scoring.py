from crengine.score import score_findings
from crengine.model_schemas import Finding

def test_scoring_basic():
    f = Finding(tool="bandit", rule_id="B001", severity="HIGH", message="test", file="a.py", line=1, tags=["security"])
    s = score_findings([f])[0]
    assert s.value_importance >= 3 and s.difficulty_risk >= 3
