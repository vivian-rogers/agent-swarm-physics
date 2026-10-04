"""H116 synthetic validation (axis F), run BEFORE any real-data statistic.

Kinetic Ising on the real call skeletons and update order of #24, #25, #26, #27 (regime I): talk at each call with
P = sigmoid(2H), H = h_agent,mode + Jself s_prev + sum_j J_ij x_ij; h = each agent's real week-level talk logit per call
mode in that period (a field). Couplings J0 between all pairs; in #26, from T* = 2026-01-05 19:35:22 UTC on, the
winner's out-couplings J_j,17 gain a step Delta.

Per world: the event statistic dJout(17, T*) (h116lib.fit_event) and the same statistic at every eligible placebo day
(same offsets from the day's calendar start; days of #24-#27 except 01-05, 01-06, 01-09) under the same world.
Kill rule (card N1): detection = dJout >= 0.05 and dJout > 95th percentile of the world's placebo values.
Reports power per Delta, size at Delta = 0, and the SE of dJout.

  uv run python hypotheses/H116-election-coupling-step/analysis/synthetic.py [--reps 50]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h116lib as L  # noqa: E402

CS = L.CS
OUT = L.DATA / "synthetic"
DELTAS = [0.0, 0.05, 0.1, 0.25, 0.5, 1.0]
LAMS = [1.0, 4.0]
J0 = 0.02
JSELF = 0.3
PERIODS = ["G24", "G25", "G26", "G27"]
EXCLUDE_DAYS = {"2026-01-05", "2026-01-06", "2026-01-09"}
_G = {}


def field(calls):
    s = calls["s"].to_numpy()
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    h = np.zeros(calls.height)
    for ag in np.unique(a):
        for m in (0, 1):
            sel = (a == ag) & (md == m)
            if sel.sum():
                p = np.clip((s[sel] > 0).mean(), 0.01, 0.99)
                h[sel] = 0.5 * np.log(p / (1 - p))
    return h


def placebo_windows(calls, day):
    """Windows at the event's offsets from the day's calendar start; skeleton-only eligibility."""
    ws_e = L.win_start(L.EVENT_DAY)
    sp_e = L.day_span(_G["G26"][0], L.EVENT_DAY)
    off_t0, off_g, off_T = sp_e[0] - ws_e, L.T_G - ws_e, L.T_STAR - ws_e
    ws = L.win_start(day)
    r = L.windows_at(calls, day, ws + off_T, ws + off_g, t0=ws + off_t0)
    if r is None:
        return None
    pre, post, _ = r
    a = calls["agent"].to_numpy()
    if ((a == L.WINNER) & pre).sum() < 30 or ((a == L.WINNER) & post).sum() < 30:
        return None
    return pre, post


def _init():
    for p in PERIODS:
        _G[p] = L.load(p)
    pl_list = []
    for p in PERIODS:
        calls = _G[p][0]
        for day in sorted(calls["pt_date"].unique().to_list()):
            if day in EXCLUDE_DAYS:
                continue
            r = placebo_windows(calls, day)
            if r is not None:
                pl_list.append((p, day, r[0], r[1]))
    _G["placebos"] = pl_list
    calls = _G["G26"][0]
    _G["event"] = L.windows_at(calls, L.EVENT_DAY, L.T_STAR, L.T_G)[:2]


def sim_period(p, delta, seed):
    calls, XR, XP, agents = _G[p]
    A = len(agents)
    base = np.full((A, A), J0)
    np.fill_diagonal(base, 0)
    step = base.copy()
    if p == "G26" and L.WINNER in agents:
        wi = agents.index(L.WINNER)
        step[:, wi] += delta
        step[wi, wi] = 0
    post = (calls["t_call"] >= L.T_STAR).to_numpy() if p == "G26" else np.zeros(calls.height, bool)

    def J_of(k):
        return step if post[k] else base

    return CS.simulate(calls, agents, field(calls), J_of, np.full(A, JSELF), seed=seed)


def world(rep):
    if not _G:
        _init()
    sims = {p: sim_period(p, 0.0, 1000 * rep + q) for q, p in enumerate(PERIODS)}
    out = {"rep": rep, "placebo": {str(l): [] for l in LAMS}, "event": {}}
    for (p, day, pre, post) in _G["placebos"]:
        calls, XR, XP, agents = _G[p]
        s, XRs, XPs = sims[p]
        for lam in LAMS:
            f = L.fit_event(calls, XRs, XPs, agents, L.WINNER, pre, post, lam, se=False, s_override=s)
            out["placebo"][str(lam)].append(np.nan if f is None else f["coef"]["dJout"])
    calls, XR, XP, agents = _G["G26"]
    pre, post = _G["event"]
    for d in DELTAS:
        s, XRs, XPs = sim_period("G26", d, 1000 * rep + 99 + int(100 * d))
        for lam in LAMS:
            f = L.fit_event(calls, XRs, XPs, agents, L.WINNER, pre, post, lam, se=True, s_override=s)
            out["event"][f"{d}_{lam}"] = {"dJout": f["coef"]["dJout"], "se": f["se"]["dJout"],
                                          "dJin": f["coef"]["dJin"], "rmi": f["read_minus_inflight"]}
    return out


def summarize(res):
    rows = []
    for lam in LAMS:
        for d in DELTAS:
            det, ests, ses = [], [], []
            for r in res:
                pv = np.array(r["placebo"][str(lam)], dtype=float)
                thr = np.nanpercentile(pv, 95)
                e = r["event"][f"{d}_{lam}"]
                det.append((e["dJout"] >= 0.05) and (e["dJout"] > thr))
                ests.append(e["dJout"])
                ses.append(e["se"])
            rows.append({"lam": lam, "delta": d, "power": float(np.mean(det)), "mean_est": float(np.mean(ests)),
                         "sd_est": float(np.std(ests)), "mean_se": float(np.nanmean(ses))})
        allp = np.concatenate([np.array(r["placebo"][str(lam)], dtype=float) for r in res])
        rows.append({"lam": lam, "placebo_sd": float(np.nanstd(allp)), "placebo_q95": float(np.nanpercentile(allp, 95)),
                     "n_placebo_days": len(res[0]["placebo"][str(lam)])})
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=50)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_init) as ex:
        res = list(ex.map(world, range(a.reps)))
    summ = summarize(res)
    _init() if not _G else None
    meta = {"grid": summ, "J0": J0, "Jself": JSELF, "deltas": DELTAS, "lams": LAMS, "reps": a.reps,
            "placebo_days": [(p, d) for (p, d, _, _) in _G["placebos"]], "seconds": time.time() - t0}
    (OUT / "synthetic_raw.json").write_text(json.dumps(res))
    (OUT / "synthetic.json").write_text(json.dumps(meta, indent=1, default=str))
    for r in summ:
        print(json.dumps(r))
