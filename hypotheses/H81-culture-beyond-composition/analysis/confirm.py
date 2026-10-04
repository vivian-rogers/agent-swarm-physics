"""H81 CONFIRMATORY test on the locked holdout. FROZEN 2026-10-04 (round 1). DO NOT RUN without Vivian's sign-off.

Guard: runs only with H81_CONFIRM_SIGNOFF="<name> <YYYY-MM-DD>" in the environment AND the run listed in the holdout
ledger (infra/shared/holdout_ledger.py). `--dry-run` executes every code path on NON-holdout data with stand-in
"held-out" goals (regime I: 16, 23, 30; regime III: 39, 44) and writes nothing outside the scratch folder given.

Frozen design (from the round-1 card, Amendments A1-A4):
  panel        every eligible agent-day of regime I and III (n_stat >= 5; agents 19, 28, 30 excluded), INCLUDING the
               held-out goals; blocks = goal x ISO week; DQ5 style_resid vectors, both models; exogenous directions
               projected (kickoff, goal text, room kickoffs, human-message centroid, #51 agent goals)
  estimator    two-way FE leave-goal-out personal vectors; goal-equal centering; goal-pair weights (h81lib, frozen)
  statistic    D_adjg and D_adj computed on cross-goal block pairs with AT LEAST ONE held-out block (new pairs only)
  null         S0 synthetic on the same full panel (200 replicates; same pair restriction)
  prediction   (HH293, as pre-registered) D_adjg > S0 q95 in regime I in both models (P2) and D_adj > S0 q95 (P3).
               Round-1 exploratory reading to be confirmed or overturned: see the card's Results.
Output: data/processed/H81-culture-beyond-composition/confirm/confirm.json (or the dry-run folder)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h81lib as L  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
STANDIN = {"I": [16, 23, 30], "III": [39, 44]}
FROZEN = "2026-10-04"


def guard(dry: bool):
    if dry:
        return
    sig = os.environ.get("H81_CONFIRM_SIGNOFF", "").strip()
    if not sig:
        sys.exit("H81 confirm.py: refused. Set H81_CONFIRM_SIGNOFF='<name> <date>' after Vivian's sign-off, and list the "
                 "run in the holdout ledger.")
    sys.path.insert(0, str(ROOT / "infra/shared"))
    try:
        import holdout_ledger  # noqa: F401
    except Exception as e:  # noqa: BLE001
        sys.exit(f"H81 confirm.py: holdout ledger not importable ({e}); refused.")


def full_panel(model: str, regime: str, dry: bool):
    """Agent-days INCLUDING held-out goals (confirmatory) or non-holdout only with stand-ins (dry run)."""
    ad = pl.read_parquet(SH / "embeddings/agent_day.parquet").with_row_index("src")
    ad = ad.with_columns((pl.col("n_chat") + pl.col("n_intent")).alias("n_stat"))
    ad = ad.filter((pl.col("regime") == regime) & (pl.col("n_stat") >= L_MIN) & ~pl.col("agent").is_in([19, 28, 30]))
    if dry:
        sys.path.insert(0, str(ROOT / "infra/shared"))
        from common import holdout_mask
        hm = np.array(holdout_mask(ad["pt_date"].to_list(), ad["goal_no"].to_list()))
        ad = ad.filter(~pl.Series(hm) & ~pl.col("holdout"))
        held = set(STANDIN[regime])
    else:
        held = set(ad.filter(pl.col("holdout"))["goal_no"].unique().to_list())
    return ad, held


L_MIN = 5


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=200)
    a = ap.parse_args()
    guard(a.dry_run)
    out = Path(a.out) if a.out else (L.OUT / "confirm")
    out.mkdir(parents=True, exist_ok=True)
    # The confirmatory panel must be rebuilt with the frozen scheme including held-out rows; the scheme's vectors and
    # directions come from scheme/build.py logic applied to all rows (imported, not copied).
    sys.path.insert(0, str(HERE.parent / "scheme"))
    import build as B  # noqa: E402
    res = {"frozen": FROZEN, "dry_run": a.dry_run, "results": {}}
    for model in ("bge_small", "gte_modernbert"):
        for regime in ("I", "III"):
            ad, held = full_panel(model, regime, a.dry_run)
            X = np.load(SH / "embeddings" / f"agent_day_style_resid_{B.MODELS[model]['suffix']}.npy").astype(np.float64)
            X = B.unit(X[ad["src"].to_numpy()])
            d = ad["pt_date"].str.to_date()
            ad = ad.with_columns((d.dt.iso_year().cast(pl.Int32) * 100 + d.dt.week().cast(pl.Int32)).alias("week"))
            ad = ad.with_columns((pl.col("goal_no").cast(pl.Utf8) + pl.col("regime") + "w" + pl.col("week").cast(pl.Utf8)).alias("block"))
            blocks = B.build_blocks(ad.with_columns(pl.lit(None, dtype=pl.Int8).alias("room")))
            V, idx = B.directions(model, ad, include_holdout=not a.dry_run)
            np.savez_compressed(out / f"dirs_{model}.npz", V=V)
            (out / f"dirs_index_{model}.json").write_text(json.dumps(idx))
            old_out = L.OUT
            L.OUT = out  # projectors read the confirm-time directions
            P = L.projectors(model, regime, ad)
            L.OUT = old_out
            pan = L.Panel(ad, blocks, P)
            L.OUT = out
            kick = L.goal_kickoff(model, regime, np.unique(pan.goal))
            L.OUT = old_out
            heldb = {b for b in range(pan.nb) if pan.block_goal[b] in held}

            def stat(Xm):
                A, Bk, R = L.agent_block_residuals(pan, Xm)
                T = L.pair_table(pan, A, Bk, R, kick)
                keep = np.array([(int(r[0]) in heldb) or (int(r[1]) in heldb) for r in T]) if len(T) else np.array([], bool)
                return L.slow_stats(T[keep]) if keep.any() else {}

            real = stat(X)
            sc = L.variance_scales(pan, X); rng = np.random.default_rng(20261004)
            s0 = [stat(L.simulate(pan, sc, rng)) for _ in range(a.reps)]
            q = {k: float(np.nanquantile([s.get(k, np.nan) for s in s0], 0.95)) for k in ("D_adjg", "D_adj")}
            res["results"][f"{model}/{regime}"] = {"real": real, "S0_q95": q,
                                                   "P2_pass": bool(real.get("D_adjg", np.nan) > q["D_adjg"]),
                                                   "P3_pass": bool(real.get("D_adj", np.nan) > q["D_adj"]),
                                                   "n_held_blocks": len(heldb)}
            print(model, regime, res["results"][f"{model}/{regime}"], flush=True)
    (out / "confirm.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
