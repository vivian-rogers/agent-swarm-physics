"""H20 round 1b inputs (improved data, 2026-10-04). Writes data/processed/H20-content-aging/r1b/ and leaves the round-1
files (statements.parquet, stmt_w64.npy, goal_raw.npy, goal_dirs.parquet) untouched, so the old path still runs.

What changes:
  * goal directions from the shared goal fields (embeddings/goals.parquet, goal_fields.py) instead of H01's
    goals_raw.npy (H01's #38 room-2/3 kickoff rows are swapped and its kickoff spans differ by 15-56 deg in #36-#42);
    H20's rule is kept: g = unit(unit(W goal) + unit(mean_rooms unit(W kickoff_room))), agent goals for #51;
  * a second embedding model (gte-modernbert, DQ5), whitened 64-d in its own regime basis;
  * DQ5 statement flags for dedupe (copies = self_repeat_both; restatements = either model's self_repeat);
  * style-residualized (within goal period) 32-d statement vectors for both models.

Outputs (no text):
  r1b/statements.parquet         the round-1 H20 rows in the same order + srow (shared statements row) + flags
  r1b/stmt_w64_<model>.npy       (n, 64) fp16 whitened coordinates (bge = round-1 stmt_w64 values, recomputed)
  r1b/stmt_sr32_<model>.npy      (n, 32) fp16 style-residualized vectors (shared, unit-normalized)
  r1b/goal_raw_<model>.npy + r1b/goal_dirs.parquet   shared goal / kickoff_room / agent_goal raw vectors
  r1b/check.json                 row alignment, bge identity check, cosine of the H01-derived vs shared goal directions
Usage: uv run python hypotheses/H20-content-aging/scheme/build_r1b.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20common as hc  # noqa: E402  (thread caps)

import json  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import embed_models as EM  # noqa: E402  (h20common put infra/shared on sys.path)

R1B = hc.OUT / "r1b"
MODELS = ("bge_small", "gte_modernbert")


def unit(x):
    x = np.asarray(x, dtype=np.float64)
    return x / max(np.linalg.norm(x), 1e-12)


def ghat(raw_goal, raw_kicks, W):
    parts = []
    if raw_goal is not None:
        parts.append(unit(W(raw_goal[None])[0]))
    if raw_kicks is not None and len(raw_kicks):
        parts.append(unit(np.mean([unit(x) for x in W(raw_kicks)], axis=0)))
    return unit(np.sum(parts, axis=0)) if parts else None


def main():
    R1B.mkdir(parents=True, exist_ok=True)
    held = hc.held_out_goals()
    days = pl.read_parquet(hc.OUT / "days.parquet")
    st = pl.read_parquet(hc.ED / "statements.parquet").with_row_index("srow")
    st = st.filter(~pl.col("holdout") & (pl.col("agent") != hc.CLAUDE_CODE_AGENT) & (pl.col("goal_no") > 0)
                   & ~pl.col("goal_no").is_in(list(held)))
    st = st.join(days.select("goal_no", "pt_date", "d", "d_cal"), on=["goal_no", "pt_date"], how="inner")
    old = pl.read_parquet(hc.OUT / "statements.parquet")
    # round 1 sorted by t (not stable for ties); recover its exact order by matching (t, agent, kind) and a tie rank
    key = ["t", "agent", "kind"]
    st = st.sort(key + ["srow"]).with_columns(pl.int_range(pl.len()).over(key).alias("_r"))
    old = old.with_row_index("orow").with_columns(pl.int_range(pl.len()).over(key).alias("_r"))
    m = old.join(st.select(key + ["_r", "srow"]), on=key + ["_r"], how="left").sort("orow")
    assert m["srow"].null_count() == 0 and m.height == st.height, (m["srow"].null_count(), m.height, st.height)
    srow = m["srow"].to_numpy().astype(np.int64)
    check = {"n_rows": int(m.height)}

    fl = pl.read_parquet(EM.OUT / "statement_flags.parquet",
                         columns=["srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "cross_echo_both"]).sort("srow")
    assert (fl["srow"].to_numpy() == np.arange(fl.height)).all()
    f = fl[srow].drop("srow")
    out = m.drop("orow", "_r").with_columns(pl.Series("srow", srow.astype(np.uint32))).hstack(f)
    out.write_parquet(R1B / "statements.parquet", compression="zstd")
    check["flag_rates"] = {c: float(f[c].mean()) for c in f.columns}

    reg = out["regime"].to_numpy()
    for mdl in MODELS:
        E = EM.statement_embeddings(mdl)
        Z = np.zeros((out.height, 64), dtype=np.float16)
        for r in sorted(set(reg)):
            W = EM.load_whitener(r, 64, mdl)
            sel = np.flatnonzero(reg == r)
            for a in range(0, sel.size, 20000):
                s = sel[a:a + 20000]
                Z[s] = W(E[srow[s]]).astype(np.float16)
        np.save(R1B / f"stmt_w64_{mdl}.npy", Z)
        if mdl == "bge_small":
            Z0 = np.load(hc.OUT / "stmt_w64.npy", mmap_mode="r")
            dif = np.abs(np.asarray(Z0, np.float32) - Z.astype(np.float32)).max(1)
            check["bge_max_abs_diff_vs_round1"] = float(dif.max())
            check["bge_rows_differing"] = int((dif > 1e-2).sum())
        del E
        S = np.load(EM.ED / f"statements_style_resid_period32_{EM.MODELS[mdl]['suffix']}.npy", mmap_mode="r")
        np.save(R1B / f"stmt_sr32_{mdl}.npy", np.asarray(S[srow], dtype=np.float16))

    # shared goal fields: goal, kickoff_room (per room; H20 averages rooms), agent_goal
    gm = (pl.read_parquet(EM.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
          .filter(~pl.col("holdout") & ~pl.col("goal_no").is_in(list(held))
                  & pl.col("kind").is_in(["goal", "kickoff_room", "agent_goal"])).sort("gid"))
    for mdl in MODELS:
        V = EM.goal_vectors(mdl).astype(np.float32)
        np.save(R1B / f"goal_raw_{mdl}.npy", V[gm["gid"].to_numpy()])
    gm2 = gm.with_columns(pl.when(pl.col("kind") == "kickoff_room").then(pl.lit("kickoff")).otherwise(pl.col("kind")).alias("kind"))
    gm2 = gm2.with_row_index("row")
    gm2.select("row", "gid", "goal_no", "kind", "room", "agent", "valid_from", "valid_to", "regime") \
       .write_parquet(R1B / "goal_dirs.parquet", compression="zstd")

    # compare H01-derived (round 1) and shared goal directions, bge, n = 32
    m0 = pl.read_parquet(hc.OUT / "goal_dirs.parquet"); r0 = np.load(hc.OUT / "goal_raw.npy")
    r1 = np.load(R1B / "goal_raw_bge_small.npy")
    cmp = {}
    for g in sorted(set(m0["goal_no"].to_list()) & set(gm2["goal_no"].to_list())):
        rg = m0.filter(pl.col("goal_no") == g)["regime"][0]
        W = EM.load_whitener(rg, 32, "bge_small")
        a = m0.filter(pl.col("goal_no") == g); b = gm2.filter(pl.col("goal_no") == g)
        ga = ghat(r0[a.filter(pl.col("kind") == "goal")["row"].to_list()].mean(0) if a.filter(pl.col("kind") == "goal").height else None,
                  r0[a.filter(pl.col("kind") == "kickoff")["row"].to_list()], W)
        gb = ghat(r1[b.filter(pl.col("kind") == "goal")["row"].to_list()].mean(0) if b.filter(pl.col("kind") == "goal").height else None,
                  r1[b.filter(pl.col("kind") == "kickoff")["row"].to_list()], W)
        if ga is not None and gb is not None:
            cmp[int(g)] = round(float(ga @ gb), 4)
    check["ghat_cos_round1_vs_shared_n32"] = cmp
    check["ghat_cos_min"] = min(cmp.values())
    (R1B / "check.json").write_text(json.dumps(check, indent=1))
    hc.write_provenance({"models": list(MODELS), "dim": 64, "goal_fields": "shared goals.parquet (goal, kickoff_room, agent_goal)",
                         "flags": "shared statement_flags", "style": "statements_style_resid_period32_<model>"},
                        ["shared/embeddings/statements", "shared/embeddings/*_gte_modernbert.npy",
                         "shared/embeddings/whitening_gte_modernbert_*", "shared/statement_flags",
                         "shared/embeddings/goals + goal_vectors*", "shared/embeddings/statements_style_resid_period32_*"],
                        "hypotheses/H20-content-aging/scheme/build_r1b.py")
    print(json.dumps({k: v for k, v in check.items() if k != "ghat_cos_round1_vs_shared_n32"}, indent=1))
    print("ghat cos (round1 vs shared):", cmp)


if __name__ == "__main__":
    main()
