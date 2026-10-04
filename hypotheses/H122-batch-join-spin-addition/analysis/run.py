"""H122 real-data run: every eligible non-holdout join event (replication + natives NE27, NE32), the regime-I
kickoff-matched placebo for NE27, and per-event verdicts.

    uv run python hypotheses/H122-batch-join-spin-addition/analysis/run.py [--boot 2000] [--pboot 200]

Output: data/processed/H122-batch-join-spin-addition/results/{events,placebo}.parquet, summary.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h122lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H122-batch-join-spin-addition"
RES = D / "results"
SH = ROOT / "data/processed/shared"


def _scheme():
    spec = importlib.util.spec_from_file_location("h122build", HERE.parent / "scheme" / "build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def verdict(r: dict) -> str:
    if r["n_p12_with_newcomer_read"] < 200:
        return "descriptive"
    if r["d_C_J_hi"] < 0:
        return "failed"
    if r["d_C_J_lo"] > 0:
        return "supported" if r["d_PL_J"] > 0 else "mixed"
    return "mixed"


def run_event(ev: dict, B: int, PB: int) -> dict:
    df = L.prep(pl.read_parquet(D / "calls" / f"{ev['event']}.parquet"))
    N = {0: ev["N_pre"], 1: ev["N_p12"], 2: ev["N_f37"]}
    fit = L.fit_models(df, N)
    sc = L.scores(fit, B=B, seed=1)
    tr = L.trajectory(fit)
    bp = L.boot_params(df, N, B=PB, seed=2)
    p12 = df.filter(pl.col("win") == 1)
    par = fit["par"]
    pre = par.pop("pre")
    r = {"event": ev["event"], "day1": ev["day1"], "goal_no": ev["goal_no"], "regime": ev["regime"],
         "n_new": ev["n_new"], "names": ", ".join(ev["names"]), "n_incumbents": ev["n_incumbents"],
         "N_pre": N[0], "N_p12": N[1], "N_f37": N[2], "n_calls_pre": ev["n_calls_pre"],
         "n_calls_p12": ev["n_calls_p12"], "n_calls_f37": ev["n_calls_f37"],
         "n_p12_with_newcomer_read": int((p12["RN"] > 0).sum()),
         "talk_rate_p12": float(p12["Y"].mean()),
         **{f"pre_{k}": v for k, v in pre.items()}, **par, **sc, **tr, **bp}
    # J per read on the probability scale at the incumbents' mean P12 rate (comparable to H67's J1*)
    pbar = par["mean_p_p12"]
    r["J_N_prob"] = par["J_N"] * pbar * (1 - pbar)
    r["verdict"] = verdict(r)
    return r


def placebo_events(cal: pl.DataFrame, ev_all: pl.DataFrame) -> list[dict]:
    """Regime-I goal kickoffs with no join in the 7 active days before or on days 1-2; PRE = previous goal's last
    <= 5 non-holdout days (same regime); P12 = kickoff days 1-2; F37 unused (empty)."""
    c = cal.sort("pt_date").with_row_index("ix")
    days = c["pt_date"].to_list()
    hold = dict(zip(days, c["holdout"].to_list()))
    goal = dict(zip(days, c["goal_no"].to_list()))
    reg = dict(zip(days, c["regime"].cast(pl.String).to_list()))
    join_ix = set()
    for r in ev_all.to_dicts():
        for k in range(r["ix1"] - 7, r["ix1"] + 2):
            join_ix.add(k)
    out = []
    for i, d in enumerate(days):
        if i == 0 or goal[d] == goal[days[i - 1]] or reg[d] != "I" or hold[d]:
            continue
        if i + 1 >= len(days) or hold[days[i + 1]] or goal[days[i + 1]] != goal[d]:
            continue
        if i in join_ix or (i + 1) in join_ix:
            continue
        prev_goal = goal[days[i - 1]]
        pre = [days[j] for j in range(max(0, i - 10), i) if goal[days[j]] == prev_goal and not hold[days[j]]
               and reg[days[j]] == "I"][-5:]
        if len(pre) < 2:
            continue
        out.append({"event": f"PK{d}", "day1": d, "goal_no": goal[d], "regime": "I", "newcomers": [], "names": [],
                    "n_new": 0, "pre": pre, "p12": [d, days[i + 1]], "f37": [], "recent_joiners": []})
    return out


def run_placebo(pe: dict, B: int = 1000) -> dict:
    df = L.prep(pl.read_parquet(D / "placebo" / "calls" / f"{pe['event']}.parquet"))
    N = {0: pe["N_pre"], 1: pe["N_p12"], 2: pe["N_p12"]}
    pre, p12 = df.filter(pl.col("win") == 0), df.filter(pl.col("win") == 1)
    m0 = L.M0(pre)
    eP = m0.eta(p12, L.dil_factor(N[1], N[0]))
    y = p12["Y"].to_numpy().astype(float)
    dl = L.irls1(np.ones_like(y), y, eP)
    return {"event": pe["event"], "day1": pe["day1"], "goal_no": pe["goal_no"], "delta_p12": dl,
            "n_incumbents": pe["n_incumbents"], "n_calls_p12": pe["n_calls_p12"], "N_pre": N[0], "N_p12": N[1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--pboot", type=int, default=200)
    ap.add_argument("--skip-placebo", action="store_true")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    ev = pl.read_parquet(D / "events.parquet")
    elig = ev.filter(pl.col("eligible_windows"))
    rows = []
    for e in elig.to_dicts():
        r = run_event(e, a.boot, a.pboot)
        rows.append(r)
        print(r["event"], r["verdict"], round(r["d_C_J"], 3), [round(r["d_C_J_lo"], 3), round(r["d_C_J_hi"], 3)],
              "J_N", round(r["J_N"], 3), flush=True)
    E = pl.DataFrame(rows, infer_schema_length=None)
    E.write_parquet(RES / "events.parquet")
    if not a.skip_placebo:
        B = _scheme()
        cal = pl.read_parquet(SH / "calendar.parquet")
        cw, lt, cc, cca = B.load_shared()
        pls = []
        for pe in placebo_events(cal, ev):
            meta = B.build_event(pe, cw, lt, cc, cca, cal, out_dir=D / "placebo")
            pe.update(meta)
            if meta["n_incumbents"] < 3 or meta["n_calls_p12"] < 200:
                continue
            pls.append(run_placebo(pe))
            print(pe["event"], round(pls[-1]["delta_p12"], 3), flush=True)
        P = pl.DataFrame(pls)
        P.write_parquet(RES / "placebo.parquet")


if __name__ == "__main__":
    main()
