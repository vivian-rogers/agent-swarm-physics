"""H23 round 1b (2026-10-04), G44 only (non-holdout). The frozen round-1 / confirmatory files (h23lib.py, h23run.py,
build_messages.py, confirm_g45.py) are NOT edited; this script imports them and swaps inputs from outside.

  A. DQ6 checkpoint times (ground_truth_labels, label_kind checkpoint, agent 28): relabel the leader's #44 messages and
     count disagreements with h23lib.CHECKPOINTS (which has start times only).
  B. Shared copy information: re-run run_period on G44 with h23lib's decompose / mi_parts (imported from H07's folder)
     replaced by infra/shared/copy_info's, and compare every number with round 1's results.json.
  C. Second embedding model: O3a d = cos(z, corpus centroid) - cos(z, Kimi-field centroid) in gte-modernbert's
     regime-III whitened 32-d space (corpus targets embedded here with gte, CLS pooling, normalized, offline, CPU,
     2 threads), next to the same computation in bge (which must reproduce round 1).

Usage: HF_HUB_OFFLINE=1 uv run --offline --with sentence-transformers python \
           hypotheses/H23-leader-distillation-copy/analysis/r1b.py
Output: data/processed/H23-leader-distillation-copy/G44/r1b/r1b.json (numbers only).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h23lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
import copy_info as CI  # noqa: E402
import embed_models as EM  # noqa: E402

G44 = L.OUT / "G44"
OUT = G44 / "r1b"
OUT.mkdir(parents=True, exist_ok=True)


def part_a() -> dict:
    gt = (pl.read_parquet(L.SH / "ground_truth_labels.parquet")
          .filter((pl.col("label_kind") == "checkpoint") & (pl.col("agent") == 28)).sort("t_valid_from"))
    M = pl.read_parquet(G44 / "messages.parquet").filter(pl.col("group") == "leader")

    def dq6(t):
        for v, a, b in gt.select("value", "t_valid_from", "t_valid_to").iter_rows():
            if a <= t < b:
                return v
        return "none"
    lab = [dq6(t) for t in M["t"].to_list()]
    M = M.with_columns(pl.Series("checkpoint_dq6", lab))
    dis = M.filter(pl.col("checkpoint") != pl.col("checkpoint_dq6"))
    starts = {v: str(a) for v, a in gt.select("value", "t_valid_from").iter_rows()}
    return {"n_leader_messages": M.height, "n_disagree": dis.height,
            "counts_round1": dict(M.group_by("checkpoint").len().iter_rows()),
            "counts_dq6": dict(M.group_by("checkpoint_dq6").len().iter_rows()),
            "dq6_starts": starts, "h23lib_starts": {n: str(t) for n, t in L.CHECKPOINTS},
            "live_window_messages_dq6_v7": int(M.filter(pl.col("live") & (pl.col("checkpoint_dq6") == "kimi-v7-aug-64")).height)}


def _cmp(a, b, path="", out=None, tol=1e-9):
    out = out if out is not None else {"n": 0, "max_abs_diff": 0.0, "mismatch": []}
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k in a and k in b:
                _cmp(a[k], b[k], f"{path}/{k}", out, tol)
            else:
                out["mismatch"].append(f"{path}/{k} missing")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp(x, y, f"{path}[{i}]", out, tol)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        out["n"] += 1
        if np.isfinite(a) and np.isfinite(b):
            d = abs(a - b)
            out["max_abs_diff"] = max(out["max_abs_diff"], d)
            if d > tol:
                out["mismatch"].append(f"{path}: {a} vs {b}")
    return out


def part_b() -> dict:
    import h23run
    L.decompose, L.mi_parts = CI.decompose, CI.mi_parts      # shared module instead of H07's folder
    d = OUT / "copyinfo_run"
    d.mkdir(exist_ok=True)
    for f in ("messages.parquet", "vectors.npz"):
        shutil.copy(G44 / f, d / f)
    R = h23run.run_period(d, {"checkpoints": ["kimi-v7-aug-64"], "corpus_unplaced": False})
    R = json.loads(json.dumps(R, default=h23run._np))
    old = json.loads((G44 / "results.json").read_text())
    c = _cmp(R, old)
    c["mismatch"] = c["mismatch"][:20]
    return c


def part_c() -> dict:
    from sentence_transformers import SentenceTransformer
    import torch
    torch.set_num_threads(2)
    M = pl.read_parquet(G44 / "messages.parquet")
    C = pl.read_parquet(G44 / "corpus_text.parquet")
    mem = np.array(C["member"].to_list())
    spec = EM.MODELS["gte_modernbert"]
    m = SentenceTransformer(spec["hf"], revision=spec["revision"], device="cpu")
    m.max_seq_length = 256
    tg = m.encode([s[:2000] for s in C["response"].to_list()], batch_size=16, normalize_embeddings=True,
                  convert_to_numpy=True).astype(np.float32)
    CE = np.load(G44 / "corpus_emb.npz")
    out = {}
    per = M.filter(pl.col("set") == "period")
    groups = {"leader": per.filter((pl.col("group") == "leader") & pl.col("live") & (pl.col("checkpoint") == "kimi-v7-aug-64")),
              "K_same": per.filter((pl.col("group") == "kimi") & pl.col("live")),
              "V_same": per.filter((pl.col("group") == "village") & pl.col("live"))}
    groups["CTRL"] = pl.concat([groups["K_same"], groups["V_same"]])
    kfield = M.filter(pl.col("set") == "field")
    for model, Eraw, tgt in (("bge_small", np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r"), CE["target"]),
                             ("gte_modernbert", np.load(L.SH / "embeddings/chat_gte_modernbert.npy", mmap_mode="r"), tg)):
        W = EM.load_whitener("III", 32, model)
        zbarC = W(tgt[mem]).mean(0)
        zbarK = W(np.asarray(Eraw[kfield["emb_row"].to_numpy()], dtype=np.float32)).mean(0)
        D = {}
        for g, df in groups.items():
            Z = W(np.asarray(Eraw[df["emb_row"].to_numpy()], dtype=np.float32))
            D[g] = L.cos_rows(Z, zbarC) - L.cos_rows(Z, zbarK)
        r = {"d_mean": {g: float(v.mean()) for g, v in D.items()}, "n": {g: len(v) for g, v in D.items()},
             "cos_centroids_C_K": L.cos(zbarC, zbarK)}
        r["tests"] = {f"d:leader>{o}": L.perm_mean_diff(D["leader"], D[o], seed=20261003) for o in ("CTRL", "K_same", "V_same")}
        out[model] = r
    return out


def main():
    R = {"A_checkpoints_dq6": part_a()}
    print(json.dumps(R["A_checkpoints_dq6"], indent=1, default=str), flush=True)
    R["B_copy_info_shared"] = part_b()
    print(json.dumps(R["B_copy_info_shared"], indent=1, default=str), flush=True)
    R["C_embedding_two_models"] = part_c()
    print(json.dumps(R["C_embedding_two_models"], indent=1, default=float), flush=True)
    (OUT / "r1b.json").write_text(json.dumps(R, indent=1, default=float))


if __name__ == "__main__":
    main()
