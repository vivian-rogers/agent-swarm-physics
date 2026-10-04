"""H106 synthetic validation on the real panel (regime I, both models; regime III D/M descriptive): size, power and
bias of the finite-size exponent alpha_k (V1 primary; V2-V5 point estimates) and of the NE27 two-rate contrast.
Runs the full pipeline on planted data; scales come from the real projected vectors (sampling facts, as H81).
No real-data test statistic is computed here.

Worlds: S0 (no slow mode), D (drift, alpha 0, share 0.5), M (magnet, alpha -1), H (alpha -0.5), DR3 (D + individual
drift 0.25), DR5 (D + noise SD x (N/6)^0.45), D25 / M25 (share 0.25).
Output: data/processed/H106-slow-mode-finite-size/synthetic/{replicates.parquet, synthetic.json}
Usage: uv run python hypotheses/H106-slow-mode-finite-size/analysis/synthetic.py [--reps 300] [--workers 2]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h106lib as L  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]
WORLDS = {"S0": dict(share=0.0), "D": dict(share=0.5, alpha=0.0), "M": dict(share=0.5, alpha=-1.0),
          "H": dict(share=0.5, alpha=-0.5), "DR3": dict(share=0.5, alpha=0.0, drift=0.25),
          "DR5": dict(share=0.5, alpha=0.0, depth=0.45), "D25": dict(share=0.25, alpha=0.0),
          "M25": dict(share=0.25, alpha=-1.0)}
MAIN = {"D", "M"}


def a_of(date: str) -> float:
    ad = pl.read_parquet(L.OUT / "aday.parquet")
    return float(ad.filter(pl.col("pt_date") >= date)["a"].min())


def ne27_spec(pan):
    tb = a_of(L.NE27)
    restr = np.isin(pan.block_goal, list(range(2, 9)) + list(range(10, 19)))
    # placebo breaks inside the N >= 6 era, windows of the same pre/post lengths (clipped to a >= 105)
    pre_len = tb - pan.block_a[restr].min(); post_len = pan.block_a[restr].max() - tb
    a6 = pan.block_a[pan.block_N >= 5.5].min()
    plac = []
    for date in ("2025-11-03", "2025-12-15"):
        t = a_of(date)
        r = (pan.block_a >= max(t - pre_len, a6)) & (pan.block_a <= t + post_len)
        plac.append((date, (t, r)))
    return (tb, restr), plac


def seg_bounds():
    return (a_of(L.NE04), a_of(L.NE08))


def run_world(args):
    model, regime, world, reps = args
    ad, X, blocks = L.load(model, "style_resid", regime)
    P = L.projectors(model, regime, ad)
    pan = L.Panel(ad, blocks, P)
    sc = L.variance_scales(pan, X)
    grid = L.RateGrid(pan.block_a, pan.block_N)
    rng = np.random.default_rng(zlib.crc32(f"{model}|{regime}|{world}".encode()))
    ne27, plac = ne27_spec(pan) if regime == "I" else (None, ())
    sb = seg_bounds() if regime == "I" else None
    variants = ("V1", "V2", "V3", "V4", "V5") if regime == "I" else ("V1",)
    rows = []
    t0 = time.time()
    for r in range(reps):
        Xs = L.simulate(pan, sc, rng, grid, **WORLDS[world])
        out = L.pipeline(pan, Xs, rng, variants=variants, grid=grid, seg_bounds=sb, restrict_ne27=ne27,
                         placebo_breaks=plac)
        v1 = out["V1"]
        row = {"model": model, "regime": regime, "world": world, "rep": r,
               "alpha": v1.get("alpha", np.nan), "k6": v1.get("k6", np.nan), "A": v1.get("A", np.nan),
               "s_inf": v1.get("s_inf", np.nan),
               "lo": v1.get("jk", {}).get("lo", np.nan), "hi": v1.get("jk", {}).get("hi", np.nan),
               "se": v1.get("jk", {}).get("se", np.nan), "rel_beta_lnN": out["reliability"]["beta_lnN"],
               "mean_rel": out["reliability"]["mean_rel"]}
        for v in variants[1:]:
            row[f"alpha_{v}"] = out[v].get("alpha", np.nan) if v in out else np.nan
        if ne27:
            n = out["NE27"]
            row.update({"ne27_dlnk": n.get("dlnk", np.nan), "ne27_lo": n.get("jk", {}).get("lo", np.nan),
                        "ne27_hi": n.get("jk", {}).get("hi", np.nan), "ne27_pred": n.get("magnet_pred", np.nan)})
            for nm, f in out["NE27_placebo"].items():
                row[f"plac_{nm}"] = f.get("dlnk", np.nan)
        rows.append(row)
    print(model, regime, world, reps, f"{time.time() - t0:.0f}s", flush=True)
    return rows


def summarize(df: pl.DataFrame) -> dict:
    res = {}
    for (model, regime), sub in df.group_by(["model", "regime"], maintain_order=True):
        r = {}
        for world, w in sub.group_by("world", maintain_order=True):
            world = world[0]
            a = w["alpha"].to_numpy(); lo = w["lo"].to_numpy(); hi = w["hi"].to_numpy()
            ok = ~np.isnan(a) & ~np.isnan(lo)
            excl0 = (hi < 0) | (lo > 0)
            pass_ = (hi < 0) & (lo <= -1) & (hi >= -1)
            kill = (lo <= 0) & (hi >= 0) & (lo > -0.5)
            truth = WORLDS[world].get("alpha", np.nan) if WORLDS[world]["share"] > 0 else np.nan
            cover = (lo <= truth) & (hi >= truth) if truth == truth else np.full(len(a), np.nan)
            d = {"n": int(ok.sum()), "alpha_median": float(np.nanmedian(a)), "alpha_mean": float(np.nanmean(a)),
                 "alpha_sd": float(np.nanstd(a)), "alpha_iqr": [float(np.nanquantile(a, 0.25)), float(np.nanquantile(a, 0.75))],
                 "se_median": float(np.nanmedian(w["se"].to_numpy())),
                 "frac_excl0": float(np.mean(excl0[ok])), "frac_excl0_neg": float(np.mean((hi < 0)[ok])),
                 "frac_excl0_pos": float(np.mean((lo > 0)[ok])),
                 "frac_pass_P1": float(np.mean(pass_[ok])), "frac_kill": float(np.mean(kill[ok])),
                 "coverage": float(np.nanmean(cover[ok])) if truth == truth else None,
                 "frac_alpha_lt_m05": float(np.mean(a[ok] < -0.5)),
                 "rel_beta_lnN_median": float(np.nanmedian(w["rel_beta_lnN"].to_numpy())),
                 "mean_rel_median": float(np.nanmedian(w["mean_rel"].to_numpy()))}
            for v in ("V2", "V3", "V4", "V5"):
                if f"alpha_{v}" in w.columns:
                    x = w[f"alpha_{v}"].to_numpy()
                    d[f"alpha_{v}_median"] = float(np.nanmedian(x)); d[f"alpha_{v}_sd"] = float(np.nanstd(x))
            if "ne27_dlnk" in w.columns:
                x = w["ne27_dlnk"].to_numpy()
                d["ne27"] = {"median": float(np.nanmedian(x)), "sd": float(np.nanstd(x)),
                             "q05": float(np.nanquantile(x, 0.05)), "q95": float(np.nanquantile(x, 0.95)),
                             "pred_magnet": float(np.nanmedian(w["ne27_pred"].to_numpy())),
                             "frac_ci_below0": float(np.nanmean(w["ne27_hi"].to_numpy() < 0))}
            r[world] = d
        # power of the NE27 contrast against the D-world 5th percentile
        if "D" in r and "ne27" in r["D"]:
            q05 = r["D"]["ne27"]["q05"]
            for world in r:
                x = sub.filter(pl.col("world") == world)["ne27_dlnk"].to_numpy()
                r[world]["ne27"]["frac_below_Dq05"] = float(np.nanmean(x < q05))
            # power of alpha against the D-world 5th percentile (one-sided synthetic-calibrated test)
            qa = float(np.nanquantile(sub.filter(pl.col("world") == "D")["alpha"].to_numpy(), 0.05))
            for world in r:
                x = sub.filter(pl.col("world") == world)["alpha"].to_numpy()
                r[world]["frac_alpha_below_Dq05"] = float(np.nanmean(x < qa))
            r["D_alpha_q05"] = qa
        res[f"{model}/{regime}"] = r
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=300); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--regime3", type=int, default=100)
    a = ap.parse_args()
    out = L.OUT / "synthetic"; out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for m in MODELS:
        for w in WORLDS:
            jobs.append((m, "I", w, a.reps if w in MAIN else max(a.reps * 2 // 3, 50)))
        for w in ("D", "M"):
            jobs.append((m, "III", w, a.regime3))
    rows = []
    with ProcessPoolExecutor(max_workers=min(a.workers, 2)) as ex:
        for rr in ex.map(run_world, jobs):
            rows.extend(rr)
    df = pl.DataFrame(rows)
    df.write_parquet(out / "replicates.parquet")
    res = summarize(df)
    (out / "synthetic.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
