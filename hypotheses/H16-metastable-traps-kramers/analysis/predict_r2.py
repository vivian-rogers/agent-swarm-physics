"""H16 round 2, R1: the aging exponent the Polya urn predicts from measured context composition. Outcome-free.

For every urn variant (U-tok primary, U-call, U-entry, U-rec), outcomes are drawn from the urn on the real skeleton and
the round-2 estimators are fitted to them:
  gate   P(sustained escape at gate) = c (1 - f_gate), c set so the mean is 0.5 (sensitivity 0.3, 0.7); agent-FE logit of
         y on ln(a_sus / 1 min) + nuisance (ln previous pause, hours into the day, swarm_act10, ln last run length).
  TS1r   per 30-s bin in the deep window (elapsed >= 10 min), cloglog h = alpha_i + ln(1 - f) with f the composition
         of the agent's next call after the bin start (the context its next decision sees); agent-FE cloglog slope on ln elapsed (the round-1 estimator).
No observed escape enters: the skeleton (which gates and bins exist, their covariates) is real, the outcomes simulated.
Output: data/processed/H16-metastable-traps-kramers/r2/urn_prediction.json
Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/predict_r2.py [--sims 100]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h16lib as L  # noqa: E402

GATE_PERIODS = [38, 51]
TS1R_PERIODS = ["G38", "G51"]
DEEP_S = 600.0


def gate_design(g: pl.DataFrame):
    """Nuisance-augmented design for the gate model; returns X (first column ln a), agent, day, keep mask."""
    la = np.log(np.maximum(g["a_sus"].to_numpy(), 10.0) / 60.0)
    pp = np.log(np.clip(g["prev_pause_s"].fill_null(300.0).to_numpy(), 10.0, 86400.0))
    hd = np.clip(g["h_day"].to_numpy(), 0, 12)
    sw = g["swarm_act10"].fill_null(0.0).to_numpy()
    lr = np.log1p(g["last_run_len"].fill_null(0).to_numpy())
    X = np.column_stack([la, pp, hd, sw, lr])
    return X


def gate_rows(goal: int) -> pl.DataFrame:
    g = pl.read_parquet(R.R2 / "gates_r2.parquet").filter((pl.col("goal_no") == goal) & pl.col("y_sus").is_not_null()
                                                          & pl.col("a_sus").is_not_null())
    return g


def ts1r_rows(period: str):
    """Deep-window TS1r bins with the composition of the agent's next call after the bin start."""
    ts = pl.read_parquet(R.OUT / "r1b" / period / "ts1r.parquet").filter(pl.col("first_act_s") >= 0)
    H = L.ts1_hazard_rows(ts, None)
    m = H["elapsed"] >= DEEP_S
    H = {k: v[m] for k, v in H.items()}
    H["day"] = np.array(ts["pt_date"].to_list())[H["spell"]]
    cc = pl.read_parquet(R.R2 / "calls_comp.parquet", columns=["agent", "t_call", *R.URNS]).with_columns(
        ts=pl.col("t_call").dt.epoch("us") / 1e6).sort("agent", "ts")
    F = {u: np.full(len(H["y"]), np.nan) for u in R.URNS}
    for (a,), grp in cc.group_by(["agent"]):
        mm = np.flatnonzero(H["agent"] == a)
        if len(mm) == 0:
            continue
        t = grp["ts"].to_numpy()
        j = np.searchsorted(t, H["t"][mm], "right")      # next call after the bin start: the context it will decide on
        ok = j < len(t)
        for u in R.URNS:
            v = grp[u].to_numpy().astype(float)
            F[u][mm[ok]] = v[j[ok]]
    H.update(F)
    return H


def main():
    sims = int(sys.argv[sys.argv.index("--sims") + 1]) if "--sims" in sys.argv else 100
    rng = np.random.default_rng(R.SEED)
    t0 = time.time()
    out = {"gate": {}, "ts1r": {}, "sims": sims}
    for goal in GATE_PERIODS:
        g = gate_rows(goal)
        X = gate_design(g)
        ag = g["agent"].to_numpy()
        res = {"n_gates": g.height}
        for u in R.URNS:
            f = g[u].to_numpy().astype(float)
            ok = np.isfinite(f)
            res[u] = {"f_median": float(np.nanmedian(f)), "n": int(ok.sum())}
            for lev in (0.5, 0.3, 0.7):
                p = R.urn_prob(f[ok], ag[ok], lev)
                bs = []
                for _ in range(sims if lev == 0.5 else max(sims // 4, 20)):
                    y = R.simulate_gate(rng, p)
                    fit = L.glm_fe(y, X[ok], ag[ok], "logit")
                    bs.append(fit["beta"][0])
                bs = np.array(bs, float)
                res[u][f"level_{lev}"] = {"beta_pred": float(np.nanmean(bs)), "band": R.pct_ci(bs)}
            print(f"[{time.time() - t0:5.0f}s] gate G{goal} {u}", res[u]["level_0.5"], flush=True)
        out["gate"][f"G{goal}"] = res
    for per in TS1R_PERIODS:
        H = ts1r_rows(per)
        res = {"n_rows": int(len(H["y"])), "n_spells": int(len(np.unique(H["spell"])))}
        for u in R.URNS:
            f = H[u]
            ok = np.isfinite(f)
            bs = []
            for _ in range(sims):
                y = R.simulate_bins(rng, f[ok], H["agent"][ok])
                fit = L.glm_fe(y, np.log(H["elapsed"][ok] / 60.0)[:, None], H["agent"][ok], "cloglog")
                bs.append(fit["beta"][0])
            bs = np.array(bs, float)
            # analytic projection: within-agent slope of ln(1 - f) on ln elapsed
            x = np.log(H["elapsed"][ok] / 60.0); z = R.lnq(f[ok]); a = H["agent"][ok]
            xd = x - pl.DataFrame({"a": a, "x": x}).with_columns(pl.col("x").mean().over("a"))["x"].to_numpy()
            zd = z - pl.DataFrame({"a": a, "z": z}).with_columns(pl.col("z").mean().over("a"))["z"].to_numpy()
            res[u] = {"beta_pred": float(np.nanmean(bs)), "band": R.pct_ci(bs), "projection": float(np.sum(xd * zd) / np.sum(xd * xd)),
                      "f_median": float(np.nanmedian(f)), "n": int(ok.sum())}
            print(f"[{time.time() - t0:5.0f}s] ts1r {per} {u}", res[u], flush=True)
        out["ts1r"][per] = res
    R.jdump(out, R.R2 / "urn_prediction.json")


if __name__ == "__main__":
    main()
