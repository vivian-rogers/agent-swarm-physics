"""H17 confirmatory test on the locked holdout (card P9; written 2026-10-03, NOT run).

P9 (action-class states, pre-registered in the card before any real-data run):
  t2* of #32 above the 75th percentile (numpy linear interpolation) of the regime-I non-holdout periods' t2*, and
  t2* of #45 above the 75th percentile of the regime-III non-holdout periods' t2*.
  t2* = slowest implied timescale at tau_c = 5 active minutes, pooled non-reversible MSM on the H14 coarse minute
  grid over present agent-days (identical code path to the exploratory runs: run_period.analyze).
P9b (added after exploration, before any holdout use; see the card): the same comparison for t2* after trimming
  boundary idle runs (t2_trim_boundary_idle), against the same reference periods.
P9c (added after exploration, before any holdout use): the same comparison for the median per-agent t2 at tau_c
  (agents with >= 2 present days and >= 300 transitions), which is free of the agent-mixture inflation of pooled t2*.
Reference values are read from the frozen exploratory results (data/processed/H17-behavior-metastable-sets/G<NN>/
result.json) and the list of reference periods is fixed in periods.py.

Safety:
  * Refuses to run --confirm if H14's build_states.py (sha256) differs from the one recorded in _provenance.json.
  * Refuses to read holdout days unless BOTH --confirm and --i-understand-this-uses-the-locked-holdout are given.
  * --dry-run runs the identical pipeline on non-holdout stand-ins (#31 for #32, #44 for #45), excluding the
    stand-in from its own reference distribution, and writes to confirm/dryrun_*.json.
  * --jev PATH runs on Jev behavior states (5-min windows, soft probabilities, shifted estimator at 1 window) and
    is refused with --confirm unless the card contains a 'P9-Jev' pre-registration line.

Usage:
  uv run python hypotheses/H17-behavior-metastable-sets/analysis/confirm_h17.py --dry-run
  uv run python hypotheses/H17-behavior-metastable-sets/analysis/confirm_h17.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = CARD.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h17lib as L  # noqa: E402
import run_period as RP  # noqa: E402
from common import git_commit, load_holdout  # noqa: E402
from periods import HOLDOUT_CONFIRM, REGIME1, REGIME3, TAU_C, TAUS_MIN  # noqa: E402

DATA = ROOT / "data/processed/H17-behavior-metastable-sets"
SH = ROOT / "data/processed/shared"
STANDIN = {32: 31, 45: 44}
REF = {"I": REGIME1, "III": REGIME3}


def scheme_module():
    spec = importlib.util.spec_from_file_location("h17_scheme", CARD / "scheme/build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def period_days(goal):
    cal = pl.read_parquet(SH / "calendar.parquet")
    return sorted(cal.filter(pl.col("goal_no") == goal)["pt_date"].to_list())


def agent_median(p):
    v = [a["t2"] for a in p.get("per_agent", []) if a.get("t2") and a["t2"] > 0]
    return float(np.median(v)) if v else None


def reference(regime, exclude=None, key="t2"):
    vals = {}
    for g in REF[regime]:
        if g == exclude:
            continue
        f = DATA / f"G{g:02d}" / "result.json"
        if f.exists():
            pr = json.loads(f.read_text())["primary"]
            vals[g] = agent_median(pr) if key == "t2_agent_median" else pr.get(key)
    return {g: v for g, v in vals.items() if v is not None}


def states_for(goal, holdout: bool):
    if holdout:
        mod = scheme_module()
        _st, sm, _audit = mod.build_for_days(period_days(goal))
        return sm.filter((pl.col("goal_no") == goal) & pl.col("present"))
    return RP.load_min(goal)


def run_one(goal_target, holdout, rng, jev=None):
    goal = goal_target if holdout else STANDIN[goal_target]
    regime = HOLDOUT_CONFIRM[goal_target]
    if jev is None:
        sm = states_for(goal, holdout)
        S = RP.seq_from_min(sm)
        p = RP.analyze(S, RP.COARSE, 1.0, TAUS_MIN, TAU_C, rng, nnull=100, heavy=False)
        xt, st_, frac = L.trim_boundary_state(S["x"], S["seg"], RP.COARSE.index("idle"))
        p["t2_trim_boundary_idle"] = float(L.its_from_C(L.counts(xt, st_, 6, TAU_C), TAU_C)[0])
        p["idle_boundary_frac"] = frac
        p["t2_agent_median"] = agent_median(p)
        key_main, key_trim = "t2", "t2_trim_boundary_idle"
    else:
        df, names, soft, grid = L.load_states(jev, order_col="w", state_col="behavior", prob_json_col="behavior_probs")
        cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
        df = df.join(cal, on="pt_date").filter(pl.col("goal_no") == goal).drop("goal_no")
        S = L.sequences_from_table(df, grid=True, soft=True, q=len(names))
        p = {"t2_shifted": float(L.shifted_its(S["P"], S["seg"], 1, tau0=1)[0] * 5),
             "t2_hard": float(L.its_from_C(L.counts(S["x"], S["seg"], len(names), 1), 1)[0] * 5)}
        key_main, key_trim = "t2_shifted", None
    ref = reference(regime, exclude=None if holdout else goal)
    q75 = float(np.percentile(list(ref.values()), 75))
    res = {"target": goal_target, "analysed_goal": goal, "holdout": holdout, "regime": regime,
           "t2": p.get(key_main), "ref_periods": ref, "ref_q75": q75, "P9_pass": bool(p.get(key_main) is not None and p[key_main] > q75),
           "rank_among_ref": int(sum(v < p[key_main] for v in ref.values())) + 1 if p.get(key_main) is not None else None,
           "n_ref": len(ref)}
    if key_trim:
        ref_t = reference(regime, exclude=None if holdout else goal, key=key_trim)
        q75t = float(np.percentile(list(ref_t.values()), 75))
        res.update({"t2_trim": p[key_trim], "ref_trim_q75": q75t, "P9b_pass": bool(p[key_trim] > q75t),
                    "idle_boundary_frac": p.get("idle_boundary_frac")})
        ref_a = reference(regime, exclude=None if holdout else goal, key="t2_agent_median")
        q75a = float(np.percentile(list(ref_a.values()), 75))
        res.update({"t2_agent_median": p["t2_agent_median"], "ref_agent_q75": q75a,
                    "P9c_pass": bool(p["t2_agent_median"] is not None and p["t2_agent_median"] > q75a)})
    res["details"] = {k: p.get(k) for k in ("t2_ci", "n2_med", "n2_p95", "ck_max", "sets_m2", "m", "I2", "plateau_tau") if k in p}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-builder-change", action="store_true", help="override the H14 builder hash check")
    ap.add_argument("--jev", help="Jev behavior-state parquet (pt_date, agent, w, behavior, behavior_probs)")
    a = ap.parse_args()
    holdout = a.confirm and a.ack
    if a.confirm and not a.ack:
        raise SystemExit("refusing: --confirm also needs --i-understand-this-uses-the-locked-holdout")
    if not holdout and not a.dry_run:
        raise SystemExit("refusing: pass --dry-run (non-holdout stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout")
    if holdout and a.dry_run:
        raise SystemExit("choose one of --dry-run or --confirm")
    if holdout and not a.jev:
        prov = json.loads((DATA / "_provenance.json").read_text())["states"]["params"]
        if scheme_module().builder_sha256() != prov.get("h14_builder_sha256") and not a.allow_builder_change:
            raise SystemExit("refusing: H14's build_states.py changed since the exploratory states were built "
                             "(rebuild the exploratory states and rerun the exploratory round, or pass --allow-builder-change)")
    if holdout and a.jev and "P9-Jev" not in (CARD / "README.md").read_text():
        raise SystemExit("refusing: no 'P9-Jev' pre-registration in the card for Jev states")
    h = load_holdout()
    for g in HOLDOUT_CONFIRM:
        assert g in h["goal_periods_held_out"], f"#{g} is not in the locked holdout list"
    rng = np.random.default_rng(20261003)
    out = {"run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "git_commit": git_commit(),
           "mode": "confirm" if holdout else "dry-run", "states": "jev" if a.jev else "coarse_min", "results": []}
    for g in HOLDOUT_CONFIRM:
        r = run_one(g, holdout, rng, jev=a.jev)
        out["results"].append(r)
        print(f"#{g} ({'holdout' if holdout else 'stand-in #' + str(STANDIN[g])}): t2* = {r['t2']:.1f} min; "
              f"regime-{r['regime']} reference q75 = {r['ref_q75']:.1f}; P9 {'PASS' if r['P9_pass'] else 'FAIL'}"
              + (f"; trimmed t2* = {r['t2_trim']:.1f} vs q75 {r['ref_trim_q75']:.1f}: P9b {'PASS' if r['P9b_pass'] else 'FAIL'}" if 't2_trim' in r else "")
              + (f"; median per-agent t2 = {r['t2_agent_median']:.1f} vs q75 {r['ref_agent_q75']:.1f}: P9c {'PASS' if r['P9c_pass'] else 'FAIL'}" if 't2_agent_median' in r else ""))
    od = DATA / "confirm"
    od.mkdir(parents=True, exist_ok=True)
    name = ("confirm" if holdout else "dryrun") + ("_jev" if a.jev else "") + ".json"
    (od / name).write_text(json.dumps(L.jsonable(out), indent=1))
    print("->", od / name)


if __name__ == "__main__":
    main()
