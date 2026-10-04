"""H40 synthetic validation (axis F): replies simulated on REAL call schedules and REAL item rows.

Truth: call starts redrawn uniformly inside each call's [t_call_lo, t_call_hi] (read-out calls re-derived with the
ledger rule on the jittered times); replies drawn call by call from the scenario's cloglog hazard.
Estimation: exactly the real pipeline (ledger read-out call, point t_call, 30-min risk set, cells, cloglog IRLS).

Scenarios
  S1 call clock     eta = eta1 = 0, phi = -0.6 (decay in calls)
  S2 wall clock     eta = eta1 = 1 (hazard accrues per second, executed at calls), psi = -0.6 (decay in wall age)
  S3 mixed          eta = eta1 = 0.5, phi = psi = -0.3
  S4 call clock, agent couplings correlated with cadence: alpha_i = a0 + 0.5 (log r_i - mean)  (true s = 0.5)
  S5 call clock + detection loss growing with burial at the reply call (DQ2 recency penalty analogue)

  uv run python hypotheses/H40-call-clock-coupling/analysis/synthetic.py --period 38 --reps 20
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402

BASE = {"n1": 1.0, "n1_ment": 1.2, "ment": 1.0, "n1_logrank": -0.3, "logk": -0.5, "prev_talk": 0.5}
SCEN = {
    "S1": dict(BASE, phi=-0.6),
    "S2": dict(BASE, eta=1.0, eta1=1.0, psi=-0.6),
    "S3": dict(BASE, eta=0.5, eta1=0.5, phi=-0.3, psi=-0.3),
    "S4": dict(BASE, phi=-0.6),
    "S5": dict(BASE, phi=-0.6),
}
TRUE_ETA = {"S1": 0.0, "S2": 1.0, "S3": 0.5, "S4": 0.0, "S5": 0.0}
TRUE_S = {"S1": 0.0, "S2": 0.0, "S3": 0.0, "S4": 0.5, "S5": 0.0}
SD_ALPHA = 0.5


def load_period(goal: int, unit: str | None):
    d = L.OUT / f"G{goal:02d}"
    it = pl.read_parquet(d / "items.parquet")
    cad = pl.read_parquet(d / "cadence.parquet")
    au = pl.read_parquet(d / "au.parquet")
    if unit:
        it = it.filter(pl.col("unit_id") == unit)
    it = it.with_row_index("j")
    r = au.join(cad.select("agent", "unit_id", "rate"), on=["agent", "unit_id"], how="left").sort("au")
    return it, r


def simulate_replies(calls_true: L.Calls, it: pl.DataFrame, coef: dict, fe_au: np.ndarray, rng, s5: bool = False):
    """Reply call (turn_id) per item under the truth; -1 if no reply within the horizon."""
    recv = it["recv"].to_numpy().astype(np.int16)
    t_m = it["t_m"].to_numpy()
    c1t = L.readout_call(calls_true, recv, t_m)
    ok = c1t >= 0
    # the true read-out call must be on the same day as the observed one (otherwise drop the item)
    obs_day_end = calls_true.day_end[it["c1"].to_numpy()]
    ok &= c1t <= obs_day_end
    idx = np.flatnonzero(ok)
    rank = it["rank"].to_numpy().astype(np.int64)
    ment = it["ment"].to_numpy()
    aucode = it["au"].to_numpy()
    rows = L.expand(calls_true, c1t[idx], t_m[idx], rank[idx])
    rows.item = idx[rows.item]
    eta = L.rows_linpred(rows, ment, rank, coef, fe_au, aucode)
    h, _ = L._cloglog_mu(eta)
    hit = rng.random(len(h)) < h
    if s5:
        keep = rng.random(len(h)) < np.exp(-0.15 * np.log1p(rows.b))
        hit &= keep
    reply = np.full(it.height, -1, dtype=np.int64)
    hi = np.flatnonzero(hit)
    if len(hi):
        # first hit per item
        it_hit = rows.item[hi]
        first = np.r_[True, it_hit[1:] != it_hit[:-1]]
        reply[it_hit[first]] = rows.tid[hi[first]]
    return reply


def calibrate_a0(calls: L.Calls, it, coef, dev_au, target: float) -> float:
    rank = it["rank"].to_numpy().astype(np.int64)
    rows = L.expand(calls, it["c1"].to_numpy(), it["t_m"].to_numpy(), rank)
    ment = it["ment"].to_numpy()
    aucode = it["au"].to_numpy()
    lo, hi = -15.0, 3.0
    for _ in range(40):
        mid = (lo + hi) / 2
        eta = L.rows_linpred(rows, ment, rank, coef, mid + dev_au, aucode)
        p = L.p_reply_within(rows, eta, L.H_FIT_S, it.height).mean()
        lo, hi = (mid, hi) if p < target else (lo, mid)
    return (lo + hi) / 2


def estimate(calls: L.Calls, it: pl.DataFrame, reply: np.ndarray, r_au: np.ndarray, n_au: int, heldout: bool = True):
    c1 = it["c1"].to_numpy()
    t_m = it["t_m"].to_numpy()
    rank = it["rank"].to_numpy().astype(np.int64)
    ment = it["ment"].to_numpy().astype(np.int64)
    day = it["day"].to_numpy()
    aucode = it["au"].to_numpy()
    rep = np.where(reply < c1, -1, reply)
    rows = L.expand(calls, c1, t_m, rank)
    rows, y = L.truncate(rows, rep)
    cells = L.aggregate(rows, y.astype(float), day, aucode, ment, rank)
    f, _ = L.fit_cells(cells, L.SPEC_FULL, n_au=n_au)
    out = {nm: f.get(nm) for nm in ("eta", "eta1", "phi", "psi", "chi", "logk")}
    out.update({f"se_{nm}": f.se(nm) for nm in ("eta", "eta1", "phi", "psi")})
    # between-agent slope of the FE on log rate (weights 1/se^2, agent-units with replies)
    fe, se = f.fe, f.fe_se
    has = np.bincount(cells["au"].to_numpy(), weights=cells["y"].to_numpy(), minlength=n_au) >= 3
    ok = has & np.isfinite(r_au) & (r_au > 0) & np.isfinite(se) & (se > 0)
    if ok.sum() >= 4:
        x = np.log(r_au[ok]); yy = fe[ok]; w = 1 / se[ok] ** 2
        X = np.column_stack([np.ones(ok.sum()), x])
        b = np.linalg.solve(X.T @ (X * w[:, None]), X.T @ (w * yy))
        out["s"] = float(b[1])
    else:
        out["s"] = np.nan
    if heldout:
        even = (cells["day"].to_numpy() % 2) == 0
        ce, co = cells.filter(pl.Series(even)), cells.filter(pl.Series(~even))
        nrep = np.bincount(ce["au"].to_numpy(), weights=ce["y"].to_numpy(), minlength=n_au)
        co = co.filter(pl.col("au").is_in(np.flatnonzero(nrep >= 3).tolist()))
        res = {}
        for spec in (L.SPEC_CALL, L.SPEC_WALL, L.SPEC_FULL):
            fs, _ = L.fit_cells(ce, spec, n_au=n_au)
            res[spec] = L.loglik(co, spec, fs, n_au)
        n_items_odd = float(co.filter(pl.col("nb") == 0)["N"].sum())
        out["dll_call_wall"] = (res[L.SPEC_CALL] - res[L.SPEC_WALL]) / max(n_items_odd, 1)
        out["dll_full_call"] = (res[L.SPEC_FULL] - res[L.SPEC_CALL]) / max(n_items_odd, 1)
    out["n_replies"] = float(cells["y"].sum())
    out["n_items"] = it.height
    return out, f, rows


def run(goal: int, unit: str | None, reps: int, seed: int, scen: list[str]):
    calls = L.load_calls()
    it, r = load_period(goal, unit)
    n_au = int(pl.read_parquet(L.OUT / f"G{goal:02d}" / "au.parquet")["au"].max()) + 1
    r_au = np.full(n_au, np.nan)
    r_au[r["au"].to_numpy()] = r["rate"].to_numpy()
    target = float((it["r_tid"] >= 0).mean())
    rng = np.random.default_rng(seed)
    lr = np.log(np.where(np.isfinite(r_au) & (r_au > 0), r_au, np.nanmedian(r_au)))
    out = []
    for sc in scen:
        coef = SCEN[sc]
        for rep in range(reps):
            t0 = time.time()
            dev = rng.normal(0, SD_ALPHA, n_au)
            if sc == "S4":
                dev = 0.5 * (lr - lr.mean()) + rng.normal(0, 0.3, n_au)
            a0 = calibrate_a0(calls, it, coef, dev, target) if rep == 0 else a0  # noqa: F821
            fe_au = a0 + dev
            ctrue = L.with_times(calls, L.jitter_times(calls, rng))
            reply = simulate_replies(ctrue, it, coef, fe_au, rng, s5=(sc == "S5"))
            res, f, rows = estimate(calls, it, reply, r_au, n_au, heldout=(rep < max(5, reps // 2)))
            # true and estimated cadence elasticity at 5 and 30 min (on the observed rows, subsample of items)
            if rep < 3:
                rank = it["rank"].to_numpy().astype(np.int64)
                sub = rng.choice(it.height, size=min(20000, it.height), replace=False)
                sub.sort()
                rws = L.expand(calls, it["c1"].to_numpy()[sub], it["t_m"].to_numpy()[sub], rank[sub], horizon=L.H_EPS_S)
                im = it["ment"].to_numpy()[sub]; ir = rank[sub]; ia = it["au"].to_numpy()[sub]
                est = {nm: f.beta[i] for i, nm in enumerate(f.names)}
                for T in (300.0, 1800.0):
                    res[f"eps_true_{int(T)}"] = L.cadence_elasticity(rws, im, ir, ia, coef, fe_au, T, len(sub))
                    res[f"eps_est_{int(T)}"] = L.cadence_elasticity(rws, im, ir, ia, est, f.fe, T, len(sub))
            res.update(scenario=sc, rep=rep, goal=goal, unit=unit or "all", true_eta=TRUE_ETA[sc], true_s=TRUE_S[sc],
                       secs=round(time.time() - t0, 1), target_rate=target)
            out.append(res)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()}, flush=True)
    df = pl.DataFrame(out)
    tag = f"G{goal:02d}" + (f"_{unit}" if unit else "")
    (L.OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    df.write_parquet(L.OUT / "synthetic" / f"{tag}.parquet")
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, required=True)
    ap.add_argument("--unit", default=None)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--seed", type=int, default=L.SEED)
    ap.add_argument("--scen", default="S1,S2,S3,S4,S5")
    a = ap.parse_args()
    run(a.period, a.unit, a.reps, a.seed + a.period, a.scen.split(","))


if __name__ == "__main__":
    main()
