from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class FileEntry(BaseModel):
    path: str
    language: Optional[str] = None
    bytes: int
    sha256: str

class Manifest(BaseModel):
    repo_root: str
    commit: str
    files: List[FileEntry]

class Finding(BaseModel):
    tool: str
    rule_id: str
    severity: str
    message: str
    file: str
    line: Optional[int] = None
    col: Optional[int] = None
    suggestion: Optional[str] = None
    tags: List[str] = []

class ScoredItem(BaseModel):
    finding: Finding
    difficulty_risk: float
    value_importance: float
    est_hours: float

class PhaseItem(BaseModel):
    phase: str
    items: List[ScoredItem]

class DeltaFinding(BaseModel):
    file: str
    hunks: List[Dict[str, Any]]
    findings: List[Finding]
