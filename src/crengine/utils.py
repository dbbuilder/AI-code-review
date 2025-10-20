import hashlib, json, os, subprocess, sys
from pathlib import Path
from typing import List
from rich.console import Console

console = Console()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def run_tool(cmd: List[str]) -> subprocess.CompletedProcess:
    # Safe subprocess wrapper: no shell=True; captures output & errors
    console.log(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
