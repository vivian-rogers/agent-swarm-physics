"""Write H86 goal-period READMEs (goalperiod-subhypotheses/G<NN>/, NE14/, NE43/) from the round-1 outputs.

Per-period verdict (templated from the card's P1-P4, applied per unit; rule fixed 2026-10-04 20:22 UTC after the
card-level run, labelled as such in each README):
  failed       a unit has phi_activity,trim >= 0.5 with the within-day shift null p < 0.05 (P4 kill at unit level)
  descriptive  every unit has c_x,raw <= 0.01 (no shared field for trimming to remove)
  supported    c_x,trim < c_x,raw in a majority of units and every unit has phi_activity,trim < 0.3 (the gauge sees
               the scheduler and leaves no unaccounted shared field)
  mixed        otherwise
The HH's own Taylor clauses (b_raw ~ 2) fail in every period; the per-period verdict grades the shared-field gauge.
Usage: uv run python hypotheses/H86-taylor-law-field-gauge/analysis/write_period_cards.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h86lib as L  # noqa: E402

HYP = L.ROOT / "hypotheses/H86-taylor-law-field-gauge"
GP = HYP / "goalperiod-subhypotheses"
CARD_TIME = "2026-10-04 20:05 UTC"


def titles() -> dict:
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def f(x, d=3):
    return "–" if x is None or x != x else f"{x:.{d}f}"


def verdict(w: pl.DataFrame) -> str:
    if ((w["phi_trim"] >= 0.5) & (w["c_xw_p_trim"] < 0.05)).any():
        return "failed"
    if (w["c_x_raw"] <= 0.01).all():
        return "descriptive"
    if (w["c_x_trim"] < w["c_x_raw"]).mean() > 0.5 and (w["phi_trim"].fill_nan(0) < 0.3).all():
        return "supported"
    return "mixed"


def main():
    g = pl.read_parquet(L.DATA / "replication/gauge.parquet")
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet").select("unit_id", "first_day", "last_day", "start")
    ttl = titles()
    act = (g.filter(pl.col("channel") == "activity")
           .pivot(on="grid", index=["unit_id", "goal_no", "regime"], values=["b", "c_T", "c_x", "c_xw", "phi", "c_xw_p", "n_agents"])
           .join(pu, on="unit_id").sort("start"))
    msg = g.filter((pl.col("channel") == "msg") & (pl.col("grid") == "trim")).select("unit_id", pl.col("phi").alias("phi_msg"),
                                                                                       pl.col("b").alias("b_msg"))
    com = g.filter((pl.col("channel") == "commit") & (pl.col("grid") == "trim")).select("unit_id", pl.col("b").alias("b_com"),
                                                                                          pl.col("c_x").alias("cx_com"))
    act = act.join(msg, on="unit_id", how="left").join(com, on="unit_id", how="left")
    for gn in sorted(act["goal_no"].unique().to_list()):
        w = act.filter(pl.col("goal_no") == gn)
        v = verdict(w)
        tab = ["| Unit | agents | b raw / trim | c_T raw / trim | c_× raw / trim | c_×w trim (shift p) | φ raw / trim | φ msg trim | b commit (60 min) |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in w.iter_rows(named=True):
            tab.append(f"| {r['unit_id']} | {int(r['n_agents_raw'] or 0)} | {f(r['b_raw'], 2)} / {f(r['b_trim'], 2)} | "
                       f"{f(r['c_T_raw'])} / {f(r['c_T_trim'])} | {f(r['c_x_raw'])} / {f(r['c_x_trim'])} | "
                       f"{f(r['c_xw_trim'])} ({f(r['c_xw_p_trim'], 2)}) | {f(r['phi_raw'], 2)} / {f(r['phi_trim'], 2)} | "
                       f"{f(r['phi_msg'], 2)} | {f(r['b_com'], 2)} |")
        title = ttl.get(gn, f"goal {gn}")
        txt = f"""# H86 × G{gn:02d}: {title} ({w['first_day'].min()} → {w['last_day'].max()})

**Verdict:** {v}
**Role:** replication (exploratory)
**Period:** regime {'/'.join(sorted(set(w['regime'].to_list())))} · units {', '.join(w['unit_id'].to_list())}.

## Why this period
A replication point for the gauge (layer 1): every eligible unit gets the same Taylor fit and shared-field coefficient, raw and trimmed, so units are comparable points on a field-strength axis.

## Prediction
*Written {CARD_TIME} in the card (templated per unit; the per-period verdict rule in `analysis/write_period_cards.py` was fixed after the card-level run, 2026-10-04 20:22 UTC).*
- Raw activity: Taylor b ≈ 2 with c_T > 0 (HH, P1). Trimmed: b ≤ 1.3 (HH, P2; prior 0.25).
- Shared field: c_× falls under trimming (regime III by 60–90%, regime I < 40%); trimmed φ < 0.3 (no unaccounted shared field).
- *Counts against:* trimmed φ ≥ 0.5 with the within-day shift null p < 0.05 (P4 kill).

## Result
*Run 2026-10-04 20:16 UTC (`analysis/gauge.py` → `data/processed/H86-taylor-law-field-gauge/replication/gauge.parquet`). Activity = records per 15-min bin; CIs in the parquet (day bootstrap; they under-cover, A2).*

{chr(10).join(tab)}

- **Verdict: {v}** (gauge rule). The HH's Taylor clause fails here as everywhere: across agents b is near or below 1 and c_T near or below 0.

## Scorecard (period-specific axes)
- Replication point: informs C (shared share vs the shift null) and I (consistency across units) in the main card.
"""
        d = GP / f"G{gn:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(txt)

    nat = json.loads((L.DATA / "natives/natives.json").read_text())

    def line(r, lab):
        return f"| {lab} | {f(r['before'], 4)} | {f(r['after'], 4)} | {f(r['diff'], 4)} [{f(r['ci'][0], 4)}, {f(r['ci'][1], 4)}] | {r['n_days'][0]} / {r['n_days'][1]} |"

    n14 = nat["NE14"]
    rows = "\n".join(line(n14[k], lab) for k, lab in (("c_x_raw", "c_× raw: II (35, 36a) → III (36b, 36c, 37)"),
                                                       ("c_x_raw_placebo_II", "c_× raw placebo 35 → 36a"),
                                                       ("c_x_raw_placebo_III", "c_× raw placebo 36b/c → 37"),
                                                       ("c_x_trim", "c_× trimmed: II → III"),
                                                       ("c_x_trim_placebo_III", "c_× trimmed placebo 36b/c → 37"),
                                                       ("phi_trim", "φ trimmed: II → III")))
    txt = f"""# H86 × NE14: regime II → III, the always-on computer-use runner (2026-03-24), G35–G37

**Verdict:** failed
**Role:** native (exploratory)
**Period:** units 35, 36a (regime II) and 36b, 36c, 37 (regime III); 12 agents throughout.

## Why this period
H38 found that the regime-III runner's daily start and stop carries 70–80% of co-activation; the switch should add scheduler covariance on raw grids and none on trimmed grids.

## Prediction
*Written {CARD_TIME} in the card.* c_×,raw (activity) rises across the boundary (III − II, day-bootstrap CI > 0); the trimmed change is less than half of the raw change. Placebos 35 → 36a and 36c → 37 move c_×,raw by less than the NE14 change. *Against:* the trimmed change ≥ the raw change.

## Result
*Run 2026-10-04 20:18 UTC (`analysis/natives.py`; daily c_× on 15-min activity bins; day bootstrap of side means, 4,000 draws).*

| Contrast | before | after | difference [95% CI] | days |
| --- | --- | --- | --- | --- |
{rows}

- The raw rise (+0.31) is one day: 2026-03-31 (G37), whose window holds a 513-min all-silent gap (`infra/README.md` known issue), gives c_×,raw = 2.17; every other regime-III day is ≤ 0.03, like regime II. The CI includes 0, and the III → III placebo is larger.
- The trimmed grid is flat across the boundary (+0.001 [−0.007, +0.011]), as predicted.
- **Verdict: failed** for the raw clause (no boundary-specific scheduler jump in count covariance). The "against" condition is not met: trimming removes what raw grids add. Raw c_× is a detector of village-off gaps inside windows.

## Scorecard (period-specific axes)
- E (interventional): the regime switch does not change the shared-field gauge on trimmed grids; the raw gauge reacts to off-gaps, not to the runner.
"""
    (GP / "NE14" / "figures").mkdir(parents=True, exist_ok=True)
    (GP / "NE14" / "README.md").write_text(txt)

    n43 = nat["NE43"]
    rows = "\n".join(line(n43[k], lab) for k, lab in (("c_x_raw_bookends", "c_× raw, bookends stop (51f → 51g)"),
                                                       ("c_x_trim_bookends", "c_× trimmed, bookends stop"),
                                                       ("c_x_trim_nudges", "c_× trimmed, nudges stop (51g → 51h, 51i)"),
                                                       ("c_T_trim_nudges", "c_T trimmed, nudges stop"),
                                                       ("phi_trim_nudges", "φ trimmed, nudges stop")))
    txt = f"""# H86 × NE43: operator bookends stop (2026-08-05), nudges stop (2026-08-21), inside G51

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III; units 51f (07-29 → 08-04), 51g (08-05 → 08-21, two rooms: #general and #focus), 51h–51i (08-24 → 08-31); 26–28 agents.

## Why this period
Two operator drives switch off one after the other while the runner keeps its schedule: a test of what the gauge attributes to the operator.

## Prediction
*Written {CARD_TIME} in the card.* (i) Bookends stop: c_×,raw changes by less than its 95% CI (the runner, not the bookends, drives the day edges). (ii) Nudges stop: c_×,trim does not change (CI includes 0) while c_T,trim rises (idle agents stay idle longer: private variance). *Against:* a c_×,raw drop beyond its CI at 08-05; a c_×,trim change beyond its CI at 08-21.

## Result
*Run 2026-10-04 20:18 UTC (`analysis/natives.py`; daily statistics, day bootstrap of side means).*

| Contrast | before | after | difference [95% CI] | days |
| --- | --- | --- | --- | --- |
{rows}

- (i) passes: the raw shared field does not move when the bookends stop (+0.001 [−0.003, +0.006]).
- (ii) the shared part passes (c_×,trim −0.005 [−0.011, +0.003]); the private part fails: c_T,trim does not rise (+0.008 [−0.034, +0.047]).
- **Verdict: mixed.** The gauge assigns nothing to the operator's bookends or nudges; the predicted private-variance signature of the nudge stop is absent. 51g also adds the #focus room (a confound for (ii)).

## Scorecard (period-specific axes)
- E (interventional): two operator interventions leave the shared-field gauge unchanged, as the scheduler reading predicts.
"""
    (GP / "NE43" / "figures").mkdir(parents=True, exist_ok=True)
    (GP / "NE43" / "README.md").write_text(txt)
    vs = {}
    for p in GP.glob("*/README.md"):
        vv = re.search(r"\*\*Verdict:\*\* (\w+)", p.read_text()).group(1)
        vs[vv] = vs.get(vv, 0) + 1
    print(vs)


if __name__ == "__main__":
    main()
