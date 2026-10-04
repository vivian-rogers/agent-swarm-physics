#!/usr/bin/env python3
"""Map the per-section prefixed bib keys onto the canonical keys of refs.bib.

The four section agents wrote refs-coupling.bib (cp:), refs-fields.bib (fd:),
refs-collective.bib (cl:) and refs-information.bib (in:), so one paper could
appear under several keys and print twice. refs.bib now holds one canonical,
unprefixed entry per paper. This script

  1. rewrites the keys inside every \\cite-family command (\\cite, \\citep,
     \\citet, \\onlinecite, \\nocite, ...) in sections/*.tex from the prefixed
     key to the canonical key;
  2. sets main.tex to \\bibliography{refs} (full run only, see --only);
  3. checks that every cited key exists in refs.bib.

It is idempotent: canonical keys are left alone, and a second run changes
nothing.

Usage (from anywhere):
  uv run python writeup/paper/fix_bib_keys.py                # all sections + main.tex
  uv run python writeup/paper/fix_bib_keys.py --only intro.tex theses.tex
  uv run python writeup/paper/fix_bib_keys.py --dry-run      # report only

With --only, main.tex is NOT changed (the other sections may still cite
prefixed keys that live only in refs-*.bib); pass --main to force it.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
SECTIONS = PAPER / "sections"
MAIN = PAPER / "main.tex"
REFS = PAPER / "refs.bib"

# Every key defined in refs-coupling/-fields/-collective/-information.bib.
KEYMAP = {
    # refs-coupling.bib
    "cp:aguilera2026": "aguilera2026",
    "cp:ashery2025": "ashery2025",
    # refs-fields.bib
    "fd:kolchinsky2018": "kolchinsky2018",
    "fd:centola2015": "centola2015",
    "fd:ashery2025": "ashery2025",
    "fd:aguilera2026": "aguilera2026",
    # refs-collective.bib
    "cl:kolchinsky2018": "kolchinsky2018",
    "cl:krakauer2020": "krakauer2020",
    "cl:heylighen2016": "heylighen2016",
    "cl:rosas2019": "rosas2019",
    "cl:mediano2022": "mediano2022",
    "cl:centola2015": "centola2015",
    "cl:ashery2025": "ashery2025",
    # refs-information.bib
    "in:kolchinsky2018": "kolchinsky2018",
    "in:sowinski2023": "sowinski2023",
    "in:aguilera2026": "aguilera2026",
    "in:kolchinsky2026": "kolchinsky2026",
    "in:pinero2025": "pinero2025",
    "in:kolchinsky2024": "kolchinsky2024",
    "in:kolchinsky2025": "kolchinsky2025",
    "in:hordijk2023": "hordijk2023",
    "in:sharma2023": "sharma2023",
    "in:abrahao2024": "abrahao2024",
}
PREFIX = re.compile(r"^(cp|fd|cl|in):(.+)$")

# \cite, \citep, \citet*, \onlinecite, \nocite, \citealp, \Citet ... with up to
# two optional [..] arguments before the {keys}.
CITE = re.compile(
    r"(\\(?:no|online)?[cC]ite[a-zA-Z]*\*?\s*(?:\[[^\]]*\]\s*){0,2}\{)([^}]*)(\})"
)
BIBLIO = re.compile(r"\\bibliography\{[^}]*\}")


def bib_keys(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", text))


def canonical(key: str, refs: set[str]) -> str:
    if key in KEYMAP:
        return KEYMAP[key]
    m = PREFIX.match(key)
    # A prefixed key added after this script was written: strip the prefix
    # if refs.bib has the bare key.
    if m and m.group(2) in refs:
        return m.group(2)
    return key


def fix_text(text: str, refs: set[str]) -> tuple[str, list[tuple[str, str]]]:
    changes: list[tuple[str, str]] = []

    def repl(m: re.Match) -> str:
        parts = m.group(2).split(",")
        out = []
        for p in parts:
            key = p.strip()
            new = canonical(key, refs) if key else key
            if new != key:
                changes.append((key, new))
                p = p.replace(key, new)
            out.append(p)
        # drop a key that now appears twice in the same \cite (e.g. cp:x,fd:x)
        seen, dedup = set(), []
        for p in out:
            k = p.strip()
            if k and k in seen:
                continue
            seen.add(k)
            dedup.append(p)
        return m.group(1) + ",".join(dedup) + m.group(3)

    return CITE.sub(repl, text), changes


def cited_keys(text: str) -> set[str]:
    keys = set()
    for m in CITE.finditer(text):
        keys.update(k.strip() for k in m.group(2).split(",") if k.strip())
    return keys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", nargs="+", metavar="FILE",
                    help="section files (basename, e.g. intro.tex) to fix; main.tex is left alone")
    ap.add_argument("--main", action="store_true",
                    help="with --only, also set main.tex to \\bibliography{refs}")
    ap.add_argument("--dry-run", action="store_true", help="report changes, write nothing")
    args = ap.parse_args()

    refs = bib_keys(REFS)
    missing_targets = sorted(set(KEYMAP.values()) - refs)
    if missing_targets:
        print(f"ERROR: refs.bib lacks canonical keys: {missing_targets}", file=sys.stderr)
        return 2

    if args.only:
        files = []
        for name in args.only:
            f = SECTIONS / Path(name).name
            if not f.exists():
                print(f"ERROR: no such section file: {f}", file=sys.stderr)
                return 2
            files.append(f)
    else:
        files = sorted(SECTIONS.glob("*.tex"))

    unresolved: dict[str, set[str]] = {}
    for f in files:
        old = f.read_text(encoding="utf-8")
        new, changes = fix_text(old, refs)
        if changes:
            summary = ", ".join(f"{a}->{b}" for a, b in changes)
            print(f"{f.relative_to(PAPER)}: {len(changes)} key(s): {summary}")
            if not args.dry_run:
                f.write_text(new, encoding="utf-8")
        bad = cited_keys(new) - refs
        if bad:
            unresolved[f.name] = bad

    do_main = (not args.only) or args.main
    if do_main and unresolved:
        print("main.tex NOT changed: some cited keys are missing from refs.bib.", file=sys.stderr)
    elif do_main:
        text = MAIN.read_text(encoding="utf-8")
        new = BIBLIO.sub(r"\\bibliography{refs}", text)
        if new != text:
            print("main.tex: \\bibliography{...} -> \\bibliography{refs}")
            if not args.dry_run:
                MAIN.write_text(new, encoding="utf-8")

    if unresolved:
        print("\nWARNING: cited keys not in refs.bib (add them there):", file=sys.stderr)
        for name, keys in unresolved.items():
            print(f"  {name}: {', '.join(sorted(keys))}", file=sys.stderr)
        return 1
    print("OK: every cited key in the processed files is in refs.bib.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
