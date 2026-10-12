"""Create the static Pages artifact after content validation."""
from __future__ import annotations

import shutil
import sys
import json
from pathlib import Path
from validate_content import prepare

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> int:
    try:
        packs, summary = prepare()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"内容校验失败：{exc}", file=sys.stderr)
        return 1
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for name in ("index.html", "manifest.webmanifest", "sw.js", "CONTENT_SPEC.md"):
        shutil.copy2(ROOT / name, DIST / name)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    (DIST / "data").mkdir()
    for kind, rows in packs.items():
        path = DIST / "data" / f"{kind}.jsonl"
        path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")
    (DIST / "data" / "summary.json").write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")
    notes = ROOT / "data" / "review-notes.md"
    if notes.exists():
        shutil.copy2(notes, DIST / "data" / notes.name)
    (DIST / ".nojekyll").touch()
    print("内容结构校验通过：" + json.dumps(summary, ensure_ascii=False))
    print(f"站点已构建：{DIST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

