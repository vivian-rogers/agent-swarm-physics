"""Check that H52's vectorized content statistic equals H30's chi_orth (h30lib.content_scores, imported read-only)
when both see the same pre/post statements and the same placebo pool. Also checks that message vectors for agent
messages equal the shared statement white32 vectors. Numbers only; writes analysis check json.

Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/verify_chi.py [G44]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(L.ROOT / "hypotheses/H30-operator-susceptibility/analysis"))
import h30lib  # noqa: E402  (read-only import)


def main(period: str = "G44", n_check: int = 150):
    goal = L.PERIODS[period]["goal"]
    days = L.period_days(goal)
    R = pl.read_parquet(L.OUT / period / "rows.parquet")
    regime = "III" if goal >= 37 else "I"
    st, V = L.statement_table(days)
    rng = np.random.default_rng(1)
    sub = R.filter(pl.col("chi").is_not_null()).sample(n=min(n_check, R.filter(pl.col("chi").is_not_null()).height), seed=3)
    recv = sub["recv"].to_numpy().astype(int); tc = sub["tc"].to_numpy()
    bidx, pmask, qidx = L.window_indices(st["agent"].to_numpy(), st["ts"].to_numpy(), recv, tc)
    pool_msgs = R.filter(pl.col("cls") == 0)["msg"].unique().to_numpy().astype(np.int64)
    pl_idx = pool_msgs[rng.integers(len(pool_msgs), size=(sub.height, L.N_PL))]
    allm = np.unique(np.concatenate([sub["msg"].to_numpy().astype(np.int64), pl_idx.ravel()]))
    Mv = L.message_vectors(allm, regime)
    pos = {int(m): k for k, m in enumerate(allm)}
    U = Mv[[pos[int(m)] for m in sub["msg"].to_numpy()]]
    Up = Mv[np.vectorize(lambda m: pos[int(m)])(pl_idx)]
    mine = L.content_rows(V, bidx, pmask, qidx, U, Up)
    diffs = []
    dep = []
    for i in range(sub.height):
        if not np.isfinite(mine["chi"][i]):
            continue
        # H30 inputs for this one row: P, Q, S from the same windows; pool = the same 30 placebos on "other days"
        S = np.full((1, L.K_BASIS, 32), np.nan, np.float32)
        b = bidx[i]
        S[0, b >= 0] = V[b[b >= 0]]
        pm = bidx[i][pmask[i]]
        P = V[pm].mean(0, keepdims=True)
        q = qidx[i][qidx[i] >= 0]
        Q = V[q].mean(0, keepdims=True)
        ids = np.r_[0, np.arange(1, L.N_PL + 1)]
        Ufull = np.vstack([U[i:i + 1], Up[i]])
        meta = pl.DataFrame({"msg": ids, "day": [0] + [1] * L.N_PL, "kind": ["agent"] * (L.N_PL + 1),
                             "targets": [[] for _ in ids]}, schema_overrides={"targets": pl.List(pl.Int64)})
        pairs = pl.DataFrame({"pair": [0], "msg": [0], "agent": [int(recv[i])], "day": [0], "kind": ["agent"]})
        cs = h30lib.content_scores(pairs, P, Q, Ufull, meta, S=S, rng=np.random.default_rng(0))
        diffs.append(float(cs["chi_orth"][0]) - float(mine["chi"][i]))
        Xb = V[b[b >= 0]].astype(np.float64)
        dep.append(bool(np.linalg.svd(Xb.T, compute_uv=False).min() < 1e-6))
    diffs = np.array(diffs)
    dep = np.array(dep)
    # message vectors vs shared statement white32 for agent messages
    ci = pl.read_parquet(L.ED / "chat_index.parquet").with_row_index("src_row").with_columns(pl.col("src_row").cast(pl.UInt32))
    sta = st.filter(pl.col("kind") == "chat").join(ci, on="src_row").join(
        pl.read_parquet(L.SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg"), on="message_id")
    sta = sta.head(500)
    srow_pos = {int(s): k for k, s in enumerate(st["srow"].to_list())}
    vs = V[[srow_pos[int(s)] for s in sta["srow"]]]
    vm = L.message_vectors(sta["msg"].to_numpy().astype(np.int64), regime)
    vec_diff = float(np.nanmax(np.abs(vs - vm)))
    out = dict(period=period, n_compared=int(len(diffs)), max_abs_diff_chi=float(np.abs(diffs).max()) if len(diffs) else None,
               mean_abs_diff_chi=float(np.abs(diffs).mean()) if len(diffs) else None,
               n_exactly_dependent_basis=int(dep.sum()),
               max_abs_diff_chi_independent_basis=float(np.abs(diffs[~dep]).max()) if (~dep).any() else None,
               note="rows whose recent statements contain exact repeats: h30lib's QR basis keeps an arbitrary direction "
                    "there; H52 uses an SVD basis (exact span)", max_abs_diff_msgvec_vs_statement=vec_diff)
    L.jdump(out, L.OUT / "checks" / f"verify_chi_{period}.json")
    print(out)


if __name__ == "__main__":
    main(*(sys.argv[1:2] or ["G44"]))
