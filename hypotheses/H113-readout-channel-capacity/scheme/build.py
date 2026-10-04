"""Build data/processed/H113-readout-channel-capacity/G<NN>/ (per-call uptake terms, per-item terms, projected vectors).

Usage: uv run python hypotheses/H113-readout-channel-capacity/scheme/build.py [--period 38 ...] [--wakes] [--all]
Inputs: data/processed/shared/pending_sets/G<NN>/ (non-holdout by construction) and shared embeddings. No text.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h113scheme as S  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

OUT = S.ROOT / "data/processed/H113-readout-channel-capacity"
PS = S.SHARED / "pending_sets"
HOLD = {1, 9, 14, 15, 22, 28, 29, 32, 34, 43, 45, 46, 47, 48, 49, 50}


def kmeans_labels(Y: np.ndarray, X: np.ndarray, read: np.ndarray, K: int = 8, seed: int = 0):
    """Plain k-means (25 iterations) fitted on reader statements plus read items; labels for all rows."""
    rng = np.random.default_rng(seed)
    Yf = Y.astype(np.float32); Xf = X.astype(np.float32)
    pool = np.vstack([Yf, Xf[read]]) if read.any() else Yf
    cent = pool[rng.choice(len(pool), K, replace=False)]
    for _ in range(25):
        lab = np.argmin(((pool[:, None, :] - cent[None]) ** 2).sum(-1), 1)
        cent = np.vstack([pool[lab == j].mean(0) if (lab == j).any() else cent[j] for j in range(K)])
    yl = np.argmin(((Yf[:, None, :] - cent[None]) ** 2).sum(-1), 1)
    xl = np.argmin(((Xf[:, None, :] - cent[None]) ** 2).sum(-1), 1) if len(Xf) else np.zeros(0, int)
    return yl, xl


def periods_available() -> list[int]:
    return sorted(int(p.name[1:]) for p in PS.glob("G*") if p.is_dir() and int(p.name[1:]) not in HOLD)


def build(g: int, wakes: bool = False, models=S.MODELS, variants=("style_resid32",)) -> dict:
    t0 = time.time()
    d = OUT / f"G{g:02d}"
    d.mkdir(parents=True, exist_ok=True)
    cr = S.chat_rows()
    psd = PS / f"G{g:02d}"
    calls, items = S.build_frames_talks(g, psd)
    items = S.at_call_items(calls, items, cr)
    cnt = {"goal_no": g, "talks": len(calls)}
    for model in models:
        for var in variants:
          for fld in (False, True):   # A1: primary = raw projection (no window field); F = window-field variant
            tag = (model if var == "style_resid32" else f"{model}_{var}") + ("_F" if fld else "")
            c, i, Y, X = S.compute(g, calls, items, model, var, field=fld)
            if not fld and len(c):  # discrete check: K = 8 cluster labels instead of stored vectors (storage budget)
                yl, xl = kmeans_labels(Y, X, i["read"].to_numpy() if len(i) else np.zeros(0, bool), seed=g)
                c = c.with_columns(pl.Series("ylab", yl, dtype=pl.Int8))
                if len(i):
                    i = i.with_columns(pl.Series("xlab", xl, dtype=pl.Int8))
            c.write_parquet(d / f"calls_{tag}.parquet", compression="zstd")
            if not fld:
                i.write_parquet(d / f"items_{tag}.parquet", compression="zstd")
            cnt[f"calls_{tag}"] = len(c)
            if len(c):
                cnt[f"k_ge1_{tag}"] = int((c["k"] >= 1).sum()); cnt[f"k_ge8_{tag}"] = int((c["k"] >= 8).sum())
                cnt[f"inflight_items_{tag}"] = int(c["kF"].sum())
    if wakes and (psd / "wakes.parquet").exists():
        wc, wi = S.build_frames_wakes(g, psd, cr)
        wi = wi.with_columns(pl.lit(False).alias("at_call"))
        for model in models:
            c, i, Y, X = S.compute(g, wc, wi, model, field=False)
            c.write_parquet(d / f"wcalls_{model}.parquet", compression="zstd")
            i.write_parquet(d / f"witems_{model}.parquet", compression="zstd")
            cnt[f"wake_calls_{model}"] = len(c)
    cnt["build_s"] = round(time.time() - t0, 1)
    (d / "counts.json").write_text(json.dumps(cnt, indent=1))
    return cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--wakes", action="store_true")
    ap.add_argument("--white", action="store_true", help="also build the white32 variant")
    a = ap.parse_args()
    periods = periods_available() if a.all or not a.period else a.period
    variants = ("style_resid32", "white32") if a.white else ("style_resid32",)
    OUT.mkdir(parents=True, exist_ok=True)
    for g in periods:
        print(json.dumps(build(g, wakes=a.wakes or g == 51, variants=variants)), flush=True)
    prov = {"built_by": "hypotheses/H113-readout-channel-capacity/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["pending_sets/G<NN> (talks, pending, wakes, wake_pending)", "chat_core", "producing_calls",
                                   "context_ledger_items", "embeddings/statements + chat_index", "statements_style_resid32_<model>",
                                   "goal_vectors_<model> + goals", "whitening_<model>_<regime>", "period_units"]}],
            "params": {"field_window_s": S.FIELD_WIN_S, "field_min": S.FIELD_MIN, "models": list(S.MODELS), "periods": periods},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pp = OUT / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    old["scheme"] = prov
    pp.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
