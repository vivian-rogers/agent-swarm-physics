"""Move per-period folders into each hypothesis' goalperiod-subhypotheses/ subfolder, and fix links.

    hypotheses/H<NN>-*/G<NN>[a-z]/   →  hypotheses/H<NN>-*/goalperiod-subhypotheses/G<NN>[a-z]/
    hypotheses/H<NN>-*/NE<NN>[-…]/   →  hypotheses/H<NN>-*/goalperiod-subhypotheses/NE<NN>[-…]/

Idempotent: safe to rerun whenever a script recreates a folder at the old place (files are merged; the newer
copy wins). Links are fixed in the moved READMEs (paths to hypothesis-level files gain one "../") and in the
card (links to G/NE folders gain the subfolder prefix).

Usage: uv run python infra/overview/organize_period_folders.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HYP = ROOT / "hypotheses"
SUB = "goalperiod-subhypotheses"
PERIOD_RE = re.compile(r"^(G\d{2}[a-z]?|NE\d{2}(-.*)?)$")


def merge(src: Path, dst: Path):
    for f in src.rglob("*"):
        if f.is_file():
            t = dst / f.relative_to(src)
            if not t.exists() or f.stat().st_mtime >= t.stat().st_mtime:
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, t)
    shutil.rmtree(src)


def fix_period_links(md: Path):
    t = md.read_text(errors="replace")

    def rep(m):
        target = m.group(2)
        if re.match(r"(G\d{2}|NE\d{2})", target):  # sibling period folder: unchanged
            return m.group(0)
        return f"{m.group(1)}../../{target}"
    new = re.sub(r"(\]\()\.\./(?!\.\./\.\./\.\./\.\./)([^)]*)", rep, t)
    if new != t:
        md.write_text(new)


def fix_card_links(card: Path):
    t = card.read_text(errors="replace")
    new = re.sub(r"\]\(((?:G\d{2}[a-z]?|NE\d{2}[^/)]*)/)", rf"]({SUB}/\1", t)
    if new != t:
        card.write_text(new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    moved = 0
    for h in sorted(HYP.glob("H[0-9][0-9]-*")):
        if not h.is_dir():
            continue
        dirs = [d for d in h.iterdir() if d.is_dir() and PERIOD_RE.match(d.name)]
        if not dirs:
            continue
        sub = h / SUB
        for d in dirs:
            dst = sub / d.name
            print(f"{d.relative_to(ROOT)} → {dst.relative_to(ROOT)}" + (" (merge)" if dst.exists() else ""))
            moved += 1
            if args.dry_run:
                continue
            sub.mkdir(exist_ok=True)
            if dst.exists():
                merge(d, dst)
            else:
                shutil.move(str(d), str(dst))
                for md in dst.rglob("*.md"):
                    fix_period_links(md)
        if not args.dry_run and (h / "README.md").exists():
            fix_card_links(h / "README.md")
    print(f"{moved} folder(s) {'would be ' if args.dry_run else ''}moved")


if __name__ == "__main__":
    main()
