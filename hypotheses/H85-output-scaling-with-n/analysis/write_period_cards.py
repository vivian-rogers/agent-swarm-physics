"""Write H85 goal-period READMEs (goalperiod-subhypotheses/G<NN>/, NE42/) from the round-1 outputs.

Replication periods: the period's unit points on the cross-unit scaling lines (descriptive: one period cannot test a
slope). Natives: G38 (room contrast), G51 (day sweep), NE42 (merge across G39-G41).
Usage: uv run python hypotheses/H85-output-scaling-with-n/analysis/write_period_cards.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h85lib as L  # noqa: E402

HYP = L.ROOT / "hypotheses/H85-output-scaling-with-n"
GP = HYP / "goalperiod-subhypotheses"
CARD_TIME = "2026-10-04 20:04 UTC"


def titles() -> dict:
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def f(x, d=2):
    return "–" if x is None or x != x else f"{x:.{d}f}"


def unit_table(p: pl.DataFrame) -> str:
    s = ["| Unit | Days | N | T (h) | msg / h | msg per agent-h | addressed / msg | reply share | k at talk | commits per agent-h | resid msg | resid addressed |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in p.iter_rows(named=True):
        NT = r["N"] * r["T_h"]
        s.append(f"| {r['unit_id']} | {r['first_day']} → {r['last_day']} | {f(r['N'], 1)} | {f(r['T_h'], 1)} | {f(r['msg'] / r['T_h'], 1)} | "
                 f"{f(r['msg'] / NT)} | {f(r['ment'] / r['msg'])} | {f(r['reply'] / r['msg'])} | {f(r['k_talk'], 1)} | "
                 f"{f(r['commit'] / NT) if r['git_dense'] else '– (not git-dense)'} | {f(r['resid_msg'])} | {f(r['resid_ment'])} |")
    return "\n".join(s)


def main():
    u = pl.read_parquet(L.DATA / "units.parquet")
    pts = pl.read_parquet(L.DATA / "replication/unit_points.parquet").select("unit_id", "resid_msg", "resid_ment")
    u = u.join(pts, on="unit_id", how="left").sort("start")
    rep = json.loads((L.DATA / "replication/replication.json").read_text())
    nat = json.loads((L.DATA / "natives/natives.json").read_text())
    ttl = titles()
    m1 = rep["levels"]["msg"]["M1"]
    common_pred = (f"*Written {CARD_TIME} in the card, before any real-data statistic (templated replication prediction).*\n"
                   "- This period's units are points on the cross-unit lines ln(Y/T) = α_regime + β ln N. One period cannot test β.\n"
                   "- Card predictions the points feed: messages β ∈ [0.85, 1.15]; addressing per message rises with N as 0.34 γ_k; "
                   "reply parents β ≈ 1.25 (budget-corrected); committed work β = 1.0 ± 0.1 (descriptive after A3).\n"
                   "- *Counts against (card level only):* the cross-unit CIs; a single period's residual is descriptive.")
    for g in sorted(u["goal_no"].unique().to_list()):
        p = u.filter(pl.col("goal_no") == g)
        reg = "/".join(sorted(set(p["regime"].to_list())))
        role, verdict = "replication (exploratory)", "descriptive"
        extra = ""
        if g == 38:
            role = "native (exploratory)"
            v = nat["rooms"]["G38"]
            ok_msg = 0.7 <= v["msg"]["est"] <= 1.3
            verdict = "mixed"
            extra = ("\n## Native N3: within-day room-size contrast (#best vs #rest)\n"
                     f"*Prediction written {CARD_TIME} in the card:* β_room,msg ∈ [0.7, 1.3] and β_room,ment > β_room,msg; "
                     "descriptive if the SD of the within-day log room-size ratio is < 0.1.\n\n"
                     f"- Days: {v['n_days']}; SD of within-day ln(N_2/N_3) {v['sd_dlnN']:.3f} (identified); mean {v['mean_dlnN']:.2f}.\n"
                     f"- β_room,msg = {f(v['msg']['est'])} [{f(v['msg']['ci'][0])}, {f(v['msg']['ci'][1])}] → {'in' if ok_msg else 'outside'} [0.7, 1.3].\n"
                     f"- β_room,ment = {f(v['ment']['est'])} [{f(v['ment']['ci'][0])}, {f(v['ment']['ci'][1])}]; addressing per message "
                     f"{f(v['ment_per_msg']['est'])} [{f(v['ment_per_msg']['ci'][0])}, {f(v['ment_per_msg']['ci'][1])}] (> 0 as predicted, CI includes 0).\n"
                     f"- Pending set: β_room,k = {f(v['k_talk']['est'])} [{f(v['k_talk']['ci'][0])}, {f(v['k_talk']['ci'][1])}] (k ∝ room N).\n"
                     "- Estimator: slope through the origin of the within-day room differences (day fixed effects, no room fixed effect; "
                     "day bootstrap, 2,000 draws). Other rooms-era periods (G36, G42, G44 identified) and their random-effects mean are in the card.\n"
                     "- **Verdict: mixed.** Messages are sublinear in room size (fails [0.7, 1.3]); addressing grows faster than messages (as predicted, not significant).\n")
        if g == 51:
            role = "native (exploratory)"
            verdict = "descriptive"
            v = nat["G51"]["main"]
            extra = ("\n## Native N2: roster-growth sweep (day level)\n"
                     f"*Prediction written {CARD_TIME} in the card:* β_msg ∈ [0.7, 1.3]; β_ment − β_msg > 0; β_commit CI includes 1 "
                     "(day points, NE43 step dummies at 08-05 and 08-21; sensitivity with a linear day trend).\n\n"
                     f"- Non-holdout days: {nat['G51']['n_days']} (n_d {nat['G51']['n_range'][0]}–{nat['G51']['n_range'][1]}); "
                     f"SD ln n_d after steps is small ({nat['G51']['sd_lnn']:.3f}).\n"
                     + "".join(f"- β_{k} = {f(v[k]['est'])} [{f(v[k]['ci'][0])}, {f(v[k]['ci'][1])}]\n" for k in ("msg", "ment", "reply", "commit", "ment_per_msg", "k"))
                     + "- **Verdict: descriptive (unidentified).** Every CI spans more than two units of exponent: day-level N barely varies once "
                     "the NE43 steps are absorbed, and roster joins coincide with time since kickoff.\n")
        title = ttl.get(g, f"goal {g}")
        days = f"{p['first_day'].min()} → {p['last_day'].max()}"
        txt = f"""# H85 × G{g:02d}: {title} ({days})

**Verdict:** {verdict}
**Role:** {role}
**Period:** regime {reg} · mode {p['mode'][0]} · N {f(p['N'].min(), 1)}–{f(p['N'].max(), 1)} active agents · units {', '.join(p['unit_id'].to_list())} · {int(p['n_daysw'].sum())} days with a window.

## Why this period
A point (or points) on the cross-unit scaling lines (layer 1). Each unit contributes one ln(Y/T) at its active population N; the exponent is the slope across units with regime intercepts and goal-cluster CIs (`analysis/replication.py`).

## Prediction
{common_pred}

## Result
*Run 2026-10-04 20:13 UTC (`analysis/replication.py` → `data/processed/H85-output-scaling-with-n/replication/`).* Residuals are from the M1 fits across all 71 units (ln units; positive = above the line). Card-level: β_msg = {m1['beta']:.2f} [{m1['ci_lo']:.2f}, {m1['ci_hi']:.2f}].

{unit_table(p)}
{extra}
## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
"""
        d = GP / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(txt)
    # NE42
    v = nat["NE42"]
    rows = "\n".join(f"| {k} | {f(v[k]['merge_ratio'])} [{f(v[k]['merge_ci'][0])}, {f(v[k]['merge_ci'][1])}] | "
                     f"{f(v[k]['placebo_41_39'])} [{f(v[k]['placebo_ci'][0])}, {f(v[k]['placebo_ci'][1])}] |"
                     for k in ("msg", "ment", "reply", "commit", "talk_calls", "k_talk"))
    txt = f"""# H85 × NE42: #best and #rest merged for one week (2026-05-04 → 05-11), G39 → G40 → G41

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime III · {v['n_agents']} agents present in all three units (39, 40, 41) · room population ≈ {v['room_n_split_mean']:.1f} in the split weeks vs ≈ 15 merged · goal #40 (connect worlds, shared objective) sits inside the merged week.

## Why this period
The same agents meet a doubled room population for one week: an N step without roster change (exception (c): the transition is the object).

## Prediction
*Written {CARD_TIME} in the card.* Per-agent message rate ratio (merged / mean of split weeks) ∈ [0.8, 1.25]; k_talk ratio ≥ 1.5; per-agent addressed-pair ratio = (k ratio)^0.34 ± 0.15 and > 1. Placebo #39 → #41 (no room change): ratios within [0.8, 1.25]. *Against:* k ratio < 1.3, or addressed-pair ratio ≤ 1 with k ratio ≥ 1.5.

## Result
*Run 2026-10-04 20:15 UTC (`analysis/natives.py`). Per-agent rates per present hour; agent bootstrap (2,000).*

| Output | merged / split [95% CI] | placebo #41 / #39 [95% CI] |
| --- | --- | --- |
{rows}

- Predicted addressed-pair ratio from k: {f(v['pred_ment_ratio'])} [{f(v['pred_ment_ci'][0])}, {f(v['pred_ment_ci'][1])}]; observed {f(v['ment']['merge_ratio'])}.
- **The placebo fails badly:** #41 differs from #39 by ×2.5 (messages) to ×7.5 (reply parents) with no room change, so goal effects swamp any N step. The k ratio (1.34, CI includes 1) is below the predicted ≥ 1.5, and addressed pairs do not rise (0.90).
- **Verdict: failed** (design invalid at this resolution; the merge did not visibly enlarge the pending set). Commits per agent-hour rose ×1.45 [1.01, 1.70] in the merged week (placebo 0.81): descriptive, confounded with goal #40.

## Scorecard (period-specific axes)
- E (interventional): not informative (placebo violated).
"""
    (GP / "NE42" / "figures").mkdir(parents=True, exist_ok=True)
    (GP / "NE42" / "README.md").write_text(txt)
    print("written", len(list(GP.glob("*/README.md"))))


if __name__ == "__main__":
    main()
