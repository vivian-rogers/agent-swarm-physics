"""Build data/processed/H142-langevin-torque-saturation/G<NN>/: (call, direction) rows, labelled batch and in-flight
items, day-fold centroids and structural counts (rows by aligned count n_u). No text; projected values as float32/16.

Usage: uv run python hypotheses/H142-langevin-torque-saturation/scheme/build.py [--period 38 ...] [--all]
Inputs: shared pending_sets/G<NN>/ (talks, pending; wakes, wake_pending for #51), chat_core, embeddings, goals,
statement_flags, period_units. The counts in counts.json are structural (no reader outcome is read).
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
import h142scheme as S  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

OUT = S.ROOT / "data/processed/H142-langevin-torque-saturation"
PS = S.SHARED / "pending_sets"
HOLD = {1, 9, 14, 15, 22, 28, 29, 32, 34, 43, 45, 46, 47, 48, 49, 50}
K_MAIN, K_VAR = 8, 12
SYNTH_MODEL = "bge_small"


def periods_available() -> list[int]:
    return sorted(int(p.name[1:]) for p in PS.glob("G*") if p.is_dir() and int(p.name[1:]) not in HOLD)


def structural_counts(rows: pl.DataFrame) -> dict:
    n = rows["n"].to_numpy()
    out = {f"n{v}": int((n == v).sum()) for v in range(0, 6)}
    out["n6p"] = int((n >= 6).sum()); out["n_ge4"] = int((n >= 4).sum()); out["rows"] = len(rows)
    out["calls"] = int(rows["call"].n_unique())
    vals, cnt = np.unique(n, return_counts=True)
    out["n_max"] = int(n.max()) if len(n) else 0
    out["n_max_50"] = int(vals[cnt >= 50].max()) if (cnt >= 50).any() else 0     # O5 (structural)
    nf = rows["nF"].to_numpy(); out["nF_ge1"] = int((nf >= 1).sum())
    return out


def build_one(g: int, calls: pl.DataFrame, items: pl.DataFrame, model: str, d: Path, tag: str, cents_in=None) -> tuple[dict, dict]:
    P = S.project_calls(g, calls, items, model)
    cents = cents_in if cents_in is not None else S.fold_centroids(P["calls"], P["Y"], K_MAIN, seed=1000 * g)
    rows, it, infl, cc = S.rows_frame(P, cents, K_MAIN, g)
    rows.write_parquet(d / f"rows_{tag}.parquet", compression="zstd")
    cc.drop("resp_srow").write_parquet(d / f"calls_{tag}.parquet", compression="zstd")
    it.write_parquet(d / f"items_{tag}.parquet", compression="zstd")
    infl.write_parquet(d / f"inflight_{tag}.parquet", compression="zstd")
    if model == SYNTH_MODEL:
        np.save(d / f"xb_{tag}.npy", P["XB"].astype(np.float16)); np.save(d / f"xf_{tag}.npy", P["XF"].astype(np.float16))
    cnt = structural_counts(rows)
    if cents_in is None:
        np.savez_compressed(d / f"centroids_{tag}.npz", days=np.array(sorted(cents)), C=np.stack([cents[k] for k in sorted(cents)]))
        if model == SYNTH_MODEL:   # K = 12 variant labels (bge only)
            c12 = S.fold_centroids(P["calls"], P["Y"], K_VAR, seed=1000 * g + 7)
            r12, _, _, _ = S.rows_frame(P, c12, K_VAR, g)
            r12.select("call", "u", "y", "n", "nF", "newest", "nname").write_parquet(d / f"rows_{tag}_K12.parquet", compression="zstd")
            cnt["K12"] = structural_counts(r12)
            ml = S.message_labels(g, sorted(cents), cents, model)
            ml.write_parquet(d / f"msglabels_{tag}.parquet", compression="zstd")
    return cnt, cents


def build(g: int, models=S.MODELS) -> dict:
    t0 = time.time()
    d = OUT / f"G{g:02d}"
    d.mkdir(parents=True, exist_ok=True)
    psd = PS / f"G{g:02d}"
    calls, items = S.frames_talks(psd)
    if g == 40:   # NE42 card note: GPT-5 alone in #rest during #40 is excluded (keep the merged room only)
        main_room = calls.group_by("room").len().sort("len", descending=True)["room"][0]
        calls = calls.filter(pl.col("room") == main_room)
    cnt = {"goal_no": g, "talks": len(calls)}
    for model in models:
        c, cents = build_one(g, calls, items, model, d, model)
        cnt[model] = c
        if g == 51 and (psd / "wakes.parquet").exists():
            wc, wi = S.frames_wakes(psd, S.chat_rows())
            # wakes use the talk-call day-fold centroids (same ruler)
            c2, _ = build_one(g, wc, wi, model, d, f"wake_{model}", cents_in=cents)
            cnt[f"wake_{model}"] = c2
    cnt["build_s"] = round(time.time() - t0, 1)
    (d / "counts.json").write_text(json.dumps(cnt, indent=1))
    return cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    periods = periods_available() if a.all or not a.period else a.period
    OUT.mkdir(parents=True, exist_ok=True)
    for g in periods:
        c = build(g)
        print(json.dumps({"goal_no": g, "bge_n_ge4": c["bge_small"]["n_ge4"], "gte_n_ge4": c["gte_modernbert"]["n_ge4"],
                          "calls": c["bge_small"]["calls"], "s": c["build_s"]}), flush=True)
    prov = {"built_by": "hypotheses/H142-langevin-torque-saturation/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["pending_sets/G<NN> (talks, pending, wakes, wake_pending)", "chat_core",
                                   "embeddings/statements + chat_index", "statements_style_resid32_<model>",
                                   "goal_vectors_<model> + goals", "whitening_<model>_<regime>", "statement_flags",
                                   "period_units"]}],
            "params": {"K": K_MAIN, "K_variant": K_VAR, "cos_min": S.COS_MIN, "field_window_s": S.FIELD_WIN_S,
                       "field_min": S.FIELD_MIN, "models": list(S.MODELS), "periods": periods,
                       "projection": "P_c removes previous statement, goal/kickoff/room-kickoff, window field (card)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pp = OUT / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    old["scheme"] = prov
    pp.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
