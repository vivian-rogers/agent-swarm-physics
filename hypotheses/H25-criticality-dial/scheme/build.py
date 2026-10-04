"""H25 scheme: per-day inputs for the criticality dial (non-holdout days only unless called by confirm.py).

Outputs (data/processed/H25-criticality-dial/inputs/):
  spins.parquet        pt_date, goal_no, regime, minute, agent, state (activity_bins; 1 silent, 2 idle, 3 act, 4 talk)
  statements.parquet   one row per agent chat message: pt_date, goal_no, regime, minute (float, since the day's window
                       start), window (30-min), agent, room, dup (near-copy of an earlier message by the same agent that day,
                       cosine > 0.95 on raw bge vectors; H12 rule)
  statements_vec.npy   row-aligned, per-regime whitened (n = 32, common.load_whitener) and re-normalized, float16
  exo.parquet          exogenous messages (human and `automated` speakers): pt_date, minute, room, kind
  exo_vec.npy          row-aligned whitened unit vectors, float16
  refs.parquet         per period: H19 g_eq active/talk (+SE), H03 n-hat TALK (+CI), fast n_x, n_s, H12 lull fraction
  h38_masks.parquet    H38's per-minute stall table as masks (sched, exo, stall), only if H38 has written it
No text is stored anywhere. Usage: uv run python hypotheses/H25-criticality-dial/scheme/build.py [--data-version fixed]
Round 1b (2026-10-04): --data-version fixed rebuilds only the activity-derived inputs (spins from activity_bins_fixed,
h38_masks from the shared outages_fixed/stall_minutes, refs + the H19 estimator recomputed on the fixed table by H38's
round-1b pipeline) into inputs_r1b/; statements and exogenous messages are unchanged and stay in inputs/.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
if "--data-version" in sys.argv:
    os.environ["H25_DATA_VERSION"] = sys.argv[sys.argv.index("--data-version") + 1]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

INP = C.INPV
DUP_COS = 0.95
H38_STALL_MIN = C.H38_STALLS


def build_spins(cal: pl.DataFrame) -> pl.DataFrame:
    days = cal["pt_date"].to_list()
    ab = (pl.scan_parquet(C.AB).filter(pl.col("pt_date").is_in(days))
          .select("pt_date", pl.col("minute").cast(pl.Int16), "agent", "state").collect())
    return ab.join(cal.select("pt_date", "goal_no", "regime"), on="pt_date").sort("pt_date", "minute", "agent")


def _whiten_rows(rows: np.ndarray, regimes: list[str], raw: np.ndarray) -> np.ndarray:
    out = np.zeros((len(rows), 32), np.float32)
    regs = np.array(regimes)
    for r in np.unique(regs):
        m = regs == r
        W = C.load_whitener(r, 32)
        z = W(raw[rows[m]].astype(np.float32))
        out[m] = z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)
    return out


def build_statements(cal: pl.DataFrame):
    days = cal["pt_date"].to_list()
    raw = np.load(C.SHARED / "embeddings/chat_bge_small.npy", mmap_mode="r")
    st = (pl.read_parquet(C.SHARED / "embeddings/statements.parquet")
          .filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days) & pl.col("agent").is_not_null())
          .join(cal.select("pt_date", "win_start", "goal_no", "regime"), on="pt_date", suffix="_cal")
          .with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 60).alias("minute"))
          .filter(pl.col("minute") >= 0)
          .with_columns((pl.col("minute") // 30).cast(pl.Int16).alias("window"))
          .sort("pt_date", "agent", "t"))
    rows = st["src_row"].to_numpy()
    R = np.asarray(raw[rows], np.float32)
    R /= np.maximum(np.linalg.norm(R, axis=1, keepdims=True), 1e-12)
    dup = np.zeros(len(rows), bool)
    keys = (st["pt_date"] + "|" + st["agent"].cast(pl.String)).to_numpy()
    starts = np.r_[0, np.flatnonzero(keys[1:] != keys[:-1]) + 1, len(keys)]
    for a, b in zip(starts[:-1], starts[1:]):
        X = R[a:b]
        G = X @ X.T
        kept = []
        for j in range(b - a):
            if kept and G[j, kept].max() > DUP_COS:
                dup[a + j] = True
            else:
                kept.append(j)
    V = _whiten_rows(rows, st["regime"].to_list(), raw)
    meta = st.select("pt_date", pl.col("goal_no").cast(pl.Int8), "regime", "minute", "window", "agent", "room",
                     pl.Series("dup", dup), pl.col("t"))
    return meta, V.astype(np.float16)


def build_exo(cal: pl.DataFrame):
    days = cal["pt_date"].to_list()
    raw = np.load(C.SHARED / "embeddings/chat_bge_small.npy", mmap_mode="r")
    idx = pl.read_parquet(C.SHARED / "embeddings/chat_index.parquet").with_row_index("src_row")
    ch = (pl.read_parquet(C.SHARED / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind"])
          .filter(pl.col("speaker_kind").is_in(["human", "automated"]) & pl.col("pt_date").is_in(days))
          .join(idx, on="message_id").join(cal.select("pt_date", "win_start", "regime"), on="pt_date")
          .with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 60).alias("minute"))
          .sort("pt_date", "t"))
    V = _whiten_rows(ch["src_row"].to_numpy(), ch["regime"].to_list(), raw)
    return ch.select("pt_date", "minute", "room", pl.col("speaker_kind").alias("kind")), V.astype(np.float16)


def build_refs() -> pl.DataFrame:
    e = pl.read_parquet(C.PROC / "H19-loop-gain-collapse/estimates.parquet")
    h19 = (e.filter(pl.col("method").is_in(["H19.geq_active", "H19.geq_talk"]))
           .with_columns(pl.col("method").str.replace("H19.geq_", "h19_"))
           .pivot(on="method", index="goal_no", values=["value", "se"]))
    h19 = h19.rename({c: c.replace("value_", "") for c in h19.columns})
    pt = (pl.read_parquet(C.PROC / "H03-self-excited-criticality/period_table.parquet").filter(pl.col("set") == "TALK")
          .select("goal_no", pl.col("n").alias("h03_n_talk"), pl.col("n_prof_lo").alias("h03_n_lo"), pl.col("n_prof_hi").alias("h03_n_hi"),
                  pl.col("n_cross_fast").alias("h03_nx_fast"), pl.col("n_self_fast").alias("h03_ns_fast"), pl.col("tau_cross").alias("h03_tau_cross"),
                  pl.col("N_active").alias("h03_N_active")))
    u = (pl.read_parquet(C.PROC / "H12-groupthink-dimensional-collapse/unit_table.parquet")
         .group_by("goal_no").agg(pl.col("lull_frac").mean().alias("h12_lull_frac")))
    out = h19.join(pt, on="goal_no", how="full", coalesce=True).join(u.with_columns(pl.col("goal_no").cast(pl.Int64)), on="goal_no", how="left").sort("goal_no")
    if C.DATA_VERSION == "fixed":
        out = out.join(h19_fixed(), on="goal_no", how="left")
    return out


def h19_fixed() -> pl.DataFrame:
    """Round 1b: H19's g_eq (active, talk) on activity_bins_fixed. H38's pipeline computes exactly H19's estimator
    (same 5-day chunks, present population, 30-min blocks, pooled suffstats; it reproduces H19's G40 value to 6
    digits on the old table), so its round-1b `raw` variant is the corrected reference. SE: the N1-null SD (H19's
    day bootstrap is not recomputed here)."""
    import json
    rows = []
    for f in sorted((C.PROC / "H38-platform-stalls/r1b").glob("G*/result.json")):
        r = json.loads(f.read_text())
        a = ((r.get("o4") or {}).get("active") or {}).get("raw") or {}
        t = ((r.get("o4") or {}).get("talk") or {}).get("raw") or {}
        rows.append({"goal_no": int(r["goal_no"]), "h19f_active": a.get("g"), "se_h19f_active": a.get("null_sd"),
                     "h19f_talk": t.get("g"), "se_h19f_talk": t.get("null_sd")})
    return pl.DataFrame(rows, schema={"goal_no": pl.Int64, "h19f_active": pl.Float64, "se_h19f_active": pl.Float64,
                                      "h19f_talk": pl.Float64, "se_h19f_talk": pl.Float64})


def build_h38_masks(cal: pl.DataFrame) -> pl.DataFrame | None:
    """H38's per-minute stall table (if written) as minute masks on the activity_bins minute grid.

    sched: village scheduled off (K-independent); exo: sched or an infrastructure-error burst (H38's K-independent
    g_exo mask); stall: H38's explained joint-silence minutes (K <= 1 runs with recorded reasons; K-dependent)."""
    if not H38_STALL_MIN.exists():
        return None
    s = pl.read_parquet(H38_STALL_MIN).filter(pl.col("pt_date").is_in(cal["pt_date"].to_list()) & ~pl.col("holdout"))
    return s.select("pt_date", pl.col("minute").cast(pl.Int16), pl.col("scheduled").alias("sched"),
                    (pl.col("scheduled") | pl.col("infra_burst")).alias("exo"), (pl.col("js") & pl.col("explained")).alias("stall"))


def main():
    cal = C.calendar_nonholdout()
    C.assert_no_holdout(cal["pt_date"], cal["goal_no"])
    INP.mkdir(parents=True, exist_ok=True)
    spins = build_spins(cal)
    spins.write_parquet(INP / "spins.parquet", compression="zstd")
    if C.DATA_VERSION == "fixed":  # statements / exo do not depend on activity_bins: keep inputs/ (round 1)
        meta = pl.read_parquet(C.INP_BASE / "statements.parquet"); ex = pl.read_parquet(C.INP_BASE / "exo.parquet")
    else:
        meta, V = build_statements(cal)
        meta.drop("t").write_parquet(INP / "statements.parquet", compression="zstd")
        np.save(INP / "statements_vec.npy", V)
        ex, EV = build_exo(cal)
        ex.write_parquet(INP / "exo.parquet", compression="zstd")
        np.save(INP / "exo_vec.npy", EV)
    refs = build_refs()
    refs.write_parquet(INP / "refs.parquet")
    out = build_h38_masks(cal)
    if out is not None:
        out.write_parquet(INP / "h38_masks.parquet")
    print(f"spins {spins.height} rows; statements {meta.height} ({meta['dup'].mean():.3f} dup); exo {ex.height}; "
          f"refs {refs.height}; H38 masks {'used' if out is not None else 'absent'}")
    C.write_provenance("scheme_inputs" if C.DATA_VERSION == "r1" else "scheme_inputs_r1b", "hypotheses/H25-criticality-dial/scheme/build.py",
                       [C.AB.name, "calendar", "chat_core", "embeddings/statements", "embeddings/chat_bge_small",
                        "embeddings/chat_index", "embeddings/whitening_*"],
                       {"days": cal.height, "dup_cos": DUP_COS, "whiten_dim": 32, "window_min": 30,
                        "h38_masks": bool(out is not None)},
                       extra_inputs=[{"source": "data/processed/H19-loop-gain-collapse", "tables": ["estimates.parquet"]},
                                     {"source": "data/processed/H03-self-excited-criticality", "tables": ["period_table.parquet"]},
                                     {"source": "data/processed/H12-groupthink-dimensional-collapse", "tables": ["unit_table.parquet"]},
                                     {"source": str(C.H38_STALLS.relative_to(C.ROOT)), "tables": ["stall_minutes.parquet"]}]
                       + ([{"source": "data/processed/H38-platform-stalls/r1b", "tables": ["G*/result.json (H19 estimator on activity_bins_fixed)"]}]
                          if C.DATA_VERSION == "fixed" else []))


if __name__ == "__main__":
    main()
