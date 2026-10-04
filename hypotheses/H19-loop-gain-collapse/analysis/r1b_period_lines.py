"""H19 round 1b: `**Verdict (1b):**` line + dated round-1b block in every replication period README (round 1 kept).
Same per-period rule as round 1 (LOPO 90% intervals of both primaries under the x_att collapse, and log density vs
the regime-only rival), on the round-1b estimates; reported for the pre-registered E1 (raw g_eq on the corrected
grid) and for the day-edge-adjusted E1 (DQ8 trim). Idempotent.
Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/r1b_period_lines.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import polars as pl

HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
D = ROOT / "data/processed/H19-loop-gain-collapse"
START, END = "<!-- R1B START -->", "<!-- R1B END -->"


def f(x, d=3):
    return "–" if x is None else f"{x:.{d}f}"


def main():
    r1 = json.loads((D / "results/explore.json").read_text())["per_period"]
    raw = json.loads((D / "r1b/results/explore.json").read_text())["per_period"]
    trm = json.loads((D / "r1b/results_trim/explore.json").read_text())["per_period"]
    est = pl.read_parquet(D / "r1b/estimates.parquet")
    old = pl.read_parquet(D / "estimates.parquet")
    for P in sorted(raw):
        g = int(P[1:])
        vr, vt = raw[P]["verdict"], trm[P]["verdict"]
        line = (f"**Verdict (1b):** {vr} (round 1b, 2026-10-04, corrected data, pre-registered E1; with the day-edge-adjusted "
                f"activity gain: {vt}; round 1: {r1[P]['verdict']})")
        rows = ["| Method | Round 1 | **Round 1b** | Round-1b LOPO prediction [90% PI] (raw E1 run) |", "| --- | --- | --- | --- |"]
        for m, lab in (("H19.geq_active", "E1 g_eq active (raw)"), ("H19.geq_active_trim", "E1 g_eq active, DQ8 trim"),
                       ("H19.geq_active_scaf", "E1 g_eq active, H38-conditioned"), ("H19.geq_talk", "E2 g_eq talk"),
                       ("H03.n_talk", "T1 n̂ TALK"), ("H03.nx_fast", "T3 fast n_x")):
            a = old.filter((pl.col("goal_no") == g) & (pl.col("method") == m))
            b = est.filter((pl.col("goal_no") == g) & (pl.col("method") == m))
            pm = raw[P]["methods"].get(m, {})
            pred = f"{f(pm.get('mu'))} [{f(pm.get('lo90'))}, {f(pm.get('hi90'))}]" if "mu" in pm else "–"
            rows.append(f"| {lab} | {f(a['value'][0]) if a.height else '–'} | **{f(b['value'][0]) if b.height else '–'} ± "
                        f"{f(b['se'][0]) if b.height else '–'}** | {pred} |")
        block = "\n".join([START, "## Round 1b (improved data, 2026-10-04)",
                           "H19's own gains re-estimated on `activity_bins_fixed` (+ `outages_fixed`), H02/H03 inputs from their round-1b "
                           "runs; H04's K_week and H05's gains (built on the buggy table, not yet re-run by their owners) are dropped. "
                           "\"DQ8 trim\": all-present window, explained joint silences removed; \"H38-conditioned\": agent-state "
                           "conditioning of day edges, infra errors and consolidations.", "", *rows, "",
                           f"Per-period rule (unchanged): (i) both primaries inside their LOPO 90% intervals: raw run {raw[P]['cond_i']}, "
                           f"trim run {trm[P]['cond_i']}; (ii) log density ≥ regime-only rival: raw {raw[P]['cond_ii']} "
                           f"({raw[P]['lpd_x']:.2f} vs {raw[P]['lpd_regime']:.2f}), trim {trm[P]['cond_ii']}.",
                           "Source: `data/processed/H19-loop-gain-collapse/r1b/results*/explore.json`.", END])
        p = HYP / f"goalperiod-subhypotheses/{P}/README.md"
        if not p.exists():
            continue
        txt = p.read_text()
        txt = re.sub(r"\n?\*\*Verdict \(1b\):\*\*.*\n", "\n", txt)
        txt = re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", lambda m_: m_.group(1) + line + "\n", txt, count=1)
        if START in txt:
            txt = txt[:txt.index(START)] + block + txt[txt.index(END) + len(END):]
        else:
            txt = txt.rstrip("\n") + "\n\n" + block + "\n"
        p.write_text(txt)
        print(P, r1[P]["verdict"], "->", vr, "/", vt)


if __name__ == "__main__":
    main()
