"""Write H25's goal-period folders: goalperiod-subhypotheses/G<NN>/README.md (+ figures/).

  --predict   write each card with its dated prediction and verdict 'pending' (run BEFORE explore.py)
  --results   keep each card's prediction block verbatim and fill verdict, result table, scorecard and notes
              from data/processed/H25-criticality-dial/{dial_daily, dial_period, period_verdicts}.parquet
Usage: uv run python hypotheses/H25-criticality-dial/analysis/write_period_folders.py --predict | --results
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(C.ROOT / "infra/shared"))
from common import load_goals  # noqa: E402

GP = C.HYP / "goalperiod-subhypotheses"

NOTES = {
    36: "Contains the 2026-03-24 scaffold switch (perma-computer-use) after its first day: the card's P7(a) step test uses it.",
    40: "The merged-rooms week (NE42: #best and #rest merged 05-04, split again 05-11).",
    41: "Starts with the 05-11 room split (NE42).",
    51: "The only 8-hour-day period (most minutes per day, so the tightest daily intervals); private roles; batch joins on 07-09 (NE32) and 09-03 (NE33) are exploratory events. Held-out tail (09-07 onward) excluded.",
    8: "First 3-hour days (07-18): exploratory hours-switch event.",
    18: "First empirical 4-hour days (10-20): exploratory hours-switch event.",
    10: "Batch join (NE27, N 4 → 7) on its first day.",
    21: "Double retirement (NE28) on its first day.",
    37: "First full regime-III period; H16 found a 513-min all-silent gap on 03-31 (a stall the mask should catch).",
    38: "Self-repetition loops (H12: 16–60% self near-copies): content dedupe matters here.",
    39: "Self-repetition loops (H12).",
}


def period_info(cal: pl.DataFrame, meta: pl.DataFrame, refs: pl.DataFrame, goals: dict, g: int) -> dict:
    c = cal.filter(pl.col("goal_no") == g)
    m = meta.filter(pl.col("goal_no") == g)
    r = refs.filter(pl.col("goal_no") == g)
    regs = c["regime"].unique().to_list()
    return {"g": g, "title": goals.get(g, {}).get("goal", "?").split("\n")[0][:110], "start": c["pt_date"].min(), "end": c["pt_date"].max(),
            "days": c.height, "regime": "/".join(sorted(regs)), "mode": m["mode"][0] if m.height else "?",
            "N_start": int(m["N_start"][0]) if m.height else None, "hours": float((c["window_s"].median() or 0) / 3600),
            "h19a": r["h19_active"][0] if r.height else None, "h19t": r["h19_talk"][0] if r.height else None,
            "h19a_se": r["se_h19_active"][0] if r.height else None, "h19t_se": r["se_h19_talk"][0] if r.height else None,
            "n_talk": r["h03_n_talk"][0] if r.height else None}


def fmt(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def prediction_block(p: dict, stamp: str) -> str:
    a, t = p["h19a"], p["h19t"]
    reg3 = "III" in p["regime"]
    lines = [f"*Written {stamp}, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; "
             "H19's per-period values were known (disclosed in the card).",
             f"- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = {fmt(a)} "
             f"(± {fmt(p['h19a_se'])}), lowered by 0–0.05 where stalls are masked: predicted range [{fmt((a or 0) - 0.08)}, {fmt((a or 0) + 0.03)}].",
             f"- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = {fmt(t)}.",
             "- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.",
             "- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.",
             ("- Regime III: activity dial expected higher than in regime I (H19's +0.11), talk dial lower." if reg3 else
              "- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19)."),
             "- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials "
             "with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; "
             "*failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.",
             "- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); "
             "content at or above 0.74 after field removal."]
    if p["days"] <= 3:
        lines.append(f"- Only {p['days']} day(s): low power; the period mean has a wide interval.")
    if p["g"] in NOTES:
        lines.append(f"- {NOTES[p['g']]}")
    return "\n".join(lines)


def card(p: dict, pred: str, verdict="pending", result="Pending (exploratory run not yet done).", score="Pending.", notes="") -> str:
    return f"""# H25 × G{p['g']:02d}: {p['title']} ({p['start']} → {p['end']})

**Verdict:** {verdict}
**Role:** exploratory (round 1, non-holdout)
**Period:** regime {p['regime']} · mode {p['mode']} · {p['N_start']} agents at start · {p['days']} non-holdout days · {p['hours']:.1f} h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active {fmt(p['h19a'])}, talk {fmt(p['h19t'])}; H03 n̂ TALK {fmt(p['n_talk'])}.

## Prediction
{pred}

## Result
{result}

## Scorecard (period-specific axes)
{score}

## Notes
{notes or '- ' + dt.datetime.now(dt.timezone.utc).date().isoformat() + ': folder written by `analysis/write_period_folders.py`.'}
"""


def results_block(g: int, daily: pl.DataFrame, per: pl.DataFrame, pv: pl.DataFrame, figrel: str) -> tuple[str, str, str, str]:
    v = pv.filter(pl.col("goal_no") == g)
    p = per.filter(pl.col("goal_no") == g)

    def row(ch, var):
        x = p.filter((pl.col("channel") == ch) & (pl.col("variant") == var))
        if not x.height:
            return None
        return x.row(0, named=True)
    rows = []
    for ch, var, lab in (("activity", "auto", "activity (stalls masked)"), ("activity", "none", "activity (stalls kept)"),
                         ("talk", "auto", "talk (stalls masked)"), ("talk", "none", "talk (stalls kept)"),
                         ("content", "F1", "content F1"), ("content", "F2", "content F2 (primary)"), ("content", "F3", "content F3")):
        r = row(ch, var)
        if r is None:
            continue
        rows.append(f"| {lab} | {r['k']} | {fmt(r['fe'], 3)} ± {fmt(r['se_fe'], 3)} | {fmt(r['re'], 3)} ± {fmt(r['se_re'], 3)} | "
                    f"{fmt(r['median'], 3)} | {fmt(r['I2'], 2)} (p {fmt(r['p_Q'], 3)}) | {fmt(r['frac_hi_lt_08'], 2)} | {fmt(r['max_lo'], 2)} |")
    vv = v.row(0, named=True) if v.height else {}
    d = daily.filter((pl.col("goal_no") == g) & (pl.col("flag") == "ok"))
    stall = d.filter((pl.col("channel") == "activity") & (pl.col("variant") == "auto"))
    sf = float((stall["stall_min"] / stall["T_day"]).mean()) if stall.height else float("nan")
    tab = ("| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |\n"
           "| --- | --- | --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows))
    checks = (f"\n\n| Check | Observed | Outcome |\n| --- | --- | --- |\n"
              f"| (i) every day subcritical (upper 90% bound < 0.8, all channels) | {'yes' if vv.get('i_subcritical') else 'no'} | {'pass' if vv.get('i_subcritical') else 'fail'} |\n"
              f"| (ii) stalls-kept dials vs H19 g_eq (active {fmt(vv.get('h19_active'))}, talk {fmt(vv.get('h19_talk'))}) | activity {fmt(vv.get('act_none'))}, talk {fmt(vv.get('talk_none'))} | {'pass' if vv.get('ii_h19') else 'fail'} |\n"
              f"| (iii) content F2 median < 0.74 | {fmt(vv.get('content_med'))} | {'pass' if vv.get('iii_content_lt074') else 'fail'} |\n"
              f"| any day confidently near-critical (lower bound > 0.8) | {'yes' if vv.get('any_lo_gt08') else 'no'} | – |\n")
    verdict = vv.get("verdict", "n/a")
    txt = (tab + checks + f"\n\nStall minutes masked: {fmt(100 * sf, 1)}% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): "
           f"{fmt(1 / vv['act']) if vv.get('act') and vv['act'] > 0 else '∞ (g ≤ 0)'}; amplification 1/(1 − g) = {fmt(1 / (1 - vv['act'])) if vv.get('act') is not None and vv['act'] < 1 else '–'}.\n\n"
           f"![daily dial]({figrel})  \nData: `data/processed/H25-criticality-dial/G{g:02d}/dial_daily.parquet`, `results.json`.")
    score = (f"- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = "
             f"{fmt(float((stall['g'] > stall['null_q95']).mean()) if stall.height else float('nan'), 2)}.\n"
             f"- **D (unfitted):** H19 agreement (ii) {'passes' if vv.get('ii_h19') else 'fails'}; H03 n̂ TALK {fmt(vv.get('h03_n_talk'))} vs talk dial {fmt(vv.get('talk'))} (cross-period test in the card).\n"
             f"- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.")
    return verdict, txt, score, ""


def main():
    mode = "--results" if "--results" in sys.argv else "--predict"
    cal = C.calendar_nonholdout()
    meta = C.goal_period_meta()
    refs = pl.read_parquet(C.OUT / "inputs/refs.parquet")
    goals = {g["goal_no"]: g for g in load_goals()}
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if mode == "--results":
        daily = pl.read_parquet(C.OUT / "dial_daily.parquet")
        per = pl.read_parquet(C.OUT / "dial_period.parquet")
        pv = pl.read_parquet(C.OUT / "period_verdicts.parquet")
    for g in sorted(cal["goal_no"].unique().to_list()):
        p = period_info(cal, meta, refs, goals, g)
        gd = GP / f"G{g:02d}"
        (gd / "figures").mkdir(parents=True, exist_ok=True)
        f = gd / "README.md"
        if mode == "--predict":
            if f.exists() and "--force" not in sys.argv:
                continue
            f.write_text(card(p, prediction_block(p, stamp)))
        else:
            old = f.read_text()
            m = re.search(r"## Prediction\n(.*?)\n## Result", old, re.S)
            pred = m.group(1).strip() if m else prediction_block(p, "(missing)")
            verdict, res, score, _ = results_block(g, daily, per, pv, f"figures/G{g:02d}_dial.png")
            notes = (f"- {stamp}: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` "
                     "(exploratory round 1). Prediction block above unchanged from the --predict pass.\n"
                     "- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; "
                     "fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects "
                     "mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).")
            f.write_text(card(p, pred, verdict, res, score, notes))
    print(f"{mode}: wrote {len(cal['goal_no'].unique())} period cards")


if __name__ == "__main__":
    main()
