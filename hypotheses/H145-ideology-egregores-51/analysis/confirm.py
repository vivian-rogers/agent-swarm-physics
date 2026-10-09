"""H145 CONFIRMATORY test on the reserved #51 tail (51m, 2026-09-07 -> 09-18). Written 2026-10-09 after exploratory
round 1. NOT RUN. Runs on reserved days only with BOTH flags and Vivian's sign-off:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` (default) checks the frozen inputs (memeplexes.json md5, rules, element table) and prints the plan. It reads
no reserved day.

Frozen inputs: data/processed/H145-ideology-egregores-51/memeplexes.json (md5 FROZEN_MD5): the 15 memeplexes K01-K15,
their element ids into elements.parquet, the A1 discovery rules. On 51m nothing is rediscovered: the element table is
re-expressed on the reserved days (clusters by nearest frozen k-means centre; the same marker hashes, repo and project
slugs), 2-h bins, DQ8 presence.

Frozen criteria (also in the card, Round 1 "Confirmatory design"):
  C1  Host renewal (P2, amended A4): for the memeplexes that passed P2 in round 1, D_K(5) on 51m is above the
      95th percentile of 200 frequency-matched pseudo-patterns. 51m has 10 days, so k = 3 days replaces k = 5 (fixed now).
  C2  Colonial individuality (P3a, A5): for the memeplexes that passed P3a in round 1, colonial A excess z >= 2 at 2 h
      with E = phase + exogenous messages + role-text field + rest-of-village activity (Besag-Clifford h 10, n_max 200).
  C3  Field control (P4): role-text patterns R0-R5 have colonial A z < 1 on 51m.
Each criterion is evaluated only for the memeplexes named in round 1's results (results/tests.json); no new ones.

Run:   uv run python hypotheses/H145-ideology-egregores-51/analysis/confirm.py --dry-run
Real:  ... --confirm --i-understand-this-uses-the-locked-holdout     (only after Vivian signs off; not implemented
       beyond the guard: the reserved-day panel builder must be written and committed before the run)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H145-ideology-egregores-51"
FROZEN_MD5 = "9b899c34009836b42774e010104f7dda"
RESERVED = ("2026-09-07", "2026-09-18")


def dry_run() -> int:
    p = OUT / "memeplexes.json"
    md5 = hashlib.md5(p.read_bytes()).hexdigest()
    mem = json.loads(p.read_text())
    ok = md5 == FROZEN_MD5
    print(f"memeplexes.json md5 {md5} {'== frozen' if ok else '!= FROZEN (refreeze needed)'}")
    print(f"rules: {mem['rules']}")
    print(f"memeplexes: {[m['id'] for m in mem['memeplexes']]}; role patterns: {[r['id'] for r in mem['role_patterns']]}")
    t = OUT / "results/tests.json"
    if t.exists():
        r = json.loads(t.read_text())
        p2 = [x["id"] for x in r["memeplexes"] if x["P2"]["pass"]]
        p3 = [x["id"] for x in r["memeplexes"] if x["P2"]["pass"] and x["P3"].get("pass_A")]
        print(f"C1 targets (round-1 P2 passes): {p2}\nC2 targets (round-1 P3a passes): {p3}")
    print(f"reserved window {RESERVED[0]} -> {RESERVED[1]} not read (dry run)")
    return 0 if ok else 1


def main():
    a = sys.argv
    if "--confirm" in a:
        if "--i-understand-this-uses-the-locked-holdout" not in a:
            sys.exit("refused: both flags and Vivian's sign-off are required")
        sys.exit("refused: the reserved-day panel builder is not written yet (round 1 froze the criteria only)")
    sys.exit(dry_run())


if __name__ == "__main__":
    main()
