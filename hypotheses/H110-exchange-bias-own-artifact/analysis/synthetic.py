"""H110 synthetic validation (axis F) on the real skeleton: real windows (agents, days, statement counts per window,
transitions, placebo periods) and the real pinning labels and last-commit days; synthetic statement vectors.

Statement z = cg G + c_old(w) e_old^P + c_new(w) e_new^P + a_i + h_id + eps (32-d), vector = unit(z).
  h_id ~ N(0, hd2 I): an agent-day topic (within-day coherence without cross-agent alignment).
  G: generic village content shared by all periods (removed by the placebo old states);
  e_old^P, e_new^P: random orthonormal directions per transition; placebo period Q gets its own e^Q at amplitude c0;
  a_i ~ N(0, tau2 I) per agent (fixed across transitions); eps ~ N(0, s2 I).
  Old days and pre: c_old = c0. Post day k: free decay f_U(k) = R1U^k with R1U = 0.25 (H96 median day-1 remanence);
  c_new = c0 (1 - f_U(k)).
Worlds:
  S0  no pinning                          f = f_U for everyone
  S1  HH340, boundary status              pinned: f = R1U^(k/2) (decay rate halved)
  S1L HH340, live only                    pinned: halved rate while k <= last_day, free rate after
  S2  activity confound                   pinned: 0.6x statements (subsampled) and 1.3x noise; f = f_U
Calibration (instrument, not an outcome): s2, tau2, c0, cg matched by grid search to the real within-agent-day
statement cosine, the real between-agent same-day agent-day cosine on the old days, the real cross-period
agent-day cosine and the real agent self-similarity across periods (style_resid32, bge / gte).
Usage: uv run python hypotheses/H110-exchange-bias-own-artifact/analysis/synthetic.py [--reps 200] [--model bge_small]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h110lib as L  # noqa: E402

OUT = L.D / "synthetic"
R1U = 0.25
WORLDS = ["S0", "S1", "S1L", "S2"]


def moments_real(win: pl.DataFrame, X: np.ndarray) -> dict:
    """Instrument moments from the real old-day statements (no pinning information used)."""
    w = win.with_row_index("wr").filter(pl.col("window") == "old")
    rows = w["wr"].to_numpy()
    ag, dd, P = w["agent"].to_numpy(), w["pt_date"].to_numpy(), w["P"].to_numpy()
    within, adv = [], {}
    key = ag.astype(np.int64) * 10 ** 7 + np.unique(dd, return_inverse=True)[1] * 100 + (P - 30)
    for k in np.unique(key):
        m = np.where(key == k)[0]
        if len(m) >= 3:
            V = X[rows[m]]
            G = V @ V.T
            within.append((G.sum() - np.trace(G)) / (len(m) * (len(m) - 1)))
            adv.setdefault((int(P[m[0]]), dd[m[0]]), []).append((int(ag[m[0]]), L.unit(V.mean(0))))
    between = []
    for lst in adv.values():
        if len(lst) >= 2:
            V = np.array([v for _, v in lst])
            G = V @ V.T
            between.append((G.sum() - np.trace(G)) / (len(V) * (len(V) - 1)))
    # cross-period: centroids of different transitions' old states; agent self-similarity across transitions
    cent = {}
    agP = {}
    for (Pp, _), lst in adv.items():
        cent.setdefault(Pp, []).extend([v for _, v in lst])
        for a, v in lst:
            agP.setdefault((a, Pp), []).append(v)
    C = np.array([L.unit(np.mean(v, 0)) for v in cent.values()])
    G = C @ C.T
    cross = (G.sum() - np.trace(G)) / (len(C) * (len(C) - 1))
    selfs, others = [], []
    am = {k: L.unit(np.mean(v, 0)) for k, v in agP.items()}
    keys = list(am)
    for i, (a, p) in enumerate(keys):
        for (b, q) in keys[i + 1:]:
            if p != q:
                (selfs if a == b else others).append(float(am[(a, p)] @ am[(b, q)]))
    return {"within": float(np.mean(within)), "between": float(np.mean(between)), "cross": float(cross),
            "self_minus_other": float(np.mean(selfs) - np.mean(others))}


def toy_moments(s2, tau2, c0, cg, rng, hd2=0.0, nag=12, nst=6, nP=6):
    G = L.unit(rng.standard_normal(32))
    A = rng.standard_normal((nag, 32)) * np.sqrt(tau2)
    within, between, cent, am = [], [], [], {}
    for p in range(nP):
        e = L.unit(rng.standard_normal(32))
        vs = []
        for i in range(nag):
            Z = cg * G + c0 * e + A[i] + rng.standard_normal(32) * np.sqrt(hd2) + rng.standard_normal((nst, 32)) * np.sqrt(s2)
            V = L.unit(Z)
            Gm = V @ V.T
            within.append((Gm.sum() - np.trace(Gm)) / (nst * (nst - 1)))
            v = L.unit(V.mean(0))
            vs.append(v)
            am[(i, p)] = v
        Vs = np.array(vs)
        Gm = Vs @ Vs.T
        between.append((Gm.sum() - np.trace(Gm)) / (nag * (nag - 1)))
        cent.append(L.unit(Vs.mean(0)))
    C = np.array(cent)
    Gm = C @ C.T
    cross = (Gm.sum() - np.trace(Gm)) / (nP * (nP - 1))
    selfs = [am[(i, p)] @ am[(i, q)] for i in range(nag) for p in range(nP) for q in range(p + 1, nP)]
    oth = [am[(i, p)] @ am[(j, q)] for i in range(nag) for j in range(nag) if i != j for p in range(nP) for q in range(p + 1, nP)]
    return {"within": float(np.mean(within)), "between": float(np.mean(between)), "cross": float(cross),
            "self_minus_other": float(np.mean(selfs) - np.mean(oth))}


def calibrate(target: dict, seed=0) -> dict:
    rng = np.random.default_rng(seed)
    best, bp = np.inf, None
    for s2 in [0.03, 0.05, 0.08, 0.12, 0.2]:
        for tau2 in [0.0, 0.003, 0.006, 0.01]:
            for c0 in [0.2, 0.3, 0.4, 0.5, 0.6, 0.8]:
                for cg in [0.0, 0.1, 0.2, 0.3, 0.4]:
                    for hd2 in [0.0, 0.01, 0.02, 0.04, 0.08]:
                        m = toy_moments(s2, tau2, c0, cg, rng, hd2)
                        err = sum((m[k] - target[k]) ** 2 for k in target)
                        if err < best:
                            best, bp = err, {"s2": s2, "tau2": tau2, "c0": c0, "cg": cg, "hd2": hd2, "toy": m}
    bp["err"] = best
    return bp


def gen(win: pl.DataFrame, pin: pl.DataFrame, cal: dict, world: str, rng) -> tuple[pl.DataFrame, np.ndarray]:
    s2, tau2, c0, cg, hd2 = cal["s2"], cal["tau2"], cal["c0"], cal["cg"], cal.get("hd2", 0.0)
    dd = win["pt_date"].to_numpy()
    H = {}
    G = L.unit(rng.standard_normal(32))
    agents = np.unique(win["agent"].to_numpy())
    A = {int(a): rng.standard_normal(32) * np.sqrt(tau2) for a in agents}
    pinfo = {(int(r["P"]), int(r["agent"])): (r["pinned_own"], r["last_day"]) for r in pin.iter_rows(named=True)}
    keep = np.ones(win.height, bool)
    Pn = win["P"].to_numpy().astype(int)
    wn = win["window"].to_numpy()
    ag = win["agent"].to_numpy().astype(int)
    Z = np.zeros((win.height, 32))
    dirs = {}
    for P in np.unique(Pn):
        Q, _ = np.linalg.qr(rng.standard_normal((32, 2)))
        dirs[P] = (Q[:, 0], Q[:, 1])
    plcdir = {}
    for i in range(win.height):
        P, w, a = Pn[i], wn[i], ag[i]
        e_old, e_new = dirs[P]
        pinned, last = pinfo.get((P, a), (False, 0))
        noise = np.sqrt(s2)
        if w.startswith("plc_"):
            q = int(w[4:])
            if q not in plcdir:
                plcdir[q] = L.unit(rng.standard_normal(32))
            z = cg * G + c0 * plcdir[q]
        elif w in ("old", "pre"):
            z = cg * G + c0 * e_old
        else:
            k = int(w[1:])
            fU = R1U ** k
            f = fU
            if pinned and world == "S1":
                f = R1U ** (k / 2)
            elif pinned and world == "S1L":
                f = R1U ** (min(k, last) / 2) * R1U ** max(k - last, 0)
            if pinned and world == "S2":
                noise *= 1.3
                if rng.random() > 0.6:
                    keep[i] = False
            z = cg * G + c0 * f * e_old + c0 * (1 - fU) * e_new
        if (a, dd[i]) not in H:
            H[(a, dd[i])] = rng.standard_normal(32) * np.sqrt(hd2)
        Z[i] = z + A[a] + H[(a, dd[i])] + rng.standard_normal(32) * noise
    return win.filter(pl.Series(keep)), L.unit(Z[keep])


def run(tr, win, X, pin, proj):
    rem = L.remanence(tr, win, X, proj)
    pan = L.panel(rem, pin, "m", "pinned_own")
    out = {"pooled": L.persistence(pan, nboot=300), "switch": L.persistence(pan, nboot=300, switchers=True),
           "offset": L.offset_end(pan, nboot=300)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--model", default="bge_small")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    tr, win, pin = L.load_tables()
    Xr = L.load_X(win["srow"].to_numpy(), a.model)
    target = moments_real(win, Xr)
    cal = calibrate(target)
    print("target", target, "\ncal", cal, flush=True)
    proj = {int(P): {"Pperp": np.eye(32), "kick": None, "dim": 0} for P in tr["P"].to_list()}
    res = {w: [] for w in WORLDS}
    t0 = time.time()
    for w in WORLDS:
        for rep in range(a.reps):
            rng = np.random.default_rng(10000 * WORLDS.index(w) + rep)
            ws, Xs = gen(win, pin, cal, w, rng)
            res[w].append(run(tr, ws, Xs, pin, proj))
        print(w, f"{time.time() - t0:.0f}s", flush=True)
    summ = {"target": target, "cal": cal, "reps": a.reps, "model": a.model, "R1U": R1U, "worlds": {}}
    for w in WORLDS:
        o = {}
        for var in ("pooled", "switch"):
            rr = [x[var] for x in res[w] if x[var].get("n", 0) > 0]
            ratio = np.array([x["ratio"] for x in rr], float)
            lo = np.array([x["ratio_ci"][0] for x in rr], float)
            o[var] = {"n_ok": len(rr), "ratio_med": float(np.nanmedian(ratio)),
                      "ratio_iqr": [float(np.nanpercentile(ratio, 25)), float(np.nanpercentile(ratio, 75))],
                      "R1P_med": float(np.nanmedian([x["R1_P"] for x in rr])),
                      "R1U_med": float(np.nanmedian([x["R1_U"] for x in rr])),
                      "hh_pass": float(np.mean((ratio >= 2) & (lo > 1))),
                      "lo_gt1": float(np.mean(lo > 1)),
                      "kill_fires": float(np.mean((ratio >= 0.8) & (ratio <= 1.25))),
                      "dR_pos": float(np.mean([x["dR_ci"][0] > 0 for x in rr]))}
        oe = [x["offset"] for x in res[w] if x["offset"].get("n", 0) > 0 and x["offset"].get("live") is not None]
        o["offset"] = {"live_med": float(np.median([x["live"] for x in oe])) if oe else None,
                       "after_med": float(np.nanmedian([x["after"] if x["after"] is not None else np.nan for x in oe])) if oe else None,
                       "live_pos": float(np.mean([x["live_ci"][0] > 0 for x in oe])) if oe else None}
        summ["worlds"][w] = o
        print(w, json.dumps(o))
    (OUT / f"synthetic_summary_{a.model}.json").write_text(json.dumps(summ, indent=1, default=float))


if __name__ == "__main__":
    main()
