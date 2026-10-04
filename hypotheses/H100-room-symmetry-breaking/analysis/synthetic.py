"""H100 synthetic validation (axis F, card P0) on the real agent x day x room skeleton of #35-#51 (non-holdout).

Generator (day-centered space): x_{i,d} = a_i + b_{r(i,d),P} + eps_{i,d}
  a_i ~ N(0, tau_a^2 I_32) (+ a composition-sorting term delta*s_i*w/2, s_i = +1 for agents whose majority room over
  #35-#44 is #best);  b_{r,P} = +-(beta/2) v_P;  eps ~ N(0, sigma^2 I).
Noise scale sigma and constant spread tau_a are calibrated on the real style_resid bge vectors (within-agent
day-to-day variance; cross-period covariance of agent constants, O2a's numerator). These are instrument
calibrations, not H100 outcomes.
Worlds: null, comp (sorted composition), field (b along the real #38/#44 room-kickoff directions only),
spont (random v_P per period, movers adopt the new room), carry (as spont, but movers keep the old room's b in the
post period), mixed (comp + field + spont).
Room-effect size: rho = |b_best - b_rest|^2 / E|a_i - a_j|^2.

Usage: uv run python hypotheses/H100-room-symmetry-breaking/analysis/synthetic.py [--reps 40]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h100lib as L  # noqa: E402

OUTD = L.DATA / "synthetic"


def calibrate(tab, Xc):
    v = []
    for P in L.REG3:
        m = ((tab["goal_no"] == P) & (tab["regime"] == "III")).to_numpy()
        sub = tab.filter(pl.Series(m)).with_columns(pl.Series("ix", np.nonzero(m)[0]))
        for _, g in sub.group_by("agent"):
            if g.height >= 2:
                v.append(Xc[g["ix"].to_numpy()].var(0, ddof=1).mean())
    sigma2 = float(np.median(v))
    inv = L.constants_invariance(tab, Xc, n_perm=10)
    odd, even = inv["odd"], inv["even"]
    A, _ = L.constants(tab, Xc, exclude=set(even)); B, _ = L.constants(tab, Xc, exclude=set(odd))
    ag = sorted(set(A) & set(B))
    a = np.array([A[x] for x in ag]); b = np.array([B[x] for x in ag]); a -= a.mean(0); b -= b.mean(0)
    tau2 = float(max((a * b).sum() / (len(ag) - 1) / a.shape[1], 1e-6))
    return sigma2, tau2


def gen(tab, world, sigma2, tau2, rho, rng, E_field, delta_comp=0.0):
    agents = tab["agent"].unique().sort().to_list()
    d = 32
    a = {k: rng.normal(0, np.sqrt(tau2), d) for k in agents}
    if delta_comp > 0:
        w = rng.standard_normal(d); w /= np.linalg.norm(w)
        maj = (tab.filter(pl.col("goal_no").is_between(35, 44) & pl.col("room").is_in([L.BEST, L.REST]))
               .group_by("agent").agg((pl.col("room") == L.BEST).mean().alias("fb")))
        for k, fb in maj.iter_rows():
            a[k] = a[k] + (delta_comp / 2) * (1 if fb > 0.5 else -1) * w
    beta = np.sqrt(rho * 2 * d * tau2)
    b = {}
    for P in range(33, 52):
        if world in ("spont", "carry", "mixed"):
            v = rng.standard_normal(d); v /= np.linalg.norm(v)
            b[P] = v
        if world in ("field", "mixed") and P in E_field and E_field[P].shape[0]:
            b[P] = b.get(P, 0) + E_field[P][0] * (1.0 if world == "field" else 1.0)
    X = np.empty((tab.height, d))
    carry = {}
    if world == "carry":
        for bnd, (pre, post, movers) in L.MOVES.items():
            for k, (frm, to) in movers.items():
                carry[(k, post)] = frm
    for i, (ag, P, room) in enumerate(zip(tab["agent"].to_list(), tab["goal_no"].to_list(), tab["room"].to_list())):
        x = a[ag].copy()
        if P in b and room in (L.BEST, L.REST):
            r_eff = carry.get((ag, P), room)
            sgn = 1.0 if r_eff == L.BEST else -1.0
            bv = b[P] / np.linalg.norm(b[P])
            x += sgn * (beta / 2) * bv
        X[i] = x + rng.normal(0, np.sqrt(sigma2), d)
    return X


def run(reps: int, rhos=(0.1, 0.3, 1.0)):
    tab, X = L.load("bge_small", "style_resid")
    Xc = L.day_center(tab, X)
    sigma2, tau2 = calibrate(tab, Xc)
    fields = pl.read_parquet(L.DATA / "fields.parquet")
    F = np.load(L.DATA / "fields_bge_small.npy")
    E_field = {P: L.field_basis(fields, F, P)[0] for P in L.FIELDED}
    rng = np.random.default_rng(20261004)
    worlds = ["null", "comp", "field", "spont", "carry", "mixed"]
    out = {"sigma2": sigma2, "tau2": tau2, "reps": reps, "worlds": {}}
    periods = [36, 37, 38, 39, 41, 42, 44]
    for world in worlds:
        for rho in (rhos if world not in ("null",) else (0.0,)):
            key = f"{world}_rho{rho}"
            rec = {"Q_p": [], "Qres_p": [], "Qspont_p": [], "f_comp": [], "f_field_fielded": [],
                   "f_field_p_fielded": [], "f_spont": [], "phi_post": [], "phi_comp": [], "phi_pre": [],
                   "phi_day1": [], "R": [], "C_ok": []}
            for r in range(reps):
                Xs = gen(tab, world, sigma2, tau2, rho, rng, E_field,
                         delta_comp=np.sqrt(rho * 2 * 32 * tau2) if world in ("comp", "mixed") else 0.0)
                Xsc = L.day_center(tab, Xs)
                for P in periods:
                    res = L.decompose(tab, Xsc, fields, F, P, n_null=200, n_boot=0, seed=r)
                    rec["Q_p"].append(res["p"]); rec["Qres_p"].append(res["p_res"]); rec["Qspont_p"].append(res["p_spont"])
                    sig = res["p"] < 0.05  # shares are read only where the rooms differ (card: O2-O4 on separated rooms)
                    rec["f_comp"].append(res["f_comp"] if sig else np.nan)
                    rec["f_spont"].append(res["f_spont"] if sig else np.nan)
                    if P in L.FIELDED:
                        rec["f_field_fielded"].append(res["f_field"] if sig else np.nan); rec["f_field_p_fielded"].append(res.get("f_field_p", np.nan))
                for bnd in L.MOVES:
                    mv = L.mover_index(tab, Xsc, bnd, n_boot=0)
                    for k, m in mv["movers"].items():
                        if m.get("skip"):
                            continue
                        ok = m["C_post_p"] < 0.05
                        rec["C_ok"].append(float(ok))
                        rec["phi_post"].append(m["phi_post"] if ok else np.nan)
                        rec["phi_comp"].append(m.get("phi_comp", np.nan) if ok else np.nan)
                        rec["phi_pre"].append(m.get("phi_pre", np.nan)); rec["phi_day1"].append(m["phi_day1"])
                rm = L.remanence(tab, Xsc, fields, F, 39, 41, n_null=200, seed=r)
                rec["R"].append(rm["R"])
            s = {}
            for k, v in rec.items():
                v = np.array(v, dtype=float)
                if k == "C_ok":
                    continue
                if k.endswith("_p") or k.endswith("_p_fielded"):
                    s[k + "_rej05"] = float(np.nanmean(v < 0.05))
                else:
                    s[k + "_med"] = float(np.nanmedian(v)) if len(v) else None
                    s[k + "_q10_q90"] = [float(np.nanpercentile(v, 10)), float(np.nanpercentile(v, 90))] if len(v) else None
            phi_post = np.array(rec["phi_post"]); phi_comp = np.array(rec["phi_comp"])
            s["mover_pass_rate"] = float(np.nanmean((phi_post >= 0.5) & (phi_post - phi_comp >= 0.5)))
            # per world: fraction of reps in which >= 3/5 movers pass (P5's rule)
            per = phi_post.reshape(reps, -1); perc = phi_comp.reshape(reps, -1)
            s["P5_rule_rate"] = float(np.mean(((per >= 0.5) & (per - perc >= 0.5)).sum(1) >= 3))
            s["C_ok_rate"] = float(np.mean(rec["C_ok"]))
            out["worlds"][key] = s
            print(key, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()}), flush=True)
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / "synthetic_summary.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    a = ap.parse_args()
    run(a.reps)
