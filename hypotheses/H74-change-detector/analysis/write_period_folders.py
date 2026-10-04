"""H74: per-goal-period replication folders (templated from the card, labelled as such) and per-period estimate rows.
Run after run_detector.py: uv run python hypotheses/H74-change-detector/analysis/write_period_folders.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

sys.path.insert(0, str(HERE))
import h74lib as L  # noqa: E402

OUT = ROOT / "data/processed/H74-change-detector"
HYP = ROOT / "hypotheses/H74-change-detector/goalperiod-subhypotheses"
TARGET = {"scaffold_tool", "scaffold_prompt", "scaffold_family", "operator", "operator_schedule", "undocumented"}
METHOD = ("H74 round 1: daily fused change-point score Z = max(S schema, M synchronous within-agent mix, O oracle format, "
          "D drive/schedule, C content R1 bge+gte); robust trailing z (10 active days); alarm at Z >= 4; hit = alarm on day -1..+1")


def wilson(k, n, z=1.96):
    if n == 0:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def main():
    sc = pl.read_parquet(OUT / "scores.parquet")
    res = json.loads((OUT / "replication" / "results.json").read_text())
    placebo = set(res["placebo_days"])
    ev = pl.read_parquet(OUT / "events.parquet").filter(~pl.col("held0"))
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter(pl.col("n_agent_events") > 0).sort("pt_date")
    cal_days = cal["pt_date"].to_list()
    day_pos = {d: i for i, d in enumerate(sc["pt_date"].to_list())}
    wm = L.window_array(sc["z_F"].to_numpy(), cal_days, day_pos)
    cpos = {d: i for i, d in enumerate(cal_days)}
    cp = pl.read_parquet(OUT / "replication" / "changepoints.parquet")
    rows, table = [], []
    for (g,), d in sc.sort("pt_date").group_by("goal_no", maintain_order=True):
        days = d["pt_date"].to_list()
        e = ev.filter(pl.col("day0").is_in(days))
        e = e.with_columns(pl.Series("w", [float(wm[cpos[x]]) for x in e["day0"].to_list()], dtype=pl.Float64))
        tgt = e.filter(pl.col("cls").is_in(list(TARGET)))
        nh = int((tgt["w"].fill_nan(None).fill_null(-1) >= L.TAU).sum())
        pd = [x for x in days if x in placebo]
        nfa = int((d.filter(pl.col("pt_date").is_in(pd))["z_F"].fill_nan(None).fill_null(-1) >= L.TAU).sum())
        far = nfa / len(pd) if pd else None
        n_alarm = int((d["z_F"].fill_nan(None).fill_null(-1) >= L.TAU).sum())
        if tgt.height == 0:
            verdict = "descriptive"
        elif nh == tgt.height and (far is None or far <= 0.10):
            verdict = "supported"
        elif nh == 0:
            verdict = "failed"
        else:
            verdict = "mixed"
        goal = e.filter(pl.col("cls") == "goal")
        gtxt = ", ".join(f"{x[:10]} (Z {w:.1f})" for x, w in zip(goal["day0"].to_list(), goal["w"].to_list())) or "none in scored days"
        unexpl = cp.filter(pl.col("pt_date").is_in(days) & pl.col("explained_by").is_null())
        folder = HYP / f"G{g:02d}"
        (folder / "figures").mkdir(parents=True, exist_ok=True)
        lines = [f"| {r['day0']} | {r['cls'].replace('_', ' ')} | {r['label'][:70].replace('|', '/')} | {r['w']:.1f} | {'hit' if r['w'] >= L.TAU else 'miss'} |"
                 for r in tgt.sort("day0").iter_rows(named=True)] or ["| – | – | no scaffold, operator or undocumented event with a non-holdout day 0 | – | – |"]
        ulines = [f"- {r['pt_date']}: Z {r['Z']:.1f}, channel {r['channel']}{' (' + r['feature'] + ')' if r['feature'] else ''}"
                  for r in unexpl.iter_rows(named=True)] or ["- none"]
        role = "replication"
        regime = "/".join(sorted(set(d["regime"].to_list())))
        text = f"""# H74 × G{g:02d}: daily change detector on goal period #{g} ({days[0]} → {days[-1]}, non-holdout days)

**Verdict:** {verdict}
**Role:** {role}
**Period:** regime {regime} · {len(days)} non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = {g}). Fused alarm days: {n_alarm}/{len(days)}. Placebo days: {len(pd)}, false alarms {nfa}{f' (FAR {far:.2f})' if far is not None else ''}.

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
""" + "\n".join(lines) + f"""

Goal kickoffs (not part of the rule): {gtxt}.

Unexplained alarms (no catalogued event within ±1 active day):
""" + "\n".join(ulines) + """

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
"""
        (folder / "README.md").write_text(text)
        unit = E.map_unit(int(g))
        base = {"period_unit": unit, "goal_no": int(g), "method": METHOD, "role": "replication",
                "first_day": days[0], "last_day": days[-1], "source": "data/processed/H74-change-detector/scores.parquet",
                "null": "trailing 10-active-day baseline; placebo days >= 3 active days from every catalogued event"}
        lo, hi = wilson(n_alarm, len(days))
        rows.append({**base, "statistic": "fused_alarm_day_rate", "channel": "multi", "estimate": n_alarm / len(days),
                     "ci_lo": lo, "ci_hi": hi, "ci_kind": "parametric", "ci_level": 0.95, "n": len(days), "n_kind": "scored days",
                     "notes": "Wilson interval"})
        if tgt.height:
            lo, hi = wilson(nh, tgt.height)
            rows.append({**base, "statistic": "platform_event_hit_rate", "channel": "multi", "estimate": nh / tgt.height,
                         "ci_lo": lo, "ci_hi": hi, "ci_kind": "parametric", "ci_level": 0.95, "n": tgt.height,
                         "n_kind": "scaffold/operator/undocumented events", "notes": "Wilson interval"})
        if pd:
            lo, hi = wilson(nfa, len(pd))
            rows.append({**base, "statistic": "placebo_far_per_day", "channel": "multi", "estimate": far, "ci_lo": lo, "ci_hi": hi,
                         "ci_kind": "parametric", "ci_level": 0.95, "n": len(pd), "n_kind": "placebo days", "notes": "Wilson interval"})
        table.append({"goal_no": int(g), "verdict": verdict, "n_days": len(days), "n_target": tgt.height, "n_hit": nh,
                      "n_placebo": len(pd), "n_fa": nfa, "n_alarm": n_alarm})
    E.write_estimates(rows, hypothesis="H74")
    pl.DataFrame(table).write_parquet(OUT / "replication" / "period_table.parquet")
    print(pl.DataFrame(table))


if __name__ == "__main__":
    main()
