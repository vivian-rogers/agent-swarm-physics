"""H75 synthetic validation (axis F): agents re-allocating across repos, observed only at work commits.

Scenarios (card, "Synthetic validation plan"):
  F  field-limited: target hazard 1/tau_f (tau_f = 5 active h), independent of cadence
  A  activity-limited: target hazard q * a_i with a_i proportional to the call rate (5 h at the median cadence)
  Z  instant freeze: every agent is on its target from t = 0 (seen at its first commit)
All scenarios carry churn: excursions to a side repo at rate a_i (1/h at the median cadence), mean 20 min.
Call rates lognormal (median 130/h, SD 0.8 in log units; H40 G51 spread); commits Poisson with rate 4 (r/130)^0.5 per h.

  uv run python hypotheses/H75-reallocation-speed-limit/analysis/synthetic.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h75lib as L  # noqa: E402

OUT = L.OUTD / "synthetic"
H = 20.0
TAU_F = 5.0


def simulate(N, scen, rng, tau_f=TAU_F, a0=1.0, exc_mean=1 / 3, c0=4.0, shared_target=0.5):
    r = np.exp(np.log(130) + 0.8 * rng.standard_normal(N))
    a = a0 * r / 130
    c = c0 * np.sqrt(r / 130) * np.exp(0.5 * rng.standard_normal(N) - 0.125)   # commit rates scatter at fixed cadence
    times, codes, init, tmove = [], [], np.empty(N, np.int64), np.empty(N)
    for i in range(N):
        old = 1000 if rng.random() < 0.3 else 100 + i
        tgt = 3000 if rng.random() < shared_target else 2000 + i
        side = 5000 if rng.random() < 0.5 else 6000 + i
        if scen == "F":
            tm = rng.exponential(tau_f)
        elif scen == "A":
            tm = rng.exponential(1 / ((1 / tau_f) * a[i] / a0))
        else:
            tm = 0.0
        tmove[i] = tm
        # excursions
        ex = []
        t = rng.exponential(1 / a[i])
        while t < H:
            d = rng.exponential(exc_mean)
            ex.append((t, t + d))
            t = t + d + rng.exponential(1 / a[i])
        n = rng.poisson(c[i] * H)
        tc = np.sort(rng.uniform(0, H, n))
        cc = np.where(tc < tm, old, tgt)
        for s0, s1 in ex:
            cc = np.where((tc >= s0) & (tc < s1), side, cc)
        times.append(tc)
        codes.append(cc.astype(np.int64))
        init[i] = old if rng.random() > 0.1 else L.NULL
    E = L.Ensemble(list(range(N)), times, codes, init, H)
    return E, r, tmove


def one(N, scen, seed):
    rng = np.random.default_rng(seed)
    E, r, tm = simulate(N, scen, rng)
    s = L.settle_stats(E)
    ag = L.agent_settling(E).with_columns(pl.Series("call_rate", r))
    el = L.elasticity(ag)
    em = L.elasticity(ag, "t_mid")
    return {"N": N, "scen": scen, "seed": seed, **{k: s[k] for k in s if k != "curve_D"}, **{f"el_{k}": v for k, v in el.items()},
            **{f"em_{k}": v for k, v in em.items()},
            "true_median_move": float(np.median(tm))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for N in (15, 25):
        for scen in ("F", "A", "Z"):
            for rep in range(100):
                rows.append(one(N, scen, 100000 * N + 1000 * ord(scen) + rep))
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "synthetic.parquet")
    summ = df.group_by(["N", "scen"], maintain_order=True).agg(
        pl.col("viol_e").sum().alias("viol_e"), pl.col("viol_90").sum().alias("viol_90"),
        pl.col("T_e").median(), pl.col("T_e").is_nan().mean().alias("T_e_cens"), pl.col("S_e").median(),
        pl.col("S_e").quantile(0.1).alias("S_e_q10"), pl.col("R_e").median(), pl.col("T_90").median(),
        pl.col("S_90").median(), (pl.col("S_e") >= 3).mean().alias("P_S_ge3"),
        pl.col("el_eps").mean().alias("eps_mean"), pl.col("el_eps").std().alias("eps_sd"),
        pl.col("el_eps_ctrl").mean().alias("eps_ctrl_mean"), pl.col("el_eps_ctrl").std().alias("eps_ctrl_sd"),
        ((pl.col("el_eps_ctrl") + 1).abs() / pl.col("el_se_ctrl") > 1.96).mean().alias("rej_m1_ctrl"),
        ((pl.col("el_eps_ctrl")).abs() / pl.col("el_se_ctrl") > 1.96).mean().alias("rej_0_ctrl"),
        ((pl.col("el_eps") + 1).abs() / pl.col("el_se") > 1.96).mean().alias("rej_m1"),
        ((pl.col("el_eps")).abs() / pl.col("el_se") > 1.96).mean().alias("rej_0"),
        pl.col("em_eps").mean().alias("mid_eps_mean"), pl.col("em_eps").std().alias("mid_eps_sd"),
        pl.col("em_eps_ctrl").mean().alias("mid_ctrl_mean"), pl.col("em_eps_ctrl").std().alias("mid_ctrl_sd"),
        ((pl.col("em_eps_ctrl") + 1).abs() / pl.col("em_se_ctrl") > 1.96).mean().alias("mid_rej_m1_ctrl"),
        ((pl.col("em_eps") + 1).abs() / pl.col("em_se") > 1.96).mean().alias("mid_rej_m1"),
        pl.col("el_n").median().alias("n_agents_ti"))
    summ.write_parquet(OUT / "summary.parquet")
    with pl.Config(tbl_cols=-1, tbl_width_chars=300, float_precision=3):
        print(summ)


if __name__ == "__main__":
    main()
