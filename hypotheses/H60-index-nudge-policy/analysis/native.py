"""H60 natives (predictions dated 2026-10-04 in the card, before running).

N1 NE43: the outcome model fitted on G51 08-07..08-20 (nudger on) predicts untreated active calls on 08-21..09-02
         (nudger off). Calibration (observed / predicted) in targeted states (k >= 4) vs the rest; and the share of the
         window's active calls bought by the logged nudges.
N2 NE44: the nudge x ln k slope on active calls in the long-pause regime-III periods (G37-G44 pooled, agent-within-
         period fixed effects; exception (c)) vs G51.
Usage: uv run python hypotheses/H60-index-nudge-policy/analysis/native.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h60lib as L  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
B = 200


def ci(x):
    x = np.asarray(x)
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def mu0(P, model, idx):
    X, nm = L._X(P, idx, model["with_r"], model["centers"], M_override=np.zeros(P["n"]))
    col = {n: i for i, n in enumerate(model["names"])}
    b = np.array([model["beta"][col[n]] if n in col else 0.0 for n in nm])
    return X @ b


def n1(g):
    d = g.filter(pl.col("goal_no") == 51)
    Bw = d.filter(pl.col("pt_date").is_between(pl.lit("2026-08-07"), pl.lit("2026-08-20")))
    Cw = d.filter(pl.col("pt_date").is_between(pl.lit("2026-08-21"), pl.lit("2026-09-02")))
    both_agents = set(Bw["agent"].unique().to_list()) & set(Cw["agent"].unique().to_list())
    BC = pl.concat([Bw, Cw]).filter(pl.col("agent").is_in(list(both_agents)))
    P = L.prep(BC, "calls30")
    isC = P["days"] >= "2026-08-21"
    rowsB, rowsC = np.flatnonzero(~isC), np.flatnonzero(isC)
    tgt = P["k"] >= 4

    def calib(rB, rC):
        m = L.fit(P, rB, True)
        pred = mu0(P, m, rC)
        obs = P["y"][rC]
        t = tgt[rC]
        r_t = obs[t].sum() / pred[t].sum()
        r_o = obs[~t].sum() / pred[~t].sum()
        g = L.g_hat(P, m, rB)
        return r_t, r_o, float(g[P["M"][rB] > 0].sum()), m
    r_t, r_o, gsum, m = calib(rowsB, rowsC)
    rng = np.random.default_rng(43)
    dB = L.HF.rows_per_day(P["day"][rowsB])
    dC = L.HF.rows_per_day(P["day"][rowsC])
    D = []
    for _ in range(B):
        sB = rowsB[np.concatenate([dB[i] for i in rng.integers(0, len(dB), len(dB))])]
        sC = rowsC[np.concatenate([dC[i] for i in rng.integers(0, len(dC), len(dC))])]
        try:
            a, b_, gs, _ = calib(np.sort(sB), np.sort(sC))
            D.append([a, b_, a / b_, gs])
        except Exception:
            continue
    D = np.array(D)
    # active calls in the B window (all non-summary active calls of G51 agents)
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("goal_no") == 51) & ~pl.col("holdout") & (pl.col("ctx_mode") != "summary")
                  & pl.col("pt_date").is_between(pl.lit("2026-08-07"), pl.lit("2026-08-20")))
          .filter(~(pl.col("kind").cast(pl.Utf8).is_in(["pause", "wait"]) & ~pl.col("talk")))
          .select(pl.len()).collect().item())
    out = {"agents": len(both_agents), "gates_B": int(len(rowsB)), "gates_C": int(len(rowsC)),
           "nudged_B": int(P["M"][rowsB].sum()), "nudged_C": int(P["M"][rowsC].sum()),
           "calib_targeted": {"est": float(r_t), "ci": ci(D[:, 0])},
           "calib_other": {"est": float(r_o), "ci": ci(D[:, 1])},
           "calib_ratio_targeted_over_other": {"est": float(r_t / r_o), "ci": ci(D[:, 2])},
           "calls_bought_B": {"est": gsum, "ci": ci(D[:, 3])}, "active_calls_B": int(cw),
           "share_bought_B": gsum / cw, "share_bought_ci": [x / cw for x in ci(D[:, 3])]}
    out["pass_a"] = bool(abs(out["calib_ratio_targeted_over_other"]["est"] - 1) < 0.15)
    out["pass_b"] = bool(out["share_bought_B"] <= 0.01)
    return out


def n2(g):
    pre = g.filter(pl.col("goal_no").is_in([37, 38, 39, 40, 41, 42, 44]))
    P = L.prep(pre, "calls30")
    # agent-within-period fixed effects: recode agent as (period, agent)
    gn = pre.filter(pl.col("y_calls30").is_not_null() & pl.col("a_sus").is_not_null()).sort("agent", "t_call")["goal_no"].to_numpy()
    P["agent"] = (gn.astype(int) * 100 + P["agent"].astype(int))
    rows = np.arange(P["n"])
    m = L.fit(P, rows, True)
    th = L.theta(m)
    rng = np.random.default_rng(44)
    rpd = L.HF.rows_per_day(P["day"])
    D = []
    for _ in range(B):
        idx = L.HF.block_resample(P["day"], rng, rpd)
        Q = L.take(P, idx)
        try:
            mm = L.fit(Q, np.arange(Q["n"]), True, centers=m["centers"])
            D.append([L.theta(mm)[k] for k in ("M", "M_la", "M_lk", "M_lr")])
        except Exception:
            continue
    D = np.array(D)
    pre_res = {"gates": P["n"], "nudged": int(P["M"].sum()), "theta": th,
               "theta_ci": {k: ci(D[:, i]) for i, k in enumerate(("M", "M_la", "M_lk", "M_lr"))}}
    g51 = json.loads((L.OUT / "G51/results.json").read_text())["calls30"]["het"]
    out = {"pre_06_11": pre_res, "G51": {"theta": g51["theta"], "theta_ci": g51["theta_ci"]}}
    out["pass"] = bool(pre_res["theta"]["M_lk"] >= 0 and g51["theta"]["M_lk"] < 0 and g51["theta_ci"]["M_lk"][1] < 0)
    return out


def main():
    g = pl.read_parquet(L.OUT / "gates.parquet")
    res = {"N1_NE43": n1(g)}
    print("N1", json.dumps(res["N1_NE43"], default=float), flush=True)
    res["N2_NE44"] = n2(g)
    print("N2", json.dumps(res["N2_NE44"], default=float), flush=True)
    (L.OUT / "native").mkdir(parents=True, exist_ok=True)
    (L.OUT / "native/native.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
