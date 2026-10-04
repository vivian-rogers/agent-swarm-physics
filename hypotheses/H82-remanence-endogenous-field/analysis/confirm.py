"""H82 CONFIRMATORY test on the locked holdout. FROZEN 2026-10-04 (round 1). DO NOT RUN without Vivian's sign-off.

Guard: runs only with H82_CONFIRM_SIGNOFF="<name> <YYYY-MM-DD>" in the environment AND the run listed in the holdout
ledger (infra/shared/holdout_ledger.py). `--dry-run` executes every code path on NON-holdout data, treating the
stand-in goals {11, 18, 25, 39} as "held out", and writes only to the folder given with --out.

Frozen design (round-1 card, Amendments A1-A3):
  boundaries   consecutive goal pairs (P-1, P) in one regime with at least one held-out side (e.g. 8->9, 9->10,
               13->14, 14->15, 15->16, 21->22, 22->23, 27->28, 28->29, 29->30, 42->43, 43->44, 44->45 ... 50->51)
  regression   h82lib.design (kickoff, goal text, previous kickoff, day human centroid, room kickoffs, #51 agent goal,
               prior leaving out P and X, leave-i-out centroid of X); X = P-1 or a placebo period (|Q-P| >= 2)
  statistic    pooled unweighted mean of Delta gamma on day 1 over these boundaries, both models
  null         S0 synthetic on the same boundaries (200 replicates; alpha_hat refitted on them)
  prediction   C1 (HH290, as pre-registered) mean Delta gamma_1 > S0 q95 in both models.
               C2 (from round-1 post hoc PH2) with the agent's own P-1 mean added as a regressor, the mean Delta gamma_1
               falls below 0.05 in both models (the trace is individual carry-over, not the village record).
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
sys.path.insert(0, str(HERE.parent / "scheme"))
import h82lib as L  # noqa: E402
import synthetic as SY  # noqa: E402

FROZEN = "2026-10-04"
STANDIN = {11, 18, 25, 39}


def guard(dry: bool):
    if dry:
        return
    if not os.environ.get("H82_CONFIRM_SIGNOFF", "").strip():
        sys.exit("H82 confirm.py: refused. Set H82_CONFIRM_SIGNOFF='<name> <date>' after Vivian's sign-off, and list the "
                 "run in the holdout ledger.")
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    try:
        import holdout_ledger  # noqa: F401
    except Exception as e:  # noqa: BLE001
        sys.exit(f"H82 confirm.py: holdout ledger not importable ({e}); refused.")


def build_folder(out: Path, dry: bool):
    import build as B  # H82 scheme (frozen logic; holdout switch used only here)
    ad = B.eligible_agentdays(include_holdout=not dry)
    src = ad["src"].to_numpy()
    for m in ("bge_small", "gte_modernbert"):
        X = np.load(B.ED / f"agent_day_style_resid_{B.MODELS[m]['suffix']}.npy").astype(np.float32)[src]
        np.save(out / f"vecs_{m}_style_resid.npy", B.unit(X).astype(np.float32))
        V, idx = B.directions(m, ad, include_holdout=not dry)
        np.savez_compressed(out / f"dirs_{m}.npz", V=V)
        (out / f"dirs_index_{m}.json").write_text(json.dumps(idx))
    ad.drop("hm").write_parquet(out / "agentdays.parquet")
    held = STANDIN if dry else set(ad.filter(pl.col("holdout"))["goal_no"].unique().to_list())
    B.build_boundaries(ad, require_holdout_side=held).write_parquet(out / "boundaries.parquet")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--out", default=None)
    ap.add_argument("--reps", type=int, default=200)
    a = ap.parse_args()
    guard(a.dry_run)
    out = Path(a.out) if a.out else (L.OUT / "confirm")
    out.mkdir(parents=True, exist_ok=True)
    build_folder(out, a.dry_run)
    L.OUT = out
    res = {"frozen": FROZEN, "dry_run": a.dry_run, "results": {}}
    for model in ("bge_small", "gte_modernbert"):
        D = L.Data(model)
        bds = list(D.bd.iter_rows(named=True))
        des = [(b, L.boundary_designs(D, b)) for b in bds]
        rows = []
        for b, dd in des:
            rows += L.boundary_stats(b, dd, n_boot=0)
        df = pl.DataFrame(rows).filter((pl.col("term") == "e") & (pl.col("d") == 1))
        real = float(np.nanmean(df["dgamma"].to_numpy()))
        fits = SY.null_fit(D, des) if {r["regime"] for r in bds} >= {"I", "III"} else None
        s0 = []
        rng = np.random.default_rng(20261004)
        for _ in range(a.reps):
            if fits is None:
                break
            ys = SY.make_ysub(D, fits, rng)
            st = []
            for b, dd in des:
                st += L.boundary_stats(b, dd, n_boot=0, Ysub=ys)
            d1 = [r["dgamma"] for r in st if r["term"] == "e" and r["d"] == 1]
            s0.append(np.nanmean(d1))
        q95 = float(np.nanquantile(s0, 0.95)) if s0 else None
        # C2: own previous-period mean as an extra regressor (zeros for agents absent from P-1)
        c2 = []
        for b, dd in des:
            item = dd[0]
            if item is None:
                continue
            day, d0, plc = item
            new = {}
            for key, d in d0.items():
                if d is None:
                    new[key] = None
                    continue
                Y, Z, names, ag, isnew = d
                own = []
                for a_ in ag:
                    mm = (D.agent == a_) & (D.goal == b["prev"]) & (D.regime == b["regime"])
                    own.append(L.unit(D.X[mm].mean(0)) if mm.sum() else np.zeros(32))
                new[key] = (Y, np.concatenate([Z[:, :, :-1], np.array(own)[:, :, None], Z[:, :, -1:]], axis=2),
                            names[:-1] + ["own_prev"] + names[-1:], ag, isnew)
            c2 += [r["dgamma"] for r in L.boundary_stats(b, [(day, new, plc)], n_boot=0) if r["term"] == "e"]
        c2m = float(np.nanmean(c2)) if c2 else None
        res["results"][model] = {"n_boundaries": len(bds), "mean_dgamma_d1": real, "S0_q95": q95,
                                 "P1_pass": bool(q95 is not None and real > q95),
                                 "C2_mean_dgamma_d1_own_prev": c2m, "C2_pass": bool(c2m is not None and c2m < 0.05),
                                 "boundaries": [(r["P"], r["prev"]) for r in bds]}
        print(model, res["results"][model], flush=True)
    (out / "confirm.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
