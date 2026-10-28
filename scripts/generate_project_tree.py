"""Regenerate human-readable folder map from distributable repository files."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", "dist", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".sqlite3", ".db", ".log"}


def source_paths(root=ROOT):
    root = Path(root)
    # The Git index is authoritative when available. In standalone ZIPs,
    # fall back to the same safe file filters used by the source archive.
    if (root / ".git").exists():
        run = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True)
        candidates = [root / line for line in run.stdout.splitlines()]
    else:
        candidates = root.rglob("*")
    paths = []
    for p in candidates:
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() in EXCLUDED_SUFFIXES or p.name in {".DS_Store", ".coverage"}:
            continue
        # Local generated datasets are not distributed; only .gitkeep markers.
        if rel.parts[:2] in (("data", "raw"), ("data", "processed"), ("data", "interim")) and p.name != ".gitkeep":
            continue
        paths.append(rel)
    return sorted(paths, key=lambda p: str(p))


def render_tree(paths):
    hierarchy = {}
    for path in paths:
        node = hierarchy
        for part in path.parts:
            node = node.setdefault(part, {})
    lines = ["TransactionShield/"]
    def walk(node, prefix=""):
        ordered = sorted(node.items(), key=lambda item: (bool(not item[1]), item[0].lower()))
        for i, (name, children) in enumerate(ordered):
            last = i == len(ordered) - 1
            lines.append(prefix + ("└── " if last else "├── ") + name)
            if children:
                walk(children, prefix + ("    " if last else "│   "))
    walk(hierarchy)
    return "\n".join(lines)


def main():
    output = ROOT / "docs/PROJECT_TREE.md"
    tree = render_tree(source_paths(ROOT))
    output.write_text("# TransactionShield repository structure\n\n"
                      "Generated from source files by `python scripts/generate_project_tree.py`. "
                      "Generated raw data, local databases, dependency caches, and credentials are excluded.\n\n"
                      "```text\n" + tree + "\n```\n\n"
                      "The ML pipeline is under `ml/`, the protected API is under `backend/`, "
                      "the React interface is under `frontend/`, and independent checks, architecture "
                      "diagrams, deployment instructions, and reproducible synthetic evaluation evidence "
                      "are under `tests/`, `docs/`, `.github/`, and `artifacts/`.\n", encoding="utf-8")
    print("Updated", output.relative_to(ROOT))


if __name__ == "__main__":
    main()
