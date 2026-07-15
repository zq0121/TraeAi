import os
import uuid
from pathlib import Path

from fastapi import HTTPException, status


def ensure_directories(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def safe_filename(original_name: str, prefix: str = "file") -> str:
    suffix = Path(original_name or "").suffix.lower()
    return f"{prefix}_{uuid.uuid4().hex}{suffix}"


def validate_extension(filename: str, allowed: set[str]) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文件格式")
    return ext


def resolve_managed_path(path: str, roots: list[Path]) -> Path:
    candidate_raw = Path(path)
    candidates = []
    if candidate_raw.is_absolute():
        candidates.append(candidate_raw)
    for root in roots:
        candidates.append(root / path)
        candidates.append(root / Path(path).name)

    resolved_roots = [r.resolve() for r in roots]
    for candidate in candidates:
        resolved = candidate.resolve()
        if any(os.path.commonpath([str(resolved), str(root)]) == str(root) for root in resolved_roots):
            if resolved.exists():
                return resolved
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
