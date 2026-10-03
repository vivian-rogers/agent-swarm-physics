"""Phase 2b: shared embedding-derived agent states, used by H01, H10, H12, H13 and later ones.

Statements are each agent's own chat messages (speaker_kind == agent) and self-written intentions.
Outputs, in data/processed/shared/embeddings/:
  statements.parquet                          one row per statement: kind, src_row, agent, t, pt_date, goal_no,
                                              regime, room, holdout, win30
  agent_day.parquet  + agent_day_vec.npy      normalized mean raw embedding per agent x pt_date (+ counts)
  agent_win30.parquet + agent_win30_vec.npy   same per agent x 30-min window of the day's activity window
  whitening_<regime>.npz                      mean, top-128 PCA components and eigenvalues per regime,
                                              fitted on NON-HOLDOUT statements only
Vectors are raw normalized means (fp16). Whiten downstream with common.load_whitener(regime, dim); center
before comparing agents (embedding anisotropy, physics-models/11). Holdout days are included as measurements
and flagged in `holdout`; never fit anything on them during exploration.

Usage: uv run python infra/shared/build_agent_vectors.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, write_provenance  # noqa: E402

ED = OUT / "embeddings"
N_COMP = 128


def group_means(E: np.ndarray, gid: np.ndarray, n_groups: int) -> np.ndarray:
    order = np.argsort(gid, kind="stable")
    g = gid[order]
    starts = np.r_[0, np.flatnonzero(np.diff(g)) + 1]
    sums = np.add.reduceat(E[order], starts, axis=0)
    out = np.zeros((n_groups, E.shape[1]), dtype=np.float32)
    out[g[starts]] = sums
    norm = np.linalg.norm(out, axis=1, keepdims=True)
    return (out / np.where(norm > 0, norm, 1)).astype(np.float16)


def main():
    t0 = time.time()
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "win_start", "goal_no", "regime", "holdout"]) \
            .with_columns(pl.col("regime").cast(pl.String))
    chat = (pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "agent"])
            .filter(pl.col("speaker_kind") == "agent")
            .join(pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row"), on="message_id")
            .select(pl.lit("chat").alias("kind"), "src_row", "agent", "t", "pt_date", "room"))
    intent = (pl.read_parquet(OUT / "intentions.parquet", columns=["event_index", "t", "agent"])
              .join(pl.read_parquet(ED / "intentions_index.parquet").with_row_index("src_row"), on="event_index")
              .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"),
                            pl.lit(None, dtype=pl.Int8).alias("room"))
              .select(pl.lit("intent").alias("kind"), "src_row", "agent", "t", "pt_date", "room"))
    st = pl.concat([chat, intent.with_columns(pl.col("room").cast(chat.schema["room"]))])
    n_all = st.height
    st = st.join(cal, on="pt_date", how="inner")
    st = st.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).cast(pl.Int16).alias("win30")) \
           .with_columns(pl.when(pl.col("win30") >= 0).then(pl.col("win30")).alias("win30")) \
           .drop("win_start").sort("t")
    print(f"statements: {st.height} of {n_all} on calendar days ({st.filter(pl.col('kind') == 'chat').height} chat)", flush=True)

    Ec = np.load(ED / "chat_bge_small.npy")
    Ei = np.load(ED / "intentions_bge_small.npy")
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy()
    E = np.empty((st.height, Ec.shape[1]), dtype=np.float32)
    m = kind == "chat"
    E[m] = Ec[src[m]]; E[~m] = Ei[src[~m]]
    del Ec, Ei
    st.write_parquet(ED / "statements.parquet", compression="zstd")

    for name, keys in (("agent_day", ["agent", "pt_date"]), ("agent_win30", ["agent", "pt_date", "win30"])):
        sub = st if name == "agent_day" else st.filter(pl.col("win30").is_not_null())
        idx = np.flatnonzero(st["win30"].is_not_null().to_numpy()) if name == "agent_win30" else np.arange(st.height)
        grp = (sub.group_by(keys, maintain_order=True)
               .agg(pl.col("goal_no").first(), pl.col("regime").first(), pl.col("holdout").first(),
                    (pl.col("kind") == "chat").sum().alias("n_chat"), (pl.col("kind") == "intent").sum().alias("n_intent"))
               .sort(keys).with_row_index("gid"))
        gid = sub.join(grp.select(*keys, "gid"), on=keys, how="left")["gid"].to_numpy()
        V = group_means(E[idx], gid, grp.height)
        np.save(ED / f"{name}_vec.npy", V)
        grp.write_parquet(ED / f"{name}.parquet", compression="zstd")
        print(f"{name}: {grp.height} rows", flush=True)

    hold = st["holdout"].to_numpy(); reg = st["regime"].to_numpy()
    for r in sorted(set(reg)):
        sel = (reg == r) & ~hold
        X = E[sel]; mu = X.mean(0)
        C = np.cov((X - mu).T, bias=True)
        w, U = np.linalg.eigh(C)
        o = np.argsort(w)[::-1][:N_COMP]
        np.savez(ED / f"whitening_{r}.npz", mean=mu.astype(np.float32), components=U[:, o].astype(np.float32),
                 eigenvalues=w[o].astype(np.float32), n=int(sel.sum()))
        print(f"whitening {r}: n={sel.sum()}, top-5 eigenvalue share {w[o][:5].sum() / w.sum():.3f}", flush=True)
    write_provenance("build_agent_vectors", ["embeddings/*_bge_small.npy", "chat_core", "intentions", "calendar"],
                     {"statements": "agent chat + intentions", "window_min": 30, "whitening_components": N_COMP,
                      "whitening_fit": "non-holdout statements per regime"})
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
