"""H71 post hoc (labelled; written 2026-10-04 after the round-1 run showed phi+ >> b(1+c) and AR(2) > 0).

Two-timescale model: x+_n = m_n + e_n, with a slowly drifting set point m_n (AR(1), persistence rho_s) and a fast,
deadbeat compression noise e_n (white). Signatures: rho_k = r rho_s^k, so rho_2 / rho_1 = rho_s > rho_1 (a single
first-order loop has rho_2 = rho_1^2). Tests:
  T1 rho_2 - rho_1^2 > 0 per period (agent bootstrap);
  T2 out of sample: exponential smoothing (local level, the optimal predictor for drift + noise) vs AR(1) vs RW;
  T3 the mixed-phase phi (H09's statistic) reproduced by a two-timescale sawtooth with fitted r, rho_s, growth.
Writes results/posthoc.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h71lib as L  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H71-memory-homeostat"
RNG = np.random.default_rng(7171)


def acf_suff(cp: pl.DataFrame, kmax: int = 3) -> np.ndarray:
    """Per agent: sums of d_n d_{n-k} (k = 0..kmax) of the agent-demeaned x+ series inside the period."""
    rows = []
    for _, g in cp.sort("agent", "t").group_by("agent", maintain_order=True):
        x = g["xplus"].to_numpy()
        if len(x) < kmax + 10:
            continue
        d = x - x.mean()
        rows.append([np.sum(d[k:] * d[:len(d) - k]) / (len(d) - k) * len(d) for k in range(kmax + 1)])
    return np.array(rows)


def acf_from(S: np.ndarray) -> np.ndarray:
    s = S.sum(0)
    return s[1:] / s[0]


def ewma_oos(cp: pl.DataFrame, frac: float = 0.7) -> pl.DataFrame:
    rows = []
    alphas = np.linspace(0.05, 1.0, 20)
    for (a,), g in cp.sort("t").group_by(["agent"], maintain_order=True):
        x = g["xplus"].to_numpy()
        n = len(x)
        if n < 20:
            continue
        k = int(frac * n)

        def run(al, upto):
            lvl = x[0]
            preds = []
            for i in range(1, upto):
                preds.append(lvl)
                lvl = al * x[i] + (1 - al) * lvl
            return np.array(preds), lvl

        best = min(alphas, key=lambda al: np.mean((x[1:k] - run(al, k)[0]) ** 2))
        preds, _ = run(best, n)
        te = x[k:]
        e_ew = te - preds[k - 1:]
        tr = x[:k]
        mu = tr.mean()
        d = tr - mu
        phi = np.sum(d[1:] * d[:-1]) / np.sum(d[:-1] ** 2)
        e_ar = te - (mu + phi * (x[k - 1:n - 1] - mu))
        e_rw = te - x[k - 1:n - 1]
        rows.append({"agent": int(a), "alpha": float(best), "mse_ewma": float(np.mean(e_ew ** 2)),
                     "mse_ar1": float(np.mean(e_ar ** 2)), "mse_rw": float(np.mean(e_rw ** 2))})
    return pl.DataFrame(rows)


def sim_two_timescale(skel: pl.DataFrame, r: float, rho_s: float, var_x: float, d: float, s_grow: float,
                      rng) -> pl.DataFrame:
    snaps = []
    for (a,), g in skel.sort("t").group_by(["agent"], maintain_order=True):
        sm = np.sqrt(max(r, 1e-3) * var_x * (1 - rho_s ** 2))
        se = np.sqrt(max(1 - r, 1e-3) * var_x)
        m = 0.0
        for j, (t, k) in enumerate(zip(g["t"].to_list(), g["n_app"].to_list())):
            m = rho_s * m + rng.normal(0, sm)
            x = m + rng.normal(0, se)
            if j > 0 and k > 0:
                y = prev + d + rng.normal(0, s_grow)
                for i in range(k):
                    snaps.append({"agent": int(a), "t": t - np.timedelta64(60 * (k - i), "s"), "period": "s",
                                  "phase": "append", "lx": prev + (y - prev) * (i + 1) / k})
            snaps.append({"agent": int(a), "t": t, "period": "s", "phase": "compress", "lx": x})
            prev = x
    return pl.DataFrame(snaps).sort("agent", "t")


def main():
    cyc = pl.read_parquet(DATA / "cycles.parquet")
    snaps = pl.read_parquet(DATA / "snapshots.parquet")
    per_res = json.loads((DATA / "results/periods.json").read_text())
    out = {}
    for per, pr in per_res.items():
        keep = [a["agent"] for a in pr["agents"]]
        cp = cyc.filter((pl.col("period") == per) & pl.col("agent").is_in(keep))
        S = acf_suff(cp)
        if len(S) < 3:
            continue
        rho = acf_from(S)
        bs = np.array([acf_from(S[i]) for i in RNG.integers(0, len(S), size=(1000, len(S)))])
        dev = bs[:, 1] - bs[:, 0] ** 2
        rho_s = rho[1] / rho[0] if rho[0] > 0 else np.nan
        r = rho[0] ** 2 / rho[1] if rho[1] > 0 else np.nan
        ew = ewma_oos(cp)
        res = {"rho1": float(rho[0]), "rho2": float(rho[1]), "rho3": float(rho[2]),
               "rho2_minus_rho1sq": float(rho[1] - rho[0] ** 2),
               "rho2_minus_rho1sq_ci": [float(np.percentile(dev, 2.5)), float(np.percentile(dev, 97.5))],
               "rho_s": float(rho_s), "r_slow": float(r), "rho3_over_rho2": float(rho[2] / rho[1]) if rho[1] > 0 else None,
               "oos_ewma_beats_ar1": float((ew["mse_ewma"] < ew["mse_ar1"]).mean()) if ew.height else None,
               "oos_ewma_beats_rw": float((ew["mse_ewma"] < ew["mse_rw"]).mean()) if ew.height else None,
               "oos_ar1_beats_rw": float((ew["mse_ar1"] < ew["mse_rw"]).mean()) if ew.height else None,
               "mse_ratio_ewma_ar1_median": float((ew["mse_ewma"] / ew["mse_ar1"]).median()) if ew.height else None,
               "alpha_median": float(ew["alpha"].median()) if ew.height else None, "n_agents": int(ew.height)}
        if pr["regime"] == "III" and np.isfinite(rho_s) and 0 < rho_s < 1 and 0 < r <= 1:
            var_x = float(np.mean([np.var(g["xplus"].to_numpy()) for _, g in cp.group_by("agent")]))
            q = L.pairs(cp).with_columns((pl.col("y1") - pl.col("x0")).alias("g"))
            d, sg = float(q["g"].mean()), float(q["g"].std())
            skel = cp.select("agent", "t", "n_app")
            sims = [L.mixed_phi(sim_two_timescale(skel, r, rho_s, var_x, d, sg, np.random.default_rng(900 + k)))
                    for k in range(4 if cp.height > 5000 else 10)]
            res["mixed_observed"] = pr["mixed_phi"]
            res["mixed_two_timescale"] = float(np.mean(sims))
            res["mixed_single_loop"] = pr["synth_mixed"]["mean"]
        out[per] = res
        print(per, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()}, flush=True)
    (DATA / "results/posthoc.json").write_text(json.dumps(out, indent=1))
    P = list(out.values())
    pos = sum(p["rho2_minus_rho1sq_ci"][0] > 0 for p in P)
    print("T1 rho2 > rho1^2 (CI):", pos, "/", len(P))
    r3 = [p for p in P if "mixed_two_timescale" in p]
    print("T3 two-timescale within 0.15:", sum(abs(p["mixed_observed"] - p["mixed_two_timescale"]) <= 0.15 for p in r3),
          "/", len(r3))


if __name__ == "__main__":
    main()
