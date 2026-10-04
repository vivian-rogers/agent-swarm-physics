"""H49 goal-period folders.

Replication periods: writes goalperiod-subhypotheses/G<NN>/README.md (templated prediction, labelled as such,
copied from the card's frozen rule; per-unit results table; verdict = majority over units).
Native folders (G44, G51, NE43, NE14) are hand-written; this script only replaces the block between
`<!-- REPLICATION_TABLE -->` and `<!-- /REPLICATION_TABLE -->` with the generated per-unit table.
Also rewrites the card's "Results by goal period" table (between the same kind of markers).

Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/write_period_folders.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
import polars as pl  # noqa: E402
from common import load_goals  # noqa: E402

GP = HYP / "goalperiod-subhypotheses"
DATA = ROOT / "data/processed/H49-dilute-ferromagnet"
NATIVE = {"G44", "G51", "NE43", "NE14"}
PRED_DATE = "2026-10-04 05:50 UTC"


def f(x, d=2):
    try:
        if x is None or x != x:
            return "–"
        return f"{x:.{d}f}"
    except TypeError:
        return str(x)


def unit_rows(df: pl.DataFrame) -> str:
    head = ("| Unit | N | days | + bonds raw → edge → cond. (− cond.) | ⟨k⟩ | κ [boot 95%] | S₁ (cm) | clusters | "
            "g cond. (z) | CV-C10 | mean z (p) | skew (null q95) | verdict |\n|" + " --- |" * 13 + "\n")
    lines = []
    for r in df.sort("unit").iter_rows(named=True):
        lines.append(
            f"| {r['unit']} | {r['N']} | {r['days']} | {r['raw_n_pos']} → {r['edge_n_pos']} → **{r['n_pos']}** ({r['n_neg']}) | "
            f"{f(r['mean_k'])} | {f(r['kappa'])} [{f(r.get('kappa_lo'))}, {f(r.get('kappa_hi'))}] | {f(r['S1'])} ({f(r['S1_cm'])}) | "
            f"{r['clusters'] or '–'} | {f(r['g'], 3)} ({f(r['z_g'], 1)}) | {f(r['cv_c10'])} | {f(r['mean_z'])} ({f(r['p_mean'])}) | "
            f"{f(r['skew'])} ({f(r['q95_skew'])}) | {r['verdict']} |")
    return head + "\n".join(lines) + "\n"


def key_numbers(df: pl.DataFrame) -> str:
    d = df.sort("unit")
    parts = [f"{r['unit']}: {r['n_pos']}/{r['n_pairs']} bonds, κ {f(r['kappa'], 1)}, z_g {f(r['z_g'], 1)}" for r in d.iter_rows(named=True)]
    return "; ".join(parts)


def replication_readme(g: int, df: pl.DataFrame, title: str, verdict: str, power: str = "") -> str:
    reg = df["regime"][0]
    units = ", ".join(df.sort("unit")["unit"].to_list())
    first, last = df["unit"].min(), df["unit"].max()
    role = "hypothesis (regime III)" if reg == "III" else "contrast (regime I)"
    why = ("Regime III: always-on computer use, a daily operator start and stop, CONSOLIDATE every ~40 actions. H38 "
           "found about two thirds of the co-activation here is day-edge infrastructure; H49 asks where the rest "
           "lives." if reg == "III" else
           "Regime I: discrete sessions, message-driven waits. H38 found co-activation is not infrastructure here "
           "(f_scaffold 0.11), so edge trimming should change little: the contrast for P5.")
    if g == 36:
        why += " Only the regime-III side (36b, 36c) is a replication unit; 36a enters NE14."
    pred = (
        f"*Written {PRED_DATE} (card, before any real-data run). Templated: the card's replication rule applied to this "
        f"period; not a period-specific design.*\n"
        f"- Conditioned (edge-trimmed) significant positive bonds ≤ 5% of pairs; ⟨k⟩ < 1; κ < 2 and S₁ ≤ 0.3 "
        f"(below percolation); clusters of ≤ 3 agents.\n"
        f"- If the conditioned collective excess is significant (z > 2): CV-C10 ≥ 0.4 (few pairs carry it).\n"
        + ("- Raw → conditioned: the count of significant positive bonds falls by ≥ 50% (P5, regime III).\n" if reg == "III"
           else "- Raw → conditioned: the count falls by ≤ 25% (P5 contrast, regime I).\n")
        + "- **Unit verdict rule:** supported = ≥ 4 significant positive bonds, κ < 2, S₁ ≤ 0.3 and (if the excess is "
          "significant) CV-C10 ≥ 0.4; failed = κ ≥ 2 or S₁ > 0.3, or a significant excess with CV-C10 ≤ 0.2 (dense); "
          "mixed otherwise (a pure paramagnet with ≤ 3 bonds is mixed). Period verdict = majority over units.\n")
    n_units = df.height
    return f"""# H49 × G{g:02d}: {title}

**Verdict:** {verdict}
**Role:** replication (exploratory)
**Period:** regime {reg} · units {units} · {n_units} eligible unit(s) · {role}. Units are `period_units` with ≥ 2 non-holdout days and ≥ 6 present agents.

## Why this period
{why}

## Prediction
{pred}
## Result
Conditioned pseudolikelihood bonds (`mask_scaffold` agent-state conditioning; 1-min activity spins; 200 joint block-shift surrogates; significant = one-sided empirical p < 1/n_pairs, ≈ 1 false bond per unit). κ = ⟨k²⟩/⟨k⟩ (Molloy–Reed threshold 2); S₁ = largest component / N, in brackets its configuration-model expectation; κ interval = day-block bootstrap (biased upward: each replicate re-adds sampling noise, so null pairs cross the threshold more often; not used for verdicts). CV-C10 is the pooled form (card, Amendment 1); it is unstable when the excess is not significant. All numbers use `activity_bins_fixed` (card, Amendment 2).

{unit_rows(df)}
Data: `data/processed/H49-dilute-ferromagnet/G{g:02d}/<unit>.json`, `bonds/<unit>.parquet`.

{power}

## Scorecard (period-specific axes)
- **C:** bonds tested against joint block-shift surrogates processed identically; internal false-positive count per surrogate ≈ 1 by construction.
- **D:** CV-C10 and the z-shape statistics are not fitted.

## Notes
- Generated by `analysis/write_period_folders.py` from `data/processed/H49-dilute-ferromagnet/unit_table.parquet`.
"""


def power_text() -> str:
    p = DATA / "synthetic/summary.json"
    if not p.exists():
        return ""
    t = {(r["template"], r["cond"], r["recall"]): r for r in json.loads(p.read_text())["table"]}
    g = lambda tpl, c, k: t.get((tpl, c, 1.0), {}).get(k)
    fmt = lambda x: "–" if x is None else f"{x:.2f}"
    return ("**Power caveat (synthetic, axis F):** at village sampling, planted J = 0.5 bonds are recovered with recall "
            f"{fmt(g('40', 'dilute05', 'scaffold_recall'))} (5 × 4 h days, N 15), {fmt(g('44b', 'dilute05', 'scaffold_recall'))} "
            f"(2 days, N 17) and {fmt(g('51d', 'dilute05', 'scaffold_recall'))} (5 × 8 h, N 26); J = 0.25 bonds are nearly invisible. "
            "A percolating graph of J = 0.3 bonds reads as percolating in only "
            f"{fmt(g('40', 'perc', 'perc_detected'))} / {fmt(g('44b', 'perc', 'perc_detected'))} / {fmt(g('51d', 'perc', 'perc_detected'))} "
            "of replicates, and a dense weak ferromagnet looks sub-percolating bond by bond, so a sub-percolating graph is weak "
            "evidence on its own. The mean-z shift, CV-C10 and pair reliability carry the dilute-vs-dense distinction.\n")


def replace_block(text: str, tag: str, body: str) -> str:
    pat = re.compile(rf"<!-- {tag} -->.*?<!-- /{tag} -->", re.S)
    return pat.sub(f"<!-- {tag} -->\n{body}<!-- /{tag} -->", text)


def main():
    goals = {g["goal_no"]: g for g in load_goals()}
    df = pl.read_parquet(DATA / "unit_table.parquet")
    out = json.loads((DATA / "outcomes.json").read_text())
    pv = out["period_verdicts"]
    rep = df.filter(pl.col("kind") == "replication")
    rows = []
    for grp in sorted(rep["group"].unique().to_list(), key=lambda s: int(s[1:])):
        g = int(grp[1:])
        d = rep.filter(pl.col("group") == grp)
        gl = goals[g]
        uu = pl.read_parquet(DATA / "units.parquet").filter(pl.col("group") == grp)
        title = f"{gl['goal'][:80]} ({uu['first_day'].min()} → {uu['last_day'].max()}, non-holdout units)"
        folder = GP / grp
        folder.mkdir(parents=True, exist_ok=True)
        readme = folder / "README.md"
        if grp in NATIVE:
            if readme.exists():
                readme.write_text(replace_block(readme.read_text(), "REPLICATION_TABLE", unit_rows(d)))
            continue
        readme.write_text(replication_readme(g, d, title, pv[grp], power_text()))
        rows.append((grp, "replication", pv[grp], key_numbers(d)))
    # native rows come from their READMEs' Verdict lines
    for nf in sorted(NATIVE):
        p = GP / nf / "README.md"
        if p.exists():
            t = p.read_text()
            v = re.search(r"\*\*Verdict:\*\*\s*(.+)", t).group(1).strip()
            kn = re.search(r"<!-- KEY -->(.*?)<!-- /KEY -->", t, re.S)
            rows.append((nf, "native", v, kn.group(1).strip() if kn else ""))
    order = lambda r: (0 if r[1] == "native" else 1, int(re.sub(r"\D", "", r[0])))
    tbl = "| Period | Role | Verdict | Key numbers |\n| --- | --- | --- | --- |\n" + "\n".join(
        f"| [{p}](goalperiod-subhypotheses/{p}/README.md) | {ro} | {v} | {k} |" for p, ro, v, k in sorted(rows, key=order)) + "\n"
    card = HYP / "README.md"
    card.write_text(replace_block(card.read_text(), "PERIOD_TABLE", tbl))
    print(tbl[:3000])


if __name__ == "__main__":
    main()
