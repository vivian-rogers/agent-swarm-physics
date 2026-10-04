"""H02 round 1b: add a `**Verdict (1b):**` line and a dated "Round 1b" section to every replication period README
(round-1 verdict and text kept). Verdict rule unchanged (RP1: fraction of significant KI-1 couplings vs N1 >= 8% in a
mode-I week, >= 12% in a mode-C week; supported if every chunk reaches it, mixed if some do, failed if none), applied
to the corrected null (activity_bins_fixed; all-present window and explained joint silences removed before the
surrogates). Idempotent: an existing round-1b block is replaced.
Usage: uv run python hypotheses/H02-couplings-are-real/analysis/r1b_period_lines.py
"""
from __future__ import annotations

import re
from pathlib import Path

import polars as pl

HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
T = pl.read_parquet(ROOT / "data/processed/H02-couplings-are-real/r1b/chunks_1b.parquet")
START, END = "<!-- R1B START -->", "<!-- R1B END -->"


def fmt(x, d=3):
    return "–" if x is None else f"{x:.{d}f}"


def main():
    for g in sorted(T["goal_no"].unique().to_list()):
        sub = T.filter(pl.col("goal_no") == g).sort("chunk")
        mode = sub["mode"][0]
        thr = 0.08 if mode == "I" else 0.12
        f = sub["block_N1_frac_sig__r1b_trim_stall"].to_list()
        hit = [x >= thr for x in f]
        v = "supported" if all(hit) else ("mixed" if any(hit) else "failed")
        cw = [(r["bJ0__r1b_trim_stall"], r["z__r1b_trim_stall"]) for r in sub.iter_rows(named=True)]
        ncw = sum(z > 2 for _, z in cw)
        line = (f"**Verdict (1b):** {v} (round 1b, 2026-10-04, corrected data and DQ8 null: significant-coupling fraction "
                f"{', '.join(fmt(x) for x in f)} vs the {int(thr * 100)}% threshold; collective βJ₀ significant in {ncw}/{len(cw)} chunk(s))")
        rows = ["| Chunk | Frac. sig. r1 | r1b whole grid | **r1b corrected null** | βJ₀ r1 (z) | βJ₀ r1b whole grid (z) | **βJ₀ corrected (z)** | g raw → trimmed → H38-conditioned | kept share |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in sub.iter_rows(named=True):
            rows.append(f"| {r['chunk']} | {fmt(r['block_N1_frac_sig__r1'])} | {fmt(r['block_N1_frac_sig__r1b'])} | **{fmt(r['block_N1_frac_sig__r1b_trim_stall'])}** | "
                        f"{fmt(r['bJ0__r1'], 2)} ({fmt(r['z__r1'], 1)}) | {fmt(r['bJ0__r1b'], 2)} ({fmt(r['z__r1b'], 1)}) | "
                        f"**{fmt(r['bJ0__r1b_trim_stall'], 2)} ({fmt(r['z__r1b_trim_stall'], 1)})** | "
                        f"{fmt(r['g_raw_fixed'], 2)} → {fmt(r['g_trim'], 2)} → {fmt(r['g_scaf'], 2)} | {fmt(r['kept_share'], 2)} |")
        block = "\n".join([START, "## Round 1b (improved data, 2026-10-04)",
                           "Inputs: `activity_bins_fixed` (the round-1 table dropped about half of all events) and `outages_fixed`. "
                           "\"Whole grid\" repeats the round-1 null (N1 block shift on the whole-day grid, which DQ8 found rejects 28–34% of "
                           "independent swarms); \"corrected null\" trims each day to the all-present window and removes explained joint "
                           "silences before drawing the surrogates. g = βJ₀·q; \"H38-conditioned\" is H38's agent-state conditioning "
                           "(from H19's round-1b estimates on the same chunk).", "", *rows, "",
                           "Source: `data/processed/H02-couplings-are-real/r1b/chunks_1b.parquet` (`analysis/r1b_report.py`).", END])
        p = HYP / f"goalperiod-subhypotheses/G{g:02d}/README.md"
        if not p.exists():
            continue
        txt = p.read_text()
        txt = re.sub(r"\n?\*\*Verdict \(1b\):\*\*.*\n", "\n", txt)
        txt = re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", lambda m: m.group(1) + line + "\n", txt, count=1)
        if START in txt:
            txt = txt[:txt.index(START)] + block + txt[txt.index(END) + len(END):]
        else:
            txt = txt.rstrip("\n") + "\n\n" + block + "\n"
        p.write_text(txt)
        print(g, v, f)


if __name__ == "__main__":
    main()
