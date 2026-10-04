"""Write H125 period READMEs (goalperiod-subhypotheses/G<NN>/, natives G51, NE38, G38).

  --init     write the dated predictions (verdict pending) before any run on the period
  (default)  fill verdicts and results from data/processed/H125-kickoff-damped-oscillator/NE34/kickoffs_all_configs.parquet
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GP = HERE.parent / "goalperiod-subhypotheses"
DATA = ROOT / "data/processed/H125-kickoff-damped-oscillator"
S = ROOT / "data/processed/shared"
CARD_TS = "2026-10-04 22:16 UTC"
Z = 1.645

PRED_REPL = ("Templated from the card (written {ts}, before any real-data statistic), labelled as such. "
             "After the step at t₀ the within-agent excess alignment along k̂ overshoots on day 1 (E₁ > 0, H97/H54) and, "
             "under HH366's inertia, swings below its days 4–5 level on days 2–3: undershoot U > 0. "
             "Rule: supported if U > 0 with jackknife 90% CI above 0 and U above the 95th percentile of the pooled "
             "placebo-day U (bge, white32); failed if U ≤ 0; mixed otherwise; descriptive if fewer than 4 agents have both day pairs. "
             "The card's credence for an undershoot is 0.2, so the expected verdict here is failed or mixed.")

NATIVE = {
    "G51": ("native", "#51 kickoff 2026-07-06: ~21 agents receive private roles at once. Each agent has its own target, "
            "so the own-role excess alignment (decoys = the other agents' roles) gives a step response with N ≈ 21, "
            "the largest single-kickoff N in the data.",
            "N1: own-role excess alignment undershoots: U_own > 0 with 90% CI above 0 in both models (credence 0.15). "
            "Counts against: U_own ≤ 0 or CI includes 0. H54 saw no decay of own-goal alignment over 9 weeks, so a flat "
            "response is the expectation."),
    "NE38": ("native", "One agent (Claude Opus 5) is reassigned (word puzzles → mathematics) at 2026-07-29 16:51 UTC while "
             "~26 others keep their roles: a one-spin step field with a same-day placebo population.",
             "N2: Opus 5's own-new-role alignment overshoots on day 1 and undershoots on days 2–3: its U exceeds the 90th "
             "percentile of the other #51 agents' own-role U over the same days, in both models (credence 0.15). "
             "Counts against: Opus 5's U within the others' range."),
    "G38": ("native (+ replication)", "Longest regime-III period with a shared kickoff (17 non-holdout days, 12 incumbents): "
            "room for a second swing of a ringing response.",
            "N3: on days 1–10, M_osc beats M_fade (ΔSSE > 0) with ζ_fit < 1 in both models (credence 0.15). "
            "Counts against: M_fade wins in either model. The templated replication rule also applies to days 1–5."),
}


def period_meta():
    pa = pl.read_parquet(S / "period_affordances.parquet").unique("goal_no")
    return {r["goal_no"]: r for r in pa.iter_rows(named=True)}


def init():
    k = pl.read_parquet(DATA / "kickoffs.parquet")
    meta = period_meta()
    for r in k.iter_rows(named=True):
        des, g = r["design"], r["goal_no"]
        m = meta.get(g, {})
        folder = des if des in ("G51", "NE38") else f"G{g:02d}"
        if des == "T51":
            folder = "G51"      # the G51 folder holds the native (own roles) and the shared-kickoff replication
        out = GP / folder
        out.mkdir(parents=True, exist_ok=True)
        f = out / "README.md"
        if des == "T51":
            continue            # written with the native
        role, why, pred = NATIVE.get(folder, ("replication", "One eligible kickoff (shared kickoff, ≥ 5 non-holdout days in one regime). "
                                              "Common estimator, templated rule.", PRED_REPL.format(ts=CARD_TS)))
        if folder == "G51":
            pred += " The shared-kickoff replication (templated rule) is reported beside it."
        title = m.get("goal_slug", f"goal {g}")
        lines = [f"# H125 × {folder}: {title} (step at {r['t0']:%Y-%m-%d %H:%M} UTC)", "",
                 "**Verdict:** pending", f"**Role:** exploratory ({role})",
                 f"**Period:** regime {r['regime']} · mode {r['mode']} · {len(r['incumbents'])} incumbents · "
                 f"{m.get('n_rooms', '?')} room(s) · {r['n_days']} non-holdout days analysed from day 1. "
                 "The step response is the object (exception (c)).", "",
                 "## Why this period", why, "",
                 "## Prediction", f"*Written {CARD_TS} (card) and copied here 2026-10-04 before any run on this period.*", pred, "",
                 "## Result", "(pending)", "",
                 "## Scorecard (period-specific axes)", "(pending)", "",
                 "## Notes", "- Holdout masked (`holdout_mask`); #23 excluded throughout."]
        f.write_text("\n".join(lines) + "\n")
        print("init", folder)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    a = ap.parse_args()
    if a.init:
        init()
        return
    fill()


def fmt(x, nd=3):
    return "–" if x is None or x != x else f"{x:+.{nd}f}"


def verdict(r):
    if r["n_u"] is None or r["n_u"] < 4 or r["U"] != r["U"]:
        return "descriptive", "fewer than 4 agents with both day pairs"
    lo = r["U"] - Z * r["se_U"]
    if r["U"] <= 0:
        return "failed", "U ≤ 0 (no undershoot)"
    if lo > 0 and r["U"] > r["placebo_q95"]:
        return "supported", "U 90% CI above 0 and above the placebo 95th percentile"
    return "mixed", ("U > 0 but its 90% CI includes 0" if lo <= 0 else "U CI above 0 but within the placebo-day range")


def fill():
    d = pl.read_parquet(DATA / "NE34/kickoffs_all_configs.parquet")
    meta = period_meta()
    for des in d.filter(pl.col("cfg") == "bge_white")["design"].unique().sort().to_list():
        g = int(des[1:])
        folder = f"G{g:02d}"
        rows = {c: d.filter((pl.col("design") == des) & (pl.col("cfg") == c)).row(0, named=True)
                for c in d.filter(pl.col("design") == des)["cfg"].to_list()}
        r = rows["bge_white"]
        v, why = verdict(r)
        f = GP / folder / "README.md"
        txt = f.read_text()
        cfgs = [c for c in ("bge_white", "gte_white", "bge_style", "gte_style", "bge_dedupe", "gte_dedupe") if c in rows]
        tab = ["| Statistic | " + " | ".join(cfgs) + " |", "| --- |" + " --- |" * len(cfgs)]

        def line(name, key, sek=None, nd=3):
            vals = []
            for c in cfgs:
                x = rows[c].get(key)
                s = f" ± {abs(rows[c].get(sek)):.{nd}f}" if sek and rows[c].get(sek) == rows[c].get(sek) and rows[c].get(sek) is not None else ""
                vals.append(fmt(x, nd) + (s if x is not None and x == x else ""))
            tab.append(f"| {name} | " + " | ".join(vals) + " |")
        line("undershoot U (days 4–5 − days 2–3)", "U", "se_U")
        line("overshoot E₁ (day 1 − days 4–5)", "E1", "se_E1")
        line("placebo-day U, 95th pct (pooled)", "placebo_q95")
        line("decoy-direction percentile π_U", "pi_U", nd=2)
        line("ΔSSE (M_fade − M_osc)/M_fade", "dsse", nd=3)
        line("ζ_fit (M_osc)", "zeta_fit", nd=2)
        line("ζ_pk (peak ratio; ≥ 1 if U ≤ 0)", "zeta_pk", nd=2)
        res = ["\n".join(tab), "",
               f"Verdict reason (bge, white32): {why}. Agents with both day pairs: {r['n_u']}. "
               f"Human messages days 4–5 minus days 2–3: {r.get('human_diff')}.",
               f"Data: `data/processed/H125-kickoff-damped-oscillator/{folder}/results.json`; all configurations in "
               "`NE34/kickoffs_all_configs.parquet`. Day profile: `NE34/series.json`."]
        sc = [f"- C: {'U beats the placebo-day null' if v == 'supported' else 'no undershoot beyond the placebo-day null' if v in ('mixed', 'failed') else 'not tested'}.",
              "- D: U and ζ_pk are unfitted signatures of M_osc (U ≤ 0 and ζ ≥ 1 under M_fade).",
              f"- H: M_osc vs M_fade ΔSSE {fmt(r['dsse'])} ({'M_osc' if (r['dsse'] or 0) > 0 else 'M_fade'} wins, bge white32)."]
        txt = txt.replace("**Verdict:** pending", f"**Verdict:** {v}", 1)
        txt = txt.replace("## Result\n(pending)", "## Result\n" + "\n".join(res), 1)
        txt = txt.replace("## Scorecard (period-specific axes)\n(pending)", "## Scorecard (period-specific axes)\n" + "\n".join(sc), 1)
        f.write_text(txt)
        (DATA / folder).mkdir(parents=True, exist_ok=True)
        (DATA / folder / "results.json").write_text(json.dumps({c: {k: v_ for k, v_ in rr.items() if not isinstance(v_, list)}
                                                              for c, rr in rows.items()}, indent=1, default=str))
        print(folder, v)


if __name__ == "__main__":
    main()
