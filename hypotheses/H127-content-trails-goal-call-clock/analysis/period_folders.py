"""Write H127 period READMEs (goalperiod-subhypotheses/G<NN>/, natives G51 and NE38).

  --init     write the dated predictions (verdict pending) before any run on the period
  (default)  fill verdicts and results from data/processed/H127-content-trails-goal-call-clock/NE34/kickoffs_all_configs.parquet
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GP = HERE.parent / "goalperiod-subhypotheses"
H125 = ROOT / "data/processed/H125-kickoff-damped-oscillator"
DATA = ROOT / "data/processed/H127-content-trails-goal-call-clock"
S = ROOT / "data/processed/shared"
CARD_TS = "2026-10-04 22:18 UTC"
Z = 1.645

PRED_REPL = ("Templated from the card (written {ts}, before any real-data statistic), labelled as such. "
             "Each rising agent's half-alignment time in hours after t₀ falls with its day-1 call rate (Theil–Sen slope s of "
             "log T½^H on log r, near −1), and the spread of log T½ shrinks in calls (CR < 1). "
             "Rule: supported if s < 0 with agent-bootstrap 90% CI below 0 and CR < 1; failed if s ≥ 0; mixed otherwise; "
             "descriptive if fewer than 5 rising agents have a fitted T½. {extra}")

NATIVE = {
    "G51": ("native (+ replication)", "#51 kickoff 2026-07-06: ~21 agents receive private roles at once, with call rates spread "
            "about 7× (H40: 25–184 calls per hour). The own-role excess alignment gives the widest cadence lever in one period.",
            "N1: own-role half-alignment time falls with call rate: Theil–Sen s < 0 with 90% CI below 0 in both models "
            "(credence 0.4). Counts against: s CI contains 0. The shared-kickoff replication (templated rule) is reported beside it."),
    "NE38": ("native", "One agent (Claude Opus 5) is reassigned at 2026-07-29 16:51 UTC while the others keep their roles: an "
             "out-of-sample test of the call-clock constant on an agent whose step was not used to fit it.",
             "N2: Opus 5's measured T½^H (own new role) is closer in |log ratio| to the call-clock prediction "
             "(regime-III replication median T½^C divided by Opus 5's call rate) than to the hour-clock prediction "
             "(regime-III median T½^H), in both models (credence 0.5). Counts against: the hour-clock prediction is closer."),
}


def period_meta():
    pa = pl.read_parquet(S / "period_affordances.parquet").unique("goal_no")
    return {r["goal_no"]: r for r in pa.iter_rows(named=True)}


def init():
    k = pl.read_parquet(H125 / "kickoffs.parquet")
    meta = period_meta()
    for r in k.iter_rows(named=True):
        des, g = r["design"], r["goal_no"]
        if des == "T51":
            continue
        m = meta.get(g, {})
        folder = des if des in ("G51", "NE38") else f"G{g:02d}"
        reg = r["regime"]
        extra = ("Regime I: H40 found neither clock for replies here, so the card expects a weaker slope (S1)."
                 if reg == "I" else "Regimes II–III: H40's call clock holds for replies here.")
        role, why, pred = NATIVE.get(folder, ("replication", "One eligible kickoff (H125's set: shared kickoff, ≥ 5 non-holdout days "
                                              "in one regime). Common estimator, templated rule.",
                                              PRED_REPL.format(ts=CARD_TS, extra=extra)))
        out = GP / folder
        out.mkdir(parents=True, exist_ok=True)
        lines = [f"# H127 × {folder}: {m.get('goal_slug', f'goal {g}')} (step at {r['t0']:%Y-%m-%d %H:%M} UTC)", "",
                 "**Verdict:** pending", f"**Role:** exploratory ({role})",
                 f"**Period:** regime {reg} · mode {r['mode']} · {len(r['incumbents'])} incumbents · {m.get('n_rooms', '?')} room(s). "
                 "Day 1 after the step is the fit window; days 2–5 give the settled level. The step response is the object (exception (c)).", "",
                 "## Why this period", why, "",
                 "## Prediction", f"*Written {CARD_TS} (card) and copied here 2026-10-04 before any run on this period.*", pred, "",
                 "## Result", "(pending)", "",
                 "## Scorecard (period-specific axes)", "(pending)", "",
                 "## Notes", "- Holdout masked (`holdout_mask`); #23 excluded throughout."]
        (out / "README.md").write_text("\n".join(lines) + "\n")
        print("init", folder)


def fmt(x, nd=2):
    return "–" if x is None or x != x else f"{x:+.{nd}f}"


def verdict(r):
    if r["n_fit"] is None or r["n_fit"] < 5 or r["s"] != r["s"]:
        return "descriptive", "fewer than 5 rising agents with a fitted T½"
    if r["s"] >= 0:
        return "failed", "s ≥ 0"
    if r["s_hi"] < 0 and r["CR"] < 1:
        return "supported", "s 90% CI below 0 and CR < 1"
    return "mixed", ("s < 0 but its 90% CI includes 0" if r["s_hi"] >= 0 else "s CI below 0 but CR ≥ 1")


def fill():
    d = pl.read_parquet(DATA / "NE34/kickoffs_all_configs.parquet")
    for des in d.filter(pl.col("cfg") == "bge_white")["design"].unique().sort().to_list():
        g = int(des[1:])
        folder = f"G{g:02d}"
        rows = {c: d.filter((pl.col("design") == des) & (pl.col("cfg") == c)).row(0, named=True)
                for c in d.filter(pl.col("design") == des)["cfg"].to_list()}
        r = rows["bge_white"]
        v, why = verdict(r)
        cfgs = [c for c in ("bge_white", "gte_white", "bge_style", "gte_style") if c in rows]
        tab = ["| Statistic | " + " | ".join(cfgs) + " |", "| --- |" + " --- |" * len(cfgs)]

        def line(name, key, nd=2, ci=None):
            vals = []
            for c in cfgs:
                x = rows[c].get(key)
                s = ""
                if ci and rows[c].get(ci[0]) is not None and rows[c].get(ci[0]) == rows[c].get(ci[0]):
                    s = f" [{rows[c][ci[0]]:+.{nd}f}, {rows[c][ci[1]]:+.{nd}f}]"
                vals.append(fmt(x, nd) + (s if x is not None and x == x else ""))
            tab.append(f"| {name} | " + " | ".join(vals) + " |")
        line("rising / eligible agents", "rise_share")
        line("agents with fitted T½", "n_fit", nd=0)
        line("slope s (log T½^H on log r), 90% CI", "s", ci=("s_lo", "s_hi"))
        line("collapse ratio CR (calls / hours)", "CR")
        line("within-agent clock gain ΔSSE", "dsse")
        line("median T½^H (h)", "med_T_H", nd=3)
        line("median T½^C (calls)", "med_T_C", nd=1)
        line("share immediate from read-out", "imm_ro")
        line("slope from read-out s^ro", "s_ro")
        res = ["\n".join(tab), "", f"Verdict reason (bge, white32): {why}.",
               f"Data: `data/processed/H127-content-trails-goal-call-clock/{folder}/results.json`; all configurations in "
               "`NE34/kickoffs_all_configs.parquet`."]
        sc = [f"- C: {'slope below 0 beyond the agent bootstrap' if v == 'supported' else 'no slope beyond the agent bootstrap' if v in ('mixed', 'failed') else 'not tested'}.",
              "- D: CR (collapse) is an unfitted consequence of slope −1.",
              "- H: read-out rival R_L read from the share of immediate fits from the read-out call."]
        f = GP / folder / "README.md"
        txt = f.read_text()
        txt = txt.replace("**Verdict:** pending", f"**Verdict:** {v}", 1)
        txt = txt.replace("## Result\n(pending)", "## Result\n" + "\n".join(res), 1)
        txt = txt.replace("## Scorecard (period-specific axes)\n(pending)", "## Scorecard (period-specific axes)\n" + "\n".join(sc), 1)
        f.write_text(txt)
        (DATA / folder).mkdir(parents=True, exist_ok=True)
        (DATA / folder / "results.json").write_text(json.dumps(rows, indent=1, default=str))
        print(folder, v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    a = ap.parse_args()
    init() if a.init else fill()


if __name__ == "__main__":
    main()
