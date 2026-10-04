"""H10 round 1b inputs (improved data, 2026-10-04). Adds to data/processed/H10-goals-are-legendre-pushes/r1b/ without
touching the round-1 files (statements.parquet, stmt_w64.npy, goal_vecs.npz stay as they were, so the old path runs).

Outputs (no text):
  r1b/srow.npy                   row of shared embeddings/statements.parquet for every H10 statement row (int32)
  r1b/flags.parquet              row, self_repeat_bge, self_repeat_gte, self_repeat_both, cross_echo_both (DQ5 flags)
  r1b/stmt_w64_gte_modernbert.npy  (n, 64) fp16 regime-whitened gte-modernbert coordinates (not normalized; nested PCA)
  r1b/stmt_sr32_<model>.npy      (n, 32) fp16 style-residualized (within goal period) statement vectors, both models
                                 (shared statements_style_resid_period32_<model>.npy, unit-normalized there)
  r1b/goal_vecs_<model>.npz      goal_no, goal_raw (shared kind `goal`), kick_raw (kind `kickoff`, all rooms; NaN if none)
  r1b/goal_rooms.parquet + goal_rooms_<model>.npy   per-room kickoffs (kind `kickoff_room`) and agent goals (`agent_goal`)
  r1b/check.json                 alignment of the H10 rows with the shared rows; cosine of H10's own goal/kickoff vectors
                                 with the shared ones (bge)
Holdout goal periods and #23 are excluded exactly as in scheme/build.py (rows are the same rows, verified).

Usage: uv run python hypotheses/H10-goals-are-legendre-pushes/scheme/build_r1b.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build import EXCLUDED_GOALS, OUT, load_statements  # noqa: E402
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
from common import REVISION, git_commit, load_holdout  # noqa: E402
import embed_models as EM  # noqa: E402

R1B = OUT / "r1b"
MODELS = ("bge_small", "gte_modernbert")


def main():
    R1B.mkdir(parents=True, exist_ok=True)
    st = load_statements()                      # same filter as round 1, with emb_row = shared statements row
    old = pl.read_parquet(OUT / "statements.parquet")
    assert st.height == old.height, (st.height, old.height)
    same = (st.select("kind", "agent", "t", "goal_no").equals(old.select("kind", "agent", "t", "goal_no")))
    assert same, "H10 rows do not match the shared rows in order"
    srow = st["emb_row"].to_numpy().astype(np.int32)
    np.save(R1B / "srow.npy", srow)
    check = {"n_rows": int(st.height), "rows_match_round1": bool(same)}

    fl = pl.read_parquet(EM.OUT / "statement_flags.parquet",
                         columns=["srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "cross_echo_both"])
    fl = fl.sort("srow")
    assert (fl["srow"].to_numpy() == np.arange(fl.height)).all()
    f = fl[srow].with_columns(pl.Series("row", np.arange(st.height, dtype=np.uint32))).drop("srow")
    f.write_parquet(R1B / "flags.parquet", compression="zstd")
    check["flag_rates"] = {c: float(f[c].mean()) for c in f.columns if c != "row"}

    # gte whitened 64-d (regime basis, non-holdout fit), same layout as stmt_w64.npy
    E = EM.statement_embeddings("gte_modernbert")
    reg = st["regime"].to_numpy()
    Z = np.zeros((st.height, 64), dtype=np.float16)
    for r in sorted(set(reg)):
        W = EM.load_whitener(r, 64, "gte_modernbert")
        sel = np.flatnonzero(reg == r)
        for a in range(0, sel.size, 20000):
            s = sel[a:a + 20000]
            Z[s] = W(E[srow[s]]).astype(np.float16)
    np.save(R1B / "stmt_w64_gte_modernbert.npy", Z)
    del E

    # bge check: shared white32 equals the normalized first 32 dims of H10's stmt_w64
    Zb = np.load(OUT / "stmt_w64.npy", mmap_mode="r")
    w32 = np.load(EM.ED / "statements_white32_bge_small.npy", mmap_mode="r")
    idx = np.random.default_rng(0).choice(st.height, 2000, replace=False)
    a = np.asarray(Zb[idx, :32], dtype=np.float64); a /= np.linalg.norm(a, axis=1, keepdims=True)
    b = np.asarray(w32[srow[idx]], dtype=np.float64); b /= np.linalg.norm(b, axis=1, keepdims=True)
    check["bge_white32_cos_min"] = float((a * b).sum(1).min())

    for m in MODELS:
        S = np.load(EM.ED / f"statements_style_resid_period32_{EM.MODELS[m]['suffix']}.npy", mmap_mode="r")
        np.save(R1B / f"stmt_sr32_{m}.npy", np.asarray(S[srow], dtype=np.float16))

    # shared goal fields
    held = set(load_holdout()["goal_periods_held_out"]) | EXCLUDED_GOALS
    gm = pl.read_parquet(EM.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    gm = gm.filter(~pl.col("holdout") & ~pl.col("goal_no").is_in(list(held)))
    goal_nos = sorted(set(gm.filter(pl.col("kind") == "goal")["goal_no"].to_list()))
    for m in MODELS:
        V = EM.goal_vectors(m).astype(np.float32)
        G = np.full((len(goal_nos), V.shape[1]), np.nan, np.float32)
        K = np.full((len(goal_nos), V.shape[1]), np.nan, np.float32)
        for i, g in enumerate(goal_nos):
            q = gm.filter((pl.col("goal_no") == g) & (pl.col("kind") == "goal"))
            G[i] = V[q["gid"][0]]
            q = gm.filter((pl.col("goal_no") == g) & (pl.col("kind") == "kickoff"))
            if q.height:
                K[i] = V[q["gid"][0]]
        np.savez(R1B / f"goal_vecs_{m}.npz", goal_no=np.array(goal_nos), goal_raw=G, kick_raw=K)
        rr = gm.filter(pl.col("kind").is_in(["kickoff_room", "agent_goal"])).sort("gid")
        np.save(R1B / f"goal_rooms_{m}.npy", V[rr["gid"].to_numpy()])
    rr.select(pl.int_range(pl.len(), dtype=pl.UInt32).alias("i"), "gid", "goal_no", "kind", "room", "agent", "valid_from",
              "valid_to", "regime").write_parquet(R1B / "goal_rooms.parquet")

    # H10's own vectors vs the shared ones (bge)
    old = np.load(OUT / "goal_vecs.npz")
    new = np.load(R1B / "goal_vecs_bge_small.npz")
    cos = {}
    for i, g in enumerate(old["goal_no"]):
        j = np.flatnonzero(new["goal_no"] == g)
        if not j.size:
            continue
        c = {}
        for k in ("goal_raw", "kick_raw"):
            x, y = old[k][i], new[k][j[0]]
            c[k] = (float(x @ y / np.linalg.norm(x) / np.linalg.norm(y)) if np.isfinite(x).all() and np.isfinite(y).all()
                    else None)
        cos[int(g)] = c
    check["goal_cos_h10_vs_shared"] = cos
    vals = [v for c in cos.values() for v in c.values() if v is not None]
    check["goal_cos_min"] = float(min(vals))
    (R1B / "check.json").write_text(json.dumps(check, indent=1))

    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text())
    prov.setdefault("r1b", {})
    prov["r1b"] = {"built_by": "hypotheses/H10-goals-are-legendre-pushes/scheme/build_r1b.py", "git_commit": git_commit(),
                   "inputs": [{"source": "ai-village", "revision": REVISION,
                               "tables": ["shared/embeddings/statements", "shared/embeddings/{chat,intentions}_gte_modernbert",
                                          "shared/embeddings/whitening_gte_modernbert_*",
                                          "shared/embeddings/statements_style_resid_period32_*",
                                          "shared/statement_flags", "shared/embeddings/goals + goal_vectors*"]}],
                   "params": {"models": list(MODELS), "dim": 64}, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(json.dumps({k: v for k, v in check.items() if k != "goal_cos_h10_vs_shared"}, indent=1))


if __name__ == "__main__":
    main()
