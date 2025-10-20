from pathlib import Path
from typing import List, Dict
from git import Repo

def changed_files(repo_root: Path, base_ref: str = "HEAD~1") -> List[str]:
    repo = Repo(repo_root)
    diff = repo.git.diff("--name-only", base_ref, "HEAD")
    return [p for p in diff.splitlines() if p.strip()]

def changed_hunks(repo_root: Path, base_ref: str = "HEAD~1") -> Dict[str, str]:
    repo = Repo(repo_root)
    unified = repo.git.diff(base_ref, "HEAD", "--", ".")
    out, current = {}, None
    for line in unified.splitlines():
        if line.startswith("diff --git"):
            parts = line.split(" ")
            current = parts[-1].split("b/")[-1]
            out[current] = ""
        if current is not None:
            out[current] += line + "\n"
    return out
