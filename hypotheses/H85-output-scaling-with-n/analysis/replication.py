"""H85 replication layer: unit-level exponents across the 71 non-holdout units (goal-cluster bootstrap CIs).

Reads data/processed/H85-output-scaling-with-n/units.parquet (scheme/build.py). Holdout units are not in it (asserted).
Writes replication/replication.json and replication/unit_points.parquet (per-unit M1 residuals).
Usage: uv run python hypotheses/H85-output-scaling-with-n/analysis/replication.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h85lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import load_holdout  # noqa: E402

B = 2000
RATE_OUT = ["msg", "ment", "reply", "reply_any", "talk_calls", "commit"]


def load():
    u = pl.read_parquet(L.DATA / "units.parquet")
    held = set(load_holdout()["goal_periods_held_out"])
    assert not set(u["goal_no"].to_list()) & held, "held-out goal in units"
    return u.filter((pl.col("T_h") >= 1) & (pl.col("msg") >= 20))


def tcrit(G):
    from scipy.stats import t
    return float(t.ppf(0.975, max(G - 1, 1)))


def fit(u, y, nvar="N", regime=True, extra=None, w=None, unit_boot=False):
    lnN = np.log(u[nvar].to_numpy())
    f = L.fit_beta(y, lnN, u["regime"].to_numpy() if regime else None, u["goal_no"].to_numpy(), extra=extra, w=w, B=B,
                   unit_boot=unit_boot)
    q = tcrit(f["n_goals"])
    f["ci_cr1"] = [f["beta"] - q * f["se_cr1"], f["beta"] + q * f["se_cr1"]]
    f["ci_wide"] = [min(f["ci_lo"], f["ci_cr1"][0]), max(f["ci_hi"], f["ci_cr1"][1])]
    f.pop("coefs", None)
    return f


def joint_boot(u, ys: dict, rng):
    """Joint goal-cluster bootstrap of M1 slopes for several outcomes on the same units."""
    lnN = np.log(u["N"].to_numpy())
    X, names = L.design(lnN, u["regime"].to_numpy())
    cl = u["goal_no"].to_numpy()
    groups = sorted(set(cl))
    idx_by = {g: np.where(cl == g)[0] for g in groups}
    out = {k: [] for k in ys}
    for _ in range(B):
        ii = np.concatenate([idx_by[groups[p]] for p in rng.choice(len(groups), len(groups), replace=True)])
        for k, y in ys.items():
            out[k].append(L.ols(X[ii], y[ii])[0])
    return {k: np.asarray(v) for k, v in out.items()}


def ci(a):
    a = a[np.isfinite(a)]
    return [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))]


def main():
    rng = np.random.default_rng(20261004)
    u = load()
    T = u["T_h"].to_numpy()
    res = {"n_units": u.height, "n_goals": int(u["goal_no"].n_unique()), "B": B}

    # O1 level exponents
    lev = {}
    for k in RATE_OUT:
        sub = u.filter(pl.col(k) > 0)
        if k == "commit":
            sub = sub.filter(pl.col("git_dense"))
        y = np.log(sub[k].to_numpy() / sub["T_h"].to_numpy())
        lev[k] = {"M1": fit(sub, y, unit_boot=True), "M0": fit(sub, y, regime=False),
                  "M2": fit(sub, y, extra={"shared": sub["shared_mode"].to_numpy().astype(float)}),
                  "WLS": fit(sub, y, w=np.minimum(sub["T_h"].to_numpy(), 40)),
                  "N_roster": fit(sub, y, nvar="n_roster"), "N_span": fit(sub, y, nvar="N_span"),
                  "active_hours": fit(sub.filter(pl.col("active_hours") > 0),
                                      np.log(sub.filter(pl.col("active_hours") > 0)[k].to_numpy()
                                             / sub.filter(pl.col("active_hours") > 0)["active_hours"].to_numpy()))}
        for r in ("I", "III"):
            s2 = sub.filter(pl.col("regime") == r)
            lev[k][f"within_{r}"] = fit(s2, np.log(s2[k].to_numpy() / s2["T_h"].to_numpy()), regime=False) if s2.height >= 8 else None
        lev[k]["n"] = sub.height
    res["levels"] = lev

    # O2 mechanism: gamma_k (k_talk on N), rho (talk calls per agent-hour), per-message ratios
    sub = u.filter((pl.col("k_n") > 0) & (pl.col("ment") > 0) & (pl.col("reply") > 0) & (pl.col("talk_calls") > 0))
    lnk = np.log(sub["k_talk"].to_numpy())
    ys = {"msg": np.log(sub["msg"].to_numpy() / sub["T_h"].to_numpy()),
          "ment": np.log(sub["ment"].to_numpy() / sub["T_h"].to_numpy()),
          "reply": np.log(sub["reply"].to_numpy() / sub["T_h"].to_numpy()),
          "k": lnk,
          "rho": np.log(sub["talk_calls"].to_numpy() / (sub["N"].to_numpy() * sub["T_h"].to_numpy())),
          "ment_per_msg": np.log(sub["ment"].to_numpy() / sub["msg"].to_numpy()),
          "reply_per_msg": np.log(sub["reply"].to_numpy() / sub["msg"].to_numpy()),
          "msg_per_talk": np.log(sub["msg"].to_numpy() / sub["talk_calls"].to_numpy())}
    X = L.design(np.log(sub["N"].to_numpy()), sub["regime"].to_numpy())[0]
    pt = {k: float(L.ols(X, y)[0]) for k, y in ys.items()}
    jb = joint_boot(sub, ys, rng)
    mech = {k: {"est": pt[k], "ci": ci(jb[k])} for k in ys}
    d_ment = jb["ment_per_msg"] - (1 - L.BETA_D) * jb["k"]
    d_reply = jb["reply_per_msg"] - 0.25 * jb["k"]
    mech["ment_minus_pred"] = {"est": pt["ment_per_msg"] - (1 - L.BETA_D) * pt["k"], "ci": ci(d_ment)}
    mech["reply_minus_pred"] = {"est": pt["reply_per_msg"] - 0.25 * pt["k"], "ci": ci(d_reply)}
    mech["pred_dbeta_ment"] = {"est": (1 - L.BETA_D) * pt["k"], "ci": ci((1 - L.BETA_D) * jb["k"])}
    mech["pred_dbeta_reply"] = {"est": 0.25 * pt["k"], "ci": ci(0.25 * jb["k"])}
    mech["n_units"] = sub.height
    for r in ("I", "III"):
        s2 = sub.filter(pl.col("regime") == r)
        X2 = L.design(np.log(s2["N"].to_numpy()), None)[0]
        mech[f"within_{r}"] = {k: float(L.ols(X2, np.log(s2[a].to_numpy() / s2[b].to_numpy()) if b else np.log(s2[a].to_numpy()))[0])
                               for k, a, b in (("ment_per_msg", "ment", "msg"), ("reply_per_msg", "reply", "msg"),
                                               ("k", "k_talk", None))}
    res["mechanism"] = mech

    # O3 repos per day by mode class (git-dense units)
    g = u.filter(pl.col("git_dense") & (pl.col("repos_day") > 0))
    rep = {}
    for cls, flag in (("own", False), ("shared", True)):
        s2 = g.filter(pl.col("shared_mode") == flag)
        if s2.height >= 6:
            rep[cls] = fit(s2, np.log(s2["repos_day"].to_numpy()), extra={"ln_hday": np.log(s2["h_day"].to_numpy())})
            rep[cls]["n"] = s2.height
    lnN = np.log(g["N"].to_numpy()); sh = g["shared_mode"].to_numpy().astype(float)
    rep["interaction"] = fit(g, np.log(g["repos_day"].to_numpy()),
                             extra={"lnN_x_shared": lnN * sh, "shared": sh, "ln_hday": np.log(g["h_day"].to_numpy())})
    rep["interaction"] |= L.fit_beta(np.log(g["repos_day"].to_numpy()), lnN, g["regime"].to_numpy(), g["goal_no"].to_numpy(),
                                     extra={"lnN_x_shared": lnN * sh, "shared": sh, "ln_hday": np.log(g["h_day"].to_numpy())},
                                     coef="lnN_x_shared", B=B)
    rep["interaction"].pop("coefs", None)
    res["repos"] = rep

    # O4 residuals per unit (M1, all-unit fits)
    pts = u.select("unit_id", "goal_no", "regime", "mode", "N", "T_h", "msg", "ment", "reply", "commit", "repos_day", "k_talk",
                   "talk_calls")
    X = L.design(np.log(u["N"].to_numpy()), u["regime"].to_numpy())[0]
    for k in ("msg", "ment", "reply", "commit"):
        y = np.log(np.maximum(u[k].to_numpy(), 0.5) / T)
        okm = u[k].to_numpy() > 0
        if k == "commit":
            okm &= u["git_dense"].to_numpy()
        b = L.ols(X[okm], y[okm])
        r = np.full(len(y), np.nan)
        r[okm] = y[okm] - X[okm] @ np.nan_to_num(b)
        pts = pts.with_columns(pl.Series(f"resid_{k}", r))
    out = L.DATA / "replication"
    out.mkdir(parents=True, exist_ok=True)
    pts.write_parquet(out / "unit_points.parquet")
    (out / "replication.json").write_text(json.dumps(res, indent=1, default=float))

    # console summary
    for k, v in lev.items():
        m = v["M1"]
        print(f"{k:10s} n={v['n']:2d} beta={m['beta']:.3f} [{m['ci_lo']:.3f},{m['ci_hi']:.3f}] cr1 [{m['ci_cr1'][0]:.3f},{m['ci_cr1'][1]:.3f}]"
              f" M0={v['M0']['beta']:.3f} M2={v['M2']['beta']:.3f} WLS={v['WLS']['beta']:.3f} roster={v['N_roster']['beta']:.3f}"
              f" span={v['N_span']['beta']:.3f} act_h={v['active_hours']['beta']:.3f}"
              f" I={v['within_I']['beta'] if v['within_I'] else float('nan'):.3f} III={v['within_III']['beta'] if v['within_III'] else float('nan'):.3f}")
    for k, v in mech.items():
        if isinstance(v, dict) and "est" in v:
            print(f"mech {k:18s} {v['est']:.3f} {v['ci']}")
    print("mech within", mech["within_I"], mech["within_III"])
    for k, v in rep.items():
        print("repos", k, round(v["beta"], 3), round(v["ci_lo"], 3), round(v["ci_hi"], 3), v.get("n"))


if __name__ == "__main__":
    main()
