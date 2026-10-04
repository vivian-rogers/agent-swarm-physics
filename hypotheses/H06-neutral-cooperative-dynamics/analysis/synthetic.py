"""H06 synthetic validation (axis F): can the full pipeline tell neutral cooperative dynamics (NCD) from Hubbell
neutral drift and from a herding (conformist) rival at village sampling, and does mu come back?

For each configuration (N agent slots, D days x W windows, label-observation probability p_obs, true mu, k):
  1. draw a random iid observation mask (the village's missing labels);
  2. simulate R_TEST datasets from each true model;
  3. for every dataset, fit (mu, k) under each candidate model from the two fitted moments (change rate c,
     novelty fraction f_nov), simulate that model's predictive distribution of the unfitted statistics at the
     fitted point (cached on a fine grid), and compute the Gaussian synthetic log-likelihood of the dataset's
     statistics under each model;
  4. classify by the largest synthetic likelihood; report confusion matrices, LLR(NCD - Hubbell) power, the
     per-statistic power, and mu recovery.

Outputs: data/processed/H06-neutral-cooperative-dynamics/synthetic/validation.json (+ per-dataset parquet).
Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/synthetic.py [--quick]
Runs with at most 2 worker processes.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import get_context
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("POLARS_MAX_THREADS", "1")

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncd_core as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H06-neutral-cooperative-dynamics/synthetic"

def configs(quick=False):
    out = []
    for mu in (0.01, 0.05, 0.2):
        out.append(dict(name=f"N7_D5W6_p85_mu{mu}", N=7, D=5, W=6, p=0.85, mu=mu, k=1.0))      # #11, #16 (intent)
        out.append(dict(name=f"N13_D5W8_p85_mu{mu}", N=13, D=5, W=8, p=0.85, mu=mu, k=1.0))    # #31 (intent)
        out.append(dict(name=f"N13_D5W8_p50_mu{mu}", N=13, D=5, W=8, p=0.50, mu=mu, k=1.0))    # #31 (artifact)
        out.append(dict(name=f"N12_D3W8_p85_mu{mu}", N=12, D=3, W=8, p=0.85, mu=mu, k=1.0))    # #37, #44 #rest
    if quick:
        out = [c for c in out if c["mu"] in (0.01, 0.05) and c["N"] in (7, 13) and c["p"] == 0.85]
    return out


PRED_R = 200


def run_config(cfg, r_test=60, seed=7):
    """Profile synthetic-likelihood pipeline (amendment 1): each candidate model is fitted to all 9 statistics
    over its (mu, k) grid; the model comparison uses fresh simulations at each model's best cell."""
    t0 = time.time()
    rng = np.random.default_rng(M._seed(seed, cfg["name"]))
    day = np.repeat(np.arange(cfg["D"]), cfg["W"])
    mask = rng.random((len(day), cfg["N"])) < cfg["p"]
    bank = M.Bank(mask, day, seed=M._seed(seed, cfg["name"], "bank"))
    for m in M.MODELS:
        bank.full_grid(m)
    cache = {}

    def fresh(model, ij):
        key = (model, ij)
        if key not in cache:
            F, H, cf, _ = bank.fresh(model, M.PMU_GRID[ij[0]], M.PK_GRID[ij[1]], R=PRED_R, tag=M._seed(*ij))
            cache[key] = F
        return cache[key]

    rows = []
    for truth in M.MODELS:
        s0, n0 = M.burn(truth, cfg["N"], cfg["mu"], r_test, seed=M._seed(seed, cfg["name"], truth, "test"))
        snaps = M.observe(truth, s0, n0, cfg["mu"], cfg["k"], day, seed=M._seed(seed, cfg["name"], truth, "obs"))
        labs = M.mask_snaps(snaps, mask)
        Ft, _, cft = M.full_stats(labs, day, bank.m_core)
        for r in range(r_test):
            row = dict(config=cfg["name"], truth=truth, rep=r)
            row.update({f"obs_{k}": float(Ft[r, i]) for i, k in enumerate(M.FIT_NAMES)})
            for m in M.MODELS:
                mu_h, k_h, L, ij = bank.profile(m, Ft[r])
                Fp = fresh(m, ij)
                ll, cols = M.synth_loglik(Ft[r], Fp)
                row[f"mu_{m}"], row[f"k_{m}"], row[f"ll_{m}"], row[f"llgrid_{m}"] = mu_h, k_h, ll, float(np.nanmax(L))
                row[f"ppcj_{m}"] = M.joint_ppc(Ft[r], Fp)
                for i, k in enumerate(M.FIT_NAMES):
                    x = Fp[:, i]
                    x = x[np.isfinite(x)]
                    if np.isfinite(Ft[r, i]) and len(x) > 10 and x.std() > 0:
                        row[f"ll1_{m}_{k}"] = float(-0.5 * ((Ft[r, i] - x.mean()) / x.std()) ** 2 - np.log(x.std()))
                    row[f"ppc_{m}_{k}"] = M.ppc_p(Ft[r, i], Fp[:, i])
            rows.append(row)
    print(f"{cfg['name']}: {time.time() - t0:.0f}s, {len(cache)} fresh cells", flush=True)
    return rows


def summarize(rows, cfgs):
    import polars as pl
    df = pl.DataFrame(rows, infer_schema_length=None)
    out = {}
    for cfg in cfgs:
        d = df.filter(pl.col("config") == cfg["name"])
        res = {"config": cfg, "lambda_star_theory": M.lambda_star(cfg["mu"], cfg["N"]), "mu_B": M.mu_B(cfg["N"]),
               "mu_L": M.mu_L(cfg["N"])}
        conf = {}
        for truth in M.MODELS:
            x = d.filter(pl.col("truth") == truth)
            ll = np.stack([x[f"ll_{m}"].to_numpy() for m in M.MODELS], 1)
            ok = np.isfinite(ll).all(1)
            pick = np.argmax(np.where(np.isfinite(ll), ll, -np.inf), 1)
            conf[truth] = {m: float(np.mean(pick[ok] == j)) for j, m in enumerate(M.MODELS)}
            llr = (x["ll_ncd"] - x["ll_hubbell"]).to_numpy()
            res[f"truth_{truth}"] = {
                "n": int(ok.sum()),
                "obs_c": float(np.nanmedian(x["obs_c"].to_numpy())), "obs_f_nov": float(np.nanmedian(x["obs_f"].to_numpy())),
                "obs_lam_median": float(np.nanmedian(x["obs_lam"].to_numpy())),
                "obs_beta_median": float(np.nanmedian(x["obs_beta"].to_numpy())),
                "llr_ncd_hub_median": float(np.nanmedian(llr)),
                "p_llr_gt0": float(np.nanmean(llr > 0)), "p_llr_gt2": float(np.nanmean(llr > 2)),
                "p_llr_lt_m2": float(np.nanmean(llr < -2)),
                "mu_hat_ncd_median": float(np.nanmedian(x["mu_ncd"].to_numpy())),
                "mu_hat_ncd_iqr": [float(np.nanpercentile(x["mu_ncd"].to_numpy(), 25)), float(np.nanpercentile(x["mu_ncd"].to_numpy(), 75))],
                "mu_hat_hub_median": float(np.nanmedian(x["mu_hubbell"].to_numpy())),
                "ppc_ncd_lam_lt05": float(np.nanmean(x["ppc_ncd_lam"].to_numpy() < 0.05)),
                "ppc_hub_lam_lt05": float(np.nanmean(x["ppc_hubbell_lam"].to_numpy() < 0.05)),
                "ncd_adequate": float(np.nanmean(np.stack([x[f"ppc_ncd_{k}"].to_numpy() for k in M.FIT_NAMES], 1).min(1) >= 0.05 / 9)),
                "p_llr_nc_gt2": float(np.nanmean((x["ll_ncd"] - x["ll_conformist"]).to_numpy() > 2)),
                "p_llr_nc_lt_m2": float(np.nanmean((x["ll_ncd"] - x["ll_conformist"]).to_numpy() < -2)),
                "p1_supported": float(np.nanmean(((x["ll_ncd"] - x["ll_hubbell"]).to_numpy() >= 2) & ((x["ll_ncd"] - x["ll_conformist"]).to_numpy() >= 2))),
                "p1_failed": float(np.nanmean(((x["ll_ncd"] - x["ll_hubbell"]).to_numpy() <= -2) | ((x["ll_ncd"] - x["ll_conformist"]).to_numpy() <= -2))),
            }
            # per-statistic power: fraction where the single statistic favours the true model over the other
            per = {}
            for k in M.FIT_NAMES:
                a, b = f"ll1_ncd_{k}", f"ll1_hubbell_{k}"
                if a in x.columns and b in x.columns:
                    v = (x[a] - x[b]).to_numpy()
                    v = v[np.isfinite(v)]
                    if len(v):
                        per[k] = float(np.mean(v > 0)) if truth == "ncd" else float(np.mean(v < 0))
            res[f"truth_{truth}"]["per_stat_correct_vs_other"] = per
        res["confusion"] = conf
        out[cfg["name"]] = res
    return df, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    cfgs = configs(a.quick)
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(min(2, a.workers)) as pool:
        parts = pool.map(run_config, cfgs, chunksize=1)
    rows = [r for p in parts for r in p]
    df, summ = summarize(rows, cfgs)
    df.write_parquet(OUT / ("validation_quick.parquet" if a.quick else "validation_profile.parquet"), compression="zstd")
    (OUT / ("validation_quick.json" if a.quick else "validation_profile.json")).write_text(json.dumps(summ, indent=1))
    for name, r in summ.items():
        print(name, "confusion", {t: {m: round(v, 2) for m, v in c.items()} for t, c in r["confusion"].items()})
        for t in M.MODELS:
            x = r[f"truth_{t}"]
            print(f"   truth={t}: c={x['obs_c']:.2f} f={x['obs_f_nov']:.2f} lam={x['obs_lam_median']:.2f} beta={x['obs_beta_median']:.2f} "
                  f"LLR>2 {x['p_llr_gt2']:.2f} LLR<-2 {x['p_llr_lt_m2']:.2f} NC>2 {x['p_llr_nc_gt2']:.2f} NC<-2 {x['p_llr_nc_lt_m2']:.2f} "
                  f"P1sup {x['p1_supported']:.2f} P1fail {x['p1_failed']:.2f} adeq {x['ncd_adequate']:.2f} mu_ncd {x['mu_hat_ncd_median']:.3f}")
    print(f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
