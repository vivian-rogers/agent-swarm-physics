"""H105 synthetic validation (axis F), before the real analysis.

Heterogeneous Curie-Weiss Glauber dynamics of latent on-goal spins on the REAL window structure of each primary pair
(which agent-windows are eligible and how many statements each has; no content), observed through statements: each
statement is on-goal with probability Q1 if the latent spin is on, Q0 = 0.05 (the decoy rate) if off; the measured spin
is the majority rule, exactly as in the real pipeline. Scenarios (assigned week A vs free week F):
  H      tilt: h_i^A = h_i^F + LAM, J unchanged
  Hs     small tilt (LAM / 2)
  R5     coupling change: J_A = 2.5 J_F
  R5s    scheduled drive in A: a common field shock per 4-window block (sd 1.2)
  R2     common target: h_i^A equal for all agents
  R6     agent-specific receptivity: lambda_i = LAM + N(0, 1.5)
Writes data/processed/H105-two-state-goal-order/synthetic/results.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h105lib as L  # noqa: E402

PAIRS = ["P11_12", "P16_17", "P37_38"]
P0, H_SD, J_F, LAM, Q1, Q0, UPD = 0.06, 0.8, 3.0, 2.0, 0.6, 0.05, 0.6


def structure(design):
    st, pr, thr = L.load(design)
    on = np.zeros(st.height, bool)
    F = L.spin_tables(st, on, "F"); A = L.spin_tables(st, on, "A")
    ag = L.common_agents(F, A)
    return L.restrict(F, ag), L.restrict(A, ag)


def glauber(rng, h, J, T, drive=None):
    n = len(h)
    s = (rng.random(n) < 1 / (1 + np.exp(-h))).astype(float)
    out = np.empty((T, n))
    for t in range(T):
        f = 0.0 if drive is None else drive[t]
        for i in rng.permutation(n):
            if rng.random() > UPD:
                continue
            m = (s.sum() - s[i]) / n
            s[i] = float(rng.random() < 1 / (1 + np.exp(-(h[i] + f + J * (m + 0.5 / n)))))
        out[t] = s
    return out


def observe(rng, lat, Nn):
    k = rng.binomial(Nn.astype(int), np.where(lat > 0.5, Q1, Q0))
    S = np.where(Nn >= L.MIN_STMT_WIN, (k >= 0.5 * Nn).astype(float), np.nan)
    return S, k.astype(float)


def one(rng, F, A, scen):
    n = len(F["agents"])
    hF = np.log(P0 / (1 - P0)) + rng.normal(0, H_SD, n)
    lam = LAM / 2 if scen == "Hs" else LAM
    if scen == "R2":
        hA = np.full(n, np.log(P0 / (1 - P0)) + lam)
    elif scen == "R6":
        hA = hF + lam + rng.normal(0, 1.5, n)
    else:
        hA = hF + lam
    JA = J_F * 2.5 if scen == "R5" else J_F
    drive = None
    if scen == "R5s":
        TA = A["S"].shape[0]
        drive = np.repeat(rng.normal(0, 1.2, TA // 4 + 1), 4)[:TA]
    latF = glauber(rng, hF, J_F, F["S"].shape[0]); latA = glauber(rng, hA, JA, A["S"].shape[0], drive)
    SF, KF = observe(rng, latF, F["N"]); SA, KA = observe(rng, latA, A["N"])
    Fs = dict(F, S=SF, K=KF); As = dict(A, S=SA, K=KA)
    core = L.pair_core(SF, SA)
    bs = L.boot_pair(Fs, As, n_boot=150, seed=int(rng.integers(1e9)))
    lo, hi = np.nanpercentile(bs["rho"], 5), np.nanpercentile(bs["rho"], 95)
    dlo, dhi = np.nanpercentile(bs["dg"], 5), np.nanpercentile(bs["dg"], 95)
    ls = L.logit_slope(Fs, As, n_boot=150, seed=int(rng.integers(1e9)))
    return dict(rho=core["rho"], rho_lo=lo, rho_hi=hi, p1=L.p1_verdict(core["rho"], lo, hi), pF=core["pF"], pA=core["pA"],
                gF=core["gF"], gA=core["gA"], dg=core["dg"], p3_pass=bool(dlo <= 0 <= dhi), p3_fail=bool(dlo > 0),
                s=ls["s"], p2=L.p2_verdict(ls["s"], ls["lo"], ls["hi"]), crit=core["crit"],
                cov=bool(lo <= core["rho"] <= hi))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--scen", default="H,Hs,R5,R5s,R2,R6")
    args = ap.parse_args()
    structs = {d: structure(d) for d in PAIRS}
    print({d: (len(F["agents"]), F["S"].shape[0], A["S"].shape[0]) for d, (F, A) in structs.items()})
    out = {"params": dict(P0=P0, H_SD=H_SD, J_F=J_F, LAM=LAM, Q1=Q1, Q0=Q0, UPD=UPD), "reps": args.reps, "scenarios": {}}
    for scen in args.scen.split(","):
        rng = np.random.default_rng(abs(hash(scen)) % 2 ** 32)
        rows = []
        for rep in range(args.reps):
            for d, (F, A) in structs.items():
                r = one(rng, F, A, scen); r.update(pair=d, rep=rep); rows.append(r)
        df = pl.DataFrame(rows)
        # combined verdict per replicate (3 pairs): supported if >= 2/3 supported and none failed; failed if >= 2/3 failed same sign
        comb = []
        for rep, g in df.group_by("rep"):
            v = g["p1"].to_list(); rh = g["rho"].to_numpy()
            nf_pos = sum(1 for x, r in zip(v, rh) if x == "failed" and r > 0); nf_neg = sum(1 for x, r in zip(v, rh) if x == "failed" and r < 0)
            sup = v.count("supported") >= 2 and v.count("failed") == 0
            fail = nf_pos >= 2 or nf_neg >= 2
            p2s = g["p2"].to_list()
            comb.append(dict(sup=sup, fail=fail, p2_sup=p2s.count("supported") >= 2, p2_fail=p2s.count("failed") >= 2))
        cb = pl.DataFrame(comb)
        summ = dict(p1_supported_pair=float((df["p1"] == "supported").mean()), p1_failed_pair=float((df["p1"] == "failed").mean()),
                    p1_comb_supported=float(cb["sup"].mean()), p1_comb_failed=float(cb["fail"].mean()),
                    rho_median=float(df["rho"].median()), rho_q10=float(df["rho"].quantile(0.1)), rho_q90=float(df["rho"].quantile(0.9)),
                    ci_coverage_of_point=float(df["cov"].mean()),
                    p2_supported_pair=float((df["p2"] == "supported").mean()), p2_failed_pair=float((df["p2"] == "failed").mean()),
                    p2_comb_supported=float(cb["p2_sup"].mean()), p2_comb_failed=float(cb["p2_fail"].mean()),
                    s_median=float(df["s"].median()), p3_pass=float(df["p3_pass"].mean()), p3_fail=float(df["p3_fail"].mean()),
                    dg_median=float(df["dg"].median()), pF=float(df["pF"].median()), pA=float(df["pA"].median()),
                    gF=float(df["gF"].median()), gA=float(df["gA"].median()), crit=float(df["crit"].mean()))
        out["scenarios"][scen] = summ
        print(scen, {k: round(v, 3) for k, v in summ.items()}, flush=True)
    (L.DATA / "synthetic").mkdir(exist_ok=True)
    (L.DATA / "synthetic/results.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
