"""Markdown tables for the H03 card, generated from the processed outputs (no hand transcription).
Run after summarize.py: uv run python hypotheses/H03-self-excited-criticality/analysis/card_tables.py > /tmp/x.md
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl

from common import DATA


def f(x, d=2):
    if x is None:
        return "–"
    if isinstance(x, float) and np.isinf(x):
        return "∞"
    if isinstance(x, float) and not np.isfinite(x):
        return "–"
    return f"{x:.{d}f}"


def main():
    tab = pl.read_parquet(DATA / "period_table.parquet")
    att = pl.read_parquet(DATA / "attribution.parquet")
    jt = pl.read_parquet(DATA / "jitter_table.parquet") if (DATA / "jitter_table.parquet").exists() else None
    tab = tab.join(att.select("goal_no", "set", "frac_exo", "frac_baseline"), on=["goal_no", "set"], how="left")
    if jt is not None:
        tab = tab.join(jt.select("goal_no", "set", "t5_real", "t5_jit600_mean", "n_cross_fast300_shift_mean"),
                       on=["goal_no", "set"], how="left")
    print("#### Per-period fits (M1, B2 + exogenous; TALK | ALL)\n")
    print("| # | mode | reg | days | N | h/day | n̂ TALK [95% day-boot] | τ̂ s | n̂ ALL [95% day-boot] | τ̂ s | "
          "n̂ B0 (naive) T/A | n̂ B3 30-min T/A | n_self≤300s T | n_cross≤300s T (shift null) | exo share T | CV Δℓ/ev T/A |")
    print("|" + "---|" * 16)
    T = tab.filter(pl.col("set") == "TALK").sort("goal_no")
    A = {r["goal_no"]: r for r in tab.filter(pl.col("set") == "ALL").iter_rows(named=True)}
    for r in T.iter_rows(named=True):
        a = A[r["goal_no"]]
        bt = f"{f(r['n'])} [{f(r.get('n_boot_lo'))}, {f(r.get('n_boot_hi'))}]" if r.get("n_boot_lo") is not None else f"{f(r['n'])} [prof {f(r['n_prof_lo'])}, {f(r['n_prof_hi'])}]"
        ba = f"{f(a['n'])} [{f(a.get('n_boot_lo'))}, {f(a.get('n_boot_hi'))}]" if a.get("n_boot_lo") is not None else f"{f(a['n'])} [prof {f(a['n_prof_lo'])}, {f(a['n_prof_hi'])}]"
        print(f"| {r['goal_no']} | {r['mode']} | {r['regime']} | {r['n_days']} | {r['N_active']:.1f} | {r['hours']:.0f} | {bt} | "
              f"{r['tau_s']:.0f} | {ba} | {a['tau_s']:.0f} | {f(r['n_B0'])}/{f(a['n_B0'])} | {f(r['n_B3'])}/{f(a['n_B3'])} | "
              f"{f(r['n_self_fast'])} | {f(r['n_cross_fast'], 3)} ({f(r.get('n_cross_fast300_shift_mean'), 3)}) | "
              f"{f(r['frac_exo'], 3)} | {f(r['cv_B2'], 3)}/{f(a['cv_B2'], 3)} |")
    st = pl.read_parquet(DATA / "segment_table.parquet") if (DATA / "segment_table.parquet").exists() else None
    if st is not None:
        print("\n#### Segments of split periods (goal period × step change; TALK)\n")
        print("| # | seg | start | days | N | n̂ | SE (kind) | n̂ partially pooled | n_cross≤300s |")
        print("|---|---|---|---|---|---|---|---|---|")
        split = st.filter(pl.col("set") == "TALK").group_by("goal_no").len().filter(pl.col("len") > 1)["goal_no"].to_list()
        for r in st.filter((pl.col("set") == "TALK") & pl.col("goal_no").is_in(split)).sort("goal_no", "seg").iter_rows(named=True):
            print(f"| {r['goal_no']} | {r['seg']} | {r['first_date']} | {r['n_days']} | {r['N_active']:.0f} | {f(r['n'])} | "
                  f"{f(r['se'])} ({r['se_kind']}) | {f(r.get('n_shrunk'))} | {f(r['n_cross_fast'], 3)} |")
    res = json.loads((DATA / "summary.json").read_text())
    print("\n#### Key summary numbers\n")
    print("```")
    keep = {k: res[k] for k in ("ladder_median", "cv", "aic", "ks") if k in res}
    print(json.dumps(keep, indent=1)[:6000])
    print("```")


if __name__ == "__main__":
    main()
