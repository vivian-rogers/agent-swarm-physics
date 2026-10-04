"""Write H43 replication-layer period folders (goalperiod-subhypotheses/G<NN>/README.md).

  --stage predict   README with Verdict: pending, Role: replication, period facts, structural counts (kick-receiving
                    calls, primers, second kicks; no outcomes) and the templated prediction, dated before the run.
  --stage results   fills the Result section from data/processed/H43-kick-refractory-window/G<NN>/results.json,
                    keeping the prediction text verbatim.
Native folders (NE43, G38, G04) are written by hand and skipped here (G38 and G04 also carry their replication rows,
added by hand from the same results.json).
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/write_period_folders.py --stage predict|results
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402

GP = L.HDIR / "goalperiod-subhypotheses"
NATIVE = {"G38", "G04"}
PRED_DATE = "2026-10-04"


def period_facts(g: int) -> dict:
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter((pl.col("goal_no") == g) & ~pl.col("holdout"))
    calls = pl.read_parquet(L.OUT / "calls.parquet").filter(pl.col("goal_no") == g)
    days = sorted(calls["pt_date"].unique().to_list())
    rooms = sorted({int(r) for rs in pu["rooms"].to_list() for r in rs}) if pu.height else []
    return {"first": days[0], "last": days[-1], "n_days": len(days), "regime": ", ".join(sorted(calls["regime"].unique().to_list())),
            "agents": int(calls["agent"].n_unique()), "units": pu["unit_id"].to_list(), "n_rooms": len(rooms),
            "reasons": [r for r in pu["reason"].to_list()]}


def structural_counts(g: int) -> dict:
    calls, states, writes, cal = L.load_real(g)
    P = L.Prep(calls, states, writes, cal)
    q = P.gt
    elig = P.has_prev & ~P.first_of_day
    quiet = L._count_in(P.any_key, q - L.QUIET_S, q) == 0
    out = {"writes_per_agentday": round(P.writes_per_agentday, 2)}
    for cl in L.CLASSES:
        kc = P.k[cl] > 0
        pure = kc & ((P.k["N"] + P.k["H"] + P.k["A"]) == P.k[cl])
        pr = np.flatnonzero(elig & pure & quiet)
        read = P.idle_at_read[pr] if L.PRIMARY[cl] == "O1" else ~P.idle_at_read[pr]
        tn = L._next_same(q[pr], P.kick_key[cl], P.kick_t[cl], True)
        d = (tn - P.t[pr]) / 60
        sec = np.isfinite(d) & (d <= 240)
        out[cl] = {"kick_calls": int(kc.sum()), "primers": int(len(pr)), "primers_primary_read": int(read.sum()),
                   "second": int(sec.sum())}
    return out


def predict(g: int):
    name = f"G{g:02d}"
    if name in NATIVE:
        return
    f = period_facts(g)
    sc = structural_counts(g)
    powered = [cl for cl in L.CLASSES if sc[cl]["primers_primary_read"] >= 20 and sc[cl]["second"] >= 20]
    lab = {"N": "nudges (O1, idle recipients)", "H": "human messages (O2, busy recipients)",
           "A": "@-mentions (O2, busy recipients)"}
    txt = f"""# H43 × {name}: kick refractory window ({f['first']} → {f['last']})

**Verdict:** pending
**Role:** replication
**Period:** regime {f['regime']} · {f['agents']} agents · {f['n_rooms']} room(s) · {f['n_days']} non-holdout days. Units (matching strata, `period_units`): {', '.join(f['units'])}.

## Why this period
Replication layer: the common estimator on every eligible non-holdout period, so that fitted refractory windows are comparable phase-diagram points. Nothing period-specific is claimed here; the native tests are NE43, G38 and G04.

Structural counts (treatment structure only, no outcomes; primary read state per class; second kicks within 240 min):
| Class | kick-receiving calls | primers (30-min quiet) | in primary read state | second kicks |
| --- | --- | --- | --- | --- |
""" + "\n".join(f"| {cl} | {sc[cl]['kick_calls']} | {sc[cl]['primers']} | {sc[cl]['primers_primary_read']} | {sc[cl]['second']} |" for cl in L.CLASSES) + f"""

Writes per agent-day: {sc['writes_per_agentday']} (O3 computed only if ≥ 1).

## Prediction
*Written {PRED_DATE}, before running on this period. Templated (replication layer; card, "Replication layer").*
Every powered class (≥ 20 primers in the primary read state and ≥ 20 second kicks) whose first-kick effect is positive (E1 day-bootstrap 95% CI above 0) has R(short) < R(long) and a refractory window δ½ within a factor 2 of the median launched-episode length L̃. Powered by structure here: {', '.join(lab[c] for c in powered) if powered else 'none (expected verdict: descriptive)'}. Synthetic power (card, Synthetic validation): only mention curves are resolvable at G51 size; elsewhere expect wide intervals.
Verdict rule: all testable classes pass → supported; none → failed; some → mixed; no testable class → descriptive.

## Result
*Pending.*
"""
    p = GP / name / "README.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    (p.parent / "figures").mkdir(exist_ok=True)
    p.write_text(txt)


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}"


def ci(d):
    if not d:
        return "–"
    return f"{fmt(d.get('est'))} [{fmt(d.get('lo'))}, {fmt(d.get('hi'))}]"


def result_block(res: dict) -> str:
    rows = []
    for cl in L.CLASSES:
        c = res["classes"][cl]
        t = res["tests"][cl]
        o = c.get("outcomes", {}).get(L.PRIMARY[cl], {})
        if not o or "skipped" in o:
            rows.append(f"| {cl} | {L.PRIMARY[cl]} | {c.get('n_primers', 0)} | – | – | – | – | – | {t.get('why', 'no primers')} |")
            continue
        pool = o.get("R_pool", {})
        fit = o.get("fit")
        dh = f"{fmt(fit['delta_half'], 1)} [{fmt(fit['delta_half_lo'], 1)}, {fmt(fit['delta_half_hi'], 1)}]" if fit else "–"
        status = "pass" if t.get("pass") else ("fail" if t.get("testable") else t.get("why", ""))
        rows.append(f"| {cl} | {L.PRIMARY[cl]} | {o['E1']['n']} / {t.get('n_second', 0)} | {ci(o['E1'])} | "
                    f"{ci(pool.get('0-15', {}).get('R'))} | {ci(pool.get('15-60', {}).get('R'))} | "
                    f"{ci(pool.get('60-240', {}).get('R'))} | {dh} vs L̃ {fmt(c.get('L_median'), 0)} | {status} |")
    head = ("| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
    return head + "\n".join(rows)


def results(g: int):
    name = f"G{g:02d}"
    if name in NATIVE:
        return
    p = GP / name / "README.md"
    rj = L.OUT / name / "results.json"
    if not p.exists() or not rj.exists():
        return
    res = json.loads(rj.read_text())
    txt = p.read_text()
    v = res["verdict_templated"]
    txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {v}", txt, count=1)
    body = f"""## Result
Run {res['built_at'][:10]} with `analysis/run_period.py --period {name}` (B = {res['B']} two-way day-block bootstrap draws); numbers in `data/processed/H43-kick-refractory-window/{name}/results.json`.
Effects are pooled log hazard ratios over the outcome window (E1: isolated first kick vs matched no-kick calls; E2: second kick vs post-primer calls without one, same spacing bin). R = E2/E1 with E1 standardized to the second kicks' stratum mix; R is meaningful only where E1 > 0.

{result_block(res)}

Templated verdict: **{v}**. A test "passes" when R(short) < R(long) and δ½ lies within [L̃/2, 2L̃]; "underpowered" or "no first-kick effect" classes do not count.
"""
    txt = re.sub(r"## Result\n.*", body, txt, flags=re.S)
    p.write_text(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["predict", "results"])
    ap.add_argument("--period", default=None)
    a = ap.parse_args()
    import run_period
    gs = [int(a.period.lstrip("G"))] if a.period else run_period.eligible_periods()
    for g in gs:
        (predict if a.stage == "predict" else results)(g)
        print(a.stage, g, flush=True)


if __name__ == "__main__":
    main()
