"""H03 round 1b: add a `**Verdict (1b):**` line and a dated round-1b block to every replication period README
(round-1 verdict and text kept). Same verdict rules as round 1 (write_period_cards.verdict), applied to the round-1b
period table (corrected exogenous drive from kicks_classified; days split at operator-off gaps >= 60 min).
Idempotent (an existing round-1b block is replaced).
Usage: uv run python hypotheses/H03-self-excited-criticality/analysis/r1b_period_lines.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import polars as pl

HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
D = ROOT / "data/processed/H03-self-excited-criticality"
START, END = "<!-- R1B START -->", "<!-- R1B END -->"


def f(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def ci(r):
    lo, hi = r.get("n_boot_lo"), r.get("n_boot_hi")
    if lo is not None and hi is not None:
        return f"[{f(lo)}, {f(hi)}]"
    lo, hi = r.get("n_prof_lo"), r.get("n_prof_hi")
    return f"[{f(lo)}, {f(hi)}] (profile)"


def main():
    t1 = pl.read_parquet(D / "period_table.parquet")
    tb = pl.read_parquet(D / "r1b/period_table.parquet")
    sm = json.loads((D / "r1b/summary.json").read_text())
    info = json.loads((D / "r1b/build_info.json").read_text())
    days = pl.read_parquet(D / "r1b/days.parquet")
    for g in sorted(tb["goal_no"].unique().to_list()):
        v = sm["verdicts"][str(g)]
        rows = []
        for eset in ("TALK", "ALL"):
            a = t1.filter((pl.col("goal_no") == g) & (pl.col("set") == eset)).to_dicts()[0]
            b = tb.filter((pl.col("goal_no") == g) & (pl.col("set") == eset)).to_dicts()[0]
            rows.append(f"| {eset} | {f(a['n'])} {ci(a)} | **{f(b['n'])} {ci(b)}** | {f(a.get('n_cross_fast'), 3)} | "
                        f"**{f(b.get('n_cross_fast'), 3)}** (shift null {f(b.get('shift_null_fast'), 3)}) | {f(a.get('n_B3'))} → {f(b.get('n_B3'))} |")
        gd = days.filter(pl.col("goal_no") == g)
        split = sorted(set(gd["pt_date"].to_list()) & set(info["split_days"]))
        nexo_old = int(pl.read_parquet(D / "days.parquet").filter(pl.col("goal_no") == g)["n_exo"].sum())
        nexo_new = int(gd["n_exo"].sum())
        line = (f"**Verdict (1b):** {v['r1b']['verdict']} (round 1b, 2026-10-04: n̂ TALK {f(v['r1']['n'])} → {f(v['r1b']['n'])} on "
                f"corrected inputs; {'unchanged verdict' if v['r1']['verdict'] == v['r1b']['verdict'] else 'verdict changed'})")
        block = "\n".join([START, "## Round 1b (improved data, 2026-10-04)",
                           "H03 never read the buggy `activity_bins`; round 1b re-runs the round-1 specification (M1_B2 primary, M3 fast "
                           "self/cross, day bootstrap B = 50 / 25, agent-shift null R = 5) on corrected inputs: exogenous drive from "
                           "`kicks_classified` (human messages + nudges; round 1 also counted the operator's pause/resume bookends) and "
                           f"days split at operator-off gaps ≥ 60 min (`outages_fixed`). Here: exogenous messages in window {nexo_old} → {nexo_new}; "
                           f"split / trimmed days: {', '.join(split) if split else 'none'}.", "",
                           "| Events | n̂ round 1 [95% CI] | **n̂ round 1b** | fast n_x round 1 | **fast n_x round 1b** | n̂ B3 (lower bound) r1 → 1b |",
                           "| --- | --- | --- | --- | --- | --- |", *rows, "",
                           f"Rule: {v['r1b']['why']}. Source: `data/processed/H03-self-excited-criticality/r1b/period_table.parquet` "
                           "(`analysis/r1b.py`).", END])
        p = HYP / f"goalperiod-subhypotheses/G{g:02d}/README.md"
        txt = p.read_text()
        txt = re.sub(r"\n?\*\*Verdict \(1b\):\*\*.*\n", "\n", txt)
        txt = re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", lambda m: m.group(1) + line + "\n", txt, count=1)
        if START in txt:
            txt = txt[:txt.index(START)] + block + txt[txt.index(END) + len(END):]
        else:
            txt = txt.rstrip("\n") + "\n\n" + block + "\n"
        p.write_text(txt)
        print(g, v["r1"]["verdict"], "->", v["r1b"]["verdict"])


if __name__ == "__main__":
    main()
