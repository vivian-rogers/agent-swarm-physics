"""H138 synthetic validation (axis F) on the real skeletons, before any real-data hazard statistic.

Worlds (card): W0 renewal walker (gamma_d = -0.3, eps = 0); W1 Glauber walker (eps = 1 and 0.5); W2 co-arrival bursts
(leaves driven by project births in windows g-2..g+2, eps = 0); W3 shared drive (leaves driven by the number of active
agents, which also raises q; eps = 0); W4 label noise (attention only: spurious switches at a rate per call x q_live,
30% of leaves, plus their return switch). Agent frailty theta_i ~ N(0, 0.5). The base rate is calibrated to the real
leave count of the unit-channel (a structural count). Only the leave outcomes are redrawn; the rows, own calls, q series,
births and actives are the real skeleton (targets do not feed back into others' menus: a stated simplification).

Per replicate: O1 (eps_q with the agent-cluster sandwich, t(G-1)), O3 (eps_q - eps_lead, sandwich), and the DL pool of
eps_q over the channel's skeletons. O4 power at b_q = 1: per-unit ln r_u = c + b ln(qbar_u) + e_u with
e_u ~ N(0, 1/n_leaves_u + tau^2), tau = 0.5, over the real testable work units, WLS and a unit bootstrap.

Writes data/processed/H138-glauber-escape-vs-options/synthetic/{reps.parquet, summary.json}.
Usage: uv run python hypotheses/H138-glauber-escape-vs-options/analysis/synthetic.py [--reps 200]
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
import h138lib as L  # noqa: E402

CARD_SKEL = {"work": [("G31", "31"), ("G38", "38"), ("G41", "41"), ("G44", "44"), ("G51", "51c"), ("G51", "51g")],
             "attention": [("G19", "19"), ("G38", "38"), ("G51", "51d")]}


def testable_units(ch: str) -> list[tuple[str, str]]:
    """Every unit-channel with >= 25 leaves (structural count from the scheme's counts.json)."""
    out = []
    for g in (L.WORK_GOALS if ch == "work" else L.ATT_GOALS):
        cp = L.D / f"G{g:02d}" / "counts.json"
        if not cp.exists():
            continue
        c = json.loads(cp.read_text()).get(ch, {})
        out += [(f"G{g:02d}", u) for u, v in c.items() if v.get("leaves", 0) >= L.MIN_LEAVES]
    return out
WORLDS = {"work": [("W0", 0.0), ("W1", 1.0), ("W1h", 0.5), ("W2", 0.0), ("W3", 0.0)],
          "attention": [("W0", 0.0), ("W1", 1.0), ("W1h", 0.5), ("W2", 0.0), ("W3", 0.0), ("W4", 0.0)]}
OUTD = L.D / "synthetic"


def load(per: str, unit: str, ch: str) -> pl.DataFrame:
    d = pl.read_parquet(L.D / per / f"windows_{ch}.parquet").filter(pl.col("unit") == unit)
    return d.with_columns(pl.when((pl.col("calls") == 0) & (pl.col("leave") == 1)).then(1).otherwise(pl.col("calls"))
                          .alias("calls")).filter(pl.col("calls") > 0)


def fit_syn(df: pl.DataFrame, y: np.ndarray, model: str, dwell: np.ndarray | None = None) -> dict:
    d = df.with_columns(pl.Series("leave", y.astype(np.int8)))
    if dwell is not None:
        d = d.with_columns(pl.Series("dwell", np.round(dwell).astype(np.int64)))
    ag = d.group_by("agent").agg(pl.col("leave").sum().alias("n")).filter(pl.col("n") > 0)["agent"]
    d = d.filter(pl.col("agent").is_in(ag.implode()))
    if d["leave"].sum() < 3 or d["agent"].n_unique() < 2:
        return {}
    r = L.fit(d, model)
    out = {"G": r["G"], "events": r["events"]}
    c = L.coef(r, "lnq")
    out.update({"eps": c["est"], "se": c["se"], "lo": c["lo"], "hi": c["hi"]})
    if model == "O3":
        k = L.contrast(r, "lnq", "lnlead")
        out.update({"diff": k["est"], "diff_se": k["se"], "diff_lo": k["lo"], "diff_hi": k["hi"],
                    "lead": L.coef(r, "lnlead")["est"]})
    return out


def o4_power(units: list[dict], n_rep=1000, tau=0.5, b=1.0, n_boot=200, seed=7) -> dict:
    rng = np.random.default_rng(seed)
    x = np.log(np.array([u["qbar"] for u in units]))
    lnN = np.log(np.array([u["N"] for u in units]))
    own = np.array([u["own"] for u in units], float)
    se2 = 1.0 / np.array([u["leaves"] for u in units], float)
    X = np.c_[np.ones_like(x), x, lnN, own]
    keep = [j for j in range(X.shape[1]) if j == 0 or np.ptp(X[:, j]) > 0]
    X = X[:, keep]
    w = 1.0 / (se2 + tau ** 2)
    hits, inband, ests = 0, 0, []
    n = len(x)
    for _ in range(n_rep):
        y = -7 + b * x + rng.normal(0, np.sqrt(se2 + tau ** 2))
        bh = wls(X, y, w)[1]
        bs = []
        for _ in range(n_boot):
            i = rng.integers(0, n, n)
            if np.linalg.matrix_rank(X[i]) < X.shape[1]:
                continue
            bs.append(wls(X[i], y[i], w[i])[1])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        hits += lo > 0
        inband += (0.5 <= bh <= 1.5) and lo > 0
        ests.append(bh)
    return {"power_ci_above_0": hits / n_rep, "power_P5_pass": inband / n_rep, "mean_b": float(np.mean(ests)),
            "n_units": n, "tau": tau}


def wls(X, y, w):
    Wx = X * w[:, None]
    return np.linalg.solve(X.T @ Wx, Wx.T @ y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=200)
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261007)
    rows = []
    t0 = time.time()
    for ch in ("work", "attention"):
        sk = testable_units(ch)
        data = {(per, u): load(per, u, ch) for per, u in sk}
        for wname, eps in WORLDS[ch]:
            worlds = {}
            for key, df in data.items():
                W = L.World(df, int(df["leave"].sum()), rng)
                h0, fl = W.calibrate(wname if wname != "W1h" else "W1", eps, rng, flicker_share=0.3 if wname == "W4" else 0.0)
                worlds[key] = (W, h0, fl)
            for rep in range(a.reps):
                for key, (W, h0, fl) in worlds.items():
                    wn = "W1" if wname == "W1h" else wname
                    y = W.simulate(wn, eps, h0, rng, flicker=fl)
                    r1 = fit_syn(W.df, y, "O1", W.last_dwell)
                    r3 = fit_syn(W.df, y, "O3", W.last_dwell) if wname in ("W0", "W1", "W1h", "W2") else {}
                    rows.append({"channel": ch, "world": wname, "eps_true": eps, "rep": rep, "unit": key[1],
                                 "leaves": int(y.sum()), **{k: v for k, v in r1.items()},
                                 **{("o3_" + k): v for k, v in r3.items()}})
            print(f"{ch} {wname}: {time.time() - t0:.0f}s", flush=True)
            pl.DataFrame(rows).write_parquet(OUTD / "reps.parquet")
    R = pl.DataFrame(rows)
    R.write_parquet(OUTD / "reps.parquet")
    summary = summarize(R)
    # O4 power on the real testable work units (structural counts and covariates only)
    units = []
    for per in [f"G{g:02d}" for g in L.WORK_GOALS]:
        p = L.D / per / "windows_work.parquet"
        if not p.exists():
            continue
        d = pl.read_parquet(p)
        for u, g in d.group_by("unit"):
            nl = int(g["leave"].sum())
            if nl < L.MIN_LEAVES:
                continue
            gg = g.filter(pl.col("calls") > 0)
            qbar = float((gg["q_live"] * gg["calls"]).sum() / gg["calls"].sum())
            units.append({"unit": u[0], "leaves": nl, "qbar": max(qbar, 0.05),
                          "N": float(gg["n_active"].mean()), "own": int(int(g["goal_no"][0]) in L.OWN_ROLE)})
    summary["O4_power"] = {f"tau{t}": o4_power(units, tau=t) for t in (0.25, 0.5)}
    summary["O4_units"] = units
    (OUTD / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1)[:6000])


def summarize(R: pl.DataFrame) -> dict:
    out = {}
    for ch in R["channel"].unique().to_list():
        S = {}
        for w in R.filter(pl.col("channel") == ch)["world"].unique().sort().to_list():
            x = R.filter((pl.col("channel") == ch) & (pl.col("world") == w) & pl.col("eps").is_not_null())
            eps_true = float(x["eps_true"][0]) if x.height else None
            per_unit = {}
            card = {u for _, u in CARD_SKEL[ch]}
            for u, g in x.group_by("unit"):
                if u[0] not in card:
                    continue
                per_unit[u[0]] = {"mean_eps": float(g["eps"].mean()), "bias": float(g["eps"].mean() - eps_true),
                                  "sd_eps": float(g["eps"].std()),
                                  "reject": float(((g["lo"] > 0) | (g["hi"] < 0)).mean()),
                                  "ci_above0": float((g["lo"] > 0).mean()), "n": g.height,
                                  "mean_leaves": float(g["leaves"].mean()),
                                  "cover": float(((g["lo"] <= eps_true) & (g["hi"] >= eps_true)).mean())}
                if "o3_diff" in g.columns and g["o3_diff"].drop_nulls().len():
                    gd = g.filter(pl.col("o3_diff").is_not_null())
                    per_unit[u[0]].update({"o3_diff_mean": float(gd["o3_diff"].mean()),
                                           "o3_lag_gt_lead": float((gd["o3_diff_lo"] > 0).mean())})
            S[w] = {"eps_true": eps_true, "per_unit": per_unit}
            for pool_name, sel in (("pooled_card", card), ("pooled_all", None)):
                S[w].update(pool_block(x if sel is None else x.filter(pl.col("unit").is_in(list(sel))), eps_true, pool_name))
        out[ch] = S
    return out


def pool_block(x: pl.DataFrame, eps_true: float, name: str) -> dict:
    pooled, pooled_d = [], []
    for rep, g in x.group_by("rep"):
        p = L.dl_pool(g["eps"].to_numpy(), g["se"].to_numpy())
        pooled.append((p["est"], p["lo"], p["hi"]))
        if "o3_diff" in g.columns:
            gd = g.filter(pl.col("o3_diff").is_not_null())
            if gd.height:
                q = L.dl_pool(gd["o3_diff"].to_numpy(), gd["o3_diff_se"].to_numpy())
                pooled_d.append((q["est"], q["lo"], q["hi"]))
    P = np.array([p for p in pooled if p[0] is not None], float)
    res = {name: {"mean": float(P[:, 0].mean()), "bias": float(P[:, 0].mean() - eps_true),
                  "ci_above0": float((P[:, 1] > 0).mean()), "reject": float(((P[:, 1] > 0) | (P[:, 2] < 0)).mean()),
                  "cover": float(((P[:, 1] <= eps_true) & (P[:, 2] >= eps_true)).mean()), "n_reps": len(P),
                  "n_units": int(x["unit"].n_unique())}}
    if pooled_d:
        Q = np.array([p for p in pooled_d if p[0] is not None], float)
        res[name + "_o3"] = {"mean_diff": float(Q[:, 0].mean()), "lag_gt_lead": float((Q[:, 1] > 0).mean()),
                             "n_reps": len(Q)}
    return res


if __name__ == "__main__":
    main()
