"""Write the H32 goal-period folders (goalperiod-subhypotheses/G<NN>/README.md and NE42/README.md).

  predict  write each folder's header and dated Prediction section (before any real-data run); verdict pending
  results  fill Verdict, Result and Scorecard from data/processed/H32-information-current-leaders/explore.json,
           keeping the Prediction section verbatim

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/period_folders.py predict|results
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H32-information-current-leaders"
PDIR = HYP / "goalperiod-subhypotheses"
SH = ROOT / "data/processed/shared"
PRED_DATE = "2026-10-03"
MODE = {"C": "shared objective", "I": "each agent its own objective", "F": "free / none", "K": "competition",
        "M": "teams / hidden saboteurs"}


def titles():
    txt = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    out = {}
    for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M):
        out[int(m.group(1))] = m.group(2).strip()
    return out


def period_rows():
    pinfo = json.loads((DATA / "periods.json").read_text())
    msgs = pl.read_parquet(DATA / "messages.parquet").filter(pl.col("kind") == 0)
    rows = []
    for p in pinfo:
        g = p["goal_no"]
        m = msgs.filter(pl.col("goal_no") == g)
        ag = m.filter(pl.col("spk") < 100)
        rooms = ag.group_by("room").len().filter(pl.col("len") >= 20)
        rows.append({**p, "n_agents": ag["spk"].n_unique(), "n_msgs": ag.height, "n_human": int((m["spk"] == 100).sum()),
                     "n_auto": int((m["spk"] == 101).sum()), "n_rooms": rooms.height})
    return rows


def prediction_text(p: dict) -> str:
    g, mode = p["goal_no"], p["mode"]
    L = []
    L.append(f"*Written {PRED_DATE}, before running on this period.* The card's predictions as they apply here.")
    L.append("- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null "
             "(p_T < 0.05). " + ("Mode C, so I expect T at or above the median period." if mode == "C" else
                                 "Mode " + mode + ", so I expect T at or below the median period (P10a)." if mode in ("I", "F") else
                                 "Mode " + mode + ": no mode-specific expectation."))
    if len(p["days"]) >= 4 and p["n_agents"] >= 6:
        L.append("- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.")
    else:
        L.append("- **Stability:** not eligible (needs ≥ 4 days and ≥ 6 agents); heterogeneity by Cochran's Q only (P2).")
    if p["n_human"] >= 15:
        L.append(f"- **Humans as a source (P5, positive control):** {p['n_human']} human messages; the human pseudo-agent's "
                 "Out exceeds the median agent's Out.")
    if p["n_rooms"] >= 2:
        L.append("- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms "
                 "j was not in; the unseen gain's 90% CI includes 0.")
    if g == 26:
        L.append("- **P6a:** over the whole week, DeepSeek-V3.2 (agent 17, the elected leader) is not the top source "
                 "(Out rank > 3 of 10). [0.55]")
        L.append("- **P6b:** after the election decision (2026-01-09 18:59:29 UTC, H11 vote codes) to the end of that day, "
                 "DeepSeek's pooled Out* is the largest of all agents. [0.30]")
    if g == 44:
        L.append("- **P7a:** the temporary leader (agent 28) is not the top source in #best on 05-28/29: pooled Out* rank ≥ 3 "
                 "among the #best agents present. [0.75]")
        L.append("- **P7b:** the operator (human pseudo-agent; 57 messages in #best) is the top source in #best. [0.55]")
        L.append("- **P7c:** same-room pair transfer exceeds cross-room; cross-room ΔG's 90% CI includes 0. [0.70]")
    if g in (39, 40, 41):
        L.append("- **NE42 (P9):** " + ({39: "before the merge: pairs in different rooms here are unexposed, so their ΔG ≈ 0.",
                                          40: "merged week (#universe-coordination): pairs that were split in #39/#41 are "
                                              "exposed here, so their ΔG > 0 and exceeds their #39 and #41 values.",
                                          41: "after the split: the #39 cross-room pairs are again unexposed, ΔG ≈ 0."}[g]))
    if g == 13:
        L.append("- **Coordination week (10 days, 6 agents):** I expect an identifiable, stable top source (Q p < 0.05, "
                 "split-half ρ > 0.3); no ground truth for who it is.")
    L.append("- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 "
             "where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.")
    L.append("- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); "
             "mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests "
             "(P5–P7) decide the verdict where they apply.")
    return "\n".join(L)


def write_predict():
    T = titles()
    for p in period_rows():
        g = p["goal_no"]
        d = PDIR / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        regs = "/".join(p["regimes"])
        rooms = f"{p['n_rooms']} room{'s' if p['n_rooms'] != 1 else ''} with ≥ 20 agent messages"
        why = []
        if g in (26, 44):
            why.append("ground truth for the leader call (card: Candidate goal periods)")
        if p["n_human"] >= 15:
            why.append(f"{p['n_human']} human messages: positive control (humans as a known source)")
        if p["n_rooms"] >= 2:
            why.append("several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival")
        if g in (39, 40, 41):
            why.append("NE42 A-B-A room merge")
        if g == 13:
            why.append("card candidate: a long coordination week")
        if not why:
            why.append(f"mode {p['mode']} ({MODE.get(p['mode'], '?')}) comparison of transfer and centralization")
        txt = f"""# H32 × G{g:02d}: {T.get(g, '?')} ({p['days'][0]} → {p['days'][-1]})

**Verdict:** pending
**Role:** exploratory
**Period:** regime {regs} · mode {p['mode']} ({MODE.get(p['mode'], '?')}) · {p['n_agents']} agents · {rooms} · {len(p['days'])} days. No splits (one unit per goal period).

## Why this period
{'; '.join(why)}.

## Prediction
{prediction_text(p)}

## Result
Pending.

## Scorecard (period-specific axes)
Pending.

## Notes
- {PRED_DATE}: folder and prediction written before any H32 statistic was computed on this period. Counts used: {p['n_msgs']} agent messages, {p['n_human']} human, {p['n_auto']} automated.
"""
        (d / "README.md").write_text(txt)
    ne = PDIR / "NE42"
    (ne / "figures").mkdir(parents=True, exist_ok=True)
    (ne / "figures" / ".gitkeep").touch()
    (ne / "README.md").write_text(f"""# H32 × NE42: #best and #rest merged into #universe-coordination for #40, split back for #41 (2026-04-27 → 2026-05-15)

**Verdict:** pending
**Role:** exploratory
**Period:** regime III · spans #39 (mode I, two rooms), #40 (mode C, merged room), #41 (mode I, two rooms). Goal-confounded: each week has its own goal.

## Why this period
An A–B–A switch of exposure for the pairs that sat in different rooms in #39 and #41: the cleanest exposure manipulation in the non-holdout data (natural-experiments.md, NE42).

## Prediction
*Written {PRED_DATE}, before running on these periods.*
- **P9:** for ordered pairs (i, j) in different rooms in both #39 and #41 and both present in #40, ΔG_ij ≈ 0 in #39 and #41 and > 0 in #40. Test: pair-level sign test of ΔG(#40) − mean(ΔG(#39), ΔG(#41)) > 0, p < 0.10. [0.55]
- **Control:** pairs in the same room throughout show no systematic #40 increase beyond what the goal change gives everyone (difference-in-differences: split pairs' increase > same-room pairs' increase). [0.45]
- **Counts against:** split pairs' #40 ΔG not above their #39/#41 values, or #39/#41 cross-room ΔG clearly > 0 (transfer without exposure, i.e. common drive or cross-room channels such as shared repos).

## Result
Pending.

## Scorecard (period-specific axes)
Pending.

## Notes
- {PRED_DATE}: prediction written before any H32 statistic on #39–#41.
""")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "predict"
    if cmd == "predict":
        write_predict()
    else:
        raise SystemExit("results mode is implemented in write_results.py")
