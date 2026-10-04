"""H106 CONFIRMATORY test on the locked holdout. FROZEN 2026-10-04 (round 1). DO NOT RUN without Vivian's sign-off.

Guard: runs only with H106_CONFIRM_SIGNOFF="<name> <YYYY-MM-DD>" in the environment AND the run listed in the holdout
ledger (infra/shared/holdout_ledger.py). `--dry-run` executes every code path on NON-holdout data with stand-in
"held-out" goals (N < 8: #10, #13, #17; N >= 8: #23, #26, #30) and writes only to a folder whose name contains "dry".

Frozen design (round-1 card, Amendments A1-A3 and the post hoc era result):
  panel      regime-I eligible agent-days INCLUDING the held-out goals #9, #14, #15, #22, #28, #29 (culture_vectors
             include_holdout=True, in memory only); blocks goal x ISO week; DQ5 style_resid, both models; exogenous
             directions projected; two-way FE personal vectors; 4-agent subsets (D = 200); split-half disattenuation;
             active population N_b and active-day index as scheme/build.py (held-out days included here only)
  C1 (HH)    V1 finite-size exponent alpha_k on the full panel; reported as percentiles of the drift (D) and magnet (M)
             worlds simulated on the same full panel (100 replicates each) and the likelihood ratio M/D.
             Prediction (round 1, A3): uninformative, LR M/D in [0.33, 3]. Not a test of the HH (power <= 0.09).
  C2 (era)   post hoc round-1 result to confirm: d_rho = mean rho_G over held-out periods with N_G >= 8 (#22, #28, #29)
             minus mean rho_G over held-out periods with N_G < 8 (#9, #14, #15); rho_G = mean disattenuated similarity of
             the period's blocks with any other goal's blocks within 10 active days.
             Prediction: d_rho < 0 AND below the 5th percentile of the drift world D (same panel, 100 replicates), in
             both models. Round-1 exploratory values: -0.14 (bge, D percentile 0.11), -0.28 (gte, 0.00).
Output: data/processed/H106-slow-mode-finite-size/confirm/confirm.json (or the dry-run folder)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h106lib as L  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
FROZEN = "2026-10-04"
HELD = {"I": [9, 14, 15, 22, 28, 29]}
STANDIN = {"lo": [10, 13, 17], "hi": [23, 26, 30]}
REPS = 100


def guard(dry: bool):
    if dry:
        return
    sig = os.environ.get("H106_CONFIRM_SIGNOFF", "").strip()
    if not sig:
        sys.exit("H106 confirm.py: refused. Set H106_CONFIRM_SIGNOFF='<name> <date>' after Vivian's sign-off, and list "
                 "the run in the holdout ledger.")
    sys.path.insert(0, str(ROOT / "infra/shared"))
    try:
        import holdout_ledger  # noqa: F401
    except Exception as e:  # noqa: BLE001
        sys.exit(f"H106 confirm.py: holdout ledger not importable ({e}); refused.")


def panel(model: str, dry: bool, exercise_build: bool = False):
    """Regime-I panel with N_b and a_b. dry: the non-holdout shared build; real: in-memory build with held-out rows."""
    import culture_vectors as CVM
    aday = pl.read_parquet(L.OUT / "aday.parquet")
    inc = not dry          # held-out rows only in the real run
    if dry and not exercise_build:
        ad, X, blocks = L.load(model, "style_resid", "I")
        P = L.projectors(model, "I", ad)
        return ad, X, blocks, P
    ad = CVM.eligible_agentdays(include_holdout=inc).filter(pl.col("regime") == "I")
    X = np.load(SH / "embeddings" / f"agent_day_style_resid_{CVM.MODELS[model]['suffix']}.npy").astype(np.float64)
    X = CVM.unit(X[ad["src"].to_numpy()])
    ad = ad.join(aday, on="pt_date", how="left")
    days = sorted(set(ad["pt_date"].to_list()))
    cc = set(pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list())
    act = (pl.scan_parquet(SH / "activity_bins_fixed.parquet")
           .filter(pl.col("pt_date").is_in(days) & ~pl.col("agent").is_in(list(cc)))
           .filter((pl.col("turns") + pl.col("talk") + pl.col("idle") + pl.col("consolidate") + pl.col("other_event")) > 0)
           .group_by("pt_date").agg(pl.col("agent").n_unique().alias("N_d")).collect())
    nd = dict(zip(act["pt_date"].to_list(), act["N_d"].to_list()))
    ai = dict(zip(aday["pt_date"].to_list(), aday["a"].to_list()))
    blocks = CVM.build_blocks(ad)
    bd = ad.group_by("block").agg(pl.col("pt_date").unique().alias("ds"))
    rows = [{"block": b, "N_b": float(np.mean([nd[d] for d in ds])), "a_b": float(np.mean([ai[d] for d in ds]))}
            for b, ds in zip(bd["block"].to_list(), bd["ds"].to_list())]
    blocks = blocks.join(pl.DataFrame(rows), on="block").rename({"n_agents": "n_members"}).sort("a_b")
    V, idx = CVM.directions(model, ad, include_holdout=inc)
    goals = sorted(set(ad["goal_no"].to_list()))
    abg = {g: sorted(set(ad.filter(pl.col("goal_no") == g)["agent"].to_list())) for g in goals}
    P = CVM.projectors(V, idx, "I", goals, abg)
    return ad, X, blocks, P


def stats(pan, X, rng, lo_goals, hi_goals, jack=False):
    from replication import periods_table
    A, B, R, Rh = L.residuals(pan, X)
    sel = L.draw_subsets(A, B, pan.nb, rng, 200)
    U, Uh, ok = L.culture_vectors(R, Rh, sel, pan.block_goal)
    S = L.pair_similarity(U, ok)
    _, Rsb = L.split_half(Uh, ok)
    Rhat, _ = L.smooth_reliability(Rsb, pan.block_N, pan.block_ndays, ok)
    T = L.pairs(pan, S, ok, Rhat)
    grid = L.RateGrid(pan.block_a, pan.block_N)
    f = L.fit_rate(T, grid)
    if jack and f["ok"]:
        f["jk"] = L.jackknife(T, grid, pan, f)
    per = pl.DataFrame(periods_table(pan, T, f.get("A", 0.4), "x", "I")).drop_nans("rho")
    d_rho = float(per.filter(pl.col("goal_no").is_in(hi_goals))["rho"].mean()
                  - per.filter(pl.col("goal_no").is_in(lo_goals))["rho"].mean())
    return f, d_rho


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--exercise-build", action="store_true", help="dry run through the in-memory build (no holdout)")
    a = ap.parse_args()
    guard(a.dry_run)
    out = Path(a.out) if a.out else (L.OUT / ("confirm_dryrun" if a.dry_run else "confirm"))
    if a.dry_run:
        assert "dry" in str(out), "dry-run output folder name must contain 'dry'"
    out.mkdir(parents=True, exist_ok=True)
    lo_goals, hi_goals = (STANDIN["lo"], STANDIN["hi"]) if a.dry_run else ([9, 14, 15], [22, 28, 29])
    res = {"frozen": FROZEN, "dry_run": a.dry_run, "lo_goals": lo_goals, "hi_goals": hi_goals, "results": {},
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    for model in ("bge_small", "gte_modernbert"):
        ad, X, blocks, P = panel(model, a.dry_run, a.dry_run and a.exercise_build)
        pan = L.Panel(ad, blocks, P)
        rng = np.random.default_rng(zlib.crc32(f"H106|confirm|{model}".encode()))
        f, d_rho = stats(pan, X, rng, lo_goals, hi_goals, jack=True)
        sc = L.variance_scales(pan, X); grid = L.RateGrid(pan.block_a, pan.block_N)
        dist = {}
        for w, kw in (("D", dict(share=0.5, alpha=0.0)), ("M", dict(share=0.5, alpha=-1.0))):
            dist[w] = [stats(pan, L.simulate(pan, sc, rng, grid, **kw), rng, lo_goals, hi_goals) for _ in range(a.reps)]
        al = {w: np.array([x[0].get("alpha", np.nan) for x in v]) for w, v in dist.items()}
        dr = {w: np.array([x[1] for x in v]) for w, v in dist.items()}

        def dens(x, v):
            v = v[~np.isnan(v)]; bw = 1.06 * v.std() * len(v) ** -0.2
            return float(np.mean(np.exp(-0.5 * ((x - v) / bw) ** 2)) / (bw * np.sqrt(2 * np.pi)))
        lr = dens(f["alpha"], al["M"]) / max(dens(f["alpha"], al["D"]), 1e-12)
        q05 = float(np.nanquantile(dr["D"], 0.05))
        res["results"][model] = {
            "alpha": f["alpha"], "alpha_jk": f.get("jk"), "alpha_pct_D": float(np.nanmean(al["D"] < f["alpha"])),
            "alpha_pct_M": float(np.nanmean(al["M"] < f["alpha"])), "LR_M_over_D": lr,
            "C1_uninformative_as_predicted": bool(1 / 3 <= lr <= 3),
            "d_rho": d_rho, "d_rho_D_q05": q05, "d_rho_pct_D": float(np.nanmean(dr["D"] < d_rho)),
            "C2_pass": bool(d_rho < 0 and d_rho < q05), "n_blocks": int(pan.nb)}
        print(model, json.dumps({k: v for k, v in res["results"][model].items() if k != "alpha_jk"}, default=float),
              flush=True)
    res["C2_pass_both"] = all(r["C2_pass"] for r in res["results"].values())
    (out / ("confirm_dryrun.json" if a.dry_run else "confirm.json")).write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
