"""H94 round-1 analysis per goal period (non-holdout quanta built by scheme/build.py).

  uv run python hypotheses/H94-maxent-work-allocation/analysis/run.py --period 31 [--period ...] [--draws 200]
  uv run python hypotheses/H94-maxent-work-allocation/analysis/run.py --native g44|g40

Per unit: max-ent hierarchy D0-D3 (bits per quantum), floors (Patefield, parametric, run-preserving persistence),
ownership and room prices with agent-block bootstrap CIs, kappa (episodes; quanta variant), signatures under M1/M2.
Units with < 100 quanta, < 3 agents or < 3 repos are descriptive (hierarchy and kappa only, no floors).
Variants (hierarchy only): owner = first committer in the period; quanta = commits; quanta = agent-days.
Writes results/G<NN>.json (and native_G44.json, native_G40.json).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h94lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

DATA = ROOT / "data/processed/H94-maxent-work-allocation"
OWN_UNITS = {"39", "42a", "42b", "44a", "44b"} | {f"51{c}" for c in "abcdefghijkl"}


def labs() -> dict:
    return dict(pl.read_parquet(ROOT / "data/processed/shared/roster.parquet", columns=["agent", "lab"]).iter_rows())


def load(g: int) -> pl.DataFrame:
    q = pl.read_parquet(DATA / f"G{g:02d}" / "quanta.parquet")
    assert not any(holdout_mask(q["pt_date"].to_list(), [g] * q.height)), "held-out rows in exploratory input"
    return q


def testable(q: pl.DataFrame) -> bool:
    return q.height >= 100 and q["agent"].n_unique() >= 3 and q["repo"].n_unique() >= 3


def light(q: pl.DataFrame, two: bool, lb, own_col="own") -> dict:
    t = L.unit_table(q, own_col, lb)
    h = L.hierarchy(t, two)
    h.pop("_mu")
    h["kappa"] = L.kappa(L.run_counts(t))["kappa"]
    return h


def expand_commits(q: pl.DataFrame) -> pl.DataFrame:
    return q.with_columns(pl.int_ranges(0, pl.col("n_commits")).alias("_k")).explode("_k").drop("_k")


def agent_days(q: pl.DataFrame) -> pl.DataFrame:
    return q.sort("win").unique(subset=["agent", "pt_date", "repo"], keep="first")


def analyse_units(q: pl.DataFrame, draws: int, lb) -> dict:
    out = {}
    for (u,), qu in q.group_by(["unit"], maintain_order=True):
        two = qu["room_mode"].drop_nulls().n_unique() > 1
        ok = testable(qu)
        if ok:
            r = L.unit_analysis(qu, two, draws=draws, seed=sum(map(ord, str(u))), labs=lb)
        else:
            r = light(qu, two, lb) if qu["repo"].n_unique() >= 2 and qu["agent"].n_unique() >= 2 else {}
        r["testable"] = ok
        r["two_rooms"] = two
        r["own_unit"] = u in OWN_UNITS
        try:
            r["var_own_period"] = light(qu, two, lb, "own_period") if qu["repo"].n_unique() >= 2 else None
            r["var_commits"] = light(expand_commits(qu), two, lb) if qu["repo"].n_unique() >= 2 else None
            r["var_agentday"] = light(agent_days(qu), two, lb) if qu["repo"].n_unique() >= 2 else None
        except Exception as e:  # noqa: BLE001
            r["variant_error"] = str(e)
        out[str(u)] = r
    return out


def summarise(units: dict) -> dict:
    """Quanta-weighted means over testable units (descriptive units excluded), next to per-unit values."""
    ok = {u: r for u, r in units.items() if r.get("testable")}
    if not ok:
        return {"testable_units": 0}
    w = np.array([r["N"] for r in ok.values()])

    def wm(key, sub=None):
        v = [(r[key] if sub is None else (r[key] or {}).get(sub)) for r in ok.values()]
        m = [(x, ww) for x, ww in zip(v, w) if x is not None and np.isfinite(x)]
        return float(sum(x * ww for x, ww in m) / sum(ww for _, ww in m)) if m else None
    s = {k: wm(k) for k in ("D0", "D1", "D2", "D3", "floor1", "pfloor1", "floor2", "pfloor2", "pfloor3", "lam_own",
                             "own_share", "room_share", "resid_share", "resid_share_persist", "D1_minus_floor")}
    s["kappa"] = wm("kappa", "kappa")
    s["kappa_no_named"] = wm("kappa_no_named", "kappa")
    s["breadth_M2"] = wm("sig_M2", "breadth_ratio")
    s["reach_top3_M2"] = wm("sig_M2", "reach_ratio_top3")
    s["testable_units"] = len(ok)
    s["N"] = float(w.sum())
    return s


def native_g44(draws: int, lb) -> dict:
    """Arms by the agent's modal room in the unit (#best = room 2, #rest = room 3 in #44)."""
    q = load(44)
    out = {}
    for (rm,), qa in q.filter(pl.col("room_mode").is_not_null()).group_by(["room_mode"]):
        r = L.unit_analysis(qa, False, draws=draws, seed=int(rm), labs=lb) if testable(qa) else light(qa, False, lb)
        r["testable"] = testable(qa)
        r["agents"] = qa["agent"].n_unique()
        r["repos"] = qa["repo"].n_unique()
        top = qa.group_by("repo").len().sort("len", descending=True)
        r["top_share"] = float(top["len"][0] / qa.height)
        out[str(rm)] = r
    return out


def native_g40(draws: int, lb) -> dict:
    out = {}
    for g in (39, 40):
        q = load(g)
        two = q["room_mode"].drop_nulls().n_unique() > 1
        r = L.unit_analysis(q, two, draws=draws, seed=g, labs=lb)
        top = q.group_by("repo").agg(pl.len(), pl.col("named").first()).sort("len", descending=True)
        r["top_share"] = float(top["len"][0] / q.height)
        r["top_named"] = bool(top["named"][0])
        r["own_quanta_share"] = float(q["own"].mean())
        out[f"G{g}"] = r
    # difference in lambda_own with an agent-block bootstrap over the agents present in both weeks
    out["d_lam_own"] = out["G40"]["lam_own"] - out["G39"]["lam_own"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--native", action="append", choices=["g44", "g40"])
    ap.add_argument("--draws", type=int, default=200)
    a = ap.parse_args()
    (DATA / "results").mkdir(parents=True, exist_ok=True)
    lb = labs()
    for g in a.period or []:
        units = analyse_units(load(g), a.draws, lb)
        res = {"goal_no": g, "units": units, "summary": summarise(units)}
        (DATA / "results" / f"G{g:02d}.json").write_text(json.dumps(res, indent=1, default=float))
        s = res["summary"]
        print(g, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()}, flush=True)
    for n in a.native or []:
        r = native_g44(a.draws, lb) if n == "g44" else native_g40(a.draws, lb)
        (DATA / "results" / f"native_{n.upper()}.json").write_text(json.dumps(r, indent=1, default=float))
        print(n, "done", flush=True)


if __name__ == "__main__":
    main()
