import yaml
from pathlib import Path
from typing import List
from git import Repo
from .model_schemas import Manifest, FileEntry
from .utils import sha256_file

LANG_BY_EXT = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".cs": "c_sharp",
    ".java": "java", ".go": "go", ".rs": "rust", ".cpp": "cpp", ".c": "c"
}

def build_manifest(repo_root: Path, include_exclude_path: Path) -> Manifest:
    repo = Repo(repo_root)
    commit = repo.head.commit.hexsha

    patterns = yaml.safe_load(include_exclude_path.read_text(encoding="utf-8"))
    includes = patterns.get("include", ["**/*"])
    excludes = patterns.get("exclude", [])

    files: List[FileEntry] = []
    for inc in includes:
        for p in repo_root.glob(inc):
            if p.is_file() and not any(p.match(ex) for ex in excludes):
                ext = p.suffix.lower()
                lang = LANG_BY_EXT.get(ext)
                files.append(FileEntry(
                    path=str(p.relative_to(repo_root)),
                    language=lang,
                    bytes=p.stat().st_size,
                    sha256=sha256_file(p)
                ))
    return Manifest(repo_root=str(repo_root), commit=commit, files=files)
