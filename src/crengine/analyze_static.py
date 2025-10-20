import json
from pathlib import Path
from typing import List
from .model_schemas import Finding
from .utils import run_tool

def run_flake8(repo_root: Path, config_path: Path) -> List[Finding]:
    cp = run_tool(["flake8", "--format=%(path)s::%(row)d::%(col)d::%(code)s::%(text)s",
                   f"--config={config_path}", str(repo_root)])
    findings: List[Finding] = []
    for line in cp.stdout.splitlines():
        try:
            path,row,col,code,text = line.split("::", 4)
            findings.append(Finding(tool="flake8", rule_id=code, severity="INFO",
                                    message=text, file=path, line=int(row), col=int(col), tags=["style"]))
        except Exception:
            continue
    return findings

def run_bandit(repo_root: Path, config_path: Path) -> List[Finding]:
    cp = run_tool(["bandit", "-r", str(repo_root), "-f", "json", "-c", str(config_path)])
    try:
        data = json.loads(cp.stdout or "{}")
    except Exception:
        data = {}
    findings: List[Finding] = []
    for res in data.get("results", []):
        findings.append(Finding(
            tool="bandit",
            rule_id=res.get("test_id","BXXX"),
            severity=res.get("issue_severity","LOW"),
            message=res.get("issue_text",""),
            file=res.get("filename",""),
            line=res.get("line_number"),
            col=None,
            tags=["security","sast"]
        ))
    return findings

def run_semgrep(repo_root: Path, rules_path: Path) -> List[Finding]:
    cp = run_tool(["semgrep", "--config", str(rules_path), "--json", str(repo_root)])
    try:
        data = json.loads(cp.stdout or "{}")
    except Exception:
        data = {}
    findings: List[Finding] = []
    for r in data.get("results", []):
        findings.append(Finding(
            tool="semgrep",
            rule_id=r.get("check_id",""),
            severity=(r.get("extra", {}).get("severity","INFO")).upper(),
            message=r.get("extra", {}).get("message",""),
            file=r.get("path",""),
            line=r.get("start",{}).get("line"),
            col=r.get("start",{}).get("col"),
            tags=["pattern","security"] if "security" in r.get("check_id","") else ["pattern"]
        ))
    return findings
