"""H103 synthetic validation (axis F), run before any real-data outcome.

O1: planted window vectors on the real window skeletons (incumbents, windows, clocks, slots) of every O1 period:
    s_iw = unit( A_p p_i + A_k(t) k_P + A_v v + xi_iw ),  A_k(t) = A_inf + dA f_T(t) [+ pulse in slot 0 for T-ToD]
    xi_iw = real within-agent-day window residuals (window vector - the agent-day mean of its windows), permuted
    across the period's windows. Truths T: N (lambda 0.5/night), H (tau 5 active h), W (tau 20 wall h),
    R (rho = 5 h x the period's resets per active hour), 0 (no decay), ToD (no decay; +0.25 amplitude pulse in the
    first quarter of every day).
    Outputs: clock confusion matrix, false-night rates (N wins; nested lambda < 1) under H, W, ToD, 0.
O3: latent per-agent processes on real unit skeletons: s_iw = unit(A_p p_i + A_x x_i(t_w) + xi_iw), with x an
    OU process on the active-hour clock (tau 4 h), a night-jump process (x constant inside a day, AR 0.6 per night),
    a time-of-day profile (shared per-slot directions) plus active-hour OU, or a wall-clock OU (tau 24 h).
    Outputs: size of beta_N under H and ToD, power under N; beta_G under W.
Writes data/processed/H103-nights-demagnetize/synthetic/synthetic.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h103lib as L  # noqa: E402

OUTD = L.DATA / "synthetic"
A_P, A_V, A_INF, D_A, PULSE = 0.6, 0.4, 0.2, 0.45, 0.25   # levels near H54: day-1 excess ~0.24, plateau ~0.11


def residuals(S: L.Store):
    w = S.w
    key = (w["agent"].cast(pl.String) + "|" + w["pt_date"]).to_numpy()
    _, inv = np.unique(key, return_inverse=True)
    sums = np.zeros((inv.max() + 1, 32)); cnt = np.bincount(inv)
    np.add.at(sums, inv, S.V)
    R = S.V - (sums / cnt[:, None])[inv]
    R[cnt[inv] < 2] = 0
    return R.astype(np.float32)


def f_truth(T, g, rate_r):
    H, N, W, R = (g[c].to_numpy().astype(float) for c in ("H", "N", "W", "Ri"))
    if T == "N":
        return 0.5 ** N
    if T == "H":
        return np.exp(-H / 5.0)
    if T == "W":
        return np.exp(-W / 20.0)
    if T == "R":
        return np.exp(-R / max(rate_r * 5.0, 1e-3))
    return np.zeros(len(H))


def plant_o1(S, rec, w, Rres, T, rng):
    rows = w["ri"].to_numpy()
    reg = rec["regime"]
    kP = S.G[reg][S.kick[rec["goal_no"]]]
    agents = w["agent"].to_numpy()
    P = {a: L.unit(rng.standard_normal(32)) for a in np.unique(agents)}
    v = L.unit(rng.standard_normal(32))
    Hh = w["H"].to_numpy(); Ri = w["Ri"].to_numpy().astype(float)
    rate_r = (Ri.max() / max(Hh.max(), 1e-3)) if len(Hh) else 1.0
    amp = A_INF + D_A * f_truth(T, w, rate_r)
    if T == "ToD":
        amp = amp + PULSE * (w["slot"].to_numpy() == 0)
    X = (A_P * np.stack([P[a] for a in agents]) + amp[:, None] * kP[None, :] + A_V * v[None, :]
         + Rres[rng.permutation(rows)])
    V = np.array(S.V, copy=True)
    V[rows] = L.unit(X)
    return V


def run_o1(S, Rres, n_rep, rng, truths=("N", "H", "W", "R", "0", "ToD"), n_boot=0, every=1):
    out = {T: [] for T in truths}
    recs = S.periods.to_dicts()[::every]
    for T in truths:
        for rec in recs:
            w = L.period_windows(S, rec)
            if w.height < 10:
                continue
            for rep in range(n_rep):
                V = plant_o1(S, rec, w, Rres, T, rng)
                r = L.o1_period(S, rec, n_boot=n_boot, seed=rep, V=V)
                out[T].append({"goal_no": rec["goal_no"], "winner": r["winner"], "lam": r["nested"]["lam"],
                               "lam_ci": r["lam_ci"], "verdict": r["verdict"], "N_beats_H": r["sse"]["N"] < r["sse"]["H"],
                               "SNmid": r["steps"]["S_N"] - r["steps"]["S_mid"],
                               "level_day1": float(np.nanmean(np.array(r["series"]["A"])[np.array(r["series"]["N"]) == 0])),
                               "level_last": float(np.nanmean(np.array(r["series"]["A"])[np.array(r["series"]["N"]) == max(r["series"]["N"])]))})
    summ = {}
    for T, rows in out.items():
        if not rows:
            continue
        summ[T] = {"n": len(rows), "winner_share": {c: float(np.mean([x["winner"] == c for x in rows])) for c in L.CLOCKS},
                   "N_beats_H": float(np.mean([x["N_beats_H"] for x in rows])),
                   "lam_median": float(np.median([x["lam"] for x in rows])),
                   "lam_below_0.9": float(np.mean([x["lam"] < 0.9 for x in rows])),
                   "SNmid_median": float(np.nanmedian([x["SNmid"] for x in rows])),
                   "level_day1_median": float(np.nanmedian([x["level_day1"] for x in rows])),
                   "level_last_median": float(np.nanmedian([x["level_last"] for x in rows]))}
        if n_boot:
            summ[T]["verdict_share"] = {v: float(np.mean([x["verdict"] == v for x in rows]))
                                        for v in ("supported", "failed", "mixed", "descriptive")}
    return summ, out


# ------------------------------------------------------------------------------------------- O3
def plant_o3(S, w, Rres, T, rng, A_X=0.7):
    rows = w["ri"].to_numpy()
    X = np.zeros((len(rows), 32))
    agents = w["agent"].to_numpy(); h = w["hcum"].to_numpy(); di = w["day_idx"].to_numpy()
    tm = w["t_mid"].dt.epoch("s").to_numpy() / 3600.0; sl = w["slot"].to_numpy()
    tod = {k: L.unit(rng.standard_normal(32)) for k in range(4)}
    for a in np.unique(agents):
        m = np.flatnonzero(agents == a)
        o = m[np.argsort(h[m])]
        p = L.unit(rng.standard_normal(32))
        x = np.zeros((len(o), 32))
        if T in ("H", "W", "ToD"):
            clk = h[o] if T != "W" else tm[o]
            tau = 4.0 if T != "W" else 24.0
            x[0] = rng.standard_normal(32)
            for k in range(1, len(o)):
                r = np.exp(-(clk[k] - clk[k - 1]) / tau)
                x[k] = r * x[k - 1] + np.sqrt(1 - r * r) * rng.standard_normal(32)
            if T == "ToD":
                x = 0.8 * x + 1.2 * np.stack([tod[s] for s in sl[o]]) * np.sqrt(32) / 2
        elif T == "N":
            cur = rng.standard_normal(32)
            for k in range(len(o)):
                if k > 0 and di[o[k]] != di[o[k - 1]]:
                    for _ in range(di[o[k]] - di[o[k - 1]]):
                        cur = 0.6 * cur + 0.8 * rng.standard_normal(32)
                x[k] = cur
        X[o] = A_P * p + A_X * x / np.sqrt(32)
    X = X + Rres[rng.permutation(rows)]
    V = np.array(S.V, copy=True)
    V[rows] = L.unit(X)
    return V


def run_o3(S, Rres, n_rep, rng, units=("38a", "20", "40", "51c", "13", "27")):
    res = {}
    for T in ("H", "N", "ToD", "W"):
        rows = []
        for u in units:
            w = S.w.with_row_index("ri").filter(pl.col("unit_id") == u)
            if w.height < 50:
                continue
            for rep in range(n_rep):
                V = plant_o3(S, w, Rres, T, rng)
                p = L.unit_pairs(S, w, V)
                f = L.o3_fit(p, n_boot=40, seed=rep)
                rows.append({"unit": u, **{k: f[k] for k in ("beta_N", "beta_G", "beta_gap")}})
        def rej(k, side):
            v = [x[k] for x in rows]
            return float(np.mean([(x["hi"] < 0) if side < 0 else (x["lo"] > 0) for x in v]))
        res[T] = {"n": len(rows), "beta_N_median": float(np.median([x["beta_N"]["est"] for x in rows])),
                  "beta_N_neg_rate": rej("beta_N", -1), "beta_N_pos_rate": rej("beta_N", 1),
                  "beta_G_median": float(np.nanmedian([x["beta_G"]["est"] for x in rows])),
                  "beta_G_neg_rate": rej("beta_G", -1),
                  "beta_gap_neg_rate": rej("beta_gap", -1), "rows": rows}
        print("O3", T, {k: v for k, v in res[T].items() if k != "rows"}, flush=True)
    return res


def main(n_rep_sel=10, n_rep_boot=3, n_rep_o3=4, seed=11):
    OUTD.mkdir(parents=True, exist_ok=True)
    S = L.Store("bge_small", "style_resid")
    S.w = S.w  # windows frame
    Rres = residuals(S)
    rng = np.random.default_rng(seed)
    t = time.time()
    sel, _ = run_o1(S, Rres, n_rep_sel, rng)
    print("O1 selection", json.dumps(sel, indent=0), f"{time.time()-t:.0f}s", flush=True)
    boot, _ = run_o1(S, Rres, n_rep_boot, rng, truths=("N", "H", "ToD", "0"), n_boot=25, every=3)
    print("O1 verdicts", json.dumps(boot, indent=0), f"{time.time()-t:.0f}s", flush=True)
    o3 = run_o3(S, Rres, n_rep_o3, rng)
    (OUTD / "synthetic.json").write_text(json.dumps({"o1_selection": sel, "o1_verdicts": boot, "o3": o3,
                                                      "params": {"A_P": A_P, "A_V": A_V, "A_INF": A_INF, "D_A": D_A,
                                                                 "PULSE": PULSE}}, indent=1, default=float))
    print("done", f"{time.time()-t:.0f}s")


if __name__ == "__main__":
    main(*[int(x) for x in sys.argv[1:]])
