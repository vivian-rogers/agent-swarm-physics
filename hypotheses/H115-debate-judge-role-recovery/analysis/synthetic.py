"""H115 synthetic validation (axis F), run BEFORE any real-data statistic.

Kinetic Ising on the real #12 call skeleton and update order (real t_call, t_first, call modes, one room): talk at
each call with P = sigmoid(2H), H = h_agent,mode + Jself s_prev + sum_j J_ij x_ij (x = read-gated input, same rule as
the scheme). The field h is each agent's real week-level talk logit per call mode (a field, not a coupling).

Worlds (per debate window, a random planted judge k and random teams among the others):
  sink   J_kj = J0 + a for debaters j (judge reads debaters), J_jk = J0; within team J = J0 + b; else J0
  field  a = b = 0, but the planted judge gets a role field: +0.4 in 'post', -0.2 in 'deb' (impostor check)
Estimator: the additive in/out fit per debate (h115lib.fit_additive) for ridge lambda in LAMS; the planted judge's
rank under S (read) and SP (in-flight). Team blocks: pair-type model with the planted labels, J_ST - J_OT and z.

  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/synthetic.py [--reps 40]
Output: data/processed/H115-debate-judge-role-recovery/synthetic/synthetic.json (+ figures/synthetic.pdf later).
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h115lib as L  # noqa: E402

CS = L.CS
OUT = L.DATA / "synthetic"
LAMS = [1.0, 4.0, 16.0]
J0 = 0.02
JSELF = 0.3
GRID = [("sink", 0.0, 0.0), ("sink", 0.15, 0.0), ("sink", 0.3, 0.0), ("sink", 0.6, 0.0), ("sink", 1.0, 0.0),
        ("sink", 0.0, 0.3), ("sink", 0.3, 0.3), ("field", 0.0, 0.0)]

_G = {}


def _init():
    calls, XR, XP, agents = L.load("G12")
    s = calls["s"].to_numpy()
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    h = np.zeros(calls.height)
    for ag in agents:
        for m in (0, 1):
            sel = (a == ag) & (md == m)
            if sel.sum():
                p = np.clip((s[sel] > 0).mean(), 0.01, 0.99)
                h[sel] = 0.5 * np.log(p / (1 - p))
    wins = calls["win"].to_list()
    wl = sorted({w for w in wins if w is not None})
    widx = np.array([wl.index(w) if w is not None else -1 for w in wins])
    phase = np.array([p if p is not None else "none" for p in calls["phase"].to_list()])
    _G.update(calls=calls, agents=agents, h=h, widx=widx, wl=wl, phase=phase, a=a)


def world(args):
    kind, a_s, b_s, rep = args
    if not _G:
        _init()
    calls, agents, h0, widx, wl, phase, aa = (_G[k] for k in ("calls", "agents", "h", "widx", "wl", "phase", "a"))
    A = len(agents)
    rng = np.random.default_rng(1000 * rep + int(100 * a_s) + int(10 * b_s) + (7 if kind == "field" else 0))
    base = np.full((A, A), J0)
    np.fill_diagonal(base, 0)
    mats, plant = [], []
    for d in range(len(wl)):
        k = int(rng.integers(A))
        others = [q for q in range(A) if q != k]
        rng.shuffle(others)
        ng, no = (3, 3) if rng.random() < 0.5 else ((3, 2) if rng.random() < 0.5 else (2, 3))
        gov, opp = others[:ng], others[ng:ng + no]
        J = base.copy()
        if kind == "sink":
            for j in gov + opp:
                J[k, j] += a_s
            for T in (gov, opp):
                for i in T:
                    for j in T:
                        if i != j:
                            J[i, j] += b_s
        mats.append(J)
        plant.append((k, gov, opp))
    h = h0.copy()
    if kind == "field":
        for d, (k, _, _) in enumerate(plant):
            m = (widx == d) & (aa == agents[k])
            h[m & (phase == "post")] += 0.4
            h[m & (phase == "deb")] -= 0.2

    def J_of(i):
        return mats[widx[i]] if widx[i] >= 0 else base

    s, XRs, XPs = CS.simulate(calls, agents, h, J_of, np.full(A, JSELF), seed=rep + 17)
    out = {"kind": kind, "a": a_s, "b": b_s, "rep": rep, "rank": {}, "rankP": {}, "n": []}
    for lam in LAMS:
        rk, rkP = [], []
        for d, w in enumerate(wl):
            m = widx == d
            cw = calls.filter(m)
            pres = L.present_agents(cw)
            f = L.fit_additive(cw, XRs[m], XPs[m], agents, pres, lam, phase=phase[m], s_override=s[m])
            k = agents[plant[d][0]]
            if k not in pres:
                rk.append(np.nan)
                rkP.append(np.nan)
                continue
            q = pres.index(k)
            rk.append(int(L.ranks_desc(f["S"])[q]))
            rkP.append(int(L.ranks_desc(f["SP"])[q]))
        out["rank"][str(lam)] = rk
        out["rankP"][str(lam)] = rkP
    # team blocks with the planted labels (pair-type model), lambda 4
    W = []
    for d, w in enumerate(wl):
        m = widx == d
        cw = calls.filter(m)
        k, gov, opp = plant[d]
        W.append({"calls": cw.with_columns(), "XR": XRs[m], "XP": XPs[m], "pres": L.present_agents(cw),
                  "judge": agents[k], "gov": [agents[q] for q in gov], "opp": [agents[q] for q in opp],
                  "phase": phase[m], "wid": d})
    for W_ in W:
        W_["calls"] = W_["calls"].with_columns(__import__("polars").Series("s", s[widx == W_["wid"]]))
    ft = L.fit_pairtype(W, agents, lam=4.0)
    est, se = L.contrast(ft, "R_ST_all", "R_OT_all")
    estJ, seJ = L.contrast(ft, "R_JD_all", "R_DJ_all")
    out["team"] = {"est": est, "se": se, "z": est / se if se > 0 else np.nan}
    out["judge_pt"] = {"est": estJ, "se": seJ}
    return out


def summarize(res):
    rows = []
    for kind, a_s, b_s in GRID:
        rr = [r for r in res if (r["kind"], r["a"], r["b"]) == (kind, a_s, b_s)]
        row = {"kind": kind, "a": a_s, "b": b_s, "reps": len(rr)}
        for lam in LAMS:
            R = np.array([r["rank"][str(lam)] for r in rr], dtype=float)
            RP = np.array([r["rankP"][str(lam)] for r in rr], dtype=float)
            med = np.nanmedian(R, axis=1)
            n1 = np.nansum(R == 1, axis=1)
            row[f"lam{lam}"] = {"p_rank1": float(np.nanmean(R == 1)), "median_rank": float(np.nanmedian(R)),
                                "support_rate": float(np.mean((med <= 2) & (n1 >= 4))),
                                "kill_rate": float(np.mean(med >= 4)),
                                "p_rank1_P": float(np.nanmean(RP == 1)), "median_rank_P": float(np.nanmedian(RP))}
        z = np.array([r["team"]["z"] for r in rr])
        e = np.array([r["team"]["est"] for r in rr])
        row["team"] = {"mean_est": float(np.nanmean(e)), "power_z196": float(np.nanmean(z > 1.96)),
                       "fp_or_kill_rate_est_le0": float(np.nanmean(e <= 0))}
        jj = np.array([r["judge_pt"]["est"] for r in rr])
        row["JD_minus_DJ_mean"] = float(np.nanmean(jj))
        rows.append(row)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(k, x, y, r) for (k, x, y) in GRID for r in range(a.reps)]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers, initializer=_init) as ex:
        res = list(ex.map(world, jobs, chunksize=2))
    summ = summarize(res)
    (OUT / "synthetic_raw.json").write_text(json.dumps(res))
    (OUT / "synthetic.json").write_text(json.dumps({"grid": summ, "J0": J0, "Jself": JSELF, "lams": LAMS,
                                                   "reps": a.reps, "seconds": time.time() - t0}, indent=1))
    for r in summ:
        print(json.dumps(r))
