"""H38 round 1b: write the `**Verdict (1b):**` line and a "Round 1b" section into each replication period README
(G<NN>), from the round-1 tables (data/processed/H38-platform-stalls/period_table.parquet, period_results.json) and
the round-1b tables (r1b/period_table.parquet, r1b/period_results.json). Idempotent: an existing 1b line / section is
replaced. Native folders (NE14, NE43, G04's native section) are written by hand.
Usage: uv run python hypotheses/H38-platform-stalls/analysis/r1b_periods.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H38-platform-stalls"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}"


def top_cause(r):
    cs = {c: r.get(f"cause_{c}") or 0 for c in ("scheduled", "edge", "infra_error", "pause", "consolidation", "unexplained")}
    return max(cs, key=cs.get) if any(cs.values()) else "–"


def main():
    old = {r["period"]: r for r in pl.read_parquet(DATA / "period_table.parquet").to_dicts()}
    new = {r["period"]: r for r in pl.read_parquet(DATA / "r1b/period_table.parquet").to_dicts()}
    vo = json.loads((DATA / "period_results.json").read_text())
    vn = json.loads((DATA / "r1b/period_results.json").read_text())
    rows = []
    for p in sorted(new):
        f = HYP / "goalperiod-subhypotheses" / p / "README.md"
        if not f.exists():
            continue
        o, n = old.get(p, {}), new[p]
        v_old, v_new = vo.get(p, {}).get("verdict", "–"), vn[p]["verdict"]
        sig_o = (o.get("z_raw") or 0) > 2; sig_n = (n.get("z_raw") or 0) > 2
        tab = ["| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |", "| --- | --- | --- |",
               f"| joint-silence share (independent expectation) | {fmt(o.get('js'), 3)} ({fmt(o.get('js_exp'), 3)}) | {fmt(n.get('js'), 3)} ({fmt(n.get('js_exp'), 3)}) |",
               f"| explained share (N1 surrogate) | {fmt(o.get('expl'))} ({fmt(o.get('expl_surr'))}) | {fmt(n.get('expl'))} ({fmt(n.get('expl_surr'))}) |",
               f"| largest cause of joint-silence minutes | {top_cause(o)} | {top_cause(n)} |",
               f"| raw g_eq active, E (z vs N1, whole-day grid) | {fmt(o.get('g_raw'), 3)}, {fmt(o.get('E_raw'), 3)} ({fmt(o.get('z_raw'), 1)}) | {fmt(n.get('g_raw'), 3)}, {fmt(n.get('E_raw'), 3)} ({fmt(n.get('z_raw'), 1)}) |",
               f"| f_stall (pre-registered) · f_scaffold (headline) | {fmt(o.get('f_stall')) if sig_o else '–'} · {fmt(o.get('f_mask_scaffold')) if sig_o else '–'} | {fmt(n.get('f_stall')) if sig_n else '–'} · {fmt(n.get('f_mask_scaffold')) if sig_n else '–'} |",
               f"| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | {fmt(n.get('E_trim'), 3)} ({fmt(n.get('z_trim'), 1)}), {fmt(n.get('f_trim')) if sig_n else '–'} |",
               f"| trimmed + scaffold-conditioned: E (z) | not computed | {fmt(n.get('E_trim_scaffold'), 3)} ({fmt(n.get('z_trim_scaffold'), 1)}) |",
               f"| talk spin E raw (z) → trimmed E (z) | {fmt(o.get('tE_raw'), 3)} ({fmt(o.get('tz_raw'), 1)}) | {fmt(n.get('tE_raw'), 3)} ({fmt(n.get('tz_raw'), 1)}) → {fmt(n.get('tE_trim'), 3)} ({fmt(n.get('tz_trim'), 1)}) |",
               f"| per-period verdict (card rule) | {v_old} | {v_new} |"]
        sec = ("## Round 1b (improved data, 2026-10-04)\n"
               "Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared "
               "`outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses "
               "the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; "
               "2–4% after trimming).\n\n" + "\n".join(tab) +
               f"\n\nData: `data/processed/H38-platform-stalls/r1b/{p}/result.json`.\n")
        t = f.read_text()
        line = f"**Verdict (1b):** {v_new} (round 1: {v_old}; corrected tables, same rule)"
        if "**Verdict (1b):**" in t:
            t = re.sub(r"\*\*Verdict \(1b\):\*\*.*", line, t, count=1)
        else:
            t = re.sub(r"(\*\*Verdict:\*\*.*\n)", r"\1" + line.replace("\\", "\\\\") + "\n", t, count=1)
        if "## Round 1b (improved data" in t:
            t = re.sub(r"## Round 1b \(improved data.*?(?=\n## Notes)", sec.rstrip("\n") + "\n", t, flags=re.S)
        else:
            t = t.replace("\n## Notes", "\n" + sec + "\n## Notes", 1)
        f.write_text(t)
        rows.append({"period": p, "regime": n["regime"], "verdict_r1": v_old, "verdict_r1b": v_new})
    df = pl.DataFrame(rows)
    df.write_parquet(DATA / "r1b/verdict_changes.parquet")
    with pl.Config(tbl_rows=60):
        print(df.filter(pl.col("verdict_r1") != pl.col("verdict_r1b")))
    print(df.group_by("verdict_r1b").len())


if __name__ == "__main__":
    main()
